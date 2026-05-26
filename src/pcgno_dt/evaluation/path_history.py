from __future__ import annotations

import torch


def evaluate_j2_path_history_consistency(
    batch: dict[str, torch.Tensor],
    eps: float = 1.0e-12,
) -> dict[str, torch.Tensor]:
    """Evaluate thermodynamic irreversibility diagnostics for J2 history sequences."""

    if "material_history_sequence" not in batch:
        raise KeyError("batch must contain material_history_sequence")
    history = batch["material_history_sequence"]
    if history.ndim != 4 or history.shape[-1] < 5:
        raise ValueError("material_history_sequence must have shape [batch, steps, elements, >=5]")

    eq_plastic_strain = history[..., 0]
    plastic_work = history[..., 1]
    plastic_multiplier_increment = history[..., 2]
    yielded = history[..., 3]

    eqp_drop = torch.relu(eq_plastic_strain[:, :-1] - eq_plastic_strain[:, 1:]) if history.shape[1] > 1 else history.new_zeros(())
    work_drop = torch.relu(plastic_work[:, :-1] - plastic_work[:, 1:]) if history.shape[1] > 1 else history.new_zeros(())
    negative_multiplier = torch.relu(-plastic_multiplier_increment)
    yield_flag_low = torch.relu(-yielded)
    yield_flag_high = torch.relu(yielded - 1.0)

    metrics = {
        "eq_plastic_strain_monotonic_violation": eqp_drop.mean(),
        "plastic_work_monotonic_violation": work_drop.mean(),
        "negative_plastic_multiplier_violation": negative_multiplier.mean(),
        "yield_flag_bounds_violation": (yield_flag_low + yield_flag_high).mean(),
        "max_eq_plastic_strain": eq_plastic_strain.max(),
        "mean_plastic_work": plastic_work.mean(),
    }
    if "newton_residual_sequence" in batch:
        residual = batch["newton_residual_sequence"]
        metrics["path_newton_residual_rms"] = residual.square().mean().sqrt()
        forcing = batch.get("forcing_sequence")
        if forcing is not None:
            metrics["path_newton_residual_relative"] = metrics["path_newton_residual_rms"] / forcing.square().mean().sqrt().clamp_min(eps)
    params = batch.get("params")
    if params is not None and params.ndim == 2 and params.shape[-1] >= 4:
        yield_stress = params[:, None, None, 2].clamp_min(eps)
        hardening = params[:, None, None, 3].clamp_min(0.0)
        flow_stress = yield_stress + hardening * eq_plastic_strain.clamp_min(0.0)
        von_mises = history[..., 4]
        yield_surface_residual = yielded.clamp(0.0, 1.0) * (von_mises - flow_stress)
        elastic_overstress = (1.0 - yielded.clamp(0.0, 1.0)) * torch.relu(von_mises - flow_stress)
        metrics["yield_surface_relative_rms"] = (
            yield_surface_residual.square().mean().sqrt() / flow_stress.square().mean().sqrt().clamp_min(eps)
        )
        metrics["elastic_overstress_relative_violation"] = (
            elastic_overstress.square().mean().sqrt() / flow_stress.square().mean().sqrt().clamp_min(eps)
        )
        if history.shape[1] > 1:
            eqp_increment = eq_plastic_strain[:, 1:] - eq_plastic_strain[:, :-1]
            work_increment = plastic_work[:, 1:] - plastic_work[:, :-1]
            flow_previous = yield_stress + hardening * eq_plastic_strain[:, :-1].clamp_min(0.0)
            work_lower_bound_violation = torch.relu(flow_previous * torch.relu(eqp_increment) - work_increment)
            work_lower_bound_rms = work_lower_bound_violation.square().mean().sqrt()
            target_history = batch.get("target_material_history_sequence")
            if target_history is not None and target_history.ndim == 4 and target_history.shape[-1] > 1:
                target_work_increment = target_history[..., 1][:, 1:] - target_history[..., 1][:, :-1]
            else:
                target_work_increment = work_increment
            metrics["plastic_work_lower_bound_absolute_violation"] = work_lower_bound_rms
            metrics["plastic_work_lower_bound_target_normalized_violation"] = (
                work_lower_bound_rms / target_work_increment.square().mean().sqrt().clamp_min(eps)
            )
            metrics["plastic_work_lower_bound_relative_violation"] = (
                work_lower_bound_rms / work_increment.square().mean().sqrt().clamp_min(eps)
            )
    return metrics


