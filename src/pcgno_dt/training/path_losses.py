from __future__ import annotations

from dataclasses import dataclass

import torch
import torch.nn.functional as F


@dataclass(frozen=True)
class PathLossWeights:
    displacement: float = 1.0
    history: float = 1.0
    qp_history: float = 0.0
    qp_history_channel: float = 0.0
    qp_history_active: float = 0.0
    qp_plastic_scalar_active: float = 0.0
    qp_plastic_scalar_increment_active: float = 0.0
    qp_inactive_false_plasticity: float = 0.0
    qp_reversal_plastic_increment_active: float = 0.0
    qp_history_topk: float = 0.0
    qp_history_increment_topk: float = 0.0
    qp_reversal_topk_increment: float = 0.0
    qp_plastic_log_active: float = 0.0
    history_increment: float = 0.0
    qp_history_increment: float = 0.0
    qp_history_increment_channel: float = 0.0
    qp_history_increment_active: float = 0.0
    qp_yield_flag: float = 0.0
    eqp_increment: float = 0.0
    plastic_work_increment: float = 0.0
    yield_flag: float = 0.0
    yield_surface: float = 0.0
    elastic_overstress: float = 0.0
    plastic_work_lower_bound: float = 0.0
    hano_strain: float = 0.0
    hano_stress: float = 0.0
    calibration: float = 0.01
    eqp_monotonicity: float = 0.1
    plastic_work_monotonicity: float = 0.1
    plastic_multiplier_nonnegative: float = 0.1
    yield_bounds: float = 0.1
    normalize: bool = True
    eps: float = 1.0e-12
    qp_active_mask_mode: str = "accumulated"
    qp_topk_fraction: float = 0.10


