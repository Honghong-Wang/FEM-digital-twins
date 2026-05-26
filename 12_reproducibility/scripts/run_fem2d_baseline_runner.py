from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pcgno_dt.data.datasets import OperatorTensorDataset
from pcgno_dt.data.fem import (
    has_assembled_linear_fem_data,
    has_stateful_nonlinear_fem_data,
    load_fem_snapshots,
    make_assembled_linear_fem_callbacks,
    make_fem_problem_adapter,
    make_stateful_nonlinear_fem_callbacks,
)
from pcgno_dt.evaluation.comparison import evaluate_prediction
from pcgno_dt.evaluation.physics import evaluate_physics_consistency
from pcgno_dt.models.pcgno import PCGNOConfig, PhysicsConstrainedGenerativeNeuralOperator
from pcgno_dt.numerics.baselines import (
    DeepONetBaseline,
    FNOBaseline,
    MeshGraphOperatorBaseline,
    MeshToMeshGraphOperatorBaseline,
    PINNBaseline,
)
from pcgno_dt.numerics.fem2d import make_plane_stress_fem_callbacks, save_plane_stress_fem_dataset
from pcgno_dt.training.loss_balancing import make_loss_balancer
from pcgno_dt.training.losses import PhysicsLossWeights, physics_constrained_loss


def main() -> None:
    parser = argparse.ArgumentParser(description="Fair baseline runner for 2D FEM snapshots.")
    parser.add_argument(
        "--model",
        choices=("pinn", "deeponet", "fno", "meshgno", "mesh2meshgno", "pcgno", "all"),
        default="all",
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=PROJECT_ROOT / "05_data_pipeline" / "processed" / "fem2d_plane_stress",
    )
    parser.add_argument("--epochs", type=int, default=10)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--learning-rate", type=float, default=1.0e-3)
    parser.add_argument("--pde-weight", type=float, default=1.0e-4)
    parser.add_argument("--boundary-weight", type=float, default=1.0e-2)
    parser.add_argument("--energy-weight", type=float, default=1.0e-6)
    parser.add_argument(
        "--pcgno-data-loss",
        choices=("nll", "mse"),
        default="nll",
        help="Use NLL for joint probabilistic fitting or MSE for mean-first PCGNO training.",
    )
    parser.add_argument("--pcgno-hidden-dim", type=int, default=96)
    parser.add_argument("--pcgno-latent-dim", type=int, default=16)
    parser.add_argument("--pcgno-fourier-modes", type=int, default=8)
    parser.add_argument(
        "--loss-balancer",
        choices=("static", "uncertainty", "gradnorm", "softadapt", "residual_adaptive"),
        default="static",
        help="Loss balancing strategy for PCGNO.",
    )
    parser.add_argument(
        "--physics-curriculum",
        choices=("constant", "linear", "cosine", "step"),
        default="constant",
        help="Schedule for PDE, boundary, and energy terms.",
    )
    parser.add_argument(
        "--physics-warmup-epochs",
        type=int,
        default=0,
        help="Number of epochs used to ramp physics terms for non-constant curricula.",
    )
    parser.add_argument("--physics-start-scale", type=float, default=0.0)
    parser.add_argument("--physics-end-scale", type=float, default=1.0)
    parser.add_argument(
        "--gradnorm-penalty-weight",
        type=float,
        default=0.1,
        help="Reserved for sweeps that compare GradNorm penalty strength.",
    )
    parser.add_argument(
        "--normalize-physics",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Normalize PDE, boundary, and energy loss terms by batch reference scales.",
    )
    parser.add_argument("--train-samples", type=int, default=64)
    parser.add_argument("--eval-samples", type=int, default=24)
    parser.add_argument("--nx", type=int, default=9)
    parser.add_argument("--ny", type=int, default=7)
    parser.add_argument(
        "--mesh-kind",
        choices=("structured", "jittered", "hole", "notch", "curved"),
        default="structured",
    )
    parser.add_argument("--geometry-perturbation", type=float, default=0.0)
    parser.add_argument(
        "--mesh-file",
        type=Path,
        default=None,
        help="External mesh file (.msh, .inp, .xml, .xdmf inline, or .npz) to use instead of procedural mesh.",
    )
    parser.add_argument(
        "--normalize-external-mesh",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Normalize imported external mesh coordinates to a unit bounding box.",
    )
    parser.add_argument("--seed", type=int, default=20260516)
    parser.add_argument("--num-seeds", type=int, default=1)
    parser.add_argument("--force-regenerate", action="store_true")
    parser.add_argument("--device", default="cpu")
    parser.add_argument(
        "--out",
        type=Path,
        default=PROJECT_ROOT / "10_results" / "reports" / "fem2d_baseline_runner_results.json",
        help="JSON report path for the baseline comparison.",
    )
    args = parser.parse_args()

    _ensure_dataset(args)
    train = _load_split(args.data_dir, "train", args.device)
    test = _load_split(args.data_dir, "test", args.device)
    ood_material = _load_split(args.data_dir, "ood_material", args.device)
    ood_loading = _load_split(args.data_dir, "ood_loading", args.device)

    metadata = train["metadata"]
    tensors = train["tensors"]
    grid_shape = _grid_shape_from_loaded(train)
    spatial_dim = tensors["coords"].shape[-1]
    num_parameters = tensors["params"].shape[-1]
    num_fields = tensors["fields"].shape[-1]
    callbacks = _make_physics_callbacks(train)
    problem = make_fem_problem_adapter(
        tensors,
        metadata,
        residual_callback=callbacks[0] if callbacks is not None else None,
        boundary_callback=callbacks[1] if callbacks is not None else None,
        energy_callback=callbacks[2] if callbacks is not None else None,
        thermodynamic_callback=callbacks[3] if callbacks is not None and len(callbacks) > 3 else None,
    )

    full_tensor_grid = _has_full_tensor_grid(train)
    if args.model == "all":
        model_names = ["pinn", "deeponet", "meshgno", "mesh2meshgno", "pcgno"]
        if full_tensor_grid:
            model_names.insert(2, "fno")
        model_names = tuple(model_names)
    else:
        if args.model == "fno" and not full_tensor_grid:
            raise ValueError("FNO requires a full tensor-product grid; use structured/jittered/curved meshes")
        model_names = (args.model,)
    all_results = {}
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
                grid_shape=grid_shape,
                args=args,
            ).to(args.device)
            if hasattr(model, "set_source_coords"):
                model.set_source_coords(train["tensors"]["coords"])
            train_result = _train_model(model_name, model, train["tensors"], problem, args)
            seed_result = {
                "seed": run_seed,
                "train_final_loss": train_result["loss_history"][-1],
                "loss_balancer": train_result["loss_balancer"],
                "training_strategy": train_result["training_strategy"],
                "test": _evaluate_model(model, test["tensors"], model_name, problem),
                "ood_material": _evaluate_model(model, ood_material["tensors"], model_name, problem),
                "ood_loading": _evaluate_model(model, ood_loading["tensors"], model_name, problem),
            }
            seed_results.append(seed_result)
        results = {
            "seeds": seed_results,
            "summary": summarize_seed_results(seed_results),
        }
        all_results[model_name] = results
        print(json.dumps({model_name: results["summary"]}, indent=2))

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(all_results, indent=2), encoding="utf-8")
    print(f"wrote {args.out}")


