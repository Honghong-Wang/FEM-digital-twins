from __future__ import annotations

from dataclasses import dataclass

import torch

from pcgno_dt.uq.calibration import (
    empirical_crps,
    expected_calibration_error,
    interval_width,
    predictive_interval,
    predictive_sharpness,
)


@dataclass(frozen=True)
class SparsePathObservationConfig:
    num_sensors: int = 6
    observation_steps: tuple[int, ...] | None = None
    num_observation_steps: int | None = None
    noise_std: float = 0.0
    seed: int = 0
    include_final_step: bool = True


@dataclass(frozen=True)
class PathStateInversionConfig:
    steps: int = 120
    learning_rate: float = 2.0e-2
    prior_weight: float = 1.0e-4
    history_prior_weight: float = 1.0e-5
    num_chains: int = 8
    param_init_noise: float = 0.08
    history_init_noise: float = 0.02
    optimize_initial_history: bool = True
    observation_noise_std: float = 1.0e-3


@dataclass(frozen=True)
class SparsePathObservations:
    sensor_idx: torch.Tensor
    step_idx: torch.Tensor
    values: torch.Tensor
    clean_values: torch.Tensor


@dataclass(frozen=True)
class PosteriorCalibrationConfig:
    target_coverage: float = 0.95
    max_scale: float = 1.0e4
    search_steps: int = 32
    min_spread: float = 1.0e-6
    finite_sample_correction: bool = True
    prefix: str = "calibrated"


def make_sparse_path_observations(
    fields_sequence: torch.Tensor,
    config: SparsePathObservationConfig = SparsePathObservationConfig(),
) -> SparsePathObservations:
    """Select sparse displacement sensors over a path sequence.

    The returned values have shape `[batch, observed_steps, sensors, fields]`.
    """

    if fields_sequence.ndim != 4:
        raise ValueError("fields_sequence must have shape [batch, steps, nodes, fields]")
    _, n_steps, n_nodes, _ = fields_sequence.shape
    if config.num_sensors < 1 or config.num_sensors > n_nodes:
        raise ValueError("num_sensors must be between 1 and the number of nodes")
    generator = torch.Generator(device=fields_sequence.device)
    generator.manual_seed(config.seed)
    sensor_idx = torch.randperm(n_nodes, generator=generator, device=fields_sequence.device)[: config.num_sensors]
    step_idx = _observation_steps(n_steps, config, device=fields_sequence.device)
    clean_values = gather_sparse_path_values(fields_sequence, step_idx, sensor_idx)
    if config.noise_std > 0.0:
        noise = torch.randn(
            clean_values.shape,
            generator=generator,
            device=clean_values.device,
            dtype=clean_values.dtype,
        )
        values = clean_values + config.noise_std * noise
    else:
        values = clean_values
    return SparsePathObservations(sensor_idx=sensor_idx, step_idx=step_idx, values=values, clean_values=clean_values)


def gather_sparse_path_values(
    fields_sequence: torch.Tensor,
    step_idx: torch.Tensor,
    sensor_idx: torch.Tensor,
) -> torch.Tensor:
    if fields_sequence.ndim != 4:
        raise ValueError("fields_sequence must have shape [batch, steps, nodes, fields]")
    return fields_sequence.index_select(1, step_idx).index_select(2, sensor_idx)


