from __future__ import annotations

import argparse
import csv
import json
import re
from collections import defaultdict
from pathlib import Path
from statistics import mean, pstdev


PROJECT_ROOT = Path(__file__).resolve().parents[2]

REPORT_METRICS = (
    ("displacement_relative_l2", "Disp. rel. L2"),
    ("history_relative_l2", "History rel. L2"),
    ("qp_history_relative_l2", "QP hist. rel. L2"),
    ("qp_history_increment_relative_l2", "QP hist-inc. rel. L2"),
    ("reversal_history_increment_relative_l2", "Reversal hist-inc. rel. L2"),
    ("reversal_yield_flag_mae", "Reversal yield MAE"),
    ("predicted_yield_surface_relative_rms", "Yield RMS"),
    (
        "predicted_plastic_work_lower_bound_target_normalized_violation",
        "Plastic-work viol. target-norm.",
    ),
    ("fem_residual_relative_rms", "FEM residual rel. RMS"),
    ("fem_energy_relative_error", "FEM energy rel. err."),
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Aggregate the large Level-4 complex-geometry x path-family J2 matrix into "
            "paper-ready summary and appendix tables."
        )
    )
    parser.add_argument(
        "--out-root",
        type=Path,
        default=PROJECT_ROOT / "10_results" / "reports" / "level4_multigeometry_multipath_qp_hgo",
    )
    parser.add_argument(
        "--case-summary-csv",
        type=Path,
        default=PROJECT_ROOT
        / "10_results"
        / "reports"
        / "level4_t6_8step_qp_12case_dataset_summary_case_summary.csv",
    )
    parser.add_argument(
        "--summary-csv",
        type=Path,
        default=PROJECT_ROOT / "11_paper" / "tables" / "level4_multigeometry_multipath_matrix_summary.csv",
    )
    parser.add_argument(
        "--summary-md",
        type=Path,
        default=PROJECT_ROOT / "11_paper" / "tables" / "level4_multigeometry_multipath_matrix_summary.md",
    )
    parser.add_argument(
        "--case-path-csv",
        type=Path,
        default=PROJECT_ROOT / "11_paper" / "tables" / "level4_multigeometry_multipath_matrix_case_path.csv",
    )
    parser.add_argument(
        "--case-path-md",
        type=Path,
        default=PROJECT_ROOT / "11_paper" / "tables" / "level4_multigeometry_multipath_matrix_case_path.md",
    )
    parser.add_argument(
        "--manifest-json",
        type=Path,
        default=PROJECT_ROOT / "10_results" / "reports" / "level4_multigeometry_multipath_matrix_manifest.json",
    )
    args = parser.parse_args()

    case_meta = _read_case_meta(args.case_summary_csv)
    out_root = args.out_root.resolve()
    case_rows = _collect_case_path_rows(out_root, case_meta)
    if not case_rows:
        raise FileNotFoundError(f"no completed summary.json files found under {args.out_root}")
    summary_rows = _aggregate_rows(case_rows)
    _write_csv(args.case_path_csv, case_rows)
    _write_csv(args.summary_csv, summary_rows)
    _write_markdown(args.case_path_md, case_rows, title="Level-4 Multi-Geometry Multi-Path Matrix Appendix")
    _write_markdown(args.summary_md, summary_rows, title="Level-4 Multi-Geometry Multi-Path Matrix Summary")
    _write_manifest(args.manifest_json, out_root, case_rows, summary_rows)
    print(f"wrote {args.summary_csv}")
    print(f"wrote {args.summary_md}")
    print(f"wrote {args.case_path_csv}")
    print(f"wrote {args.case_path_md}")
    print(f"wrote {args.manifest_json}")


def _read_case_meta(path: Path) -> dict[str, dict[str, str]]:
    if not path.exists():
        return {}
    with path.open(newline="", encoding="utf-8") as handle:
        return {
            row["geometry"].lstrip("\ufeff"): {key.lstrip("\ufeff"): value for key, value in row.items()}
            for row in csv.DictReader(handle)
        }


