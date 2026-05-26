from __future__ import annotations

import torch


def relative_l2(
    prediction: torch.Tensor,
    target: torch.Tensor,
    eps: float = 1.0e-12,
    mask: torch.Tensor | None = None,
) -> torch.Tensor:
    """Compute batch-wise relative L2 error."""

    if mask is None:
        numerator = torch.linalg.vector_norm(prediction - target, dim=tuple(range(1, prediction.ndim)))
        denominator = torch.linalg.vector_norm(target, dim=tuple(range(1, target.ndim))).clamp_min(eps)
        return numerator / denominator

    mask = _broadcast_mask(mask, prediction)
    numerator = ((prediction - target).square() * mask).sum(dim=tuple(range(1, prediction.ndim))).sqrt()
    denominator = (target.square() * mask).sum(dim=tuple(range(1, target.ndim))).sqrt().clamp_min(eps)
    return numerator / denominator


def interval_coverage(
    lower: torch.Tensor,
    upper: torch.Tensor,
    target: torch.Tensor,
    mask: torch.Tensor | None = None,
) -> torch.Tensor:
    """Fraction of targets inside predictive intervals."""

    covered = (target >= lower) & (target <= upper)
    if mask is None:
        return covered.float().mean()
    mask = _broadcast_mask(mask, target)
    return (covered.float() * mask).sum() / mask.sum().clamp_min(1.0)


def masked_max_abs_error(
    prediction: torch.Tensor,
    target: torch.Tensor,
    mask: torch.Tensor | None = None,
) -> torch.Tensor:
    error = (prediction - target).abs()
    if mask is None:
        return error.amax()
    mask = _broadcast_mask(mask, error)
    return (error * mask).amax()


def _broadcast_mask(mask: torch.Tensor, reference: torch.Tensor) -> torch.Tensor:
    while mask.ndim < reference.ndim:
        mask = mask.unsqueeze(1)
    return mask.to(device=reference.device, dtype=reference.dtype).expand_as(reference)