def _ensure_dataset(args: argparse.Namespace) -> None:
    args.data_dir.mkdir(parents=True, exist_ok=True)
    split_counts = {
        "train": args.train_samples,
        "test": args.eval_samples,
        "ood_material": args.eval_samples,
        "ood_loading": args.eval_samples,
    }
    for index, (split, count) in enumerate(split_counts.items()):
        path = args.data_dir / f"{split}.npz"
        if path.exists() and not args.force_regenerate:
            continue
        save_plane_stress_fem_dataset(
            path,
            n_samples=count,
            split=split,
            seed=args.seed + index,
            nx=args.nx,
            ny=args.ny,
            mesh_kind=args.mesh_kind,
            perturbation=args.geometry_perturbation,
            mesh_file=args.mesh_file,
            normalize_external_mesh=args.normalize_external_mesh,
        )
        print(f"generated {path}")


def _load_split(data_dir: Path, split: str, device: str):
    return load_fem_snapshots(data_dir / f"{split}.npz", device=device)


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


def _grid_shape_from_loaded(loaded: dict) -> tuple[int, int]:
    extra = loaded["extra"]
    if "grid_shape" in extra:
        values = torch.as_tensor(extra["grid_shape"]).reshape(-1).tolist()
        if len(values) >= 2 and int(values[0]) > 0 and int(values[1]) > 0:
            return int(values[0]), int(values[1])
    n_nodes = int(loaded["tensors"]["coords"].shape[1])
    return n_nodes, 1


