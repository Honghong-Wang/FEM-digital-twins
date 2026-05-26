from __future__ import annotations

import csv
import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

SOURCES = (
    (
        "multi_hole",
        (
            (
                "reversal_final",
                PROJECT_ROOT / "10_results" / "reports" / "level4_t6_qp_reversal_audit_strict.json",
            ),
            (
                "reversal_final",
                PROJECT_ROOT / "10_results" / "reports" / "level4_t6_qp_history_gno_strict.json",
            ),
            (
                "all",
                PROJECT_ROOT / "10_results" / "reports" / "level4_t6_qp_history_gno_allstep_strict.json",
            ),
        ),
    ),
    (
        "notch",
        (
            (
                "reversal_final",
                PROJECT_ROOT / "10_results" / "reports" / "level4_t6_qp_reversal_audit_strict_notch.json",
            ),
            (
                "reversal_final",
                PROJECT_ROOT / "10_results" / "reports" / "level4_t6_qp_history_gno_strict_notch.json",
            ),
            (
                "all",
                PROJECT_ROOT / "10_results" / "reports" / "level4_t6_qp_history_gno_allstep_strict_notch.json",
            ),
        ),
    ),
    (
        "curved_hole",
        (
            (
                "reversal_final",
                PROJECT_ROOT
                / "10_results"
                / "reports"
                / "level4_t6_qp_reversal_audit_strict_curved_hole.json",
            ),
            (
                "reversal_final",
                PROJECT_ROOT / "10_results" / "reports" / "level4_t6_qp_history_gno_strict_curved_hole.json",
            ),
            (
                "all",
                PROJECT_ROOT / "10_results" / "reports" / "level4_t6_qp_history_gno_allstep_strict_curved_hole.json",
            ),
        ),
    ),
)

METRICS = (
    ("displacement_relative_l2", "Displacement rel. L2"),
    ("history_relative_l2", "History rel. L2"),
    ("qp_history_relative_l2", "QP history rel. L2"),
    ("qp_history_increment_relative_l2", "QP history-inc. rel. L2"),
    ("reversal_history_increment_relative_l2", "Reversal hist-inc. rel. L2"),
    ("reversal_yield_flag_mae", "Reversal yield-flag MAE"),
    ("predicted_yield_surface_relative_rms", "Yield-surface RMS"),
    (
        "predicted_plastic_work_lower_bound_target_normalized_violation",
        "Plastic-work violation target-norm.",
    ),
    ("fem_residual_relative_rms", "FEM residual rel. RMS"),
    ("fem_energy_relative_error", "FEM energy rel. err."),
)

MODEL_LABELS = {
    "hgo_thermo_hard": "Thermo-hard HistoryGNO",
    "hgo_qp_thermo_hard": "QP-thermo-hard HistoryGNO",
    "tinn": "TINN-style",
}


def main() -> None:
    rows = []
    metadata = []
    for geometry, path_specs in SOURCES:
        for audit_policy, path in path_specs:
            payload = json.loads(path.read_text(encoding="utf-8"))
            metadata.append((geometry, payload["metadata"]))
            for model_name, result in payload["results"].items():
                cyclic = result["summary"]["cyclic_primary"]
                row = {
                    "Geometry": geometry,
                    "Model": MODEL_LABELS.get(model_name, model_name),
                    "Audit policy": audit_policy,
                    "Seeds": str(result["summary"]["num_seeds"]),
                }
                for metric, label in METRICS:
                    row[label] = _format_stat(cyclic.get(metric))
                rows.append(row)

    out_base = PROJECT_ROOT / "10_results" / "reports" / "level4_t6_qp_reversal_audit_three_geometry"
    _write_csv(out_base.with_suffix(".csv"), rows)
    _write_markdown(out_base.with_suffix(".md"), rows, metadata)
    print(f"wrote {out_base.with_suffix('.csv')}")
    print(f"wrote {out_base.with_suffix('.md')}")


def _write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise ValueError("no rows to write")
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _write_markdown(path: Path, rows: list[dict[str, str]], metadata: list[tuple[str, dict]]) -> None:
    if not rows:
        raise ValueError("no rows to write")
    headers = list(rows[0])
    lines = [
        "# T6 QP-State and FEM Audit Across Three Geometries",
        "",
        "All rows use strict monotonic-to-cyclic training/testing, 50 epochs, five seeds, T=8, "
        "T6 elements, quadrature-point plastic strain/history, and matrix-free FEM residual/energy "
        "audit. The 'reversal_final' policy audits cyclic turning points plus the final step; "
        "the 'all' policy applies the FEM loss on every rollout step during training and reports "
        "all-step audit metrics at test time. "
        "QP history columns are populated only for the QP-level HistoryGNO that explicitly "
        "predicts quadrature-point material states.",
        "",
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---", *["---:" for _ in headers[1:]]]) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(row.get(header, "") for header in headers) + " |")
    lines.extend(["", "## Sources", ""])
    seen_sources = set()
    for geometry, meta in metadata:
        source_key = (geometry, meta["data_root"], tuple(meta["models"]))
        if source_key in seen_sources:
            continue
        seen_sources.add(source_key)
        lines.append(
            f"- {geometry}: `{meta['data_root']}`, epochs={meta['epochs']}, "
            f"models={','.join(meta['models'])}, seeds={len(meta['seeds'])}, train={','.join(meta['train_load_paths'])}, "
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
