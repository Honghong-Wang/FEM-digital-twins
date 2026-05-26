from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pcgno_dt.numerics.fem2d import save_plane_stress_fem_dataset


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate 2D plane-stress FEM snapshot datasets.")
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=PROJECT_ROOT / "05_data_pipeline" / "processed" / "fem2d_plane_stress",
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
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
