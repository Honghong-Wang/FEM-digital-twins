from __future__ import annotations

import torch

from pcgno_dt.evaluation.metrics import interval_coverage, masked_max_abs_error, relative_l2
from pcgno_dt.uq.calibration import (
    empirical_crps,
    expected_calibration_error,
    interval_width,
    masked_gaussian_negative_log_likelihood,
    predictive_interval,
    predictive_sharpness,
)


def evaluate_prediction(
    prediction: torch.Tensor,
    target: torch.Tensor,
    samples: torch.Tensor | None = None,
    logvar: torch.Tensor | None = None,
    field_mask: torch.Tensor | None = None,
) -> dict[str, torch.Tensor]:
    metrics = {
        "relative_l2": relative_l2(prediction, target, mask=field_mask).mean(),
        "max_abs_error": masked_max_abs_error(prediction, target, mask=field_mask),
    }
    if samples is not None:
        lower, upper = predictive_interval(samples)
        metrics["coverage_95"] = interval_coverage(lower, upper, target, mask=field_mask)
        metrics["ece"] = expected_calibration_error(samples, target, mask=field_mask)
        metrics["crps"] = empirical_crps(samples, target, mask=field_mask)
        metrics["sharpness"] = predictive_sharpness(samples, mask=field_mask)
        metrics["interval_width_95"] = interval_width(lower, upper, mask=field_mask)
    if logvar is not None:
        metrics["gaussian_nll"] = masked_gaussian_negative_log_likelihood(
            prediction,
            logvar,
            target,
            mask=field_mask,
        )
    return metrics