def history_graph_operator_loss(
    outputs: dict[str, torch.Tensor],
    batch: dict[str, torch.Tensor],
    weights: PathLossWeights = PathLossWeights(),
) -> dict[str, torch.Tensor]:
    """Loss for recurrent path-dependent operator models."""

    if "mean_sequence" not in outputs:
        raise KeyError("outputs must contain mean_sequence")
    if "history_sequence" not in outputs:
        raise KeyError("outputs must contain history_sequence")
    target_fields = batch["fields_sequence"]
    history_for_loss = outputs.get("history_prediction_sequence", outputs["history_sequence"])
    target_history = batch["material_history_sequence"][..., : history_for_loss.shape[-1]]
    prediction = outputs["mean_sequence"]
    history = history_for_loss
    qp_history = outputs.get("history_qp_prediction_sequence", outputs.get("history_qp_sequence"))
    target_qp_history = batch.get("material_history_qp_sequence")
    if prediction.shape != target_fields.shape:
        raise ValueError(f"mean_sequence shape {tuple(prediction.shape)} does not match target {tuple(target_fields.shape)}")
    if history.shape != target_history.shape:
        raise ValueError(f"history_sequence shape {tuple(history.shape)} does not match target {tuple(target_history.shape)}")

    displacement_error = prediction - target_fields
    history_error = history - target_history
    if weights.normalize:
        displacement_loss = displacement_error.square().mean() / _scale(target_fields, weights.eps).square()
        history_loss = history_error.square().mean() / _scale(target_history, weights.eps).square()
    else:
        displacement_loss = displacement_error.square().mean()
        history_loss = history_error.square().mean()
    history_increment_loss = _increment_loss(history, target_history, weights.eps, weights.normalize)
    if qp_history is not None and target_qp_history is not None:
        target_qp_history = target_qp_history[..., : qp_history.shape[-1]]
        if qp_history.shape != target_qp_history.shape:
            raise ValueError(
                f"history_qp_sequence shape {tuple(qp_history.shape)} does not match target {tuple(target_qp_history.shape)}"
            )
        qp_history_error = qp_history - target_qp_history
        if weights.normalize:
            qp_history_loss = qp_history_error.square().mean() / _scale(target_qp_history, weights.eps).square()
        else:
            qp_history_loss = qp_history_error.square().mean()
        qp_history_increment_loss = _increment_loss(qp_history, target_qp_history, weights.eps, weights.normalize)
        qp_history_channel_loss = _channel_balanced_loss(
            qp_history,
            target_qp_history,
            weights.eps,
            weights.normalize,
        )
        qp_history_increment_channel_loss = _channel_balanced_loss(
            _increments(qp_history),
            _increments(target_qp_history),
            weights.eps,
            weights.normalize,
        )
        active_mask = _plastic_active_mask(target_qp_history, weights.eps, weights.qp_active_mask_mode)
        increment_active_mask = _plastic_increment_active_mask(
            target_qp_history,
            weights.eps,
            weights.qp_active_mask_mode,
        )
        qp_history_active_loss = _masked_channel_balanced_loss(
            qp_history,
            target_qp_history,
            active_mask,
            weights.eps,
            weights.normalize,
        )
        qp_plastic_scalar_active_loss = _masked_plastic_scalar_loss(
            qp_history,
            target_qp_history,
            active_mask,
            weights.eps,
            weights.normalize,
        )
        qp_history_increment_active_loss = _masked_channel_balanced_loss(
            _increments(qp_history),
            _increments(target_qp_history),
            increment_active_mask,
            weights.eps,
            weights.normalize,
        )
        qp_plastic_scalar_increment_active_loss = _masked_plastic_scalar_loss(
            _increments(qp_history),
            _increments(target_qp_history),
            increment_active_mask,
            weights.eps,
            weights.normalize,
        )
        qp_inactive_false_plasticity_loss = _inactive_false_plasticity_loss(
            qp_history,
            target_qp_history,
            active_mask,
            weights.eps,
            weights.normalize,
        )
        topk_mask = _plastic_topk_mask(target_qp_history, weights.qp_topk_fraction, weights.eps)
        increment_topk_mask = _plastic_increment_topk_mask(
            target_qp_history,
            weights.qp_topk_fraction,
            weights.eps,
        )
        qp_history_topk_loss = _masked_channel_balanced_loss(
            qp_history,
            target_qp_history,
            topk_mask,
            weights.eps,
            weights.normalize,
        )
        qp_history_increment_topk_loss = _masked_channel_balanced_loss(
            _increments(qp_history),
            _increments(target_qp_history),
            increment_topk_mask,
            weights.eps,
            weights.normalize,
        )
        qp_plastic_log_active_loss = _masked_plastic_log_loss(
            qp_history,
            target_qp_history,
            topk_mask | active_mask,
            weights.eps,
        )
        qp_reversal_plastic_increment_active_loss = _reversal_plastic_increment_loss(
            qp_history,
            target_qp_history,
            batch.get("forcing_sequence"),
            weights.eps,
            weights.normalize,
            weights.qp_active_mask_mode,
        )
        qp_reversal_topk_increment_loss = _reversal_topk_increment_loss(
            qp_history,
            target_qp_history,
            batch.get("forcing_sequence"),
            weights.qp_topk_fraction,
            weights.eps,
            weights.normalize,
        )
        if qp_history.shape[-1] >= 4:
            qp_yield_flag_loss = F.binary_cross_entropy(
                qp_history[..., 3].clamp(0.0, 1.0),
                target_qp_history[..., 3].clamp(0.0, 1.0),
            )
        else:
            qp_yield_flag_loss = prediction.new_tensor(0.0)
    else:
        qp_history_loss = prediction.new_tensor(0.0)
        qp_history_increment_loss = prediction.new_tensor(0.0)
        qp_history_channel_loss = prediction.new_tensor(0.0)
        qp_history_increment_channel_loss = prediction.new_tensor(0.0)
        qp_history_active_loss = prediction.new_tensor(0.0)
        qp_plastic_scalar_active_loss = prediction.new_tensor(0.0)
        qp_plastic_scalar_increment_active_loss = prediction.new_tensor(0.0)
        qp_inactive_false_plasticity_loss = prediction.new_tensor(0.0)
        qp_reversal_plastic_increment_active_loss = prediction.new_tensor(0.0)
        qp_history_topk_loss = prediction.new_tensor(0.0)
        qp_history_increment_topk_loss = prediction.new_tensor(0.0)
        qp_reversal_topk_increment_loss = prediction.new_tensor(0.0)
        qp_plastic_log_active_loss = prediction.new_tensor(0.0)
        qp_history_increment_active_loss = prediction.new_tensor(0.0)
        qp_yield_flag_loss = prediction.new_tensor(0.0)
    if history.shape[-1] >= 1:
        eqp_increment_loss = _increment_loss(history[..., 0], target_history[..., 0], weights.eps, weights.normalize)
    else:
        eqp_increment_loss = prediction.new_tensor(0.0)
    if history.shape[-1] >= 2:
        plastic_work_increment_loss = _increment_loss(
            history[..., 1],
            target_history[..., 1],
            weights.eps,
            weights.normalize,
        )
    else:
        plastic_work_increment_loss = prediction.new_tensor(0.0)
    if history.shape[-1] >= 4:
        yield_flag_loss = F.binary_cross_entropy(
            history[..., 3].clamp(0.0, 1.0),
            target_history[..., 3].clamp(0.0, 1.0),
        )
    else:
        yield_flag_loss = prediction.new_tensor(0.0)
    thermo_constraints = j2_thermodynamic_consistency_losses(
        history,
        target_history,
        batch.get("params"),
        eps=weights.eps,
        normalize=weights.normalize,
    )

    logvar = outputs.get("logvar_sequence")
    if logvar is None:
        calibration_loss = prediction.new_tensor(0.0)
    else:
        calibration_loss = F.mse_loss(torch.exp(logvar), displacement_error.detach().square())
    hano_strain_loss, hano_stress_loss = _hano_observable_losses(outputs, batch, weights.eps, weights.normalize)

    constraints = history_irreversibility_losses(history)
    total = (
        weights.displacement * displacement_loss
        + weights.history * history_loss
        + weights.qp_history * qp_history_loss
        + weights.qp_history_channel * qp_history_channel_loss
        + weights.qp_history_active * qp_history_active_loss
        + weights.qp_plastic_scalar_active * qp_plastic_scalar_active_loss
        + weights.qp_plastic_scalar_increment_active * qp_plastic_scalar_increment_active_loss
        + weights.qp_inactive_false_plasticity * qp_inactive_false_plasticity_loss
        + weights.qp_reversal_plastic_increment_active * qp_reversal_plastic_increment_active_loss
        + weights.qp_history_topk * qp_history_topk_loss
        + weights.qp_history_increment_topk * qp_history_increment_topk_loss
        + weights.qp_reversal_topk_increment * qp_reversal_topk_increment_loss
        + weights.qp_plastic_log_active * qp_plastic_log_active_loss
        + weights.history_increment * history_increment_loss
        + weights.qp_history_increment * qp_history_increment_loss
        + weights.qp_history_increment_channel * qp_history_increment_channel_loss
        + weights.qp_history_increment_active * qp_history_increment_active_loss
        + weights.qp_yield_flag * qp_yield_flag_loss
        + weights.eqp_increment * eqp_increment_loss
        + weights.plastic_work_increment * plastic_work_increment_loss
        + weights.yield_flag * yield_flag_loss
        + weights.yield_surface * thermo_constraints["yield_surface"]
        + weights.elastic_overstress * thermo_constraints["elastic_overstress"]
        + weights.plastic_work_lower_bound * thermo_constraints["plastic_work_lower_bound"]
        + weights.hano_strain * hano_strain_loss
        + weights.hano_stress * hano_stress_loss
        + weights.calibration * calibration_loss
        + weights.eqp_monotonicity * constraints["eqp_monotonicity"]
        + weights.plastic_work_monotonicity * constraints["plastic_work_monotonicity"]
        + weights.plastic_multiplier_nonnegative * constraints["plastic_multiplier_nonnegative"]
        + weights.yield_bounds * constraints["yield_bounds"]
    )
    return {
        "total": total,
        "displacement": displacement_loss,
        "history": history_loss,
        "qp_history": qp_history_loss,
        "qp_history_channel": qp_history_channel_loss,
        "qp_history_active": qp_history_active_loss,
        "qp_plastic_scalar_active": qp_plastic_scalar_active_loss,
        "qp_plastic_scalar_increment_active": qp_plastic_scalar_increment_active_loss,
        "qp_inactive_false_plasticity": qp_inactive_false_plasticity_loss,
        "qp_reversal_plastic_increment_active": qp_reversal_plastic_increment_active_loss,
        "qp_history_topk": qp_history_topk_loss,
        "qp_history_increment_topk": qp_history_increment_topk_loss,
        "qp_reversal_topk_increment": qp_reversal_topk_increment_loss,
        "qp_plastic_log_active": qp_plastic_log_active_loss,
        "history_increment": history_increment_loss,
        "qp_history_increment": qp_history_increment_loss,
        "qp_history_increment_channel": qp_history_increment_channel_loss,
        "qp_history_increment_active": qp_history_increment_active_loss,
        "qp_yield_flag": qp_yield_flag_loss,
        "eqp_increment": eqp_increment_loss,
        "plastic_work_increment": plastic_work_increment_loss,
        "yield_flag": yield_flag_loss,
        **thermo_constraints,
        "hano_strain": hano_strain_loss,
        "hano_stress": hano_stress_loss,
        "calibration": calibration_loss,
        **constraints,
    }


