from __future__ import annotations

import torch

from pcgno_dt.evaluation.comparison import evaluate_prediction
from pcgno_dt.uq.calibration import empirical_crps, predictive_interval, predictive_sharpness


def test_empirical_crps_and_sharpness_are_finite() -> None:
    target = torch.zeros(2, 3, 1)
    samples = torch.stack(
        [
            target - 0.1,
            target,
            target + 0.1,
        ],
        dim=1,
    )
    crps = empirical_crps(samples, target)
    sharpness = predictive_sharpness(samples)

    assert torch.isfinite(crps)
    assert torch.isfinite(sharpness)
    assert crps.item() >= 0.0
    assert sharpness.item() > 0.0


def test_evaluate_prediction_reports_uq_diagnostics() -> None:
    target = torch.zeros(2, 4, 1)
    prediction = torch.zeros_like(target)
    samples = torch.stack([target - 0.2, target + 0.2], dim=1)
    lower, upper = predictive_interval(samples)
    metrics = evaluate_prediction(
        prediction,
        target,
        samples=samples,
        logvar=torch.zeros_like(target),
    )

    assert lower.shape == target.shape
    assert upper.shape == target.shape
    assert "crps" in metrics
    assert "sharpness" in metrics
    assert "interval_width_95" in metrics
    assert "gaussian_nll" in metrics
