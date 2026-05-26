from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pcgno_dt.numerics.j2plasticity2d import J2_LOAD_PATHS, save_j2_plasticity_fem_dataset


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate path-dependent 2D J2 plasticity FEM snapshots.")
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=PROJECT_ROOT / "05_data_pipeline" / "processed" / "j2_plasticity_fem2d",
    )
    parser.add_argument("--train-samples", type=int, default=24)
    parser.add_argument("--eval-samples", type=int, default=8)
    parser.add_argument("--nx", type=int, default=3)
    parser.add_argument("--ny", type=int, default=3)
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
        default="structured",
    )
    parser.add_argument("--geometry-perturbation", type=float, default=0.0)
    parser.add_argument(
        "--mesh-file",
        type=Path,
        default=None,
        help="External mesh file (.msh, .inp, .xml, .xdmf inline, or .npz).",
    )
    parser.add_argument(
        "--normalize-external-mesh",
        action=argparse.BooleanOptionalAction,
        default=True,
    )
    parser.add_argument("--load-steps", type=int, default=6)
    parser.add_argument(
        "--load-path",
        choices=J2_LOAD_PATHS,
        default="monotonic",
    )
    parser.add_argument("--max-newton-steps", type=int, default=14)
    parser.add_argument("--seed", type=int, default=20260517)
    args = parser.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)
    split_counts = {
        "train": args.train_samples,
        "test": args.eval_samples,
        "ood_material": args.eval_samples,
        "ood_loading": args.eval_samples,
    }
    for index, (split, count) in enumerate(split_counts.items()):
        path = args.out_dir / f"{split}.npz"
        save_j2_plasticity_fem_dataset(
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
            load_steps=args.load_steps,
            load_path=args.load_path,
            max_newton_steps=args.max_newton_steps,
        )
        print(f"generated {path}")


if __name__ == "__main__":
    main()