def _hano_observable_losses(
    outputs: dict[str, torch.Tensor],
    batch: dict[str, torch.Tensor],
    eps: float,
    normalize: bool,
) -> tuple[torch.Tensor, torch.Tensor]:
    prediction = outputs["mean_sequence"]
    strain = outputs.get("hano_strain_sequence")
    stress = outputs.get("hano_stress_sequence")
    target_strain = batch.get("strain_sequence")
    target_stress = batch.get("stress_sequence")
    zero = prediction.new_tensor(0.0)
    strain_loss = zero
    stress_loss = zero
    if strain is not None and target_strain is not None:
        target_strain = target_strain[..., : strain.shape[-1]]
        if strain.shape != target_strain.shape:
            raise ValueError(
                f"hano_strain_sequence shape {tuple(strain.shape)} does not match target {tuple(target_strain.shape)}"
            )
        strain_loss = (strain - target_strain).square().mean()
        if normalize:
            strain_loss = strain_loss / _scale(target_strain, eps).square()
    if stress is not None and target_stress is not None:
        target_stress = target_stress[..., : stress.shape[-1]]
        if stress.shape != target_stress.shape:
            raise ValueError(
                f"hano_stress_sequence shape {tuple(stress.shape)} does not match target {tuple(target_stress.shape)}"
            )
        stress_loss = (stress - target_stress).square().mean()
        if normalize:
            stress_loss = stress_loss / _scale(target_stress, eps).square()
    return strain_loss, stress_loss


