from __future__ import annotations

import csv
import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
REPORT_DIR = PROJECT_ROOT / "10_results" / "reports"
CASE_SUMMARY = REPORT_DIR / "level4_t6_8step_qp_12case_dataset_summary_case_summary.csv"

CASES = (
    "curved_hole_14x11",
    "curved_hole_16x12",
    "curved_hole_18x14",
    "curved_hole_20x15",
    "multi_hole_14x11",
    "multi_hole_16x12",
    "multi_hole_18x14",
    "multi_hole_20x15",
    "notch_14x11",
    "notch_16x12",
    "notch_18x14",
    "notch_20x15",
)

METRICS = (
    ("displacement_relative_l2", "Displacement rel. L2"),
    ("history_relative_l2", "History rel. L2"),
    ("qp_history_relative_l2", "QP history rel. L2"),
    ("qp_history_increment_relative_l2", "QP history-inc. rel. L2"),
    ("reversal_history_increment_relative_l2", "Reversal hist-inc. rel. L2"),
    ("reversal_yield_flag_mae", "Reversal yield-flag MAE"),
    ("predicted_yield_surface_relative_rms", "Yield-surface RMS"),
    ("predicted_plastic_work_lower_bound_target_normalized_violation", "Plastic-work violation target-norm."),
    ("fem_residual_relative_rms", "FEM residual rel. RMS"),
    ("fem_energy_relative_error", "FEM energy rel. err."),
)


def main() -> None:
    case_meta = {row["geometry"]: row for row in _read_csv(CASE_SUMMARY)}
    rows = []
    metadata = []
    missing = []
    for case in CASES:
        path = _result_path(case)
        if path is None:
            missing.append(case)
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        result = payload["results"]["hgo_qp_thermo_hard"]
        cyclic = result["summary"]["cyclic_primary"]
        meta = case_meta[case]
        row = {
            "Case": case,
            "Family": meta["family"],
            "Nodes": f"{meta['node_min']}--{meta['node_max']}",
            "Elements": f"{meta['element_min']}--{meta['element_max']}",
            "Steps": meta["steps"],
            "Seeds": str(result["summary"]["num_seeds"]),
            "Source": path.stem,
        }
        for metric, label in METRICS:
            row[label] = _format_stat(cyclic.get(metric))
        rows.append(row)
        metadata.append((case, path.name, payload["metadata"]))
    if missing:
        raise FileNotFoundError(f"missing all-step 12-case result JSON for: {', '.join(missing)}")

    out_base = REPORT_DIR / "level4_t6_qp_allstep_12case_main_table"
    _write_csv(out_base.with_suffix(".csv"), rows)
    _write_markdown(out_base.with_suffix(".md"), rows, metadata)
    print(f"wrote {out_base.with_suffix('.csv')}")
    print(f"wrote {out_base.with_suffix('.md')}")


def _result_path(case: str) -> Path | None:
    primary = REPORT_DIR / f"level4_t6_qp_allstep_12case_{case}.json"
    if primary.exists():
        return primary
    representative = REPORT_DIR / f"level4_t6_qp_allstep_representative_{case}.json"
    if representative.exists():
        return representative
    return None


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return [{key.lstrip("\ufeff"): value for key, value in row.items()} for row in csv.DictReader(handle)]


def _write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _write_markdown(path: Path, rows: list[dict[str, str]], metadata: list[tuple[str, str, dict]]) -> None:
    headers = list(rows[0])
    lines = [
        "# Level-4 T6/QP Complete 12-Case All-Step FEM Audit Main Table",
        "",
        "All rows use QP-thermo-hard HistoryGNO, strict monotonic-to-cyclic training/testing, "
        "50 epochs, five seeds, T=8, T6 elements, quadrature-point plastic strain/history, "
        "and all-step matrix-free FEM residual/energy audit loss during training and evaluation.",
        "",
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---", *["---:" for _ in headers[1:]]]) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(row.get(header, "") for header in headers) + " |")
    lines.extend(["", "## Sources", ""])
    for case, source, meta in metadata:
        lines.append(
            f"- {case}: `{source}`, data=`{meta['data_root']}`, epochs={meta['epochs']}, "
            f"seeds={len(meta['seeds'])}, train={','.join(meta['train_load_paths'])}, "
            f"eval={','.join(meta['eval_load_paths'])}"
        )
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def _format_stat(stats: dict | None) -> str:
    if stats is None:
        return ""
    return f"{stats['mean']:.4g} +/- {stats['std']:.4g}"


if __name__ == "__main__":
    main()
