from __future__ import annotations

from dataclasses import dataclass

import torch
import torch.nn.functional as F

from pcgno_dt.physics.protocols import OperatorProblem


@dataclass(frozen=True)
class PhysicsLossWeights:
    data: float = 1.0
    pde_residual: float = 0.1
    boundary: float = 0.1
    energy: float = 0.01
    calibration: float = 0.01
    thermodynamic: float = 0.01
    normalize_physics: bool = False
    data_loss_mode: str = "nll"
    eps: float = 1.0e-12


def gaussian_nll(mean: torch.Tensor, logvar: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
    return 0.5 * (logvar + (target - mean).square() / torch.exp(logvar)).mean()


def physics_constrained_loss(
    outputs: dict[str, torch.Tensor],
    batch: dict[str, torch.Tensor],
    problem: OperatorProblem,
    weights: PhysicsLossWeights = PhysicsLossWeights(),
) -> dict[str, torch.Tensor]:
    prediction_full = outputs.get("mean")
    if prediction_full is None:
        raise KeyError("outputs must contain a 'mean' tensor")
    active_params = problem.num_parameters
    active_fields = problem.num_fields
    prediction = prediction_full[..., :active_fields]
    target = batch["fields"][..., :active_fields]
    params = batch["params"][..., :active_params]
    forcing = batch["forcing"][..., :active_fields]

    logvar_full = outputs.get("logvar")
    if logvar_full is None:
        logvar = None
    else:
        logvar = logvar_full[..., :active_fields]

    _set_problem_batch_context(problem, batch)
    try:
        return _physics_constrained_loss_active(
            prediction=prediction,
            logvar=logvar,
            target=target,
            params=params,
            forcing=forcing,
            problem=problem,
            weights=weights,
        )
    finally:
        _clear_problem_batch_context(problem)


def multifamily_physics_constrained_loss(
    outputs: dict[str, torch.Tensor],
    batch: dict[str, torch.Tensor],
    problems_by_family: dict[int, OperatorProblem],
    weights: PhysicsLossWeights = PhysicsLossWeights(),
) -> dict[str, torch.Tensor]:
    """Compute physics-constrained loss for a batch containing multiple problem families."""

    if "family_id" not in batch:
        raise KeyError("multi-family batches must contain a 'family_id' tensor")
    total_items = batch["family_id"].numel()
    if total_items == 0:
        raise ValueError("empty multi-family batch")

    accumulated: dict[str, torch.Tensor] = {}
    for family_id, problem in problems_by_family.items():
        mask = batch["family_id"] == family_id
        if not torch.any(mask):
            continue
        sub_outputs = {
            key: value[mask]
            for key, value in outputs.items()
            if isinstance(value, torch.Tensor) and value.shape[0] == total_items
        }
        sub_batch = {
            key: value[mask]
            for key, value in batch.items()
            if isinstance(value, torch.Tensor) and value.shape[0] == total_items
        }
        losses = physics_constrained_loss(sub_outputs, sub_batch, problem, weights)
        scale = mask.float().mean()
        for key, value in losses.items():
            accumulated[key] = accumulated.get(key, value.new_tensor(0.0)) + scale * value
    if not accumulated:
        raise ValueError("none of the batch family ids matched problems_by_family")
    return accumulated


def _physics_constrained_loss_active(
    prediction: torch.Tensor,
    logvar: torch.Tensor | None,
    target: torch.Tensor,
    params: torch.Tensor,
    forcing: torch.Tensor,
    problem: OperatorProblem,
    weights: PhysicsLossWeights,
) -> dict[str, torch.Tensor]:
    field_mask = None
    # The active path receives sliced tensors, so the mask is all ones. This helper exists to
    # centralize the loss terms used by both single-family and multi-family training.
    del field_mask
    if prediction is None:
        raise KeyError("outputs must contain a 'mean' tensor")
    if weights.data_loss_mode not in {"nll", "mse"}:
        raise ValueError("data_loss_mode must be 'nll' or 'mse'")

    if logvar is None or weights.data_loss_mode == "mse":
        data_loss = F.mse_loss(prediction, target)
    else:
        data_loss = gaussian_nll(prediction, logvar, target)
    if logvar is None:
        calibration_loss = prediction.new_tensor(0.0)
    else:
        calibration_loss = F.mse_loss(torch.exp(logvar), (target - prediction).detach().square())

    residual = problem.residual(params, prediction, forcing=forcing)
    residual_for_loss = residual if getattr(problem, "use_full_residual", False) else residual[:, 1:-1, :]
    boundary_residual = problem.boundary_residual(params, prediction)
    energy_error = (problem.energy(params, prediction, forcing) - problem.energy(params, target, forcing))
    if weights.normalize_physics:
        residual_for_loss = residual_for_loss / _rms_scale(forcing, weights.eps)
        boundary_residual = boundary_residual / _rms_scale(target, weights.eps)
        energy_error = energy_error / _energy_scale(problem, params, target, forcing, weights.eps)
    pde_loss = residual_for_loss.square().mean()
    boundary_loss = boundary_residual.square().mean()
    energy_loss = energy_error.square().mean()
    thermo_loss = problem.thermodynamic_penalty(params)

    total = (
        weights.data * data_loss
        + weights.pde_residual * pde_loss
        + weights.boundary * boundary_loss
        + weights.energy * energy_loss
        + weights.calibration * calibration_loss
        + weights.thermodynamic * thermo_loss
    )
    return {
        "total": total,
        "data": data_loss,
        "pde_residual": pde_loss,
        "boundary": boundary_loss,
        "energy": energy_loss,
        "calibration": calibration_loss,
        "thermodynamic": thermo_loss,
    }


def _rms_scale(values: torch.Tensor, eps: float) -> torch.Tensor:
    return values.square().mean().sqrt().clamp_min(eps)


def _energy_scale(
    problem: OperatorProblem,
    params: torch.Tensor,
    target: torch.Tensor,
    forcing: torch.Tensor,
    eps: float,
) -> torch.Tensor:
    reference_energy = problem.energy(params, target, forcing).detach().abs().mean()
    return reference_energy.clamp_min(eps)


def _set_problem_batch_context(problem: OperatorProblem, batch: dict[str, torch.Tensor]) -> None:
    setter = getattr(problem, "set_batch_context", None)
    if callable(setter):
        setter(batch)


def _clear_problem_batch_context(problem: OperatorProblem) -> None:
    clearer = getattr(problem, "clear_batch_context", None)
    if callable(clearer):
        clearer()