def history_irreversibility_losses(history_sequence: torch.Tensor) -> dict[str, torch.Tensor]:
    if history_sequence.ndim != 4 or history_sequence.shape[-1] < 5:
        zero = history_sequence.new_tensor(0.0)
        return {
            "eqp_monotonicity": zero,
            "plastic_work_monotonicity": zero,
            "plastic_multiplier_nonnegative": zero,
            "yield_bounds": zero,
        }
    eqp = history_sequence[..., 0]
    plastic_work = history_sequence[..., 1]
    delta_gamma = history_sequence[..., 2]
    yield_flag = history_sequence[..., 3]
    if history_sequence.shape[1] > 1:
        eqp_loss = torch.relu(eqp[:, :-1] - eqp[:, 1:]).square().mean()
        work_loss = torch.relu(plastic_work[:, :-1] - plastic_work[:, 1:]).square().mean()
    else:
        eqp_loss = history_sequence.new_tensor(0.0)
        work_loss = history_sequence.new_tensor(0.0)
    return {
        "eqp_monotonicity": eqp_loss,
        "plastic_work_monotonicity": work_loss,
        "plastic_multiplier_nonnegative": torch.relu(-delta_gamma).square().mean(),
        "yield_bounds": (torch.relu(-yield_flag).square() + torch.relu(yield_flag - 1.0).square()).mean(),
    }