def run_multistart_path_state_inversion(
    model: torch.nn.Module,
    coords: torch.Tensor,
    forcing_sequence: torch.Tensor,
    observations: SparsePathObservations,
    initial_params: torch.Tensor,
    lower_bounds: torch.Tensor,
    upper_bounds: torch.Tensor,
    connectivity: torch.Tensor | None = None,
    history_shape: tuple[int, int] | None = None,
    initial_history: torch.Tensor | None = None,
    config: PathStateInversionConfig = PathStateInversionConfig(),
) -> dict[str, torch.Tensor]:
    """Infer material parameters and latent history from sparse path observations.

    Multiple optimization chains form a lightweight posterior proxy. This is not a
    full Bayesian sampler; it is intended as a reproducible digital-twin assimilation
    diagnostic that can be compared across operator architectures.
    """

    if coords.ndim != 3 or forcing_sequence.ndim != 4:
        raise ValueError("coords and forcing_sequence must have batched path shapes")
    batch_size = coords.shape[0]
    if initial_params.shape[0] != batch_size:
        raise ValueError("initial_params must share the batch dimension")
    n_chains = max(int(config.num_chains), 1)
    coords_chain = _repeat_batch(coords, n_chains)
    forcing_chain = _repeat_batch(forcing_sequence, n_chains)
    observed_chain = _repeat_batch(observations.values, n_chains)
    initial_params_chain = _repeat_batch(initial_params, n_chains)
    lower_chain = _prepare_bounds(lower_bounds, initial_params, n_chains)
    upper_chain = _prepare_bounds(upper_bounds, initial_params, n_chains)
    history_chain = _initial_history_guess(
        initial_history,
        batch_size=batch_size,
        n_chains=n_chains,
        history_shape=history_shape,
        device=coords.device,
        dtype=coords.dtype,
    )

    result = invert_path_state_from_sparse_observations(
        model,
        coords_chain,
        forcing_chain,
        observations.sensor_idx,
        observations.step_idx,
        observed_chain,
        initial_params_chain,
        lower_chain,
        upper_chain,
        connectivity=connectivity,
        initial_history=history_chain,
        config=config,
    )
    return {
        "params_samples": result["params"].view(batch_size, n_chains, -1),
        "initial_history_samples": result["initial_history"].view(batch_size, n_chains, *result["initial_history"].shape[1:]),
        "field_samples": result["mean_sequence"].view(batch_size, n_chains, *result["mean_sequence"].shape[1:]),
        "history_samples": result["history_sequence"].view(batch_size, n_chains, *result["history_sequence"].shape[1:]),
        "logvar_samples": result["logvar_sequence"].view(batch_size, n_chains, *result["logvar_sequence"].shape[1:]),
        "loss_history": result["loss_history"],
    }


def invert_path_state_from_sparse_observations(
    model: torch.nn.Module,
    coords: torch.Tensor,
    forcing_sequence: torch.Tensor,
    sensor_idx: torch.Tensor,
    step_idx: torch.Tensor,
    observed_values: torch.Tensor,
    initial_params: torch.Tensor,
    lower_bounds: torch.Tensor,
    upper_bounds: torch.Tensor,
    connectivity: torch.Tensor | None = None,
    initial_history: torch.Tensor | None = None,
    config: PathStateInversionConfig = PathStateInversionConfig(),
) -> dict[str, torch.Tensor]:
    """Gradient-based sparse-observation assimilation through a recurrent path operator."""

    lower_bounds = lower_bounds.to(device=initial_params.device, dtype=initial_params.dtype)
    upper_bounds = upper_bounds.to(device=initial_params.device, dtype=initial_params.dtype)
    scale = (upper_bounds - lower_bounds).clamp_min(1.0e-8)
    center = 0.5 * (lower_bounds + upper_bounds)
    raw_params = torch.nn.Parameter(_inverse_sigmoid_bounds(initial_params, lower_bounds, scale))
    if config.param_init_noise > 0.0:
        with torch.no_grad():
            raw_params.add_(config.param_init_noise * torch.randn_like(raw_params))

    history_shape = _infer_history_shape(model, coords, connectivity, initial_history)
    raw_history = torch.nn.Parameter(
        _history_to_raw(
            _initial_history_guess(
                initial_history,
                batch_size=coords.shape[0],
                n_chains=1,
                history_shape=history_shape,
                device=coords.device,
                dtype=coords.dtype,
            )
        )
    )
    if config.history_init_noise > 0.0:
        with torch.no_grad():
            raw_history.add_(config.history_init_noise * torch.randn_like(raw_history))

    parameters = [raw_params]
    if config.optimize_initial_history:
        parameters.append(raw_history)
    optimizer = torch.optim.Adam(parameters, lr=config.learning_rate)
    loss_history = []
    was_training = model.training
    requires_grad = [param.requires_grad for param in model.parameters()]
    model.eval()
    for param in model.parameters():
        param.requires_grad_(False)
    try:
        for _ in range(config.steps):
            optimizer.zero_grad()
            params = lower_bounds + torch.sigmoid(raw_params) * scale
            history = _raw_to_history(raw_history)
            outputs = model(
                coords,
                params,
                forcing_sequence,
                initial_history=history,
                connectivity=connectivity,
                teacher_forcing_ratio=0.0,
            )
            predicted_values = gather_sparse_path_values(outputs["mean_sequence"], step_idx, sensor_idx)
            data_loss = (predicted_values - observed_values).square().mean()
            prior_loss = ((params - center) / scale).square().mean()
            history_prior = history.square().mean()
            noise_scale = max(config.observation_noise_std, 1.0e-8)
            loss = data_loss / (noise_scale * noise_scale) + config.prior_weight * prior_loss
            if config.optimize_initial_history:
                loss = loss + config.history_prior_weight * history_prior
            loss.backward()
            optimizer.step()
            loss_history.append(loss.detach())

        params = lower_bounds + torch.sigmoid(raw_params.detach()) * scale
        history = _raw_to_history(raw_history.detach())
        outputs = model(
            coords,
            params,
            forcing_sequence,
            initial_history=history,
            connectivity=connectivity,
            teacher_forcing_ratio=0.0,
        )
    finally:
        for param, flag in zip(model.parameters(), requires_grad):
            param.requires_grad_(flag)
        model.train(was_training)
    return {
        "params": params.detach(),
        "initial_history": history.detach(),
        "mean_sequence": outputs["mean_sequence"].detach(),
        "history_sequence": outputs["history_sequence"].detach(),
        "logvar_sequence": outputs["logvar_sequence"].detach(),
        "loss_history": torch.stack(loss_history) if loss_history else coords.new_zeros(0),
    }