def evaluate_reversal_memory_errors(
    predicted_history: torch.Tensor,
    target_history: torch.Tensor,
    forcing_sequence: torch.Tensor,
    eps: float = 1.0e-12,
) -> dict[str, torch.Tensor]:
    """Evaluate history-increment errors at load-path reversal steps."""

    if predicted_history.shape != target_history.shape:
        raise ValueError("predicted_history and target_history must share shape")
    if predicted_history.ndim != 4:
        raise ValueError("history tensors must have shape [batch, steps, elements, history_dim]")
    reversal_mask = load_reversal_mask(forcing_sequence, eps=eps)
    zero = predicted_history.new_tensor(0.0)
    if reversal_mask.numel() == 0:
        return {
            "reversal_fraction": zero,
            "reversal_history_increment_relative_l2": zero,
            "reversal_eqp_increment_relative_l2": zero,
            "reversal_plastic_work_increment_relative_l2": zero,
            "reversal_yield_flag_mae": zero,
        }
    history_increment_prediction = predicted_history[:, 1:] - predicted_history[:, :-1]
    history_increment_target = target_history[:, 1:] - target_history[:, :-1]
    aligned_prediction = history_increment_prediction[:, 1:]
    aligned_target = history_increment_target[:, 1:]
    metrics = {
        "reversal_fraction": reversal_mask.float().mean(),
        "reversal_history_increment_relative_l2": _masked_relative_rmse(
            aligned_prediction,
            aligned_target,
            reversal_mask,
            eps,
        ),
        "reversal_eqp_increment_relative_l2": _masked_relative_rmse(
            aligned_prediction[..., 0],
            aligned_target[..., 0],
            reversal_mask,
            eps,
        ),
        "reversal_plastic_work_increment_relative_l2": _masked_relative_rmse(
            aligned_prediction[..., 1],
            aligned_target[..., 1],
            reversal_mask,
            eps,
        ),
    }
    if predicted_history.shape[-1] > 3:
        metrics["reversal_yield_flag_mae"] = _masked_mae(
            predicted_history[:, 2:, :, 3],
            target_history[:, 2:, :, 3],
            reversal_mask,
            eps,
        )
    return metrics


def evaluate_qp_reversal_memory_errors(
    predicted_qp_history: torch.Tensor,
    target_qp_history: torch.Tensor,
    forcing_sequence: torch.Tensor,
    eps: float = 1.0e-12,
) -> dict[str, torch.Tensor]:
    """QP-level reversal diagnostics for plastic scalar memory.

    The returned metrics isolate the region that matters most for cyclic memory:
    active integration points at load reversal steps. This prevents a large inactive
    elastic majority from hiding collapse in yielded QPs.
    """

    if predicted_qp_history.shape != target_qp_history.shape:
        raise ValueError("predicted_qp_history and target_qp_history must share shape")
    if predicted_qp_history.ndim != 5:
        raise ValueError("QP history tensors must have shape [batch, steps, elements, q_points, history_dim]")
    reversal_mask = load_reversal_mask(forcing_sequence, eps=eps)
    zero = predicted_qp_history.new_tensor(0.0)
    if reversal_mask.numel() == 0 or predicted_qp_history.shape[-1] < 4:
        return {
            "qp_reversal_fraction": zero,
            "qp_reversal_active_fraction": zero,
            "qp_reversal_plastic_scalar_increment_relative_l2": zero,
            "qp_reversal_eqp_increment_relative_l2": zero,
            "qp_reversal_plastic_work_increment_relative_l2": zero,
            "qp_reversal_yield_flag_mae": zero,
            "qp_inactive_false_plasticity": zero,
        }
    prediction_increment = predicted_qp_history[:, 1:] - predicted_qp_history[:, :-1]
    target_increment = target_qp_history[:, 1:] - target_qp_history[:, :-1]
    aligned_prediction = prediction_increment[:, 1:]
    aligned_target = target_increment[:, 1:]
    active_qp_mask = _plastic_active_mask(target_qp_history[:, 2:], eps)
    combined_mask = _combine_reversal_and_qp_masks(reversal_mask, active_qp_mask)
    inactive_mask = ~_plastic_active_mask(target_qp_history, eps)
    metrics = {
        "qp_reversal_fraction": reversal_mask.float().mean(),
        "qp_reversal_active_fraction": combined_mask.float().mean() if combined_mask.numel() else zero,
        "qp_reversal_plastic_scalar_increment_relative_l2": _masked_relative_rmse(
            aligned_prediction[..., :4],
            aligned_target[..., :4],
            combined_mask,
            eps,
        ),
        "qp_reversal_eqp_increment_relative_l2": _masked_relative_rmse(
            aligned_prediction[..., 0],
            aligned_target[..., 0],
            combined_mask,
            eps,
        ),
        "qp_reversal_plastic_work_increment_relative_l2": _masked_relative_rmse(
            aligned_prediction[..., 1],
            aligned_target[..., 1],
            combined_mask,
            eps,
        ),
        "qp_reversal_yield_flag_mae": _masked_mae(
            predicted_qp_history[:, 2:, ..., 3],
            target_qp_history[:, 2:, ..., 3],
            combined_mask,
            eps,
        ),
        "qp_inactive_false_plasticity": _inactive_false_plasticity_score(
            predicted_qp_history,
            inactive_mask,
            eps,
        ),
    }
    if predicted_qp_history.shape[-1] > 4:
        metrics["qp_reversal_von_mises_relative_l2"] = _masked_relative_rmse(
            predicted_qp_history[:, 2:, ..., 4],
            target_qp_history[:, 2:, ..., 4],
            combined_mask,
            eps,
        )
    return metrics


