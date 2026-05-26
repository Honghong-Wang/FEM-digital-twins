from __future__ import annotations

import torch


def predictive_interval(samples: torch.Tensor, level: float = 0.95) -> tuple[torch.Tensor, torch.Tensor]:
    if samples.ndim < 2:
        raise ValueError("samples must include a sample dimension at dim=1")
    alpha = (1.0 - level) / 2.0
    lower = torch.quantile(samples, alpha, dim=1)
    upper = torch.quantile(samples, 1.0 - alpha, dim=1)
    return lower, upper


def coverage_probability(
    lower: torch.Tensor,
    upper: torch.Tensor,
    target: torch.Tensor,
    mask: torch.Tensor | None = None,
) -> torch.Tensor:
    covered = ((target >= lower) & (target <= upper)).float()
    if mask is None:
        return covered.mean()
    while mask.ndim < target.ndim:
        mask = mask.unsqueeze(1)
    mask = mask.to(device=target.device, dtype=target.dtype).expand_as(target)
    return (covered * mask).sum() / mask.sum().clamp_min(1.0)


def expected_calibration_error(
    samples: torch.Tensor,
    target: torch.Tensor,
    levels: tuple[float, ...] = (0.5, 0.8, 0.9, 0.95),
    mask: torch.Tensor | None = None,
) -> torch.Tensor:
    errors = []
    for level in levels:
        lower, upper = predictive_interval(samples, level=level)
        errors.append((coverage_probability(lower, upper, target, mask=mask) - level).abs())
    return torch.stack(errors).mean()


def empirical_crps(
    samples: torch.Tensor,
    target: torch.Tensor,
    mask: torch.Tensor | None = None,
) -> torch.Tensor:
    """Monte-Carlo CRPS estimate for ensemble samples.

    `samples` has shape `[batch, samples, points, fields]` and target has shape
    `[batch, points, fields]`.
    """

    if samples.ndim != target.ndim + 1:
        raise ValueError("samples must have one extra sample dimension after batch")
    absolute_error = (samples - target.unsqueeze(1)).abs().mean(dim=1)
    pairwise_distance = (samples.unsqueeze(2) - samples.unsqueeze(1)).abs().mean(dim=(1, 2))
    crps = absolute_error - 0.5 * pairwise_distance
    return _masked_mean(crps, mask)


def predictive_sharpness(samples: torch.Tensor, mask: torch.Tensor | None = None) -> torch.Tensor:
    """Mean predictive standard deviation."""

    if samples.ndim < 2:
        raise ValueError("samples must include a sample dimension at dim=1")
    std = samples.std(dim=1, unbiased=False)
    return _masked_mean(std, mask)


def interval_width(
    lower: torch.Tensor,
    upper: torch.Tensor,
    mask: torch.Tensor | None = None,
) -> torch.Tensor:
    """Mean predictive interval width."""

    return _masked_mean((upper - lower).abs(), mask)


def gaussian_negative_log_likelihood(
    mean: torch.Tensor, logvar: torch.Tensor, target: torch.Tensor
) -> torch.Tensor:
    constant = torch.as_tensor(2.0 * torch.pi, device=mean.device, dtype=mean.dtype).log()
    return 0.5 * (constant + logvar + (target - mean).square() / torch.exp(logvar))


def masked_gaussian_negative_log_likelihood(
    mean: torch.Tensor,
    logvar: torch.Tensor,
    target: torch.Tensor,
    mask: torch.Tensor | None = None,
) -> torch.Tensor:
    return _masked_mean(gaussian_negative_log_likelihood(mean, logvar, target), mask)


def _masked_mean(values: torch.Tensor, mask: torch.Tensor | None = None) -> torch.Tensor:
    if mask is None:
        return values.mean()
    while mask.ndim < values.ndim:
        mask = mask.unsqueeze(1)
    mask = mask.to(device=values.device, dtype=values.dtype).expand_as(values)
    return (values * mask).sum() / mask.sum().clamp_min(1.0)