def _collect_case_path_rows(out_root: Path, case_meta: dict[str, dict[str, str]]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for summary_path in sorted(out_root.glob("*/*/summary.json")):
        case = summary_path.parent.parent.name
        protocol = summary_path.parent.name
        payload = json.loads(summary_path.read_text(encoding="utf-8"))
        meta = case_meta.get(case, {})
        family, mesh = _split_case(case)
        for model_name, result in payload["results"].items():
            by_path = result["summary"].get("by_load_path", {})
            for path_name, path_stats in sorted(by_path.items()):
                row = {
                    "Case": case,
                    "Family": meta.get("family", family),
                    "Mesh": mesh,
                    "Nodes": _range(meta, "node_min", "node_max"),
                    "Elements": _range(meta, "element_min", "element_max"),
                    "Protocol": protocol,
                    "Train paths": ",".join(payload["metadata"].get("train_load_paths", [])),
                    "Eval path": path_name,
                    "Model": model_name,
                    "Seeds": str(result["summary"].get("num_seeds", "")),
                    "Source": str(summary_path.relative_to(PROJECT_ROOT)),
                }
                for metric, label in REPORT_METRICS:
                    row[label] = _format_stat(path_stats.get(metric))
                    row[f"{label} mean"] = _format_mean(path_stats.get(metric))
                rows.append(row)
    return rows


def _aggregate_rows(case_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    groups: dict[tuple[str, str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in case_rows:
        groups[(row["Protocol"], row["Eval path"], row["Family"], row["Model"])].append(row)
    summary_rows: list[dict[str, str]] = []
    for (protocol, eval_path, family, model), rows in sorted(groups.items()):
        out = {
            "Protocol": protocol,
            "Eval path": eval_path,
            "Family": family,
            "Model": model,
            "Cases": str(len(rows)),
            "Mesh sizes": ",".join(sorted({row["Mesh"] for row in rows})),
            "Seeds per case": ",".join(sorted({row["Seeds"] for row in rows})),
        }
        for _metric, label in REPORT_METRICS:
            values = [float(row[f"{label} mean"]) for row in rows if row[f"{label} mean"]]
            out[label] = _format_cross_case(values)
        summary_rows.append(out)
    return summary_rows


def _split_case(case: str) -> tuple[str, str]:
    match = re.match(r"(?P<family>.+)_(?P<mesh>\d+x\d+)$", case)
    if not match:
        return case, ""
    return match.group("family"), match.group("mesh")


def _range(meta: dict[str, str], lo: str, hi: str) -> str:
    if lo not in meta or hi not in meta:
        return ""
    return f"{meta[lo]}--{meta[hi]}"


def _format_stat(stats: dict | None) -> str:
    if not stats or stats.get("mean") is None:
        return ""
    mean_value = stats.get("mean")
    std_value = stats.get("std", 0.0)
    median_value = stats.get("median")
    iqr_value = stats.get("iqr")
    if median_value is None:
        return f"{mean_value:.4g} +/- {std_value:.3g}"
    return f"{mean_value:.4g} +/- {std_value:.3g}; med {median_value:.4g}, IQR {iqr_value:.3g}"


def _format_mean(stats: dict | None) -> str:
    if not stats or stats.get("mean") is None:
        return ""
    return f"{stats['mean']:.12g}"


def _format_cross_case(values: list[float]) -> str:
    if not values:
        return ""
    std_value = pstdev(values) if len(values) > 1 else 0.0
    sorted_values = sorted(values)
    median_value = _median(sorted_values)
    q1 = _percentile(sorted_values, 25.0)
    q3 = _percentile(sorted_values, 75.0)
    return (
        f"{mean(values):.4g} +/- {std_value:.3g}; "
        f"case-med {median_value:.4g}, IQR {(q3 - q1):.3g}"
    )


def _median(sorted_values: list[float]) -> float:
    n = len(sorted_values)
    midpoint = n // 2
    if n % 2:
        return sorted_values[midpoint]
    return 0.5 * (sorted_values[midpoint - 1] + sorted_values[midpoint])


def _percentile(sorted_values: list[float], percentile: float) -> float:
    if not sorted_values:
        return float("nan")
    if len(sorted_values) == 1:
        return sorted_values[0]
    position = (len(sorted_values) - 1) * percentile / 100.0
    left = int(position)
    right = min(left + 1, len(sorted_values) - 1)
    weight = position - left
    return sorted_values[left] * (1.0 - weight) + sorted_values[right] * weight


def _write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]) if rows else [])
        writer.writeheader()
        writer.writerows(rows)


def _write_markdown(path: Path, rows: list[dict[str, str]], *, title: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text(f"# {title}\n\nNo completed rows.\n", encoding="utf-8")
        return
    headers = list(rows[0])
    lines = [
        f"# {title}",
        "",
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(header, "")) for header in headers) + " |")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def _write_manifest(
    path: Path,
    out_root: Path,
    case_rows: list[dict[str, str]],
    summary_rows: list[dict[str, str]],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "out_root": str(out_root),
        "num_case_path_rows": len(case_rows),
        "num_summary_rows": len(summary_rows),
        "num_cases": len({row["Case"] for row in case_rows}),
        "num_geometry_families": len({row["Family"] for row in case_rows}),
        "num_mesh_sizes": len({row["Mesh"] for row in case_rows}),
        "num_protocols": len({row["Protocol"] for row in case_rows}),
        "num_eval_paths": len({row["Eval path"] for row in case_rows}),
        "models": sorted({row["Model"] for row in case_rows}),
        "protocols": sorted({row["Protocol"] for row in case_rows}),
        "eval_paths": sorted({row["Eval path"] for row in case_rows}),
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