def _has_full_tensor_grid(loaded: dict) -> bool:
    if "grid_shape" not in loaded["extra"]:
        return False
    values = torch.as_tensor(loaded["extra"]["grid_shape"]).reshape(-1).tolist()
    if len(values) < 2:
        return False
    grid_shape = int(values[0]), int(values[1])
    return (
        grid_shape[0] > 0
        and grid_shape[1] > 0
        and int(loaded["tensors"]["coords"].shape[1]) == grid_shape[0] * grid_shape[1]
    )


def _make_model(
    model_name: str,
    num_parameters: int,
    num_fields: int,
    spatial_dim: int,
    grid_shape: tuple[int, int],
    args: argparse.Namespace,
) -> torch.nn.Module:
    if model_name == "pinn":
        return PINNBaseline(num_parameters, num_fields, spatial_dim=spatial_dim)
    if model_name == "deeponet":
        return DeepONetBaseline(num_parameters, num_fields, spatial_dim=spatial_dim)
    if model_name == "fno":
        return FNOBaseline(
            num_parameters,
            num_fields,
            spatial_dim=spatial_dim,
            grid_shape=grid_shape,
        )
    if model_name == "meshgno":
        return MeshGraphOperatorBaseline(
            num_parameters,
            num_fields,
            spatial_dim=spatial_dim,
        )
    if model_name == "mesh2meshgno":
        return MeshToMeshGraphOperatorBaseline(
            num_parameters,
            num_fields,
            spatial_dim=spatial_dim,
        )
    if model_name == "pcgno":
        return PhysicsConstrainedGenerativeNeuralOperator(
            PCGNOConfig(
                num_parameters=num_parameters,
                num_fields=num_fields,
                spatial_dim=spatial_dim,
                hidden_dim=args.pcgno_hidden_dim,
                latent_dim=args.pcgno_latent_dim,
                num_fourier_modes=args.pcgno_fourier_modes,
            )
        )
    raise ValueError(f"unknown model: {model_name}")


def _train_model(
    model_name: str,
    model: torch.nn.Module,
    train_tensors: dict[str, torch.Tensor],
    problem,
    args: argparse.Namespace,
) -> dict[str, object]:
    loader = DataLoader(OperatorTensorDataset(train_tensors), batch_size=args.batch_size, shuffle=True)
    balancer = make_loss_balancer(args.loss_balancer) if model_name == "pcgno" else None
    if balancer is not None and hasattr(balancer, "penalty_weight"):
        balancer.penalty_weight = args.gradnorm_penalty_weight
    optimizer_params = list(model.parameters())
    if balancer is not None:
        balancer = balancer.to(args.device)
        optimizer_params.extend(list(balancer.parameters()))
    optimizer = torch.optim.Adam(optimizer_params, lr=args.learning_rate)
    history = []
    last_effective_weights: dict[str, float] = {}
    last_physics_scale = 1.0
    shared_parameters = list(model.parameters()) if args.loss_balancer == "gradnorm" else None
    for epoch in range(args.epochs):
        physics_scale = _physics_curriculum_scale(epoch, args)
        last_physics_scale = physics_scale
        weights = PhysicsLossWeights(
            data=1.0,
            pde_residual=args.pde_weight * physics_scale,
            boundary=args.boundary_weight * physics_scale,
            energy=args.energy_weight * physics_scale,
            calibration=0.01,
            normalize_physics=args.normalize_physics,
            data_loss_mode=args.pcgno_data_loss,
        )
        term_scales = {
            "pde_residual": physics_scale,
            "boundary": physics_scale,
            "energy": physics_scale,
        }
        running = 0.0
        for batch in loader:
            optimizer.zero_grad()
            if model_name == "pcgno":
                outputs = model(batch["coords"], batch["params"], n_samples=0)
                losses = physics_constrained_loss(outputs, batch, problem, weights)
                balanced = (
                    balancer(
                        losses,
                        shared_parameters=shared_parameters,
                        term_scales=term_scales,
                    )
                    if balancer is not None
                    else {"total": losses["total"], "effective_weights": {}}
                )
                loss = balanced["total"]
                last_effective_weights = dict(balanced.get("effective_weights", {}))
            else:
                outputs = model(batch["coords"], batch["params"])
                loss = F.mse_loss(outputs["mean"], batch["fields"])
            loss.backward()
            optimizer.step()
            running += float(loss.detach())
        history.append(running / max(len(loader), 1))
    if balancer is None:
        balancer_state = {"type": "none" if model_name != "pcgno" else args.loss_balancer}
    else:
        balancer_state = {
            "type": args.loss_balancer,
            "effective_weights": last_effective_weights,
        }
    training_strategy = {
        "physics_curriculum": args.physics_curriculum,
        "physics_warmup_epochs": args.physics_warmup_epochs,
        "physics_start_scale": args.physics_start_scale,
        "physics_end_scale": args.physics_end_scale,
        "final_physics_scale": last_physics_scale,
        "gradnorm_penalty_weight": args.gradnorm_penalty_weight,
        "normalize_physics": args.normalize_physics,
        "pcgno_data_loss": args.pcgno_data_loss,
        "pcgno_hidden_dim": args.pcgno_hidden_dim,
        "pcgno_latent_dim": args.pcgno_latent_dim,
        "pcgno_fourier_modes": args.pcgno_fourier_modes,
    }
    return {
        "loss_history": history,
        "loss_balancer": balancer_state,
        "training_strategy": training_strategy,
    }