def evaluate_path_digital_twin_calibration(
    posterior: dict[str, torch.Tensor],
    target_fields_sequence: torch.Tensor,
    target_params: torch.Tensor,
    target_history_sequence: torch.Tensor | None = None,
    posterior_calibration: PosteriorCalibrationConfig | None = None,
) -> dict[str, torch.Tensor]:
    """Evaluate inversion accuracy and posterior calibration."""

    field_samples = posterior["field_samples"]
    params_samples = posterior["params_samples"]
    history_samples = posterior.get("history_samples")
    field_mean = field_samples.mean(dim=1)
    params_mean = params_samples.mean(dim=1)
    metrics = {
        "rollout_displacement_relative_l2": _relative_rmse(field_mean, target_fields_sequence),
        "material_parameter_relative_l2": _relative_rmse(params_mean, target_params),
        "material_parameter_mae": (params_mean - target_params).abs().mean(),
        "field_coverage_95": _coverage_from_samples(field_samples, target_fields_sequence, level=0.95),
        "field_ece": expected_calibration_error(field_samples, target_fields_sequence),
        "field_nll": _gaussian_nll_from_samples(field_samples, target_fields_sequence),
        "field_crps": empirical_crps(field_samples, target_fields_sequence),
        "field_sharpness": predictive_sharpness(field_samples),
        "field_interval_width_95": _interval_width_from_samples(field_samples, level=0.95),
        "material_parameter_coverage_95": _coverage_from_samples(params_samples, target_params, level=0.95),
        "material_parameter_ece": expected_calibration_error(params_samples, target_params),
        "material_parameter_nll": _gaussian_nll_from_samples(params_samples, target_params),
        "material_parameter_posterior_std": params_samples.std(dim=1, unbiased=False).mean(),
    }
    if history_samples is not None and target_history_sequence is not None:
        history_target = target_history_sequence[..., : history_samples.shape[-1]]
        history_mean = history_samples.mean(dim=1)
        metrics.update(
            {
                "history_relative_l2": _relative_rmse(history_mean, history_target),
                "history_final_relative_l2": _relative_rmse(history_mean[:, -1], history_target[:, -1]),
                "history_coverage_95": _coverage_from_samples(history_samples, history_target, level=0.95),
                "history_ece": expected_calibration_error(history_samples, history_target),
                "history_nll": _gaussian_nll_from_samples(history_samples, history_target),
                "history_posterior_std": history_samples.std(dim=1, unbiased=False).mean(),
            }
        )
    if posterior_calibration is not None:
        metrics.update(
            evaluate_calibrated_path_posterior(
                posterior,
                target_fields_sequence,
                target_params,
                target_history_sequence,
                config=posterior_calibration,
            )
        )
    return metrics


