from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

import torch
from torch.utils.data import DataLoader

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pcgno_dt.data.datasets import PathOperatorTensorDataset
from pcgno_dt.data.fem import load_fem_path_snapshots
from pcgno_dt.inverse.path_digital_twin import (
    PathStateInversionConfig,
    PosteriorCalibrationConfig,
    SparsePathObservationConfig,
    evaluate_path_digital_twin_calibration,
    evaluate_split_calibrated_path_posterior,
    gather_sparse_path_values,
    make_sparse_path_observations,
    run_multistart_path_state_inversion,
)
from pcgno_dt.models.history_gno import HistoryGraphOperator, HistoryGraphOperatorConfig
from pcgno_dt.numerics.j2plasticity2d import J2_LOAD_PATHS, save_j2_plasticity_fem_dataset
from pcgno_dt.training.path_losses import PathLossWeights, history_graph_operator_loss


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Sparse-observation digital-twin assimilation for J2 path-dependent FEM data. "
            "The runner infers material parameters and latent material history from sparse "
            "displacement sensors and reports posterior calibration metrics."
        )
    )
    parser.add_argument(
        "--data-root",
        type=Path,
        default=PROJECT_ROOT / "05_data_pipeline" / "processed" / "j2_sparse_dt_assimilation",
    )
    parser.add_argument("--train-load-paths", type=_parse_load_paths, default="monotonic,unload_reload,cyclic")
    parser.add_argument("--eval-load-paths", type=_parse_load_paths, default="cyclic,random_amplitude,pre_stress")
    parser.add_argument("--epochs", type=int, default=50)
    parser.add_argument("--train-samples", type=int, default=32)
    parser.add_argument("--eval-samples", type=int, default=8)
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--eval-batch-size", type=int, default=2)
    parser.add_argument("--hidden-dim", type=int, default=96)
    parser.add_argument("--message-passing-layers", type=int, default=3)
    parser.add_argument("--learning-rate", type=float, default=1.0e-3)
    parser.add_argument("--teacher-forcing-ratio", type=float, default=0.5)
    parser.add_argument(
        "--model-kind",
        choices=("history_gno", "thermo_hard_hgo"),
        default="thermo_hard_hgo",
    )
    parser.add_argument("--nx", type=int, default=8)
    parser.add_argument("--ny", type=int, default=6)
    parser.add_argument(
        "--mesh-kind",
        choices=(
            "structured",
            "jittered",
            "hole",
            "multi_hole",
            "random_holes",
            "notch",
            "crack",
            "crack_tip",
            "stress_concentration",
            "curved",
            "curved_hole",
        ),
        default="multi_hole",
    )
    parser.add_argument("--geometry-perturbation", type=float, default=0.10)
    parser.add_argument("--load-steps", type=int, default=8)
    parser.add_argument("--max-newton-steps", type=int, default=14)
    parser.add_argument("--num-sensors", type=int, default=6)
    parser.add_argument("--num-observation-steps", type=int, default=3)
    parser.add_argument("--observation-noise-std", type=float, default=1.0e-3)
    parser.add_argument("--inversion-steps", type=int, default=120)
    parser.add_argument("--inversion-learning-rate", type=float, default=2.0e-2)
    parser.add_argument("--num-posterior-chains", type=int, default=8)
    parser.add_argument("--calibrate-posterior", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--calibration-target-coverage", type=float, default=0.95)
    parser.add_argument("--calibration-max-scale", type=float, default=1.0e4)
    parser.add_argument("--calibration-search-steps", type=int, default=32)
    parser.add_argument(
        "--posterior-calibration-mode",
        choices=("split_conformal", "batch_oracle"),
        default="split_conformal",
        help=(
            "split_conformal fits spread scales on a held-out calibration subset and evaluates "
            "coverage on the remaining samples. batch_oracle keeps the legacy same-batch diagnostic."
        ),
    )
    parser.add_argument("--calibration-fraction", type=float, default=0.5)
    parser.add_argument("--prior-weight", type=float, default=1.0e-4)
    parser.add_argument("--history-prior-weight", type=float, default=1.0e-5)
    parser.add_argument("--param-bound-padding", type=float, default=0.20)
    parser.add_argument("--history-increment-weight", type=float, default=0.25)
    parser.add_argument("--eqp-increment-weight", type=float, default=0.10)
    parser.add_argument("--plastic-work-increment-weight", type=float, default=0.10)
    parser.add_argument("--yield-flag-weight", type=float, default=0.05)
    parser.add_argument("--yield-surface-weight", type=float, default=0.001)
    parser.add_argument("--elastic-overstress-weight", type=float, default=0.001)
    parser.add_argument("--plastic-work-lower-bound-weight", type=float, default=0.001)
    parser.add_argument("--seed", type=int, default=20260517)
    parser.add_argument("--force-regenerate", action="store_true")
    parser.add_argument("--device", default="cpu")
    parser.add_argument(
        "--out",
        type=Path,
        default=PROJECT_ROOT / "10_results" / "reports" / "j2_sparse_dt_assimilation.json",
    )
    parser.add_argument("--csv-out", type=Path, default=None)
    args = parser.parse_args()

    torch.manual_seed(args.seed)
    train_load_paths = _ensure_tuple(args.train_load_paths)
    eval_load_paths = _ensure_tuple(args.eval_load_paths)
    _ensure_datasets(args, train_load_paths, eval_load_paths)
    train = _load_training_splits(args.data_root, train_load_paths, args.device)
    train_connectivity = _connectivity_tensor(train, args.device)
    model = _make_model(train["tensors"], args).to(args.device)
    train_loss_history = _train(model, train, train_connectivity, args)
    lower_bounds, upper_bounds = _parameter_bounds(train["tensors"]["params"], args.param_bound_padding)

    evaluations = {}
    for path_index, load_path in enumerate(eval_load_paths):
        loaded = _load_split(args.data_root, load_path, "test", args.device)
        connectivity = _connectivity_tensor(loaded, args.device)
        evaluations[load_path] = _evaluate_sparse_assimilation(
            model,
            loaded,
            connectivity,
            lower_bounds,
            upper_bounds,
            path_index,
            args,
        )

    payload = {
        "metadata": {
            "model_kind": args.model_kind,
            "train_load_paths": list(train_load_paths),
            "eval_load_paths": list(eval_load_paths),
            "epochs": args.epochs,
            "train_samples": args.train_samples,
            "eval_samples": args.eval_samples,
            "num_sensors": args.num_sensors,
            "num_observation_steps": args.num_observation_steps,
            "observation_noise_std": args.observation_noise_std,
            "inversion_steps": args.inversion_steps,
            "num_posterior_chains": args.num_posterior_chains,
            "calibrate_posterior": args.calibrate_posterior,
            "calibration_target_coverage": args.calibration_target_coverage,
            "calibration_max_scale": args.calibration_max_scale,
            "posterior_calibration_mode": args.posterior_calibration_mode,
            "calibration_fraction": args.calibration_fraction,
            "mesh_kind": args.mesh_kind,
            "grid_shape": [args.nx, args.ny],
            "data_root": str(args.data_root),
        },
        "train_loss_history": train_loss_history,
        "evaluations": evaluations,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    csv_out = args.csv_out or args.out.with_suffix(".csv")
    _write_csv(csv_out, evaluations)
    print(json.dumps(evaluations, indent=2))
    print(f"wrote {args.out}")
    print(f"wrote {csv_out}")


def _ensure_datasets(
    args: argparse.Namespace,
    train_load_paths: tuple[str, ...],
    eval_load_paths: tuple[str, ...],
) -> None:
    for load_path in train_load_paths:
        path = _dataset_path(args.data_root, load_path, "train")
        if args.force_regenerate or not path.exists():
            _generate_dataset_split(args, path, split="train", load_path=load_path, seed=args.seed)
            print(f"generated {path}")
    for index, load_path in enumerate(eval_load_paths):
        path = _dataset_path(args.data_root, load_path, "test")
        if args.force_regenerate or not path.exists():
            _generate_dataset_split(args, path, split="test", load_path=load_path, seed=args.seed + 10_000 + index)
            print(f"generated {path}")


def _dataset_path(data_root: Path, load_path: str, split: str) -> Path:
    return data_root / load_path / f"{split}.npz"


def _generate_dataset_split(
    args: argparse.Namespace,
    path: Path,
    split: str,
    load_path: str,
    seed: int,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    save_j2_plasticity_fem_dataset(
        path,
        n_samples=args.train_samples if split == "train" else args.eval_samples,
        split=split,
        seed=seed,
        nx=args.nx,
        ny=args.ny,
        mesh_kind=args.mesh_kind,
        perturbation=args.geometry_perturbation,
        load_steps=args.load_steps,
        load_path=load_path,
        max_newton_steps=args.max_newton_steps,
    )


def _load_split(data_root: Path, load_path: str, split: str, device: str) -> dict:
    return load_fem_path_snapshots(_dataset_path(data_root, load_path, split), device=device)


def _load_training_splits(data_root: Path, load_paths: tuple[str, ...], device: str) -> dict:
    loaded_splits = [_load_split(data_root, load_path, "train", device) for load_path in load_paths]
    if len(loaded_splits) == 1:
        return loaded_splits[0]
    base = loaded_splits[0]
    tensors = {}
    for key, first_value in base["tensors"].items():
        if not isinstance(first_value, torch.Tensor) or first_value.ndim == 0:
            continue
        parts = []
        compatible = True
        for loaded in loaded_splits:
            value = loaded["tensors"].get(key)
            if value is None or not isinstance(value, torch.Tensor) or value.ndim == 0:
                compatible = False
                break
            if tuple(value.shape[1:]) != tuple(first_value.shape[1:]):
                compatible = False
                break
            parts.append(value)
        if compatible:
            tensors[key] = torch.cat(parts, dim=0)
    return {"tensors": tensors, "metadata": base["metadata"], "extra": base["extra"]}


def _connectivity_tensor(loaded: dict, device: str | torch.device) -> torch.Tensor:
    return torch.as_tensor(loaded["extra"]["connectivity"], dtype=torch.long, device=device)


def _make_model(tensors: dict[str, torch.Tensor], args: argparse.Namespace) -> HistoryGraphOperator:
    return HistoryGraphOperator(
        HistoryGraphOperatorConfig(
            num_parameters=int(tensors["params"].shape[-1]),
            num_fields=int(tensors["fields_sequence"].shape[-1]),
            spatial_dim=int(tensors["coords"].shape[-1]),
            history_dim=int(tensors["material_history_sequence"].shape[-1]),
            hidden_dim=args.hidden_dim,
            num_message_passing_layers=args.message_passing_layers,
            thermo_hard_j2_return=args.model_kind == "thermo_hard_hgo",
        )
    )


def _train(
    model: HistoryGraphOperator,
    loaded: dict,
    connectivity: torch.Tensor,
    args: argparse.Namespace,
) -> list[float]:
    dataset = PathOperatorTensorDataset(loaded["tensors"])
    generator = torch.Generator()
    generator.manual_seed(args.seed)
    loader = DataLoader(dataset, batch_size=args.batch_size, shuffle=True, generator=generator)
    optimizer = torch.optim.Adam(model.parameters(), lr=args.learning_rate)
    weights = _path_loss_weights(args)
    history = []
    model.train()
    for _ in range(args.epochs):
        running = 0.0
        n_seen = 0
        for batch in loader:
            batch = _move_batch(batch, args.device)
            optimizer.zero_grad()
            outputs = model(
                batch["coords"],
                batch["params"],
                batch["forcing_sequence"],
                connectivity=connectivity,
                teacher_plastic_strain=batch.get("plastic_strain_sequence"),
                teacher_history=batch["material_history_sequence"],
                teacher_forcing_ratio=args.teacher_forcing_ratio,
            )
            losses = history_graph_operator_loss(outputs, batch, weights)
            losses["total"].backward()
            optimizer.step()
            batch_size = int(batch["params"].shape[0])
            running += float(losses["total"].detach().cpu()) * batch_size
            n_seen += batch_size
        history.append(running / max(n_seen, 1))
    return history


def _evaluate_sparse_assimilation(
    model: HistoryGraphOperator,
    loaded: dict,
    connectivity: torch.Tensor,
    lower_bounds: torch.Tensor,
    upper_bounds: torch.Tensor,
    path_index: int,
    args: argparse.Namespace,
) -> dict[str, float]:
    dataset = PathOperatorTensorDataset(loaded["tensors"])
    loader = DataLoader(dataset, batch_size=args.eval_batch_size, shuffle=False)
    scalar_accum: dict[str, float] = {}
    posterior_parts: list[dict[str, torch.Tensor]] = []
    field_targets: list[torch.Tensor] = []
    param_targets: list[torch.Tensor] = []
    history_targets: list[torch.Tensor] = []
    n_seen = 0
    for batch_index, batch in enumerate(loader):
        batch = _move_batch(batch, args.device)
        obs_config = SparsePathObservationConfig(
            num_sensors=args.num_sensors,
            num_observation_steps=args.num_observation_steps,
            noise_std=args.observation_noise_std,
            seed=args.seed + 1000 * path_index + batch_index,
        )
        observations = make_sparse_path_observations(batch["fields_sequence"], obs_config)
        batch_size = int(batch["params"].shape[0])
        initial_params = (0.5 * (lower_bounds + upper_bounds)).unsqueeze(0).expand(batch_size, -1).contiguous()
        posterior = run_multistart_path_state_inversion(
            model,
            batch["coords"],
            batch["forcing_sequence"],
            observations,
            initial_params,
            lower_bounds,
            upper_bounds,
            connectivity=connectivity,
            history_shape=(
                int(batch["material_history_sequence"].shape[2]),
                int(batch["material_history_sequence"].shape[-1]),
            ),
            config=PathStateInversionConfig(
                steps=args.inversion_steps,
                learning_rate=args.inversion_learning_rate,
                prior_weight=args.prior_weight,
                history_prior_weight=args.history_prior_weight,
                num_chains=args.num_posterior_chains,
                observation_noise_std=max(args.observation_noise_std, 1.0e-4),
            ),
        )
        posterior_parts.append(_detach_posterior_for_metrics(posterior))
        field_targets.append(batch["fields_sequence"].detach())
        param_targets.append(batch["params"].detach())
        history_targets.append(batch["material_history_sequence"].detach())
        field_mean = posterior["field_samples"].mean(dim=1)
        observed_mean = gather_sparse_path_values(field_mean, observations.step_idx, observations.sensor_idx)
        scalar_metrics = {
            "sparse_observation_rmse": (observed_mean - observations.clean_values).square().mean().sqrt(),
            "sparse_observation_relative_l2": _relative_rmse(observed_mean, observations.clean_values),
        }
        final_loss = posterior["loss_history"][-1] if posterior["loss_history"].numel() else batch["params"].new_tensor(0.0)
        scalar_metrics["inversion_final_loss"] = final_loss
        for key, value in scalar_metrics.items():
            scalar_accum[key] = scalar_accum.get(key, 0.0) + float(value.detach().cpu()) * batch_size
        n_seen += batch_size

    posterior_all = _concat_posterior_parts(posterior_parts)
    fields_all = torch.cat(field_targets, dim=0)
    params_all = torch.cat(param_targets, dim=0)
    history_all = torch.cat(history_targets, dim=0)
    calibration_config = PosteriorCalibrationConfig(
        target_coverage=args.calibration_target_coverage,
        max_scale=args.calibration_max_scale,
        search_steps=args.calibration_search_steps,
    )
    metrics = evaluate_path_digital_twin_calibration(
        posterior_all,
        fields_all,
        params_all,
        history_all,
        posterior_calibration=(
            calibration_config
            if args.calibrate_posterior and args.posterior_calibration_mode == "batch_oracle"
            else None
        ),
    )
    if args.calibrate_posterior and args.posterior_calibration_mode == "split_conformal":
        split_metrics = _split_posterior_calibration_metrics(
            posterior_all,
            fields_all,
            params_all,
            history_all,
            calibration_config,
            args.calibration_fraction,
        )
        metrics.update(split_metrics)
    for key, value in scalar_accum.items():
        metrics[key] = torch.as_tensor(value / max(n_seen, 1), device=fields_all.device, dtype=fields_all.dtype)
    return {key: float(value.detach().cpu()) for key, value in sorted(metrics.items())}


def _detach_posterior_for_metrics(posterior: dict[str, torch.Tensor]) -> dict[str, torch.Tensor]:
    keys = ("params_samples", "field_samples", "history_samples")
    return {key: posterior[key].detach() for key in keys if key in posterior}


def _concat_posterior_parts(parts: list[dict[str, torch.Tensor]]) -> dict[str, torch.Tensor]:
    if not parts:
        raise ValueError("at least one posterior part is required")
    keys = parts[0].keys()
    return {key: torch.cat([part[key] for part in parts], dim=0) for key in keys}


def _slice_posterior(posterior: dict[str, torch.Tensor], indices: torch.Tensor) -> dict[str, torch.Tensor]:
    return {key: value.index_select(0, indices) for key, value in posterior.items()}


def _split_posterior_calibration_metrics(
    posterior: dict[str, torch.Tensor],
    fields: torch.Tensor,
    params: torch.Tensor,
    history: torch.Tensor,
    calibration_config: PosteriorCalibrationConfig,
    calibration_fraction: float,
) -> dict[str, torch.Tensor]:
    n_samples = int(fields.shape[0])
    if n_samples < 2:
        metrics = _evaluate_calibrated_path_posterior_fallback(
            posterior,
            fields,
            params,
            history,
            calibration_config,
        )
        metrics["posterior_calibration_num_calibration"] = fields.new_tensor(float(n_samples))
        metrics["posterior_calibration_num_test"] = fields.new_tensor(0.0)
        return metrics
    n_cal = int(round(n_samples * calibration_fraction))
    n_cal = max(1, min(n_samples - 1, n_cal))
    indices = torch.arange(n_samples, device=fields.device)
    calibration_idx = indices[:n_cal]
    test_idx = indices[n_cal:]
    metrics = evaluate_split_calibrated_path_posterior(
        _slice_posterior(posterior, calibration_idx),
        fields.index_select(0, calibration_idx),
        params.index_select(0, calibration_idx),
        _slice_posterior(posterior, test_idx),
        fields.index_select(0, test_idx),
        params.index_select(0, test_idx),
        calibration_history_sequence=history.index_select(0, calibration_idx),
        test_history_sequence=history.index_select(0, test_idx),
        config=calibration_config,
    )
    metrics["posterior_calibration_num_calibration"] = fields.new_tensor(float(n_cal))
    metrics["posterior_calibration_num_test"] = fields.new_tensor(float(n_samples - n_cal))
    return metrics


def _evaluate_calibrated_path_posterior_fallback(
    posterior: dict[str, torch.Tensor],
    fields: torch.Tensor,
    params: torch.Tensor,
    history: torch.Tensor,
    calibration_config: PosteriorCalibrationConfig,
) -> dict[str, torch.Tensor]:
    return evaluate_path_digital_twin_calibration(
        posterior,
        fields,
        params,
        history,
        posterior_calibration=calibration_config,
    )


def _parameter_bounds(params: torch.Tensor, padding: float) -> tuple[torch.Tensor, torch.Tensor]:
    lower = params.min(dim=0).values
    upper = params.max(dim=0).values
    span = (upper - lower).clamp_min(1.0e-6)
    lower = lower - padding * span
    upper = upper + padding * span
    if lower.numel() >= 4:
        lower[0] = lower[0].clamp_min(1.0e-4)
        lower[1] = lower[1].clamp(0.01, 0.48)
        upper[1] = upper[1].clamp(0.02, 0.49)
        lower[2] = lower[2].clamp_min(1.0e-5)
        lower[3] = lower[3].clamp_min(1.0e-5)
    return lower.detach(), upper.detach()


def _path_loss_weights(args: argparse.Namespace) -> PathLossWeights:
    return PathLossWeights(
        history_increment=args.history_increment_weight,
        eqp_increment=args.eqp_increment_weight,
        plastic_work_increment=args.plastic_work_increment_weight,
        yield_flag=args.yield_flag_weight,
        yield_surface=args.yield_surface_weight,
        elastic_overstress=args.elastic_overstress_weight,
        plastic_work_lower_bound=args.plastic_work_lower_bound_weight,
    )


def _parse_load_paths(value: str | tuple[str, ...] | list[str]) -> tuple[str, ...]:
    parsed = _ensure_tuple(value)
    unknown = sorted(set(parsed).difference(J2_LOAD_PATHS))
    if unknown:
        raise argparse.ArgumentTypeError(f"unknown load paths {unknown}; options are {list(J2_LOAD_PATHS)}")
    if not parsed:
        raise argparse.ArgumentTypeError("at least one load path is required")
    return parsed


def _ensure_tuple(value: str | tuple[str, ...] | list[str]) -> tuple[str, ...]:
    if isinstance(value, tuple):
        return value
    if isinstance(value, list):
        return tuple(value)
    return tuple(item.strip() for item in value.split(",") if item.strip())


def _move_batch(batch: dict[str, torch.Tensor], device: str | torch.device) -> dict[str, torch.Tensor]:
    return {key: value.to(device) if isinstance(value, torch.Tensor) else value for key, value in batch.items()}


def _relative_rmse(prediction: torch.Tensor, target: torch.Tensor, eps: float = 1.0e-12) -> torch.Tensor:
    error = prediction - target
    return error.square().mean().sqrt() / target.square().mean().sqrt().clamp_min(eps)


def _write_csv(path: Path, evaluations: dict[str, dict[str, float]]) -> None:
    rows = [{"load_path": load_path, **metrics} for load_path, metrics in evaluations.items()]
    fieldnames = ["load_path"]
    for row in rows:
        for key in row:
            if key not in fieldnames:
                fieldnames.append(key)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