def load_reversal_mask(forcing_sequence: torch.Tensor, eps: float = 1.0e-12) -> torch.Tensor:
    """Return a [batch, steps - 2] mask for sign/direction changes in global load increments."""

    if forcing_sequence.ndim != 4 or forcing_sequence.shape[1] < 3:
        return forcing_sequence.new_zeros(forcing_sequence.shape[0], 0, dtype=torch.bool)
    global_force = forcing_sequence.sum(dim=2)
    increments = global_force[:, 1:] - global_force[:, :-1]
    previous = increments[:, :-1]
    current = increments[:, 1:]
    dot = (previous * current).sum(dim=-1)
    active = previous.square().sum(dim=-1).sqrt() * current.square().sum(dim=-1).sqrt()
    return (dot < 0.0) & (active > eps)


def _masked_relative_rmse(
    prediction: torch.Tensor,
    target: torch.Tensor,
    mask: torch.Tensor,
    eps: float,
) -> torch.Tensor:
    if mask.numel() == 0 or not torch.any(mask):
        return prediction.new_tensor(0.0)
    expanded_mask = mask
    while expanded_mask.ndim < prediction.ndim:
        expanded_mask = expanded_mask.unsqueeze(-1)
    weights = expanded_mask.to(dtype=prediction.dtype)
    error = (prediction - target) * weights
    target_masked = target * weights
    return error.square().sum().sqrt() / target_masked.square().sum().sqrt().clamp_min(eps)


def _masked_mae(
    prediction: torch.Tensor,
    target: torch.Tensor,
    mask: torch.Tensor,
    eps: float,
) -> torch.Tensor:
    if mask.numel() == 0 or not torch.any(mask):
        return prediction.new_tensor(0.0)
    expanded_mask = mask
    while expanded_mask.ndim < prediction.ndim:
        expanded_mask = expanded_mask.unsqueeze(-1)
    weights = expanded_mask.to(dtype=prediction.dtype)
    expanded_weights = weights.expand_as(prediction)
    return ((prediction - target).abs() * expanded_weights).sum() / expanded_weights.sum().clamp_min(eps)


def _plastic_active_mask(target_history: torch.Tensor, eps: float) -> torch.Tensor:
    if target_history.shape[-1] < 4:
        return target_history.new_ones(target_history.shape[:-1], dtype=torch.bool)
    return (
        (target_history[..., 0].abs() > eps)
        | (target_history[..., 2].abs() > eps)
        | (target_history[..., 3] > 0.5)
    )


def _combine_reversal_and_qp_masks(
    reversal_mask: torch.Tensor,
    qp_active_mask: torch.Tensor,
) -> torch.Tensor:
    while reversal_mask.ndim < qp_active_mask.ndim:
        reversal_mask = reversal_mask.unsqueeze(-1)
    return qp_active_mask & reversal_mask


def _inactive_false_plasticity_score(
    predicted_qp_history: torch.Tensor,
    inactive_mask: torch.Tensor,
    eps: float,
) -> torch.Tensor:
    if inactive_mask.numel() == 0 or not torch.any(inactive_mask) or predicted_qp_history.shape[-1] < 4:
        return predicted_qp_history.new_tensor(0.0)
    predicted = predicted_qp_history[..., :4][inactive_mask].clamp_min(0.0)
    return predicted.square().mean().sqrt() / predicted_qp_history.new_tensor(1.0).clamp_min(eps)