def evaluate_calibrated_path_posterior(
    posterior: dict[str, torch.Tensor],
    target_fields_sequence: torch.Tensor,
    target_params: torch.Tensor,
    target_history_sequence: torch.Tensor | None = None,
    config: PosteriorCalibrationConfig = PosteriorCalibrationConfig(),
) -> dict[str, torch.Tensor]:
    """Evaluate spread-calibrated posterior samples.

    The calibration keeps each posterior mean fixed and inflates the sample spread by
    the smallest scalar that reaches the requested empirical coverage on the current
    calibration batch. This is a finite-sample conformal-style diagnostic rather than
    a substitute for a full Bayesian posterior.
    """

    prefix = config.prefix
    metrics: dict[str, torch.Tensor] = {}
    field_scale, field_samples = calibrate_sample_spread(
        posterior["field_samples"],
        target_fields_sequence,
        config=config,
    )
    metrics.update(
        {
            f"{prefix}_field_spread_scale": field_scale,
            f"{prefix}_field_coverage_95": _coverage_from_samples(field_samples, target_fields_sequence, level=0.95),
            f"{prefix}_field_ece": expected_calibration_error(field_samples, target_fields_sequence),
            f"{prefix}_field_nll": _gaussian_nll_from_samples(field_samples, target_fields_sequence),
            f"{prefix}_field_crps": empirical_crps(field_samples, target_fields_sequence),
            f"{prefix}_field_sharpness": predictive_sharpness(field_samples),
            f"{prefix}_field_interval_width_95": _interval_width_from_samples(field_samples, level=0.95),
        }
    )
    param_scale, params_samples = calibrate_sample_spread(
        posterior["params_samples"],
        target_params,
        config=config,
    )
    metrics.update(
        {
            f"{prefix}_material_parameter_spread_scale": param_scale,
            f"{prefix}_material_parameter_coverage_95": _coverage_from_samples(
                params_samples,
                target_params,
                level=0.95,
            ),
            f"{prefix}_material_parameter_ece": expected_calibration_error(params_samples, target_params),
            f"{prefix}_material_parameter_nll": _gaussian_nll_from_samples(params_samples, target_params),
            f"{prefix}_material_parameter_posterior_std": params_samples.std(dim=1, unbiased=False).mean(),
        }
    )
    history_samples = posterior.get("history_samples")
    if history_samples is not None and target_history_sequence is not None:
        history_target = target_history_sequence[..., : history_samples.shape[-1]]
        history_scale, calibrated_history = calibrate_sample_spread(
            history_samples,
            history_target,
            config=config,
        )
        metrics.update(
            {
                f"{prefix}_history_spread_scale": history_scale,
                f"{prefix}_history_coverage_95": _coverage_from_samples(calibrated_history, history_target, level=0.95),
                f"{prefix}_history_ece": expected_calibration_error(calibrated_history, history_target),
                f"{prefix}_history_nll": _gaussian_nll_from_samples(calibrated_history, history_target),
                f"{prefix}_history_posterior_std": calibrated_history.std(dim=1, unbiased=False).mean(),
            }
        )
    return metrics


