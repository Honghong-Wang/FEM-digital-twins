from __future__ import annotations

import torch
from torch import nn

from pcgno_dt.inverse.path_digital_twin import (
    PathStateInversionConfig,
    PosteriorCalibrationConfig,
    SparsePathObservationConfig,
    apply_sample_spread_scale,
    calibrate_sample_spread,
    evaluate_split_calibrated_path_posterior,
    fit_sample_spread_scale,
    evaluate_path_digital_twin_calibration,
    make_sparse_path_observations,
    run_multistart_path_state_inversion,
)


class LinearHistoryTwin(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.config = type("Config", (), {"history_dim": 5})()

    def forward(
        self,
        coords: torch.Tensor,
        params: torch.Tensor,
        forcing_sequence: torch.Tensor,
        initial_history: torch.Tensor | None = None,
        connectivity: torch.Tensor | None = None,
        teacher_forcing_ratio: float = 0.0,
    ) -> dict[str, torch.Tensor]:
        del coords, connectivity, teacher_forcing_ratio
        if initial_history is None:
            initial_history = torch.zeros(params.shape[0], 2, 5, device=params.device, dtype=params.dtype)
        scale = params[:, 0].view(-1, 1, 1, 1)
        history_bias = initial_history[..., 0].mean(dim=1).view(-1, 1, 1, 1)
        mean_sequence = scale * forcing_sequence + history_bias
        n_steps = forcing_sequence.shape[1]
        history_sequence = initial_history.unsqueeze(1).expand(-1, n_steps, -1, -1).clone()
        history_sequence[..., 0] = history_sequence[..., 0] + 0.05 * scale.squeeze(-1)
        return {
            "mean_sequence": mean_sequence,
            "logvar_sequence": torch.zeros_like(mean_sequence),
            "history_sequence": history_sequence,
        }


def test_sparse_path_digital_twin_inverts_parameter_and_reports_calibration() -> None:
    coords = torch.zeros(1, 3, 2)
    forcing = torch.tensor(
        [[[[0.0], [0.5], [1.0]], [[0.2], [0.7], [1.2]], [[0.4], [0.9], [1.4]]]],
        dtype=torch.float32,
    )
    target_params = torch.tensor([[1.5]], dtype=torch.float32)
    target_initial_history = torch.zeros(1, 2, 5)
    target_initial_history[..., 0] = 0.08
    model = LinearHistoryTwin()
    with torch.no_grad():
        target = model(coords, target_params, forcing, initial_history=target_initial_history)
    observations = make_sparse_path_observations(
        target["mean_sequence"],
        SparsePathObservationConfig(num_sensors=3, num_observation_steps=3, noise_std=0.0, seed=3),
    )

    posterior = run_multistart_path_state_inversion(
        model,
        coords,
        forcing,
        observations,
        initial_params=torch.tensor([[1.0]]),
        lower_bounds=torch.tensor([0.5]),
        upper_bounds=torch.tensor([2.0]),
        history_shape=(2, 5),
        config=PathStateInversionConfig(
            steps=80,
            learning_rate=4.0e-2,
            num_chains=3,
            observation_noise_std=0.05,
            prior_weight=0.0,
            history_prior_weight=0.0,
        ),
    )
    metrics = evaluate_path_digital_twin_calibration(
        posterior,
        target["mean_sequence"],
        target_params,
        target["history_sequence"],
        posterior_calibration=PosteriorCalibrationConfig(target_coverage=0.80, prefix="calibrated"),
    )
    inferred_param = posterior["params_samples"].mean(dim=1)
    assert torch.allclose(inferred_param, target_params, atol=0.15)
    assert metrics["rollout_displacement_relative_l2"] < 0.10
    assert torch.isfinite(metrics["field_ece"])
    assert torch.isfinite(metrics["material_parameter_ece"])
    assert torch.isfinite(metrics["history_ece"])
    assert "calibrated_field_coverage_95" in metrics
    assert "calibrated_material_parameter_ece" in metrics


def test_sample_spread_calibration_improves_undercovered_posterior() -> None:
    target = torch.tensor([[2.0]], dtype=torch.float32)
    samples = torch.tensor([[[0.95], [1.0], [1.05]]], dtype=torch.float32)
    raw_covered = ((target >= samples.quantile(0.025, dim=1)) & (target <= samples.quantile(0.975, dim=1))).float()
    scale, calibrated = calibrate_sample_spread(
        samples,
        target,
        PosteriorCalibrationConfig(target_coverage=0.95, max_scale=100.0, search_steps=24),
    )
    calibrated_covered = (
        (target >= calibrated.quantile(0.025, dim=1)) & (target <= calibrated.quantile(0.975, dim=1))
    ).float()
    assert raw_covered.mean() == 0.0
    assert calibrated_covered.mean() == 1.0
    assert scale > 1.0


def test_split_posterior_calibration_uses_heldout_samples() -> None:
    calibration_target = torch.tensor([[2.0], [2.2]], dtype=torch.float32)
    calibration_samples = torch.tensor(
        [
            [[0.95], [1.0], [1.05]],
            [[1.15], [1.2], [1.25]],
        ],
        dtype=torch.float32,
    )
    test_target = torch.tensor([[3.0]], dtype=torch.float32)
    test_samples = torch.tensor([[[2.9], [3.0], [3.1]]], dtype=torch.float32)
    config = PosteriorCalibrationConfig(target_coverage=0.80, max_scale=100.0, search_steps=20)

    scale = fit_sample_spread_scale(calibration_samples, calibration_target, config)
    calibrated_test = apply_sample_spread_scale(test_samples, scale, min_spread=config.min_spread)
    assert scale > 1.0
    assert calibrated_test.shape == test_samples.shape

    posterior_cal = {
        "field_samples": calibration_samples.view(2, 3, 1, 1, 1),
        "params_samples": calibration_samples,
        "history_samples": calibration_samples.view(2, 3, 1, 1, 1),
    }
    posterior_test = {
        "field_samples": test_samples.view(1, 3, 1, 1, 1),
        "params_samples": test_samples,
        "history_samples": test_samples.view(1, 3, 1, 1, 1),
    }
    metrics = evaluate_split_calibrated_path_posterior(
        posterior_cal,
        calibration_target.view(2, 1, 1, 1),
        calibration_target,
        posterior_test,
        test_target.view(1, 1, 1, 1),
        test_target,
        calibration_history_sequence=calibration_target.view(2, 1, 1, 1),
        test_history_sequence=test_target.view(1, 1, 1, 1),
        config=config,
    )
    assert "calibrated_field_coverage_95" in metrics
    assert "calibrated_material_parameter_spread_scale" in metrics
    assert torch.isfinite(metrics["calibrated_history_ece"])
