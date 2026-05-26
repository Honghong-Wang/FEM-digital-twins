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
from pcgno_dt.evaluation.path_history import (
    evaluate_j2_path_history_consistency,
    evaluate_reversal_memory_errors,
)
from pcgno_dt.models.history_gno import HistoryGraphOperator, HistoryGraphOperatorConfig
from pcgno_dt.numerics.j2plasticity2d import J2_LOAD_PATHS, save_j2_plasticity_fem_dataset
from pcgno_dt.training.path_losses import PathLossWeights, history_graph_operator_loss


SUPPORTED_LOAD_PATHS = J2_LOAD_PATHS
SUPPORTED_MESH_KINDS = (
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
)
HISTORY_CHANNELS = {
    "eq_plastic_strain": 0,
    "plastic_work": 1,
    "plastic_multiplier_increment": 2,
    "yield_flag": 3,
    "von_mises": 4,
}
DEGRADATION_METRICS = (
    "total_loss",
    "displacement_relative_l2",
    "history_relative_l2",
    "history_increment_relative_l2",
    "eq_plastic_strain_relative_l2",
    "eq_plastic_strain_increment_relative_l2",
    "plastic_work_relative_l2",
    "plastic_work_increment_relative_l2",
    "plastic_multiplier_increment_relative_l2",
    "yield_flag_mae",
    "von_mises_relative_l2",
    "predicted_yield_surface_relative_rms",
    "predicted_elastic_overstress_relative_violation",
    "predicted_plastic_work_lower_bound_relative_violation",
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Train a J2 HistoryGraphOperator on monotonic loading and evaluate "
            "path-OOD generalization across reversal, nonproportional, random-amplitude, "
            "and pre-stress loading families."
        )
    )
    parser.add_argument(
        "--data-root",
        type=Path,
        default=PROJECT_ROOT / "05_data_pipeline" / "processed" / "j2_path_ood_comparison",
    )
    parser.add_argument("--epochs", type=int, default=50)
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--eval-batch-size", type=int, default=8)
    parser.add_argument("--learning-rate", type=float, default=1.0e-3)
    parser.add_argument("--hidden-dim", type=int, default=96)
    parser.add_argument("--message-passing-layers", type=int, default=3)
    parser.add_argument("--teacher-forcing-ratio", type=float, default=0.5)
    parser.add_argument(
        "--model-kind",
        choices=("history_gno", "thermo_hard_hgo"),
        default="history_gno",
        help="Use thermo_hard_hgo to route history updates through a differentiable J2 return-mapping layer.",
    )
    parser.add_argument(
        "--train-load-paths",
        type=_parse_load_paths,
        default="monotonic",
        help="Comma-separated training load paths. Use monotonic for strict path-OOD.",
    )
    parser.add_argument("--history-increment-weight", type=float, default=0.0)
    parser.add_argument("--eqp-increment-weight", type=float, default=0.0)
    parser.add_argument("--plastic-work-increment-weight", type=float, default=0.0)
    parser.add_argument("--yield-flag-weight", type=float, default=0.0)
    parser.add_argument("--yield-surface-weight", type=float, default=0.0)
    parser.add_argument("--elastic-overstress-weight", type=float, default=0.0)
    parser.add_argument("--plastic-work-lower-bound-weight", type=float, default=0.0)
    parser.add_argument("--train-samples", type=int, default=32)
    parser.add_argument("--eval-samples", type=int, default=12)
    parser.add_argument("--nx", type=int, default=3)
    parser.add_argument("--ny", type=int, default=3)
    parser.add_argument(
        "--mesh-kind",
        choices=SUPPORTED_MESH_KINDS,
        default="structured",
    )
    parser.add_argument("--geometry-perturbation", type=float, default=0.0)
    parser.add_argument(
        "--mesh-file",
        type=Path,
        default=None,
        help="External mesh file (.msh, .inp, .xml, .xdmf inline, or .npz) for complex-geometry J2 runs.",
    )
    parser.add_argument(
        "--normalize-external-mesh",
        action=argparse.BooleanOptionalAction,
        default=True,
    )
    parser.add_argument("--load-steps", type=int, default=8)
    parser.add_argument("--max-newton-steps", type=int, default=14)
    parser.add_argument("--seed", type=int, default=20260517)
    parser.add_argument(
        "--eval-load-paths",
        type=_parse_load_paths,
        default=",".join(SUPPORTED_LOAD_PATHS),
        help="Comma-separated load paths to evaluate. Monotonic is used as the ID reference.",
    )
    parser.add_argument("--force-regenerate", action="store_true")
    parser.add_argument("--device", default="cpu")
    parser.add_argument(
        "--out",
        type=Path,
        default=PROJECT_ROOT / "10_results" / "reports" / "j2_path_ood_comparison.json",
    )
    parser.add_argument(
        "--csv-out",
        type=Path,
        default=None,
        help="Optional CSV summary path. Defaults to --out with .csv suffix.",
    )
    args = parser.parse_args()

    torch.manual_seed(args.seed)
    eval_load_paths = (
        _parse_load_paths(args.eval_load_paths)
        if isinstance(args.eval_load_paths, str)
        else tuple(args.eval_load_paths)
    )
    train_load_paths = (
        _parse_load_paths(args.train_load_paths)
        if isinstance(args.train_load_paths, str)
        else tuple(args.train_load_paths)
    )
    if "monotonic" not in eval_load_paths:
        eval_load_paths = ("monotonic", *eval_load_paths)

    _ensure_path_ood_datasets(args, eval_load_paths, train_load_paths)
    train = _load_training_splits(args.data_root, train_load_paths, args.device)
    train_tensors = train["tensors"]
    train_connectivity = _connectivity_tensor(train, args.device)
    model = _make_model(train_tensors, args).to(args.device)

    train_loss_history = _train(model, train, train_connectivity, args)
    evaluations: dict[str, dict[str, float]] = {}
    for load_path in eval_load_paths:
        loaded = _load_split(args.data_root, load_path, "test", args.device)
        connectivity = _connectivity_tensor(loaded, args.device)
        evaluations[load_path] = _evaluate(model, loaded, connectivity, args)

    degradation = _compute_degradation(evaluations)
    payload = {
        "metadata": {
            "model": "HistoryGraphOperator" if args.model_kind == "history_gno" else "ThermoHardHistoryGraphOperator",
            "model_kind": args.model_kind,
            "training_load_paths": list(train_load_paths),
            "strict_path_ood": list(train_load_paths) == ["monotonic"],
            "evaluation_load_paths": list(eval_load_paths),
            "epochs": args.epochs,
            "batch_size": args.batch_size,
            "eval_batch_size": args.eval_batch_size,
            "learning_rate": args.learning_rate,
            "teacher_forcing_ratio": args.teacher_forcing_ratio,
            "history_increment_weight": args.history_increment_weight,
            "eqp_increment_weight": args.eqp_increment_weight,
            "plastic_work_increment_weight": args.plastic_work_increment_weight,
            "yield_flag_weight": args.yield_flag_weight,
            "yield_surface_weight": args.yield_surface_weight,
            "elastic_overstress_weight": args.elastic_overstress_weight,
            "plastic_work_lower_bound_weight": args.plastic_work_lower_bound_weight,
            "train_samples": args.train_samples,
            "eval_samples": args.eval_samples,
            "nx": args.nx,
            "ny": args.ny,
            "mesh_kind": args.mesh_kind,
            "geometry_perturbation": args.geometry_perturbation,
            "mesh_file": None if args.mesh_file is None else str(args.mesh_file),
            "normalize_external_mesh": args.normalize_external_mesh,
            "load_steps": args.load_steps,
            "seed": args.seed,
        },
        "datasets": {
            "train": {
                load_path: str(_dataset_path(args.data_root, load_path, "train"))
                for load_path in train_load_paths
            },
            "evaluations": {
                load_path: str(_dataset_path(args.data_root, load_path, "test"))
                for load_path in eval_load_paths
            },
        },
        "train_loss_history": train_loss_history,
        "evaluations": evaluations,
        "path_ood_degradation_vs_monotonic": degradation,
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    csv_out = args.csv_out or args.out.with_suffix(".csv")
    _write_csv(csv_out, evaluations, degradation)
    print(json.dumps({"evaluations": evaluations, "degradation": degradation}, indent=2))
    print(f"wrote {args.out}")
    print(f"wrote {csv_out}")


def _parse_load_paths(value: str | tuple[str, ...] | list[str]) -> tuple[str, ...]:
    if isinstance(value, (tuple, list)):
        parts = [str(item).strip() for item in value]
    else:
        parts = [item.strip() for item in str(value).split(",")]
    load_paths = tuple(item for item in parts if item)
    unknown = sorted(set(load_paths).difference(SUPPORTED_LOAD_PATHS))
    if unknown:
        raise argparse.ArgumentTypeError(
            f"unknown load paths {unknown}; options are {list(SUPPORTED_LOAD_PATHS)}"
        )
    if not load_paths:
        raise argparse.ArgumentTypeError("at least one evaluation load path is required")
    return load_paths


def _ensure_path_ood_datasets(
    args: argparse.Namespace,
    eval_load_paths: tuple[str, ...],
    train_load_paths: tuple[str, ...],
) -> None:
    for load_path in train_load_paths:
        train_path = _dataset_path(args.data_root, load_path, "train")
        if args.force_regenerate or not train_path.exists():
            _generate_dataset_split(args, train_path, split="train", load_path=load_path, seed=args.seed)
            print(f"generated {train_path}")

    eval_seed = args.seed + 10_000
    for load_path in eval_load_paths:
        path = _dataset_path(args.data_root, load_path, "test")
        if path.exists() and not args.force_regenerate:
            continue
        _generate_dataset_split(args, path, split="test", load_path=load_path, seed=eval_seed)
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
    n_samples = args.train_samples if split == "train" else args.eval_samples
    save_j2_plasticity_fem_dataset(
        path,
        n_samples=n_samples,
        split=split,
        seed=seed,
        nx=args.nx,
        ny=args.ny,
        mesh_kind=args.mesh_kind,
        perturbation=args.geometry_perturbation,
        mesh_file=args.mesh_file,
        normalize_external_mesh=args.normalize_external_mesh,
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
    tensors: dict[str, torch.Tensor] = {}
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
    return {
        "tensors": tensors,
        "metadata": base["metadata"],
        "extra": base["extra"],
    }


def _connectivity_tensor(loaded: dict, device: str | torch.device) -> torch.Tensor:
    return torch.as_tensor(loaded["extra"]["connectivity"], dtype=torch.long, device=device)


def _make_model(tensors: dict[str, torch.Tensor], args: argparse.Namespace) -> HistoryGraphOperator:
    history_dim = int(tensors["material_history_sequence"].shape[-1])
    return HistoryGraphOperator(
        HistoryGraphOperatorConfig(
            num_parameters=int(tensors["params"].shape[-1]),
            num_fields=int(tensors["fields_sequence"].shape[-1]),
            spatial_dim=int(tensors["coords"].shape[-1]),
            history_dim=history_dim,
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
    loader = DataLoader(
        dataset,
        batch_size=args.batch_size,
        shuffle=True,
        generator=generator,
    )
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


def _evaluate(
    model: HistoryGraphOperator,
    loaded: dict,
    connectivity: torch.Tensor,
    args: argparse.Namespace,
) -> dict[str, float]:
    dataset = PathOperatorTensorDataset(loaded["tensors"])
    loader = DataLoader(dataset, batch_size=args.eval_batch_size, shuffle=False)
    weights = _path_loss_weights(args)
    accum: dict[str, float] = {}
    n_seen = 0
    model.eval()
    with torch.no_grad():
        for batch in loader:
            batch = _move_batch(batch, args.device)
            outputs = model(
                batch["coords"],
                batch["params"],
                batch["forcing_sequence"],
                connectivity=connectivity,
                teacher_forcing_ratio=0.0,
            )
            metrics = _path_prediction_metrics(outputs, batch, weights)
            batch_size = int(batch["params"].shape[0])
            for key, value in metrics.items():
                accum[key] = accum.get(key, 0.0) + float(value.detach().cpu()) * batch_size
            n_seen += batch_size
    model.train()
    return {key: value / max(n_seen, 1) for key, value in sorted(accum.items())}


def _path_prediction_metrics(
    outputs: dict[str, torch.Tensor],
    batch: dict[str, torch.Tensor],
    weights: PathLossWeights,
) -> dict[str, torch.Tensor]:
    losses = history_graph_operator_loss(outputs, batch, weights)
    prediction = outputs["mean_sequence"]
    target = batch["fields_sequence"]
    history_prediction = outputs["history_sequence"]
    history_target = batch["material_history_sequence"][..., : history_prediction.shape[-1]]

    metrics = {
        "total_loss": losses["total"],
        "displacement_loss": losses["displacement"],
        "history_loss": losses["history"],
        "loss_yield_surface": losses["yield_surface"],
        "loss_elastic_overstress": losses["elastic_overstress"],
        "loss_plastic_work_lower_bound": losses["plastic_work_lower_bound"],
        "displacement_relative_l2": _relative_rmse(prediction, target),
        "history_relative_l2": _relative_rmse(history_prediction, history_target),
        "final_displacement_relative_l2": _relative_rmse(prediction[:, -1], target[:, -1]),
        "final_history_relative_l2": _relative_rmse(history_prediction[:, -1], history_target[:, -1]),
        "history_increment_relative_l2": _relative_rmse(
            _path_increment(history_prediction),
            _path_increment(history_target),
        ),
    }
    for name, channel in HISTORY_CHANNELS.items():
        if channel >= history_prediction.shape[-1]:
            continue
        predicted_channel = history_prediction[..., channel]
        target_channel = history_target[..., channel]
        if name == "yield_flag":
            metrics[f"{name}_mae"] = (predicted_channel - target_channel).abs().mean()
            metrics[f"final_{name}_mae"] = (predicted_channel[:, -1] - target_channel[:, -1]).abs().mean()
        else:
            metrics[f"{name}_relative_l2"] = _relative_rmse(predicted_channel, target_channel)
            metrics[f"final_{name}_relative_l2"] = _relative_rmse(
                predicted_channel[:, -1],
                target_channel[:, -1],
            )
            if name in {"eq_plastic_strain", "plastic_work"}:
                metrics[f"{name}_increment_relative_l2"] = _relative_rmse(
                    _path_increment(predicted_channel),
                    _path_increment(target_channel),
                )

    target_consistency = evaluate_j2_path_history_consistency(batch)
    predicted_consistency = evaluate_j2_path_history_consistency(
        {
            "material_history_sequence": history_prediction,
            "forcing_sequence": batch["forcing_sequence"],
            "params": batch["params"],
        }
    )
    reversal_metrics = evaluate_reversal_memory_errors(
        history_prediction,
        history_target,
        batch["forcing_sequence"],
    )
    metrics.update({f"target_{key}": value for key, value in target_consistency.items()})
    metrics.update({f"predicted_{key}": value for key, value in predicted_consistency.items()})
    metrics.update(reversal_metrics)
    return metrics


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


def _path_increment(values: torch.Tensor) -> torch.Tensor:
    if values.shape[1] < 2:
        return values.new_zeros(values.shape[0], 0, *values.shape[2:])
    return values[:, 1:] - values[:, :-1]


def _relative_rmse(prediction: torch.Tensor, target: torch.Tensor, eps: float = 1.0e-12) -> torch.Tensor:
    if prediction.numel() == 0:
        return target.new_tensor(0.0)
    error = prediction - target
    return error.square().mean().sqrt() / target.square().mean().sqrt().clamp_min(eps)


def _compute_degradation(evaluations: dict[str, dict[str, float]]) -> dict[str, dict[str, float]]:
    reference = evaluations.get("monotonic")
    if reference is None:
        return {}
    degradation: dict[str, dict[str, float]] = {}
    for load_path, metrics in evaluations.items():
        if load_path == "monotonic":
            continue
        path_degradation = {}
        for key in DEGRADATION_METRICS:
            if key not in metrics or key not in reference:
                continue
            denominator = max(abs(reference[key]), 1.0e-12)
            path_degradation[f"{key}_ratio"] = metrics[key] / denominator
            path_degradation[f"{key}_delta"] = metrics[key] - reference[key]
        degradation[load_path] = path_degradation
    return degradation


def _write_csv(
    path: Path,
    evaluations: dict[str, dict[str, float]],
    degradation: dict[str, dict[str, float]],
) -> None:
    rows = []
    for load_path, metrics in evaluations.items():
        row = {"load_path": load_path, **metrics}
        row.update(degradation.get(load_path, {}))
        rows.append(row)
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


def _move_batch(batch: dict[str, torch.Tensor], device: str | torch.device) -> dict[str, torch.Tensor]:
    return {key: value.to(device) if isinstance(value, torch.Tensor) else value for key, value in batch.items()}


if __name__ == "__main__":
    main()