def evaluate_split_calibrated_path_posterior(
    calibration_posterior: dict[str, torch.Tensor],
    calibration_fields_sequence: torch.Tensor,
    calibration_params: torch.Tensor,
    test_posterior: dict[str, torch.Tensor],
    test_fields_sequence: torch.Tensor,
    test_params: torch.Tensor,
    calibration_history_sequence: torch.Tensor | None = None,
    test_history_sequence: torch.Tensor | None = None,
    config: PosteriorCalibrationConfig = PosteriorCalibrationConfig(),
) -> dict[str, torch.Tensor]:
    """Fit posterior spread on a calibration split and evaluate held-out coverage.

    The posterior proxy comes from multi-start sparse-observation inversion. This
    routine keeps posterior means fixed, learns one scalar spread multiplier for
    each target family on the calibration split, and reports calibrated metrics
    on a disjoint test split. It is a lightweight split-conformal diagnostic for
    digital-twin assimilation rather than a full Bayesian posterior.
    """

    prefix = config.prefix
    metrics: dict[str, torch.Tensor] = {}

    field_scale = fit_sample_spread_scale(
        calibration_posterior["field_samples"],
        calibration_fields_sequence,
        config=config,
    )
    field_samples = apply_sample_spread_scale(
        test_posterior["field_samples"],
        field_scale,
        min_spread=config.min_spread,
    )
    metrics.update(
        {
            f"{prefix}_field_spread_scale": field_scale,
            f"{prefix}_field_coverage_95": _coverage_from_samples(field_samples, test_fields_sequence, level=0.95),
            f"{prefix}_field_ece": expected_calibration_error(field_samples, test_fields_sequence),
            f"{prefix}_field_nll": _gaussian_nll_from_samples(field_samples, test_fields_sequence),
            f"{prefix}_field_crps": empirical_crps(field_samples, test_fields_sequence),
            f"{prefix}_field_sharpness": predictive_sharpness(field_samples),
            f"{prefix}_field_interval_width_95": _interval_width_from_samples(field_samples, level=0.95),
        }
    )

    param_scale = fit_sample_spread_scale(
        calibration_posterior["params_samples"],
        calibration_params,
        config=config,
    )
    params_samples = apply_sample_spread_scale(
        test_posterior["params_samples"],
        param_scale,
        min_spread=config.min_spread,
    )
    metrics.update(
        {
            f"{prefix}_material_parameter_spread_scale": param_scale,
            f"{prefix}_material_parameter_coverage_95": _coverage_from_samples(
                params_samples,
                test_params,
                level=0.95,
            ),
            f"{prefix}_material_parameter_ece": expected_calibration_error(params_samples, test_params),
            f"{prefix}_material_parameter_nll": _gaussian_nll_from_samples(params_samples, test_params),
            f"{prefix}_material_parameter_posterior_std": params_samples.std(dim=1, unbiased=False).mean(),
        }
    )

    calibration_history = calibration_posterior.get("history_samples")
    test_history = test_posterior.get("history_samples")
    if (
        calibration_history is not None
        and test_history is not None
        and calibration_history_sequence is not None
        and test_history_sequence is not None
    ):
        calibration_target = calibration_history_sequence[..., : calibration_history.shape[-1]]
        test_target = test_history_sequence[..., : test_history.shape[-1]]
        history_scale = fit_sample_spread_scale(
            calibration_history,
            calibration_target,
            config=config,
        )
        calibrated_history = apply_sample_spread_scale(
            test_history,
            history_scale,
            min_spread=config.min_spread,
        )
        metrics.update(
            {
                f"{prefix}_history_spread_scale": history_scale,
                f"{prefix}_history_coverage_95": _coverage_from_samples(calibrated_history, test_target, level=0.95),
                f"{prefix}_history_ece": expected_calibration_error(calibrated_history, test_target),
                f"{prefix}_history_nll": _gaussian_nll_from_samples(calibrated_history, test_target),
                f"{prefix}_history_posterior_std": calibrated_history.std(dim=1, unbiased=False).mean(),
            }
        )
    return metrics


def calibrate_sample_spread(
    samples: torch.Tensor,
    target: torch.Tensor,
    config: PosteriorCalibrationConfig = PosteriorCalibrationConfig(),
) -> tuple[torch.Tensor, torch.Tensor]:
    """Inflate posterior samples around their mean until target coverage is reached."""

    scale = fit_sample_spread_scale(samples, target, config=config)
    calibrated = apply_sample_spread_scale(samples, scale, min_spread=config.min_spread)
    return scale, calibrated


