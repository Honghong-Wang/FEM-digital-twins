from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import torch
from torch.utils.data import DataLoader

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pcgno_dt.data.datasets import PathOperatorTensorDataset
from pcgno_dt.data.fem import load_fem_path_snapshots
from pcgno_dt.evaluation.path_history import evaluate_j2_path_history_consistency
from pcgno_dt.models.history_gno import HistoryGraphOperator, HistoryGraphOperatorConfig
from pcgno_dt.numerics.j2plasticity2d import save_j2_plasticity_fem_dataset
from pcgno_dt.training.path_losses import PathLossWeights, history_graph_operator_loss


def main() -> None:
    parser = argparse.ArgumentParser(description="Train a recurrent HistoryGraphOperator on J2 path data.")
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=PROJECT_ROOT / "05_data_pipeline" / "processed" / "j2_plasticity_fem2d",
    )
    parser.add_argument("--epochs", type=int, default=20)
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--learning-rate", type=float, default=1.0e-3)
    parser.add_argument("--hidden-dim", type=int, default=64)
    parser.add_argument("--message-passing-layers", type=int, default=2)
    parser.add_argument("--teacher-forcing-ratio", type=float, default=0.5)
    parser.add_argument("--train-samples", type=int, default=24)
    parser.add_argument("--eval-samples", type=int, default=8)
    parser.add_argument("--nx", type=int, default=3)
    parser.add_argument("--ny", type=int, default=3)
    parser.add_argument("--load-steps", type=int, default=6)
    parser.add_argument(
        "--load-path",
        choices=("monotonic", "unload_reload", "cyclic", "nonproportional"),
        default="monotonic",
    )
    parser.add_argument("--max-newton-steps", type=int, default=14)
    parser.add_argument("--seed", type=int, default=20260517)
    parser.add_argument("--force-regenerate", action="store_true")
    parser.add_argument("--device", default="cpu")
    parser.add_argument(
        "--out",
        type=Path,
        default=PROJECT_ROOT / "10_results" / "reports" / "j2_history_operator_results.json",
    )
    args = parser.parse_args()

    _ensure_dataset(args)
    train = _load_split(args.data_dir, "train", args.device)
    test = _load_split(args.data_dir, "test", args.device)
    ood_material = _load_split(args.data_dir, "ood_material", args.device)
    ood_loading = _load_split(args.data_dir, "ood_loading", args.device)
    tensors = train["tensors"]
    connectivity = torch.as_tensor(train["extra"]["connectivity"], dtype=torch.long, device=args.device)
    history_dim = int(tensors["material_history_sequence"].shape[-1])
    model = HistoryGraphOperator(
        HistoryGraphOperatorConfig(
            num_parameters=int(tensors["params"].shape[-1]),
            num_fields=int(tensors["fields_sequence"].shape[-1]),
            spatial_dim=int(tensors["coords"].shape[-1]),
            history_dim=history_dim,
            hidden_dim=args.hidden_dim,
            num_message_passing_layers=args.message_passing_layers,
        )
    ).to(args.device)

    history = _train(model, train, connectivity, args)
    payload = {
        "metadata": {
            "model": "HistoryGraphOperator",
            "epochs": args.epochs,
            "batch_size": args.batch_size,
            "learning_rate": args.learning_rate,
            "teacher_forcing_ratio": args.teacher_forcing_ratio,
            "train_samples": args.train_samples,
            "eval_samples": args.eval_samples,
            "load_steps": args.load_steps,
            "load_path": args.load_path,
        },
        "train_loss_history": history,
        "test": _evaluate(model, test, connectivity),
        "ood_material": _evaluate(model, ood_material, connectivity),
        "ood_loading": _evaluate(model, ood_loading, connectivity),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload["test"], indent=2))
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
        save_j2_plasticity_fem_dataset(
            path,
            n_samples=count,
            split=split,
            seed=args.seed + index,
            nx=args.nx,
            ny=args.ny,
            load_steps=args.load_steps,
            load_path=args.load_path,
            max_newton_steps=args.max_newton_steps,
        )
        print(f"generated {path}")


def _load_split(data_dir: Path, split: str, device: str) -> dict:
    return load_fem_path_snapshots(data_dir / f"{split}.npz", device=device)


def _train(
    model: HistoryGraphOperator,
    loaded: dict,
    connectivity: torch.Tensor,
    args: argparse.Namespace,
) -> list[float]:
    loader = DataLoader(PathOperatorTensorDataset(loaded["tensors"]), batch_size=args.batch_size, shuffle=True)
    optimizer = torch.optim.Adam(model.parameters(), lr=args.learning_rate)
    weights = PathLossWeights()
    history = []
    for _ in range(args.epochs):
        running = 0.0
        for batch in loader:
            batch = _move_batch(batch, args.device)
            optimizer.zero_grad()
            outputs = model(
                batch["coords"],
                batch["params"],
                batch["forcing_sequence"],
                connectivity=connectivity,
                teacher_history=batch["material_history_sequence"],
                teacher_forcing_ratio=args.teacher_forcing_ratio,
            )
            losses = history_graph_operator_loss(outputs, batch, weights)
            losses["total"].backward()
            optimizer.step()
            running += float(losses["total"].detach())
        history.append(running / max(len(loader), 1))
    return history


def _evaluate(model: HistoryGraphOperator, loaded: dict, connectivity: torch.Tensor) -> dict[str, float]:
    model.eval()
    tensors = _move_batch(loaded["tensors"], next(model.parameters()).device)
    with torch.no_grad():
        outputs = model(
            tensors["coords"],
            tensors["params"],
            tensors["forcing_sequence"],
            connectivity=connectivity,
            teacher_forcing_ratio=0.0,
        )
        losses = history_graph_operator_loss(outputs, tensors, PathLossWeights())
        predicted_history_metrics = evaluate_j2_path_history_consistency(
            {
                "material_history_sequence": outputs["history_sequence"],
                "forcing_sequence": tensors["forcing_sequence"],
            }
        )
    model.train()
    metrics = {
        "total_loss": losses["total"],
        "displacement_loss": losses["displacement"],
        "history_loss": losses["history"],
        **{f"predicted_{key}": value for key, value in predicted_history_metrics.items()},
    }
    return {key: float(value.detach().cpu()) for key, value in metrics.items()}


def _move_batch(batch: dict[str, torch.Tensor], device: str | torch.device) -> dict[str, torch.Tensor]:
    return {key: value.to(device) if isinstance(value, torch.Tensor) else value for key, value in batch.items()}


if __name__ == "__main__":
    main()