def _evaluate_model(
    model: torch.nn.Module,
    tensors: dict[str, torch.Tensor],
    model_name: str,
    problem,
) -> dict[str, float]:
    model.eval()
    with torch.no_grad():
        if model_name == "pcgno":
            outputs = model(tensors["coords"], tensors["params"], n_samples=16)
            metrics = evaluate_prediction(
                outputs["mean"],
                tensors["fields"],
                outputs["samples"],
                logvar=outputs["logvar"],
            )
        else:
            outputs = model(tensors["coords"], tensors["params"])
            metrics = evaluate_prediction(outputs["mean"], tensors["fields"])
        metrics.update(evaluate_physics_consistency(outputs["mean"], tensors, problem))
    model.train()
    return {key: float(value.detach().cpu()) for key, value in metrics.items()}


def summarize_seed_results(seed_results: list[dict]) -> dict:
    summary: dict[str, object] = {"num_seeds": len(seed_results)}
    summary["training_strategy"] = seed_results[0].get("training_strategy", {})
    summary["train_final_loss"] = _mean_std([result["train_final_loss"] for result in seed_results])
    if any(result.get("loss_balancer", {}).get("effective_weights") for result in seed_results):
        weight_keys = sorted(
            {
                key
                for result in seed_results
                for key in result.get("loss_balancer", {}).get("effective_weights", {})
            }
        )
        summary["loss_balancer_weights"] = {
            key: _mean_std(
                [
                    result.get("loss_balancer", {}).get("effective_weights", {}).get(key, 0.0)
                    for result in seed_results
                ]
            )
            for key in weight_keys
        }
    for split in ("test", "ood_material", "ood_loading"):
        keys = sorted(seed_results[0][split])
        summary[split] = {
            key: _mean_std([result[split][key] for result in seed_results])
            for key in keys
        }
    if "sharpness" in seed_results[0]["test"]:
        summary["ood_uncertainty_separation"] = {
            "ood_material_sharpness_ratio": _mean_std(
                [
                    result["ood_material"]["sharpness"] / max(result["test"]["sharpness"], 1.0e-12)
                    for result in seed_results
                ]
            ),
            "ood_loading_sharpness_ratio": _mean_std(
                [
                    result["ood_loading"]["sharpness"] / max(result["test"]["sharpness"], 1.0e-12)
                    for result in seed_results
                ]
            ),
        }
    return summary


def _mean_std(values: list[float]) -> dict[str, float]:
    tensor = torch.tensor(values, dtype=torch.float64)
    std = tensor.std(unbiased=False) if tensor.numel() > 1 else tensor.new_tensor(0.0)
    return {
        "mean": float(tensor.mean()),
        "std": float(std),
    }


def _physics_curriculum_scale(epoch: int, args: argparse.Namespace) -> float:
    if args.physics_curriculum == "constant":
        return 1.0
    if args.physics_warmup_epochs <= 0:
        return args.physics_end_scale
    progress = min(max((epoch + 1) / args.physics_warmup_epochs, 0.0), 1.0)
    if args.physics_curriculum == "linear":
        factor = progress
    elif args.physics_curriculum == "cosine":
        factor = 0.5 - 0.5 * torch.cos(torch.tensor(progress * torch.pi)).item()
    elif args.physics_curriculum == "step":
        factor = 1.0 if progress >= 1.0 else 0.0
    else:
        raise ValueError(f"unknown physics curriculum: {args.physics_curriculum}")
    return args.physics_start_scale + (args.physics_end_scale - args.physics_start_scale) * factor


if __name__ == "__main__":
    main()
