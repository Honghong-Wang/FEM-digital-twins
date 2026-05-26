from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize complex-geometry J2 FEM path datasets.")
    parser.add_argument(
        "--data-root",
        type=Path,
        default=PROJECT_ROOT / "05_data_pipeline" / "processed" / "level4_large_complex_j2_evidence",
    )
    parser.add_argument(
        "--csv-out",
        type=Path,
        default=PROJECT_ROOT / "10_results" / "reports" / "level4_large_complex_j2_dataset_summary.csv",
    )
    parser.add_argument(
        "--md-out",
        type=Path,
        default=PROJECT_ROOT / "10_results" / "reports" / "level4_large_complex_j2_dataset_summary.md",
    )
    parser.add_argument(
        "--case-csv-out",
        type=Path,
        default=None,
        help="Optional case-level aggregate CSV. Defaults to <csv-out stem>_case_summary.csv.",
    )
    parser.add_argument(
        "--case-md-out",
        type=Path,
        default=None,
        help="Optional case-level aggregate Markdown. Defaults to <md-out stem>_case_summary.md.",
    )
    parser.add_argument(
        "--title",
        type=str,
        default="Complex J2 Dataset Summary",
        help="Title used in generated Markdown summaries.",
    )
    args = parser.parse_args()

    rows = []
    for path in sorted(args.data_root.rglob("*.npz")):
        with np.load(path, allow_pickle=False) as data:
            coords = data["coords"]
            fields_sequence = data["fields_sequence"]
            connectivity = data["connectivity"]
            residual_sequence = data.get("newton_residual_sequence")
            energy_sequence = data.get("reference_energy_sequence")
            tangent = data.get("tangent_stiffness")
            material_history_qp_sequence = data.get("material_history_qp_sequence")
            plastic_strain_qp_sequence = data.get("plastic_strain_qp_sequence")
            rel = path.relative_to(args.data_root)
            parts = rel.parts
            geometry = parts[0] if len(parts) >= 3 else "shared"
            load_path = parts[-2]
            split = path.stem
            residual_rms = float("nan")
            if residual_sequence is not None:
                residual_rms = float(np.sqrt(np.mean(np.square(residual_sequence))))
            energy_mean = float("nan")
            if energy_sequence is not None:
                energy_mean = float(np.mean(energy_sequence))
            rows.append(
                {
                    "geometry": geometry,
                    "load_path": load_path,
                    "split": split,
                    "samples": int(coords.shape[0]),
                    "nodes": int(coords.shape[1]),
                    "elements": int(connectivity.shape[0]),
                    "load_steps": int(fields_sequence.shape[1]),
                    "fields": int(fields_sequence.shape[-1]),
                    "has_final_tangent": bool(tangent is not None),
                    "has_tangent_sequence": "tangent_stiffness_sequence" in data.files,
                    "has_qp_history": material_history_qp_sequence is not None,
                    "has_qp_plastic_strain": plastic_strain_qp_sequence is not None,
                    "q_points": int(material_history_qp_sequence.shape[-2]) if material_history_qp_sequence is not None else 0,
                    "newton_residual_rms": residual_rms,
                    "reference_energy_mean": energy_mean,
                    "size_mb": path.stat().st_size / (1024.0 * 1024.0),
                    "path": str(path),
                }
            )

    args.csv_out.parent.mkdir(parents=True, exist_ok=True)
    with args.csv_out.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]) if rows else [])
        writer.writeheader()
        writer.writerows(rows)
    args.md_out.parent.mkdir(parents=True, exist_ok=True)
    args.md_out.write_text(_to_markdown(rows, title=args.title), encoding="utf-8")
    case_rows = _case_summary_rows(rows)
    case_csv_out = args.case_csv_out or args.csv_out.with_name(f"{args.csv_out.stem}_case_summary.csv")
    case_md_out = args.case_md_out or args.md_out.with_name(f"{args.md_out.stem}_case_summary.md")
    _write_csv(case_csv_out, case_rows)
    case_md_out.parent.mkdir(parents=True, exist_ok=True)
    case_md_out.write_text(_case_summary_markdown(case_rows, title=f"{args.title} Case Summary"), encoding="utf-8")
    manifest = {
        "data_root": str(args.data_root),
        "num_files": len(rows),
        "num_geometry_mesh_cases": len({row["geometry"] for row in rows}),
        "num_geometry_families": len({_geometry_family(row["geometry"]) for row in rows}),
        "num_load_paths": len({row["load_path"] for row in rows}),
        "node_range": [
            min(row["nodes"] for row in rows) if rows else 0,
            max(row["nodes"] for row in rows) if rows else 0,
        ],
        "element_range": [
            min(row["elements"] for row in rows) if rows else 0,
            max(row["elements"] for row in rows) if rows else 0,
        ],
        "total_size_mb": sum(row["size_mb"] for row in rows),
        "all_files_have_qp_history": all(row["has_qp_history"] for row in rows) if rows else False,
        "all_files_have_qp_plastic_strain": all(row["has_qp_plastic_strain"] for row in rows) if rows else False,
    }
    print(json.dumps(manifest, indent=2))
    print(f"wrote {args.csv_out}")
    print(f"wrote {args.md_out}")
    print(f"wrote {case_csv_out}")
    print(f"wrote {case_md_out}")