def j2_thermodynamic_consistency_losses(
    history_sequence: torch.Tensor,
    target_history_sequence: torch.Tensor,
    params: torch.Tensor | None,
    eps: float = 1.0e-12,
    normalize: bool = True,
) -> dict[str, torch.Tensor]:
    """J2-specific consistency losses tied to yield stress, hardening, and plastic work.

    Parameter order follows the local J2 exporter:
    [young_modulus, poisson_ratio, yield_stress, hardening_modulus, traction_x, traction_y].
    """

    zero = history_sequence.new_tensor(0.0)
    if history_sequence.ndim != 4 or history_sequence.shape[-1] < 5:
        return {"yield_surface": zero, "elastic_overstress": zero, "plastic_work_lower_bound": zero}
    if params is None or params.ndim != 2 or params.shape[-1] < 4:
        return {"yield_surface": zero, "elastic_overstress": zero, "plastic_work_lower_bound": zero}

    eqp = history_sequence[..., 0]
    plastic_work = history_sequence[..., 1]
    yield_flag_target = target_history_sequence[..., 3].detach().clamp(0.0, 1.0)
    von_mises = history_sequence[..., 4]
    yield_stress = params[:, None, None, 2].clamp_min(eps)
    hardening = params[:, None, None, 3].clamp_min(0.0)
    flow_stress = yield_stress + hardening * eqp.clamp_min(0.0)

    yield_surface_residual = yield_flag_target * (von_mises - flow_stress)
    elastic_overstress = (1.0 - yield_flag_target) * torch.relu(von_mises - flow_stress)
    if normalize:
        surface_scale = _scale(flow_stress, eps).square()
        yield_surface_loss = yield_surface_residual.square().mean() / surface_scale
        elastic_overstress_loss = elastic_overstress.square().mean() / surface_scale
    else:
        yield_surface_loss = yield_surface_residual.square().mean()
        elastic_overstress_loss = elastic_overstress.square().mean()

    if history_sequence.shape[1] < 2:
        work_lower_bound_loss = zero
    else:
        eqp_increment = eqp[:, 1:] - eqp[:, :-1]
        work_increment = plastic_work[:, 1:] - plastic_work[:, :-1]
        flow_stress_previous = yield_stress + hardening * eqp[:, :-1].clamp_min(0.0)
        work_lower_bound_violation = torch.relu(flow_stress_previous * torch.relu(eqp_increment) - work_increment)
        work_lower_bound_loss = work_lower_bound_violation.square().mean()
        if normalize:
            target_work_increment = target_history_sequence[..., 1][:, 1:] - target_history_sequence[..., 1][:, :-1]
            lower_bound_reference = flow_stress_previous.detach() * torch.relu(
                target_history_sequence[..., 0][:, 1:] - target_history_sequence[..., 0][:, :-1]
            )
            work_scale = torch.maximum(lower_bound_reference.abs(), target_work_increment.detach().abs())
            work_lower_bound_loss = work_lower_bound_loss / _scale(work_scale, eps).square()

    return {
        "yield_surface": yield_surface_loss,
        "elastic_overstress": elastic_overstress_loss,
        "plastic_work_lower_bound": work_lower_bound_loss,
    }


def _scale(values: torch.Tensor, eps: float) -> torch.Tensor:
    return values.detach().square().mean().sqrt().clamp_min(eps)


