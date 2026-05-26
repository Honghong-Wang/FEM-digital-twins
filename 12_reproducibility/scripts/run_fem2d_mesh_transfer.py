from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import torch

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(SCRIPT_DIR))

from pcgno_dt.data.fem import (
    has_assembled_linear_fem_data,
    has_stateful_nonlinear_fem_data,
    load_fem_snapshots,
    make_assembled_linear_fem_callbacks,
    make_fem_problem_adapter,
    make_stateful_nonlinear_fem_callbacks,
)
from pcgno_dt.numerics.fem2d import make_plane_stress_fem_callbacks, save_plane_stress_fem_dataset

from run_fem2d_baseline_runner import (
    _evaluate_model,
    _grid_shape_from_loaded,
    _make_model,
    _train_model,
    summarize_seed_results,
)


DATA_ROOT = PROJECT_ROOT / "05_data_pipeline" / "processed" / "fem2d_mesh_transfer"


def main() -> None:
    parser = argparse.ArgumentParser(description="Train on one FEM grid and evaluate on other grids.")
    parser.add_argument(
        "--model",
        choices=("pcgno", "pinn", "deeponet", "meshgno", "mesh2meshgno", "all"),
        default="pcgno",
    )
    parser.add_argument("--train-grid", default="9x7")
    parser.add_argument("--eval-grids", default="9x7,13x9,17x11")
    parser.add_argument(
        "--mesh-kind",
        choices=("structured", "jittered", "hole", "notch", "curved"),
        default="jittered",
    )
    parser.add_argument("--geometry-perturbation", type=float, default=0.15)
    parser.add_argument(
        "--train-mesh-file",
        type=Path,
        default=None,
        help="External source mesh file for training (.msh, .inp, .xml, inline .xdmf, or .npz).",
    )
    parser.add_argument(
        "--eval-mesh-files",
        default="",
        help="Comma-separated external target mesh files aligned with --eval-grids labels.",
    )
    parser.add_argument(
        "--normalize-external-mesh",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Normalize imported external mesh coordinates to a unit bounding box.",
    )
    parser.add_argument("--train-samples", type=int, default=128)
    parser.add_argument("--eval-samples", type=int, default=32)
    parser.add_argument("--epochs", type=int, default=50)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--learning-rate", type=float, default=1.0e-3)
    parser.add_argument("--seed", type=int, default=20260516)
    parser.add_argument("--num-seeds", type=int, default=5)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--loss-balancer", default="residual_adaptive")
    parser.add_argument("--pde-weight", type=float, default=1.0e-4)
    parser.add_argument("--boundary-weight", type=float, default=1.0e-2)
    parser.add_argument("--energy-weight", type=float, default=1.0e-6)
    parser.add_argument("--physics-curriculum", default="cosine")
    parser.add_argument("--physics-warmup-epochs", type=int, default=10)
    parser.add_argument("--physics-start-scale", type=float, default=0.0)
    parser.add_argument("--physics-end-scale", type=float, default=1.0)
    parser.add_argument("--gradnorm-penalty-weight", type=float, default=0.1)
    parser.add_argument("--force-regenerate", action="store_true")
    parser.add_argument(
        "--out",
        type=Path,
        default=PROJECT_ROOT / "10_results" / "reports" / "fem2d_mesh_transfer_results.json",
    )
    args = parser.parse_args()

    train_grid = _parse_grid(args.train_grid)
    eval_grids = [_parse_grid(item) for item in args.eval_grids.split(",") if item.strip()]
    eval_mesh_files = _parse_eval_mesh_files(args, eval_grids)
    _ensure_datasets(args, train_grid, eval_grids)
    train = _load_dataset(_train_dir(args, train_grid) / "train.npz", args.device)
    train_problem = _make_problem(train)
    tensors = train["tensors"]
    spatial_dim = tensors["coords"].shape[-1]
    num_parameters = tensors["params"].shape[-1]
    num_fields = tensors["fields"].shape[-1]

    model_names = (
        ("pinn", "deeponet", "meshgno", "mesh2meshgno", "pcgno")
        if args.model == "all"
        else (args.model,)
    )
    model_results = {}
    for model_name in model_names:
        seed_results = []
        for seed_offset in range(args.num_seeds):
            run_seed = args.seed + seed_offset
            torch.manual_seed(run_seed)
            model = _make_model(
                model_name,
                num_parameters=num_parameters,
                num_fields=num_fields,
                spatial_dim=spatial_dim,
                grid_shape=train_grid,
            ).to(args.device)
            if hasattr(model, "set_source_coords"):
                model.set_source_coords(train["tensors"]["coords"])
            train_args = _training_args(args)
            train_result = _train_model(model_name, model, train["tensors"], train_problem, train_args)
            seed_result = {
                "seed": run_seed,
                "train_grid": list(train_grid),
                "train_final_loss": train_result["loss_history"][-1],
                "loss_balancer": train_result["loss_balancer"],
                "training_strategy": train_result["training_strategy"],
                "eval_grids": {},
            }
            for grid in eval_grids:
                grid_key = f"{grid[0]}x{grid[1]}"
                seed_result["eval_grids"][grid_key] = {}
                for split in ("test", "ood_material", "ood_loading"):
                    loaded = _load_dataset(
                        _eval_dir(args, grid, eval_mesh_files.get(grid_key)) / f"{split}.npz",
                        args.device,
                    )
                    problem = _make_problem(loaded)
                    seed_result["eval_grids"][grid_key][split] = _evaluate_model(
                        model,
                        loaded["tensors"],
                        model_name,
                        problem,
                    )
            seed_results.append(seed_result)
        model_results[model_name] = {
            "seeds": seed_results,
            "summary": _summarize_mesh_transfer(seed_results),
        }

    payload = {
        "metadata": {
            "model": args.model,
            "models": list(model_names),
            "train_grid": list(train_grid),
            "eval_grids": [list(grid) for grid in eval_grids],
            "train_samples": args.train_samples,
            "eval_samples": args.eval_samples,
            "mesh_kind": args.mesh_kind,
            "geometry_perturbation": args.geometry_perturbation,
            "train_mesh_file": str(args.train_mesh_file) if args.train_mesh_file else None,
            "eval_mesh_files": {key: str(value) for key, value in eval_mesh_files.items()},
            "epochs": args.epochs,
            "num_seeds": args.num_seeds,
        },
        "models": model_results,
    }
    if len(model_names) == 1:
        payload["seeds"] = model_results[model_names[0]]["seeds"]
        payload["summary"] = model_results[model_names[0]]["summary"]
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    _write_csv(args.out.with_suffix(".csv"), model_results)
    print(f"wrote {args.out}")
    print(f"wrote {args.out.with_suffix('.csv')}")


