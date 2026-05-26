from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

METRIC_LABELS = {
    "displacement_relative_l2": "Displacement relative L2",
    "history_relative_l2": "History relative L2",
    "history_increment_relative_l2": "History-increment relative L2",
    "eq_plastic_strain_increment_relative_l2": "Eq. plastic strain increment relative L2",
    "plastic_work_increment_relative_l2": "Plastic-work increment relative L2",
    "yield_flag_mae": "Yield-flag MAE",
    "reversal_history_increment_relative_l2": "Reversal history-increment relative L2",
    "reversal_yield_flag_mae": "Reversal yield-flag MAE",
    "predicted_yield_surface_relative_rms": "Predicted yield-surface relative RMS",
    "predicted_plastic_work_lower_bound_relative_violation": "Plastic-work lower-bound violation",
}

CASE_LABELS = {
    "strict": "Strict path-OOD",
    "curriculum": "Unload curriculum",
    "upper_bound": "Cyclic-seen upper bound",
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Create compact primary path-OOD evidence tables.")
    parser.add_argument(
        "--input",
        type=Path,
        default=PROJECT_ROOT / "10_results" / "reports" / "thermo_path_ood_5seed_summary.json",
    )
    parser.add_argument(
        "--md-out",
        type=Path,
        default=PROJECT_ROOT / "11_paper" / "tables" / "thermo_path_ood_5seed_primary_table.md",
    )
    parser.add_argument(
        "--csv-out",
        type=Path,
        default=PROJECT_ROOT / "11_paper" / "tables" / "thermo_path_ood_5seed_primary_table.csv",
    )
    parser.add_argument("--title", default="Thermo-Aware Path-OOD Primary Evidence")
    args = parser.parse_args()

    summary = json.loads(args.input.read_text(encoding="utf-8"))
    rows = _rows(summary)
    _write_csv(args.csv_out, rows)
    _write_markdown(args.md_out, args.title, args.input, summary, rows)
    print(f"wrote {args.csv_out}")
    print(f"wrote {args.md_out}")


def _rows(summary: dict) -> list[dict[str, str]]:
    cases = tuple(summary["metadata"].get("cases", summary.get("cyclic_primary", {}).keys()))
    metrics = tuple(summary["metadata"].get("primary_metrics", METRIC_LABELS))
    rows = []
    for metric in metrics:
        if metric not in METRIC_LABELS:
            continue
        row = {"metric": METRIC_LABELS[metric]}
        for case in cases:
            stats = summary.get("cyclic_primary", {}).get(case, {}).get(metric)
            row[CASE_LABELS.get(case, case)] = _format_stat(stats)
        rows.append(row)
    return rows


def _write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    fieldnames = []
    for row in rows:
        for key in row:
            if key not in fieldnames:
                fieldnames.append(key)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _write_markdown(path: Path, title: str, source: Path, summary: dict, rows: list[dict[str, str]]) -> None:
    if not rows:
        raise ValueError("no primary rows to write")
    headers = list(rows[0])
    metadata = summary.get("metadata", {})
    lines = [
        f"# {title}",
        "",
        f"Source: `{source}`",
        "",
    ]
    if metadata.get("shared_data_root"):
        lines.extend([f"Shared data root: `{metadata['shared_data_root']}`", ""])
    lines.extend(
        [
            "| " + " | ".join(headers) + " |",
            "| " + " | ".join(["---", *["---:" for _ in headers[1:]]]) + " |",
        ]
    )
    for row in rows:
        lines.append("| " + " | ".join(row.get(header, "") for header in headers) + " |")
    lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _format_stat(stats: dict | None) -> str:
    if stats is None:
        return ""
    return f"{stats['mean']:.4f} +/- {stats['std']:.4f}"


if __name__ == "__main__":
    main()
