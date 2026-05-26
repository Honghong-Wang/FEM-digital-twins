from __future__ import annotations

import torch

from pcgno_dt.physics.protocols import OperatorProblem


def evaluate_physics_consistency(
    prediction: torch.Tensor,
    batch: dict[str, torch.Tensor],
    problem: OperatorProblem,
    eps: float = 1.0e-12,
) -> dict[str, torch.Tensor]:
    """Evaluate FEM/PDE residual, boundary violation, and energy consistency."""

    params = batch["params"][..., : problem.num_parameters]
    target = batch["fields"][..., : problem.num_fields]
    forcing = batch["forcing"][..., : problem.num_fields]
    prediction = prediction[..., : problem.num_fields]

    _set_problem_batch_context(problem, batch)
    try:
        residual = problem.residual(params, prediction, forcing=forcing)
        residual_for_metric = residual if getattr(problem, "use_full_residual", False) else residual[:, 1:-1, :]
        boundary = problem.boundary_residual(params, prediction)
        energy_error = problem.energy(params, prediction, forcing) - problem.energy(params, target, forcing)

        forcing_scale = forcing.square().mean().sqrt().clamp_min(eps)
        field_scale = target.square().mean().sqrt().clamp_min(eps)
        energy_scale = problem.energy(params, target, forcing).detach().abs().mean().clamp_min(eps)
    finally:
        _clear_problem_batch_context(problem)

    return {
        "pde_residual_rms": residual_for_metric.square().mean().sqrt(),
        "pde_residual_relative": residual_for_metric.square().mean().sqrt() / forcing_scale,
        "boundary_rms": boundary.square().mean().sqrt(),
        "boundary_relative": boundary.square().mean().sqrt() / field_scale,
        "energy_error_relative": energy_error.abs().mean() / energy_scale,
    }


def _set_problem_batch_context(problem: OperatorProblem, batch: dict[str, torch.Tensor]) -> None:
    setter = getattr(problem, "set_batch_context", None)
    if callable(setter):
        setter(batch)


def _clear_problem_batch_context(problem: OperatorProblem) -> None:
    clearer = getattr(problem, "clear_batch_context", None)
    if callable(clearer):
        clearer()
