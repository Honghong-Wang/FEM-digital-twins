from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pcgno_dt.data.mesh_io import load_external_tri_mesh, save_external_tri_mesh_npz


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert external 2D FEM/CAD mesh exports to local NPZ.")
    parser.add_argument("mesh_file", type=Path)
    parser.add_argument(
        "--out",
        type=Path,
        default=PROJECT_ROOT / "05_data_pipeline" / "processed" / "external_mesh.npz",
    )
    parser.add_argument(
        "--normalize",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Normalize coordinates to a unit bounding box.",
    )
    args = parser.parse_args()

    mesh = load_external_tri_mesh(args.mesh_file, normalize=args.normalize)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    save_external_tri_mesh_npz(args.out, mesh.coords, mesh.connectivity, mesh.boundary_edges)
    print(f"wrote {args.out}")
    print(f"nodes={mesh.coords.shape[0]} triangles={mesh.connectivity.shape[0]} source={mesh.source_format}")


if __name__ == "__main__":
    main()