def _ensure_datasets(args: argparse.Namespace, train_grid: tuple[int, int], eval_grids: list[tuple[int, int]]) -> None:
    eval_mesh_files = _parse_eval_mesh_files(args, eval_grids)
    train_path = _train_dir(args, train_grid) / "train.npz"
    _maybe_generate(
        train_path,
        n_samples=args.train_samples,
        split="train",
        seed=args.seed,
        grid=train_grid,
        mesh_kind=args.mesh_kind,
        perturbation=args.geometry_perturbation,
        mesh_file=args.train_mesh_file,
        normalize_external_mesh=args.normalize_external_mesh,
        force=args.force_regenerate,
    )
    for grid_index, grid in enumerate(eval_grids):
        grid_key = f"{grid[0]}x{grid[1]}"
        for split_index, split in enumerate(("test", "ood_material", "ood_loading")):
            path = _eval_dir(args, grid, eval_mesh_files.get(grid_key)) / f"{split}.npz"
            _maybe_generate(
                path,
                n_samples=args.eval_samples,
                split=split,
                seed=args.seed + 100 * (grid_index + 1) + split_index,
                grid=grid,
                mesh_kind=args.mesh_kind,
                perturbation=args.geometry_perturbation,
                mesh_file=eval_mesh_files.get(grid_key),
                normalize_external_mesh=args.normalize_external_mesh,
                force=args.force_regenerate,
            )


def _maybe_generate(
    path: Path,
    n_samples: int,
    split: str,
    seed: int,
    grid: tuple[int, int],
    mesh_kind: str,
    perturbation: float,
    mesh_file: Path | None,
    normalize_external_mesh: bool,
    force: bool,
) -> None:
    if path.exists() and not force:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    save_plane_stress_fem_dataset(
        path,
        n_samples=n_samples,
        split=split,
        seed=seed,
        nx=grid[0],
        ny=grid[1],
        mesh_kind=mesh_kind,
        perturbation=perturbation,
        mesh_file=mesh_file,
        normalize_external_mesh=normalize_external_mesh,
    )
    print(f"generated {path}")


def _load_dataset(path: Path, device: str) -> dict:
    return load_fem_snapshots(path, device=device)


def _make_problem(loaded: dict):
    tensors = loaded["tensors"]
    callbacks = _make_physics_callbacks(loaded)
    return make_fem_problem_adapter(
        tensors,
        loaded["metadata"],
        residual_callback=callbacks[0] if callbacks is not None else None,
        boundary_callback=callbacks[1] if callbacks is not None else None,
        energy_callback=callbacks[2] if callbacks is not None else None,
        thermodynamic_callback=callbacks[3] if callbacks is not None and len(callbacks) > 3 else None,
    )


def _make_physics_callbacks(loaded: dict):
    tensors = loaded["tensors"]
    extra = loaded["extra"]
    if has_stateful_nonlinear_fem_data(tensors, extra):
        return make_stateful_nonlinear_fem_callbacks(tensors, extra)
    if has_assembled_linear_fem_data(extra):
        return make_assembled_linear_fem_callbacks(tensors, extra)
    if "connectivity" in extra:
        return make_plane_stress_fem_callbacks(
            coords=tensors["coords"],
            connectivity=extra["connectivity"],
            grid_shape=_grid_shape_from_loaded(loaded),
        )
    return None