def _write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]) if rows else [])
        writer.writeheader()
        writer.writerows(rows)


def _to_markdown(rows: list[dict], title: str) -> str:
    if not rows:
        return f"# {title}\n\nNo dataset files found.\n"
    header = [
        "Geometry",
        "Path",
        "Split",
        "Samples",
        "Nodes",
        "Elements",
        "Steps",
        "K final",
        "K seq",
        "QP hist",
        "Q pts",
        "Residual RMS",
        "Size MB",
    ]
    lines = [
        f"# {title}",
        "",
        "| " + " | ".join(header) + " |",
        "| " + " | ".join(["---"] * len(header)) + " |",
    ]
    for row in rows:
        lines.append(
            "| "
            + " | ".join(
                [
                    str(row["geometry"]),
                    str(row["load_path"]),
                    str(row["split"]),
                    str(row["samples"]),
                    str(row["nodes"]),
                    str(row["elements"]),
                    str(row["load_steps"]),
                    "yes" if row["has_final_tangent"] else "no",
                    "yes" if row["has_tangent_sequence"] else "no",
                    "yes" if row["has_qp_history"] else "no",
                    str(row["q_points"]),
                    f"{row['newton_residual_rms']:.3e}",
                    f"{row['size_mb']:.2f}",
                ]
            )
            + " |"
        )
    return "\n".join(lines) + "\n"


def _case_summary_rows(rows: list[dict]) -> list[dict]:
    groups: dict[str, list[dict]] = {}
    for row in rows:
        groups.setdefault(row["geometry"], []).append(row)
    case_rows = []
    for geometry, group in sorted(groups.items()):
        case_rows.append(
            {
                "geometry": geometry,
                "family": _geometry_family(geometry),
                "files": len(group),
                "samples": sum(int(row["samples"]) for row in group),
                "load_paths": len({row["load_path"] for row in group}),
                "splits": ",".join(sorted({row["split"] for row in group})),
                "node_min": min(int(row["nodes"]) for row in group),
                "node_max": max(int(row["nodes"]) for row in group),
                "element_min": min(int(row["elements"]) for row in group),
                "element_max": max(int(row["elements"]) for row in group),
                "steps": ",".join(str(step) for step in sorted({int(row["load_steps"]) for row in group})),
                "q_points": ",".join(str(qp) for qp in sorted({int(row["q_points"]) for row in group})),
                "qp_history": all(bool(row["has_qp_history"]) for row in group),
                "qp_plastic_strain": all(bool(row["has_qp_plastic_strain"]) for row in group),
                "final_tangent": all(bool(row["has_final_tangent"]) for row in group),
                "tangent_sequence": all(bool(row["has_tangent_sequence"]) for row in group),
                "residual_rms_mean": float(np.nanmean([row["newton_residual_rms"] for row in group])),
                "size_mb": sum(float(row["size_mb"]) for row in group),
            }
        )
    return case_rows


def _case_summary_markdown(rows: list[dict], title: str) -> str:
    if not rows:
        return f"# {title}\n\nNo dataset files found.\n"
    header = [
        "Geometry",
        "Family",
        "Files",
        "Samples",
        "Paths",
        "Splits",
        "Nodes",
        "Elements",
        "Steps",
        "Q pts",
        "QP hist",
        "K final",
        "K seq",
        "Residual RMS",
        "Size MB",
    ]
    lines = [
        f"# {title}",
        "",
        "| " + " | ".join(header) + " |",
        "| " + " | ".join(["---"] * len(header)) + " |",
    ]
    for row in rows:
        lines.append(
            "| "
            + " | ".join(
                [
                    str(row["geometry"]),
                    str(row["family"]),
                    str(row["files"]),
                    str(row["samples"]),
                    str(row["load_paths"]),
                    str(row["splits"]),
                    f"{row['node_min']}--{row['node_max']}",
                    f"{row['element_min']}--{row['element_max']}",
                    str(row["steps"]),
                    str(row["q_points"]),
                    "yes" if row["qp_history"] else "no",
                    "yes" if row["final_tangent"] else "no",
                    "yes" if row["tangent_sequence"] else "no",
                    f"{row['residual_rms_mean']:.3e}",
                    f"{row['size_mb']:.2f}",
                ]
            )
            + " |"
        )
    total_files = sum(int(row["files"]) for row in rows)
    total_samples = sum(int(row["samples"]) for row in rows)
    total_size = sum(float(row["size_mb"]) for row in rows)
    lines.extend(
        [
            "",
            f"Total: {len(rows)} geometry-mesh cases, {total_files} split files, "
            f"{total_samples} path samples, {total_size:.2f} MB.",
            "",
        ]
    )
    return "\n".join(lines)


def _geometry_family(label: str) -> str:
    return re.sub(r"_\d+x\d+$", "", label)


if __name__ == "__main__":
    main()