def _increments(values: torch.Tensor) -> torch.Tensor:
    if values.shape[1] < 2:
        return values[:, :0]
    return values[:, 1:] - values[:, :-1]


def _increment_loss(
    prediction: torch.Tensor,
    target: torch.Tensor,
    eps: float,
    normalize: bool,
) -> torch.Tensor:
    prediction_increment = _increments(prediction)
    target_increment = _increments(target)
    if prediction_increment.numel() == 0:
        return prediction.new_tensor(0.0)
    loss = (prediction_increment - target_increment).square().mean()
    if normalize:
        loss = loss / _scale(target_increment, eps).square()
    return loss


def _channel_balanced_loss(
    prediction: torch.Tensor,
    target: torch.Tensor,
    eps: float,
    normalize: bool,
) -> torch.Tensor:
    if prediction.numel() == 0:
        return prediction.new_tensor(0.0)
    error = prediction - target
    reduce_dims = tuple(range(error.ndim - 1))
    channel_loss = error.square().mean(dim=reduce_dims)
    if normalize:
        channel_scale = target.detach().square().mean(dim=reduce_dims).sqrt().clamp_min(eps)
        channel_loss = channel_loss / channel_scale.square()
    return channel_loss.mean()


def _plastic_active_mask(target_history: torch.Tensor, eps: float, mode: str = "accumulated") -> torch.Tensor:
    if target_history.shape[-1] < 4:
        return target_history.new_ones(target_history.shape[:-1], dtype=torch.bool)
    current_plastic = (target_history[..., 2].abs() > eps) | (target_history[..., 3] > 0.5)
    if mode in {"current", "increment", "current_increment"}:
        return current_plastic
    if mode in {"accumulated_or_current", "accumulated"}:
        return (target_history[..., 0].abs() > eps) | current_plastic
    raise ValueError(f"unknown qp_active_mask_mode: {mode}")


def _plastic_increment_active_mask(
    target_history: torch.Tensor,
    eps: float,
    mode: str = "accumulated",
) -> torch.Tensor:
    if target_history.shape[1] < 2:
        shape = target_history.shape[:1] + (0,) + target_history.shape[2:-1]
        return target_history.new_zeros(shape, dtype=torch.bool)
    if target_history.shape[-1] < 4:
        shape = target_history.shape[:1] + (target_history.shape[1] - 1,) + target_history.shape[2:-1]
        return target_history.new_ones(shape, dtype=torch.bool)
    if mode in {"current", "increment", "current_increment"}:
        increment = _increments(target_history)
        return (
            (increment[..., 0].abs() > eps)
            | (increment[..., 1].abs() > eps)
            | (increment[..., 2].abs() > eps)
            | (target_history[:, 1:, ..., 3] > 0.5)
        )
    if mode in {"accumulated_or_current", "accumulated"}:
        return _plastic_active_mask(target_history[:, 1:], eps, mode)
    raise ValueError(f"unknown qp_active_mask_mode: {mode}")


def _masked_channel_balanced_loss(
    prediction: torch.Tensor,
    target: torch.Tensor,
    mask: torch.Tensor,
    eps: float,
    normalize: bool,
) -> torch.Tensor:
    if prediction.numel() == 0 or mask.numel() == 0 or not bool(mask.any()):
        return prediction.new_tensor(0.0)
    selected_prediction = prediction[mask]
    selected_target = target[mask]
    channel_loss = (selected_prediction - selected_target).square().mean(dim=0)
    if normalize:
        channel_scale = selected_target.detach().square().mean(dim=0).sqrt().clamp_min(eps)
        channel_loss = channel_loss / channel_scale.square()
    return channel_loss.mean()


def _masked_plastic_scalar_loss(
    prediction: torch.Tensor,
    target: torch.Tensor,
    mask: torch.Tensor,
    eps: float,
    normalize: bool,
) -> torch.Tensor:
    if prediction.numel() == 0 or prediction.shape[-1] < 4:
        return prediction.new_tensor(0.0)
    scalar_channels = prediction.new_tensor([0, 1, 2, 3], dtype=torch.long)
    return _masked_channel_balanced_loss(
        prediction.index_select(dim=-1, index=scalar_channels),
        target.index_select(dim=-1, index=scalar_channels),
        mask,
        eps,
        normalize,
    )