def _training_args(args: argparse.Namespace) -> SimpleNamespace:
    return SimpleNamespace(
        batch_size=args.batch_size,
        learning_rate=args.learning_rate,
        pde_weight=args.pde_weight,
        boundary_weight=args.boundary_weight,
        energy_weight=args.energy_weight,
        loss_balancer=args.loss_balancer,
        normalize_physics=True,
        epochs=args.epochs,
        device=args.device,
        physics_curriculum=args.physics_curriculum,
        physics_warmup_epochs=args.physics_warmup_epochs,
        physics_start_scale=args.physics_start_scale,
        physics_end_scale=args.physics_end_scale,
        gradnorm_penalty_weight=args.gradnorm_penalty_weight,
    )


def _summarize_mesh_transfer(seed_results: list[dict]) -> dict:
    grid_keys = sorted(seed_results[0]["eval_grids"])
    summary = {
        "num_seeds": len(seed_results),
        "training_strategy": seed_results[0].get("training_strategy", {}),
        "train_final_loss": _mean_std([result["train_final_loss"] for result in seed_results]),
        "eval_grids": {},
    }
    for grid_key in grid_keys:
        summary["eval_grids"][grid_key] = {}
        for split in ("test", "ood_material", "ood_loading"):
            metric_keys = sorted(seed_results[0]["eval_grids"][grid_key][split])
            summary["eval_grids"][grid_key][split] = {
                metric: _mean_std(
                    [result["eval_grids"][grid_key][split][metric] for result in seed_results]
                )
                for metric in metric_keys
            }
    return summary


def _write_csv(path: Path, model_results: dict) -> None:
    fields = [
        "model",
        "grid",
        "split",
        "relative_l2",
        "pde_residual_relative",
        "boundary_relative",
        "energy_error_relative",
        "coverage_95",
        "ece",
        "crps",
        "sharpness",
        "interval_width_95",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for model_name, result in model_results.items():
            for grid_key, grid_result in result["summary"]["eval_grids"].items():
                for split, split_result in grid_result.items():
                    writer.writerow(
                        {
                            "model": model_name,
                            "grid": grid_key,
                            "split": split,
                            "relative_l2": _maybe_metric(split_result, "relative_l2"),
                            "pde_residual_relative": _maybe_metric(split_result, "pde_residual_relative"),
                            "boundary_relative": _maybe_metric(split_result, "boundary_relative"),
                            "energy_error_relative": _maybe_metric(split_result, "energy_error_relative"),
                            "coverage_95": _maybe_metric(split_result, "coverage_95"),
                            "ece": _maybe_metric(split_result, "ece"),
                            "crps": _maybe_metric(split_result, "crps"),
                            "sharpness": _maybe_metric(split_result, "sharpness"),
                            "interval_width_95": _maybe_metric(split_result, "interval_width_95"),
                        }
                    )


def _maybe_metric(split_result: dict, key: str) -> float | str:
    if key not in split_result:
        return ""
    return split_result[key]["mean"]


def _parse_grid(text: str) -> tuple[int, int]:
    parts = text.strip().lower().split("x")
    if len(parts) != 2:
        raise ValueError(f"grid must look like 9x7, got {text!r}")
    return int(parts[0]), int(parts[1])


def _train_dir(args: argparse.Namespace, grid: tuple[int, int]) -> Path:
    return DATA_ROOT / f"{_mesh_tag(args)}_train_nx{grid[0]}_ny{grid[1]}_n{args.train_samples}"


def _eval_dir(args: argparse.Namespace, grid: tuple[int, int], mesh_file: Path | None = None) -> Path:
    tag = _mesh_tag(args) if mesh_file is None else _external_mesh_tag(mesh_file)
    return DATA_ROOT / f"{tag}_eval_nx{grid[0]}_ny{grid[1]}_n{args.eval_samples}"


def _mesh_tag(args: argparse.Namespace) -> str:
    if args.train_mesh_file is not None:
        return _external_mesh_tag(args.train_mesh_file)
    perturb = int(round(args.geometry_perturbation * 1000))
    return f"{args.mesh_kind}_p{perturb}"


def _external_mesh_tag(path: Path) -> str:
    return f"external_{path.stem}"


def _parse_eval_mesh_files(args: argparse.Namespace, eval_grids: list[tuple[int, int]]) -> dict[str, Path]:
    if not args.eval_mesh_files.strip():
        return {}
    files = [Path(part.strip()) for part in args.eval_mesh_files.split(",") if part.strip()]
    if len(files) != len(eval_grids):
        raise ValueError("--eval-mesh-files must have the same count as --eval-grids")
    return {f"{grid[0]}x{grid[1]}": file for grid, file in zip(eval_grids, files, strict=True)}


def _mean_std(values: list[float]) -> dict[str, float]:
    tensor = torch.tensor(values, dtype=torch.float64)
    std = tensor.std(unbiased=False) if tensor.numel() > 1 else tensor.new_tensor(0.0)
    return {"mean": float(tensor.mean()), "std": float(std)}


if __name__ == "__main__":
    main()
