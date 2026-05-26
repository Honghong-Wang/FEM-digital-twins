from __future__ import annotations

import argparse
import csv
import json
import statistics
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROTOCOLS = ("strict_path_ood", "reversal_curriculum", "family_upper_bound")
SPARSE_CONFIGS = ("s2_t2", "s4_t2", "s6_t3")
SEEDS = (20260517, 20260518, 20260519, 20260520, 20260521)
EXPECTED_EVAL_PATHS = {
    "strict_path_ood": ("unload_reload", "cyclic", "nonproportional", "random_amplitude", "pre_stress"),
    "reversal_curriculum": ("cyclic", "nonproportional", "random_amplitude", "pre_stress"),
    "family_upper_bound": (
        "monotonic",
        "unload_reload",
        "cyclic",
        "nonproportional",
        "random_amplitude",
        "pre_stress",
    ),
}
REQUIRED_METRICS = (
    "sparse_observation_relative_l2",
    "rollout_displacement_relative_l2",
    "material_parameter_relative_l2",
    "material_parameter_coverage_95",
    "material_parameter_ece",
    "material_parameter_nll",
    "calibrated_material_parameter_coverage_95",
    "calibrated_material_parameter_ece",
    "calibrated_material_parameter_nll",
    "calibrated_material_parameter_spread_scale",
    "history_relative_l2",
    "history_final_relative_l2",
    "history_coverage_95",
    "history_ece",
    "history_nll",
    "calibrated_history_coverage_95",
    "calibrated_history_ece",
    "calibrated_history_nll",
    "calibrated_history_spread_scale",
    "field_coverage_95",
    "field_ece",
    "field_nll",
    "field_crps",
    "calibrated_field_coverage_95",
    "calibrated_field_ece",
    "calibrated_field_nll",
    "calibrated_field_crps",
    "calibrated_field_spread_scale",
    "posterior_calibration_num_calibration",
    "posterior_calibration_num_test",
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Audit the full 9-condition sparse-DT posterior calibration formal table."
    )
    parser.add_argument(
        "--report-root",
        type=Path,
        default=PROJECT_ROOT / "10_results" / "reports" / "j2_sparse_dt_posterior_calibration_main",
    )
    parser.add_argument(
        "--paper-main",
        type=Path,
        default=PROJECT_ROOT / "11_paper" / "tables" / "j2_sparse_dt_posterior_calibration_main_table.csv",
    )
    parser.add_argument(
        "--paper-compact",
        type=Path,
        default=PROJECT_ROOT / "11_paper" / "tables" / "j2_sparse_dt_posterior_calibration_compact_main.csv",
    )
    parser.add_argument(
        "--paper-gain",
        type=Path,
        default=PROJECT_ROOT / "11_paper" / "tables" / "j2_sparse_dt_posterior_calibration_gain_table.csv",
    )
    parser.add_argument(
        "--paper-gain-aggregate",
        type=Path,
        default=PROJECT_ROOT / "11_paper" / "tables" / "j2_sparse_dt_posterior_calibration_gain_aggregate.csv",
    )
    parser.add_argument(
        "--audit-csv",
        type=Path,
        default=PROJECT_ROOT / "10_results" / "reports" / "j2_sparse_dt_posterior_calibration_formal_audit.csv",
    )
    parser.add_argument(
        "--audit-md",
        type=Path,
        default=PROJECT_ROOT / "10_results" / "reports" / "j2_sparse_dt_posterior_calibration_formal_audit.md",
    )
    parser.add_argument("--tolerance", type=float, default=5.0e-10)
    parser.add_argument("--relative-tolerance", type=float, default=1.0e-10)
    args = parser.parse_args()

    condition_rows: list[dict[str, str]] = []
    stat_rows: list[dict[str, str]] = []
    failed_stat_checks = 0
    max_absdiff = 0.0
    max_reldiff = 0.0

    for protocol in PROTOCOLS:
        for sparse_config in SPARSE_CONFIGS:
            root = args.report_root / protocol / sparse_config
            summary_path = root / "summary.json"
            per_seed_path = root / "per_seed.csv"
            seed_root = root / "seeds"
            seed_paths = [seed_root / f"seed_{seed}.json" for seed in SEEDS]
            missing_seed_paths = [path for path in seed_paths if not path.exists()]
            status = "complete"
            notes: list[str] = []
            if not summary_path.exists():
                status = "missing"
                notes.append("missing summary.json")
            if not per_seed_path.exists():
                status = "missing"
                notes.append("missing per_seed.csv")
            if missing_seed_paths:
                status = "missing"
                notes.append("missing seed json: " + ",".join(path.stem for path in missing_seed_paths))

            summary = None
            if summary_path.exists():
                summary = json.loads(summary_path.read_text(encoding="utf-8"))
                found_paths = tuple(summary.get("by_load_path", {}).keys())
                missing_eval_paths = [
                    load_path for load_path in EXPECTED_EVAL_PATHS[protocol] if load_path not in found_paths
                ]
                if missing_eval_paths:
                    status = "incomplete"
                    notes.append("missing eval paths: " + ",".join(missing_eval_paths))

            if summary is not None and not missing_seed_paths:
                for load_path in EXPECTED_EVAL_PATHS[protocol]:
                    for metric in REQUIRED_METRICS:
                        if load_path not in summary.get("by_load_path", {}):
                            continue
                        stats = summary["by_load_path"][load_path].get(metric)
                        if not stats:
                            status = "incomplete"
                            notes.append(f"missing metric {load_path}/{metric}")
                            continue
                        values = []
                        for seed_path in seed_paths:
                            payload = json.loads(seed_path.read_text(encoding="utf-8"))
                            try:
                                values.append(float(payload["evaluations"][load_path][metric]))
                            except KeyError:
                                status = "incomplete"
                                notes.append(f"missing seed metric {seed_path.name}/{load_path}/{metric}")
                                values = []
                                break
                        if not values:
                            continue
                        recomputed = {
                            "mean": _mean(values),
                            "std": _std(values),
                            "median": statistics.median(values),
                            "iqr": _iqr(values),
                        }
                        for stat_name, value in recomputed.items():
                            summary_value = float(stats[stat_name])
                            diff = abs(value - summary_value)
                            scale = max(1.0, abs(value), abs(summary_value))
                            rel_diff = diff / scale
                            max_absdiff = max(max_absdiff, diff)
                            max_reldiff = max(max_reldiff, rel_diff)
                            ok = diff <= (args.tolerance + args.relative_tolerance * scale)
                            if not ok:
                                failed_stat_checks += 1
                                status = "failed_audit"
                            stat_rows.append(
                                {
                                    "protocol": protocol,
                                    "sparse_config": sparse_config,
                                    "load_path": load_path,
                                    "metric": metric,
                                    "stat": stat_name,
                                    "recomputed_from_seed_json": f"{value:.12g}",
                                    "summary_json": f"{summary_value:.12g}",
                                    "abs_diff": f"{diff:.3e}",
                                    "rel_diff": f"{rel_diff:.3e}",
                                    "pass": str(ok),
                                }
                            )

            condition_rows.append(
                {
                    "Protocol": protocol,
                    "Sparse config": sparse_config,
                    "Condition root": str(root),
                    "Summary JSON": "yes" if summary_path.exists() else "no",
                    "Per-seed CSV": "yes" if per_seed_path.exists() else "no",
                    "Seed JSONs": str(len(seed_paths) - len(missing_seed_paths)),
                    "Expected seed JSONs": str(len(SEEDS)),
                    "Status": status,
                    "Notes": "; ".join(dict.fromkeys(notes)),
                }
            )

    expected_main_rows = sum(len(EXPECTED_EVAL_PATHS[p]) for p in PROTOCOLS) * len(SPARSE_CONFIGS)
    expected_gain_rows = expected_main_rows * 10
    expected_gain_aggregate_rows = len(PROTOCOLS) * len(SPARSE_CONFIGS) * 10
    table_counts = {
        "main_rows": _csv_row_count(args.paper_main),
        "compact_rows": _csv_row_count(args.paper_compact),
        "gain_rows": _csv_row_count(args.paper_gain),
        "gain_aggregate_rows": _csv_row_count(args.paper_gain_aggregate),
    }
    complete_conditions = sum(1 for row in condition_rows if row["Status"] == "complete")
    all_complete = complete_conditions == len(condition_rows)
    table_shape_ok = (
        table_counts["main_rows"] == expected_main_rows
        and table_counts["compact_rows"] == expected_main_rows
        and table_counts["gain_rows"] == expected_gain_rows
        and table_counts["gain_aggregate_rows"] == expected_gain_aggregate_rows
    )
    audit_ok = all_complete and failed_stat_checks == 0 and table_shape_ok

    args.audit_csv.parent.mkdir(parents=True, exist_ok=True)
    _write_csv(args.audit_csv, condition_rows + [{"Protocol": "", "Sparse config": "", "Condition root": "", "Summary JSON": "", "Per-seed CSV": "", "Seed JSONs": "", "Expected seed JSONs": "", "Status": "", "Notes": ""}])
    stat_csv = args.audit_csv.with_name(args.audit_csv.stem + "_stats.csv")
    if stat_rows:
        _write_csv(stat_csv, stat_rows)

    lines = [
        "# Sparse-DT posterior calibration formal audit",
        "",
        f"- complete_conditions: {complete_conditions} / {len(condition_rows)}",
        f"- failed_stat_checks: {failed_stat_checks}",
        f"- max_absdiff_seed_recompute_vs_summary: {max_absdiff:.3e}",
        f"- max_reldiff_seed_recompute_vs_summary: {max_reldiff:.3e}",
        f"- expected_main_rows: {expected_main_rows}",
        f"- actual_main_rows: {table_counts['main_rows']}",
        f"- expected_gain_rows: {expected_gain_rows}",
        f"- actual_gain_rows: {table_counts['gain_rows']}",
        f"- expected_gain_aggregate_rows: {expected_gain_aggregate_rows}",
        f"- actual_gain_aggregate_rows: {table_counts['gain_aggregate_rows']}",
        f"- audit_pass: {audit_ok}",
        "",
        "## Condition Status",
        "",
        _markdown_table(condition_rows),
    ]
    args.audit_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {args.audit_md}")
    print(f"wrote {args.audit_csv}")
    if stat_rows:
        print(f"wrote {stat_csv}")
    print(f"formal_audit_pass={audit_ok}")
    if not audit_ok:
        sys.exit(1)


def _mean(values: list[float]) -> float:
    return sum(values) / len(values)


def _std(values: list[float]) -> float:
    return statistics.stdev(values) if len(values) > 1 else 0.0


def _linear_quantile(values: list[float], q: float) -> float:
    sorted_values = sorted(values)
    if len(sorted_values) == 1:
        return sorted_values[0]
    pos = (len(sorted_values) - 1) * q
    lo = int(pos)
    hi = min(lo + 1, len(sorted_values) - 1)
    frac = pos - lo
    return sorted_values[lo] * (1.0 - frac) + sorted_values[hi] * frac


def _iqr(values: list[float]) -> float:
    return _linear_quantile(values, 0.75) - _linear_quantile(values, 0.25)


def _csv_row_count(path: Path) -> int:
    if not path.exists():
        return 0
    with path.open("r", encoding="utf-8", newline="") as f:
        return sum(1 for _ in csv.DictReader(f))


def _write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames = list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _markdown_table(rows: list[dict[str, str]]) -> str:
    if not rows:
        return ""
    headers = list(rows[0].keys())
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(header, "")) for header in headers) + " |")
    return "\n".join(lines)


if __name__ == "__main__":
    main()