def _masked_plastic_log_loss(
    prediction: torch.Tensor,
    target: torch.Tensor,
    mask: torch.Tensor,
    eps: float,
) -> torch.Tensor:
    if prediction.numel() == 0 or prediction.shape[-1] < 5 or mask.numel() == 0 or not bool(mask.any()):
        return prediction.new_tensor(0.0)
    scalar_channels = prediction.new_tensor([0, 1, 2, 4], dtype=torch.long)
    selected_prediction = prediction.index_select(dim=-1, index=scalar_channels)[mask].clamp_min(0.0)
    selected_target = target.index_select(dim=-1, index=scalar_channels)[mask].clamp_min(0.0)
    scale = selected_target.detach().mean(dim=0).clamp_min(eps)
    return (torch.log1p(selected_prediction / scale) - torch.log1p(selected_target / scale)).square().mean()


def _plastic_topk_mask(target_history: torch.Tensor, fraction: float, eps: float) -> torch.Tensor:
    if target_history.shape[-1] < 4:
        return target_history.new_ones(target_history.shape[:-1], dtype=torch.bool)
    fraction = float(max(min(fraction, 1.0), 0.0))
    if fraction <= 0.0:
        return target_history.new_zeros(target_history.shape[:-1], dtype=torch.bool)
    score = (
        target_history[..., 0].abs()
        + target_history[..., 1].abs()
        + target_history[..., 2].abs()
        + target_history[..., 3].clamp(0.0, 1.0)
    )
    return _top_fraction_mask(score, fraction, eps)


def _plastic_increment_topk_mask(target_history: torch.Tensor, fraction: float, eps: float) -> torch.Tensor:
    if target_history.shape[1] < 2:
        shape = target_history.shape[:1] + (0,) + target_history.shape[2:-1]
        return target_history.new_zeros(shape, dtype=torch.bool)
    if target_history.shape[-1] < 4:
        shape = target_history.shape[:1] + (target_history.shape[1] - 1,) + target_history.shape[2:-1]
        return target_history.new_ones(shape, dtype=torch.bool)
    increment = _increments(target_history)
    score = (
        increment[..., 0].abs()
        + increment[..., 1].abs()
        + increment[..., 2].abs()
        + target_history[:, 1:, ..., 3].clamp(0.0, 1.0)
    )
    return _top_fraction_mask(score, fraction, eps)


def _top_fraction_mask(score: torch.Tensor, fraction: float, eps: float) -> torch.Tensor:
    if score.numel() == 0:
        return score.new_zeros(score.shape, dtype=torch.bool)
    flat = score.detach().reshape(-1)
    active = flat > eps
    if not bool(active.any()):
        return score.new_zeros(score.shape, dtype=torch.bool)
    active_values = flat[active]
    k = max(1, int(round(float(active_values.numel()) * float(fraction))))
    k = min(k, int(active_values.numel()))
    threshold = torch.topk(active_values, k=k, largest=True).values[-1]
    return score >= threshold


def _inactive_false_plasticity_loss(
    prediction: torch.Tensor,
    target: torch.Tensor,
    active_mask: torch.Tensor,
    eps: float,
    normalize: bool,
) -> torch.Tensor:
    if prediction.numel() == 0 or prediction.shape[-1] < 4:
        return prediction.new_tensor(0.0)
    inactive_mask = ~active_mask
    if inactive_mask.numel() == 0 or not bool(inactive_mask.any()):
        return prediction.new_tensor(0.0)
    predicted_plastic = torch.stack(
        [
            prediction[..., 0].clamp_min(0.0),
            prediction[..., 1].clamp_min(0.0),
            prediction[..., 2].clamp_min(0.0),
            prediction[..., 3].clamp(0.0, 1.0),
        ],
        dim=-1,
    )
    selected = predicted_plastic[inactive_mask]
    loss = selected.square().mean()
    if normalize:
        target_reference = target[..., :4][inactive_mask].detach().abs().mean().clamp_min(eps)
        loss = loss / torch.maximum(target_reference, prediction.new_tensor(1.0)).square()
    return loss


