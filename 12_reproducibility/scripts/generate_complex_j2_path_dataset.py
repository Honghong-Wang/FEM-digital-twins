from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pcgno_dt.numerics.j2plasticity2d import J2_LOAD_PATHS, save_j2_plasticity_fem_dataset

LOAD_PATHS = J2_LOAD_PATHS
MESH_KINDS = (
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


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Generate a medium-scale complex-geometry J2 FEM path dataset for path-OOD "
            "stateful operator evidence."
        )
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=PROJECT_ROOT / "05_data_pipeline" / "processed" / "j2_complex_geometry_path_fem2d",
    )
    parser.add_argument("--train-samples", type=int, default=40)
    parser.add_argument("--eval-samples", type=int, default=16)
    parser.add_argument("--nx", type=int, default=8)
    parser.add_argument("--ny", type=int, default=6)
    parser.add_argument(
        "--mesh-kind",
        choices=MESH_KINDS,
        default="hole",
    )
    parser.add_argument(
        "--mesh-kinds",
        type=str,
        default=None,
        help=(
            "Comma-separated geometry families. When more than one family or mesh size is "
            "requested, outputs are nested as <out-dir>/<mesh-kind>_<nx>x<ny>/<load-path>/<split>.npz."
        ),
    )
    parser.add_argument(
        "--mesh-sizes",
        type=str,
        default=None,
        help="Comma-separated grid sizes, e.g. 16x12,24x18,32x24.",
    )
    parser.add_argument("--geometry-perturbation", type=float, default=0.12)
    parser.add_argument(
        "--mesh-file",
        type=Path,
        default=None,
        help="Optional external triangular mesh exported from Gmsh/Abaqus/FEniCS/NPZ.",
    )
    parser.add_argument(
        "--normalize-external-mesh",
        action=argparse.BooleanOptionalAction,
        default=True,
    )
    parser.add_argument("--load-steps", type=int, default=10)
    parser.add_argument("--max-newton-steps", type=int, default=18)
    parser.add_argument(
        "--element-order",
        choices=("linear", "quadratic", "t3", "t6", "p1", "p2"),
        default="linear",
        help="Use linear T3/P1 or quadratic T6/P2 triangular elements.",
    )
    parser.add_argument(
        "--quadrature-order",
        type=int,
        default=None,
        help="Triangle quadrature order. Defaults to 1 for T3 and 2 for T6.",
    )
    parser.add_argument(
        "--solver-backend",
        choices=("auto", "dense", "sparse"),
        default="auto",
        help="Newton tangent solve backend; auto switches large systems to sparse solves.",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=1,
        help="Sample-level parallel workers inside each split file.",
    )
    parser.add_argument(
        "--samples-per-shard",
        type=int,
        default=0,
        help=(
            "When positive, generate each split as resumable sample shards before merging "
            "into train/test.npz."
        ),
    )
    parser.add_argument(
        "--keep-shards",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Keep shard NPZ files after the merged split is written.",
    )
    parser.add_argument(
        "--splits",
        type=str,
        default="train,test,ood_material,ood_loading",
        help="Comma-separated splits to generate.",
    )
    parser.add_argument(
        "--export-tangent-sequence",
        action=argparse.BooleanOptionalAction,
        default=True,
        help=(
            "Store dense tangent matrices at every load step. Use "
            "--no-export-tangent-sequence for 200+ node data while keeping final tangents."
        ),
    )
    parser.add_argument(
        "--export-final-tangent",
        action=argparse.BooleanOptionalAction,
        default=True,
        help=(
            "Store dense final tangent matrices. Use --no-export-final-tangent for "
            "500-1000 node formal training datasets and keep a smaller audit shard with tangents."
        ),
    )
    parser.add_argument("--load-paths", type=str, default=",".join(LOAD_PATHS))
    parser.add_argument("--seed", type=int, default=20260517)
    parser.add_argument(
        "--path-specific-sampling",
        action="store_true",
        help=(
            "Use different mesh/parameter seeds for each load path. By default, all load "
            "paths share the same split seeds so path-OOD is not confounded with geometry OOD."
        ),
    )
    parser.add_argument(
        "--force-regenerate",
        action="store_true",
        help="Regenerate existing split files instead of resuming missing files only.",
    )
    parser.add_argument(
        "--paper-preset",
        action="store_true",
        help=(
            "Use a Level-4 complex-geometry preset: multi_hole/notch/curved_hole, "
            "16x12/24x18/32x24 meshes, 96 train and 32 evaluation samples per path."
        ),
    )
    parser.add_argument(
        "--level6-preset",
        action="store_true",
        help=(
            "Use a Level-6 benchmark matrix preset with six path families, six "
            "geometry families, and multiple mesh sizes."
        ),
    )
    parser.add_argument(
        "--level6-smoke-preset",
        action="store_true",
        help=(
            "Use a small geometry-family x path-family x mesh-family matrix for "
            "fast schema and runner validation."
        ),
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=None,
        help="Optional JSON manifest path. Defaults to a preset-aware manifest under <out-dir>.",
    )
    args = parser.parse_args()

    if args.level6_smoke_preset:
        args.train_samples = 2
        args.eval_samples = 1
        args.load_steps = 4
        args.max_newton_steps = 8
        args.load_paths = "monotonic,cyclic,nonproportional"
        args.mesh_kinds = args.mesh_kinds or "multi_hole,notch"
        args.mesh_sizes = args.mesh_sizes or "6x5,8x6"
        args.splits = "train,test"
        args.export_tangent_sequence = False
        args.export_final_tangent = False
    if args.paper_preset:
        args.train_samples = max(args.train_samples, 96)
        args.eval_samples = max(args.eval_samples, 32)
        args.load_steps = max(args.load_steps, 12)
        args.max_newton_steps = max(args.max_newton_steps, 20)
        args.mesh_kinds = args.mesh_kinds or "multi_hole,notch,curved_hole"
        if args.mesh_sizes is None:
            args.mesh_sizes = "14x11,16x12,18x14" if args.element_order in {"quadratic", "t6", "p2"} else "16x12,24x18,32x24"
    if args.level6_preset:
        args.train_samples = max(args.train_samples, 128)
        args.eval_samples = max(args.eval_samples, 40)
        args.load_steps = max(args.load_steps, 12)
        args.max_newton_steps = max(args.max_newton_steps, 24)
        args.load_paths = ",".join(LOAD_PATHS)
        args.mesh_kinds = args.mesh_kinds or "multi_hole,notch,curved_hole,random_holes,crack_tip,stress_concentration"
        if args.mesh_sizes is None:
            args.mesh_sizes = "14x11,18x14,22x17" if args.element_order in {"quadratic", "t6", "p2"} else "16x12,24x18,32x24"

    load_paths = _parse_load_paths(args.load_paths)
    mesh_kinds = _parse_mesh_kinds(args.mesh_kinds or args.mesh_kind)
    mesh_sizes = _parse_mesh_sizes(args.mesh_sizes, args.nx, args.ny)
    splits = _parse_splits(args.splits)
    multi_case = len(mesh_kinds) > 1 or len(mesh_sizes) > 1
    split_counts_all = {
        "train": args.train_samples,
        "test": args.eval_samples,
        "ood_material": args.eval_samples,
        "ood_loading": args.eval_samples,
    }
    split_counts = {split: split_counts_all[split] for split in splits}
    manifest_entries = []
    for geometry_index, mesh_kind in enumerate(mesh_kinds):
        for size_index, (nx, ny) in enumerate(mesh_sizes):
            geometry_root = args.out_dir / f"{mesh_kind}_{nx}x{ny}" if multi_case else args.out_dir
            for path_index, load_path in enumerate(load_paths):
                path_dir = geometry_root / load_path
                path_dir.mkdir(parents=True, exist_ok=True)
                for split_index, (split, count) in enumerate(split_counts.items()):
                    out = path_dir / f"{split}.npz"
                    seed = args.seed + 10_000 * geometry_index + 1_000 * size_index + split_index
                    if args.path_specific_sampling:
                        seed += 100 * path_index
                    manifest_entries.append(
                        {
                            "path": str(out),
                            "mesh_kind": mesh_kind,
                            "nx": nx,
                            "ny": ny,
                            "load_path": load_path,
                            "split": split,
                            "samples": count,
                            "seed": seed,
                            "load_steps": args.load_steps,
                            "export_tangent_sequence": args.export_tangent_sequence,
                            "export_final_tangent": args.export_final_tangent,
                            "element_order": args.element_order,
                            "quadrature_order": args.quadrature_order,
                            "solver_backend": args.solver_backend,
                            "workers": args.workers,
                            "samples_per_shard": args.samples_per_shard,
                        }
                    )
                    if out.exists() and not args.force_regenerate:
                        print(f"skip existing {out}")
                        continue
                    _save_j2_dataset(
                        out,
                        n_samples=count,
                        split=split,
                        seed=seed,
                        nx=nx,
                        ny=ny,
                        mesh_kind=mesh_kind,
                        perturbation=args.geometry_perturbation,
                        mesh_file=args.mesh_file,
                        normalize_external_mesh=args.normalize_external_mesh,
                        load_steps=args.load_steps,
                        load_path=load_path,
                        max_newton_steps=args.max_newton_steps,
                        element_order=args.element_order,
                        quadrature_order=args.quadrature_order,
                        solver_backend=args.solver_backend,
                        export_tangent_sequence=args.export_tangent_sequence,
                        export_final_tangent=args.export_final_tangent,
                        num_workers=args.workers,
                        samples_per_shard=args.samples_per_shard,
                        keep_shards=args.keep_shards,
                        force_regenerate=args.force_regenerate,
                    )
                    print(f"generated {out}")
    if args.level6_preset:
        default_manifest_name = "level6_j2_benchmark_manifest.json"
    elif args.level6_smoke_preset:
        default_manifest_name = "level6_j2_benchmark_smoke_manifest.json"
    elif args.paper_preset:
        default_manifest_name = "level4_complex_j2_manifest.json"
    else:
        default_manifest_name = "j2_complex_path_benchmark_manifest.json"
    manifest_path = args.manifest or args.out_dir / default_manifest_name
    if args.level6_preset:
        description = "Level-6 path-family x geometry-family x mesh-family J2 benchmark manifest"
    elif args.level6_smoke_preset:
        description = "Level-6 smoke path-family x geometry-family x mesh-family J2 benchmark manifest"
    elif args.paper_preset:
        description = "Level-4 complex-geometry J2 path dataset manifest"
    else:
        description = "Custom path-family x geometry-family x mesh-family J2 benchmark manifest"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps(
            {
                "description": description,
                "train_samples": args.train_samples,
                "eval_samples": args.eval_samples,
                "load_steps": args.load_steps,
                "max_newton_steps": args.max_newton_steps,
                "splits": list(splits),
                "export_tangent_sequence": args.export_tangent_sequence,
                "export_final_tangent": args.export_final_tangent,
                "element_order": args.element_order,
                "quadrature_order": args.quadrature_order,
                "solver_backend": args.solver_backend,
                "workers": args.workers,
                "path_specific_sampling": args.path_specific_sampling,
                "path_families": list(load_paths),
                "geometry_families": list(mesh_kinds),
                "mesh_sizes": [list(size) for size in mesh_sizes],
                "entries": manifest_entries,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"wrote {manifest_path}")


def _save_j2_dataset(
    path: Path,
    *,
    n_samples: int,
    split: str,
    seed: int,
    nx: int,
    ny: int,
    mesh_kind: str,
    perturbation: float,
    mesh_file: Path | None,
    normalize_external_mesh: bool,
    load_steps: int,
    load_path: str,
    max_newton_steps: int,
    element_order: str,
    quadrature_order: int | None,
    solver_backend: str,
    export_tangent_sequence: bool,
    export_final_tangent: bool,
    num_workers: int,
    samples_per_shard: int,
    keep_shards: bool,
    force_regenerate: bool,
) -> None:
    if samples_per_shard <= 0 or n_samples <= samples_per_shard:
        save_j2_plasticity_fem_dataset(
            path,
            n_samples=n_samples,
            split=split,
            seed=seed,
            nx=nx,
            ny=ny,
            mesh_kind=mesh_kind,
            perturbation=perturbation,
            mesh_file=mesh_file,
            normalize_external_mesh=normalize_external_mesh,
            load_steps=load_steps,
            load_path=load_path,
            max_newton_steps=max_newton_steps,
            element_order=element_order,
            quadrature_order=quadrature_order,
            solver_backend=solver_backend,
            export_tangent_sequence=export_tangent_sequence,
            export_final_tangent=export_final_tangent,
            num_workers=num_workers,
        )
        return

    shard_dir = path.parent / f".{path.stem}_shards"
    shard_dir.mkdir(parents=True, exist_ok=True)
    shard_paths = []
    for shard_index, sample_offset in enumerate(range(0, n_samples, samples_per_shard)):
        shard_count = min(samples_per_shard, n_samples - sample_offset)
        shard_path = shard_dir / f"{path.stem}_shard_{shard_index:04d}.npz"
        shard_paths.append(shard_path)
        if shard_path.exists() and not force_regenerate and _is_readable_npz(shard_path):
            print(f"reuse shard {shard_path}")
            continue
        tmp_path = shard_path.with_name(f"{shard_path.stem}.tmp{shard_path.suffix}")
        tmp_path.unlink(missing_ok=True)
        save_j2_plasticity_fem_dataset(
            tmp_path,
            n_samples=shard_count,
            split=split,
            seed=seed,
            sample_offset=sample_offset,
            nx=nx,
            ny=ny,
            mesh_kind=mesh_kind,
            perturbation=perturbation,
            mesh_file=mesh_file,
            normalize_external_mesh=normalize_external_mesh,
            load_steps=load_steps,
            load_path=load_path,
            max_newton_steps=max_newton_steps,
            element_order=element_order,
            quadrature_order=quadrature_order,
            solver_backend=solver_backend,
            export_tangent_sequence=export_tangent_sequence,
            export_final_tangent=export_final_tangent,
            num_workers=num_workers,
        )
        tmp_path.replace(shard_path)
        print(f"generated shard {shard_path}")
    _merge_shards(path, shard_paths)
    if not keep_shards:
        for shard_path in shard_paths:
            shard_path.unlink(missing_ok=True)


def _merge_shards(path: Path, shard_paths: list[Path]) -> None:
    loaded = [dict(np.load(shard_path, allow_pickle=True)) for shard_path in shard_paths]
    sample_counts = [int(np.asarray(shard["params"]).shape[0]) for shard in loaded]
    merged = {}
    first = loaded[0]
    for key, first_value in first.items():
        first_array = np.asarray(first_value)
        if first_array.ndim > 0 and first_array.shape[0] == sample_counts[0]:
            merged[key] = np.concatenate([np.asarray(shard[key]) for shard in loaded], axis=0)
        else:
            merged[key] = first_array
    merged["sample_id"] = np.arange(sum(sample_counts), dtype=np.int64)
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez(path, **merged)


def _is_readable_npz(path: Path) -> bool:
    try:
        with np.load(path, allow_pickle=True) as data:
            return "params" in data and int(np.asarray(data["params"]).shape[0]) > 0
    except Exception:
        return False


def _parse_load_paths(value: str) -> tuple[str, ...]:
    paths = tuple(item.strip() for item in value.split(",") if item.strip())
    unknown = sorted(set(paths).difference(LOAD_PATHS))
    if unknown:
        raise argparse.ArgumentTypeError(f"unknown load paths {unknown}; options are {list(LOAD_PATHS)}")
    if not paths:
        raise argparse.ArgumentTypeError("at least one load path is required")
    return paths


def _parse_mesh_kinds(value: str) -> tuple[str, ...]:
    supported = MESH_KINDS
    kinds = tuple(item.strip() for item in value.split(",") if item.strip())
    unknown = sorted(set(kinds).difference(supported))
    if unknown:
        raise argparse.ArgumentTypeError(f"unknown mesh kinds {unknown}; options are {list(supported)}")
    if not kinds:
        raise argparse.ArgumentTypeError("at least one mesh kind is required")
    return kinds


def _parse_mesh_sizes(value: str | None, nx: int, ny: int) -> tuple[tuple[int, int], ...]:
    if value is None:
        return ((nx, ny),)
    sizes = []
    for item in value.split(","):
        item = item.strip().lower()
        if not item:
            continue
        if "x" not in item:
            raise argparse.ArgumentTypeError("mesh sizes must use the form NxM, e.g. 16x12")
        left, right = item.split("x", 1)
        sizes.append((int(left), int(right)))
    if not sizes:
        raise argparse.ArgumentTypeError("at least one mesh size is required")
    return tuple(sizes)


def _parse_splits(value: str) -> tuple[str, ...]:
    supported = ("train", "test", "ood_material", "ood_loading")
    splits = tuple(item.strip() for item in value.split(",") if item.strip())
    unknown = sorted(set(splits).difference(supported))
    if unknown:
        raise argparse.ArgumentTypeError(f"unknown splits {unknown}; options are {list(supported)}")
    if not splits:
        raise argparse.ArgumentTypeError("at least one split is required")
    return splits


if __name__ == "__main__":
    main()