def fit_sample_spread_scale(
    samples: torch.Tensor,
    target: torch.Tensor,
    config: PosteriorCalibrationConfig = PosteriorCalibrationConfig(),
) -> torch.Tensor:
    """Fit a scalar spread multiplier to reach empirical target coverage."""

    if samples.ndim != target.ndim + 1:
        raise ValueError("samples must have one posterior-sample dimension after batch")
    mean = samples.mean(dim=1, keepdim=True)
    centered = samples - mean
    if centered.abs().amax() <= config.min_spread:
        centered = _minimum_symmetric_spread(mean, n_samples=samples.shape[1], min_spread=config.min_spread)
    low = samples.new_tensor(1.0)
    high = samples.new_tensor(max(config.max_scale, 1.0))
    target_coverage = _finite_sample_target_coverage(config.target_coverage, target) if config.finite_sample_correction else config.target_coverage
    if _coverage_from_samples(mean + low * centered, target, config.target_coverage) >= target_coverage:
        return low
    for _ in range(config.search_steps):
        mid = (low + high) * 0.5
        coverage = _coverage_from_samples(mean + mid * centered, target, config.target_coverage)
        if coverage >= target_coverage:
            high = mid
        else:
            low = mid
    return high


def apply_sample_spread_scale(
    samples: torch.Tensor,
    scale: torch.Tensor | float,
    min_spread: float = 1.0e-6,
) -> torch.Tensor:
    """Apply a fitted spread multiplier around the posterior mean."""

    mean = samples.mean(dim=1, keepdim=True)
    centered = samples - mean
    if centered.abs().amax() <= min_spread:
        centered = _minimum_symmetric_spread(mean, n_samples=samples.shape[1], min_spread=min_spread)
    scale_tensor = torch.as_tensor(scale, device=samples.device, dtype=samples.dtype)
    return mean + scale_tensor * centered


def _observation_steps(
    n_steps: int,
    config: SparsePathObservationConfig,
    device: torch.device,
) -> torch.Tensor:
    if config.observation_steps is not None:
        steps = torch.as_tensor(config.observation_steps, dtype=torch.long, device=device)
    else:
        n_observed = config.num_observation_steps or min(n_steps, 3)
        steps = torch.linspace(0, n_steps - 1, n_observed, device=device).round().long().unique(sorted=True)
    if config.include_final_step:
        steps = torch.cat([steps, torch.as_tensor([n_steps - 1], dtype=torch.long, device=device)]).unique(sorted=True)
    if torch.any((steps < 0) | (steps >= n_steps)):
        raise ValueError("observation steps must lie inside the path length")
    return steps


def _repeat_batch(value: torch.Tensor, n_chains: int) -> torch.Tensor:
    return value.repeat_interleave(n_chains, dim=0)


def _prepare_bounds(bounds: torch.Tensor, initial_params: torch.Tensor, n_chains: int) -> torch.Tensor:
    bounds = bounds.to(device=initial_params.device, dtype=initial_params.dtype)
    if bounds.ndim == 1:
        bounds = bounds.unsqueeze(0).expand_as(initial_params)
    if bounds.shape != initial_params.shape:
        raise ValueError("bounds must have shape [params] or [batch, params]")
    return _repeat_batch(bounds, n_chains)


def _inverse_sigmoid_bounds(initial: torch.Tensor, lower: torch.Tensor, scale: torch.Tensor) -> torch.Tensor:
    normalized = ((initial - lower) / scale).clamp(1.0e-4, 1.0 - 1.0e-4)
    return torch.logit(normalized)


def _infer_history_shape(
    model: torch.nn.Module,
    coords: torch.Tensor,
    connectivity: torch.Tensor | None,
    initial_history: torch.Tensor | None,
) -> tuple[int, int]:
    if initial_history is not None:
        return int(initial_history.shape[1]), int(initial_history.shape[2])
    history_dim = int(getattr(getattr(model, "config", object()), "history_dim", 5))
    if connectivity is not None:
        n_elements = int(connectivity.shape[0])
    else:
        n_elements = int(coords.shape[1])
    return n_elements, history_dim


def _initial_history_guess(
    initial_history: torch.Tensor | None,
    batch_size: int,
    n_chains: int,
    history_shape: tuple[int, int] | None,
    device: torch.device,
    dtype: torch.dtype,
) -> torch.Tensor:
    if initial_history is not None:
        value = initial_history.to(device=device, dtype=dtype)
        if value.shape[0] == batch_size:
            return _repeat_batch(value, n_chains)
        if value.shape[0] == batch_size * n_chains:
            return value
        raise ValueError("initial_history has incompatible batch dimension")
    if history_shape is None:
        raise ValueError("history_shape is required when initial_history is absent")
    n_elements, history_dim = history_shape
    return torch.zeros(batch_size * n_chains, n_elements, history_dim, device=device, dtype=dtype)