def _reversal_plastic_increment_loss(
    prediction: torch.Tensor,
    target: torch.Tensor,
    forcing_sequence: torch.Tensor | None,
    eps: float,
    normalize: bool,
    active_mask_mode: str = "accumulated",
) -> torch.Tensor:
    if (
        forcing_sequence is None
        or prediction.shape[1] < 3
        or prediction.shape[-1] < 4
        or target.shape != prediction.shape
    ):
        return prediction.new_tensor(0.0)
    reversal_mask = _load_reversal_mask(forcing_sequence, eps)
    if reversal_mask.numel() == 0 or not bool(reversal_mask.any()):
        return prediction.new_tensor(0.0)
    prediction_increment = _increments(prediction)[:, 1:, ..., :4]
    target_increment = _increments(target)[:, 1:, ..., :4]
    active_mask = _plastic_increment_active_mask(target, eps, active_mask_mode)[:, 1:]
    while reversal_mask.ndim < active_mask.ndim:
        reversal_mask = reversal_mask.unsqueeze(-1)
    combined_mask = active_mask & reversal_mask
    if not bool(combined_mask.any()):
        return prediction.new_tensor(0.0)
    selected_prediction = prediction_increment[combined_mask]
    selected_target = target_increment[combined_mask]
    channel_loss = (selected_prediction - selected_target).square().mean(dim=0)
    if normalize:
        channel_scale = selected_target.detach().square().mean(dim=0).sqrt().clamp_min(eps)
        channel_loss = channel_loss / channel_scale.square()
    return channel_loss.mean()


def _reversal_topk_increment_loss(
    prediction: torch.Tensor,
    target: torch.Tensor,
    forcing_sequence: torch.Tensor | None,
    topk_fraction: float,
    eps: float,
    normalize: bool,
) -> torch.Tensor:
    if (
        forcing_sequence is None
        or prediction.shape[1] < 3
        or prediction.shape[-1] < 4
        or target.shape != prediction.shape
    ):
        return prediction.new_tensor(0.0)
    reversal_mask = _load_reversal_mask(forcing_sequence, eps)
    if reversal_mask.numel() == 0 or not bool(reversal_mask.any()):
        return prediction.new_tensor(0.0)
    topk_mask = _plastic_increment_topk_mask(target, topk_fraction, eps)[:, 1:]
    while reversal_mask.ndim < topk_mask.ndim:
        reversal_mask = reversal_mask.unsqueeze(-1)
    combined_mask = topk_mask & reversal_mask
    if not bool(combined_mask.any()):
        return prediction.new_tensor(0.0)
    prediction_increment = _increments(prediction)[:, 1:]
    target_increment = _increments(target)[:, 1:]
    return _masked_channel_balanced_loss(
        prediction_increment,
        target_increment,
        combined_mask,
        eps,
        normalize,
    )


def _load_reversal_mask(forcing_sequence: torch.Tensor, eps: float) -> torch.Tensor:
    if forcing_sequence.ndim != 4 or forcing_sequence.shape[1] < 3:
        return forcing_sequence.new_zeros(forcing_sequence.shape[0], 0, dtype=torch.bool)
    global_force = forcing_sequence.sum(dim=2)
    increments = global_force[:, 1:] - global_force[:, :-1]
    previous = increments[:, :-1]
    current = increments[:, 1:]
    dot = (previous * current).sum(dim=-1)
    active = previous.square().sum(dim=-1).sqrt() * current.square().sum(dim=-1).sqrt()
    return (dot < 0.0) & (active > eps)