def _history_to_raw(history: torch.Tensor) -> torch.Tensor:
    raw = history.clone()
    if history.shape[-1] >= 1:
        raw[..., 0] = _softplus_inverse(history[..., 0].clamp_min(0.0))
    if history.shape[-1] >= 2:
        raw[..., 1] = _softplus_inverse(history[..., 1].clamp_min(0.0))
    if history.shape[-1] >= 3:
        raw[..., 2] = _softplus_inverse(history[..., 2].clamp_min(0.0))
    if history.shape[-1] >= 4:
        raw[..., 3] = torch.logit(history[..., 3].clamp(1.0e-4, 1.0 - 1.0e-4))
    if history.shape[-1] >= 5:
        raw[..., 4] = _softplus_inverse(history[..., 4].clamp_min(0.0))
    return raw


def _raw_to_history(raw: torch.Tensor) -> torch.Tensor:
    history = raw.clone()
    if raw.shape[-1] >= 1:
        history[..., 0] = torch.nn.functional.softplus(raw[..., 0])
    if raw.shape[-1] >= 2:
        history[..., 1] = torch.nn.functional.softplus(raw[..., 1])
    if raw.shape[-1] >= 3:
        history[..., 2] = torch.nn.functional.softplus(raw[..., 2])
    if raw.shape[-1] >= 4:
        history[..., 3] = torch.sigmoid(raw[..., 3])
    if raw.shape[-1] >= 5:
        history[..., 4] = torch.nn.functional.softplus(raw[..., 4])
    return history


def _softplus_inverse(value: torch.Tensor) -> torch.Tensor:
    return value + torch.log(-torch.expm1(-value.clamp_min(1.0e-4)))


def _coverage_from_samples(samples: torch.Tensor, target: torch.Tensor, level: float) -> torch.Tensor:
    lower, upper = predictive_interval(samples, level=level)
    return ((target >= lower) & (target <= upper)).float().mean()


def _interval_width_from_samples(samples: torch.Tensor, level: float) -> torch.Tensor:
    lower, upper = predictive_interval(samples, level=level)
    return interval_width(lower, upper)


def _gaussian_nll_from_samples(samples: torch.Tensor, target: torch.Tensor, min_variance: float = 1.0e-8) -> torch.Tensor:
    """Gaussian posterior NLL from ensemble mean and variance."""

    if samples.ndim != target.ndim + 1:
        raise ValueError("samples must have one posterior-sample dimension after batch")
    mean = samples.mean(dim=1)
    variance = samples.var(dim=1, unbiased=False).clamp_min(min_variance)
    constant = torch.as_tensor(2.0 * torch.pi, device=samples.device, dtype=samples.dtype).log()
    nll = 0.5 * (constant + variance.log() + (target - mean).square() / variance)
    return nll.mean()


def _relative_rmse(prediction: torch.Tensor, target: torch.Tensor, eps: float = 1.0e-12) -> torch.Tensor:
    error = prediction - target
    return error.square().mean().sqrt() / target.square().mean().sqrt().clamp_min(eps)


def _minimum_symmetric_spread(
    mean: torch.Tensor,
    n_samples: int,
    min_spread: float,
) -> torch.Tensor:
    offsets = torch.linspace(-1.0, 1.0, n_samples, device=mean.device, dtype=mean.dtype)
    shape = [1, n_samples, *([1] * (mean.ndim - 2))]
    template = mean.expand(-1, n_samples, *mean.shape[2:])
    return min_spread * offsets.view(*shape).expand_as(template)


def _finite_sample_target_coverage(target_coverage: float, target: torch.Tensor) -> float:
    n = max(int(target.numel()), 1)
    corrected = torch.ceil(torch.as_tensor((n + 1) * target_coverage)).item() / n
    return float(min(1.0, max(target_coverage, corrected)))
