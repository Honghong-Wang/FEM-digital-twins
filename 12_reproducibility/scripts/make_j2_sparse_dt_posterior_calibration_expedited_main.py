from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SUMMARY = (
    PROJECT_ROOT / "10_results" / "reports" / "j2_sparse_dt_assimilation_5seed_calibrated_2sample_summary.json"
)
DEFAULT_TABLE_ROOT = PROJECT_ROOT / "11_paper" / "tables"

TABLE_METRICS = (
    "sparse_observation_relative_l2",
    "rollout_displacement_relative_l2",
    "material_parameter_relative_l2",
    "material_parameter_coverage_95",
    "material_parameter_ece",
    "material_parameter_nll",
    "material_parameter_posterior_std",
    "calibrated_material_parameter_coverage_95",
    "calibrated_material_parameter_ece",
    "calibrated_material_parameter_nll",
    "calibrated_material_parameter_spread_scale",
    "calibrated_material_parameter_posterior_std",
    "history_relative_l2",
    "history_final_relative_l2",
    "history_coverage_95",
    "history_ece",
    "history_nll",
    "history_posterior_std",
    "calibrated_history_coverage_95",
    "calibrated_history_ece",
    "calibrated_history_nll",
    "calibrated_history_spread_scale",
    "calibrated_history_posterior_std",
    "field_coverage_95",
    "field_ece",
    "field_nll",
    "field_crps",
    "field_sharpness",
    "field_interval_width_95",
    "calibrated_field_coverage_95",
    "calibrated_field_ece",
    "calibrated_field_nll",
    "calibrated_field_crps",
    "calibrated_field_sharpness",
    "calibrated_field_interval_width_95",
    "calibrated_field_spread_scale",
    "inversion_final_loss",
)

COMPACT_METRICS = (
    ("sparse_observation_relative_l2", "Sparse obs. L2"),
    ("rollout_displacement_relative_l2", "Rollout disp. L2"),
    ("material_parameter_relative_l2", "Material rel. L2"),
    ("material_parameter_coverage_95", "Param cov. raw"),
    ("calibrated_material_parameter_coverage_95", "Param cov. cal."),
    ("material_parameter_ece", "Param ECE raw"),
    ("calibrated_material_parameter_ece", "Param ECE cal."),
    ("history_relative_l2", "History rel. L2"),
    ("history_coverage_95", "History cov. raw"),
    ("calibrated_history_coverage_95", "History cov. cal."),
    ("history_ece", "History ECE raw"),
    ("calibrated_history_ece", "History ECE cal."),
    ("field_coverage_95", "Field cov. raw"),
    ("calibrated_field_coverage_95", "Field cov. cal."),
    ("field_ece", "Field ECE raw"),
    ("calibrated_field_ece", "Field ECE cal."),
    ("field_nll", "Field NLL raw"),
    ("calibrated_field_nll", "Field NLL cal."),
    ("field_crps", "Field CRPS raw"),
    ("calibrated_field_crps", "Field CRPS cal."),
    ("calibrated_material_parameter_spread_scale", "Param spread scale"),
    ("calibrated_history_spread_scale", "History spread scale"),
    ("calibrated_field_spread_scale", "Field spread scale"),
)

CALIBRATION_PAIRS = (
    ("material_parameter", "material_parameter_coverage_95", "calibrated_material_parameter_coverage_95", "higher"),
    ("material_parameter", "material_parameter_ece", "calibrated_material_parameter_ece", "lower"),
    ("material_parameter", "material_parameter_nll", "calibrated_material_parameter_nll", "lower"),
    ("history", "history_coverage_95", "calibrated_history_coverage_95", "higher"),
    ("history", "history_ece", "calibrated_history_ece", "lower"),
    ("history", "history_nll", "calibrated_history_nll", "lower"),
    ("field", "field_coverage_95", "calibrated_field_coverage_95", "higher"),
    ("field", "field_ece", "calibrated_field_ece", "lower"),
    ("field", "field_nll", "calibrated_field_nll", "lower"),
    ("field", "field_crps", "calibrated_field_crps", "lower"),
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Convert the completed 5-seed calibrated sparse-DT posterior run into an "
            "expedited manuscript main table while the full 9-condition formal campaign runs."
        )
    )
    parser.add_argument("--summary-json", type=Path, default=DEFAULT_SUMMARY)
    parser.add_argument("--table-root", type=Path, default=DEFAULT_TABLE_ROOT)
    parser.add_argument("--protocol-name", default="expedited_reversal_curriculum_2sample")
    parser.add_argument("--sparse-config", default="s6_t3")
    parser.add_argument("--formal-aliases", action=argparse.BooleanOptionalAction, default=True)
    args = parser.parse_args()

    payload = json.loads(args.summary_json.read_text(encoding="utf-8"))
    metadata = payload.get("metadata", {})
    wide_rows = _wide_rows(payload, metadata, args.protocol_name, args.sparse_config)
    compact_rows = _compact_rows(payload, metadata, args.protocol_name, args.sparse_config)
    gain_rows = _gain_rows(payload, metadata, args.protocol_name, args.sparse_config)
    gain_aggregate_rows = _gain_aggregate_rows(gain_rows)

    outputs = {
        "expedited_main_table": wide_rows,
        "expedited_compact_main": compact_rows,
        "expedited_gain_table": gain_rows,
        "expedited_gain_aggregate": gain_aggregate_rows,
    }
    for stem, rows in outputs.items():
        _write_rows(args.table_root / f"j2_sparse_dt_posterior_calibration_{stem}.csv", rows)
        _write_markdown(args.table_root / f"j2_sparse_dt_posterior_calibration_{stem}.md", rows, stem)

    if args.formal_aliases:
        alias_map = {
            "main_table": wide_rows,
            "compact_main": compact_rows,
            "gain_table": gain_rows,
            "gain_aggregate": gain_aggregate_rows,
        }
        for stem, rows in alias_map.items():
            _write_rows(args.table_root / f"j2_sparse_dt_posterior_calibration_{stem}.csv", rows)
            _write_markdown(args.table_root / f"j2_sparse_dt_posterior_calibration_{stem}.md", rows, stem)

    print(f"wrote expedited posterior calibration tables under {args.table_root}")


def _base_row(metadata: dict, protocol_name: str, sparse_config: str, load_path: str) -> dict[str, str]:
    train_paths = ",".join(str(item) for item in metadata.get("train_load_paths", []))
    return {
        "Evidence tier": "expedited_5seed_2sample_current_main; full_9condition_formal_running",
        "Protocol": protocol_name,
        "Train paths": train_paths,
        "Eval path": load_path,
        "Path OOD": "yes" if load_path not in set(metadata.get("train_load_paths", [])) else "no",
        "Sparse config": sparse_config,
        "Sensors": str(metadata.get("num_sensors", "")),
        "Observed steps": str(metadata.get("num_observation_steps", "")),
        "Seeds": str(len(metadata.get("seeds", []))),
        "Epochs": str(metadata.get("epochs", "")),
        "Train samples": str(metadata.get("train_samples", "")),
        "Eval samples": str(metadata.get("eval_samples", "")),
        "Posterior chains": str(metadata.get("num_posterior_chains", "")),
        "Inversion steps": str(metadata.get("inversion_steps", "")),
        "Calibration mode": str(metadata.get("posterior_calibration_mode", "split_conformal")),
        "Source summary": str(DEFAULT_SUMMARY),
    }


def _wide_rows(payload: dict, metadata: dict, protocol_name: str, sparse_config: str) -> list[dict[str, str]]:
    rows = []
    for load_path, metrics in sorted(payload.get("by_load_path", {}).items()):
        row = _base_row(metadata, protocol_name, sparse_config, load_path)
        for metric in TABLE_METRICS:
            row[metric] = _format_stat(metrics.get(metric))
        rows.append(row)
    return rows


def _compact_rows(payload: dict, metadata: dict, protocol_name: str, sparse_config: str) -> list[dict[str, str]]:
    rows = []
    for load_path, metrics in sorted(payload.get("by_load_path", {}).items()):
        row = _base_row(metadata, protocol_name, sparse_config, load_path)
        for metric, label in COMPACT_METRICS:
            row[label] = _format_stat(metrics.get(metric))
        rows.append(row)
    return rows


def _gain_rows(payload: dict, metadata: dict, protocol_name: str, sparse_config: str) -> list[dict[str, str]]:
    rows = []
    for load_path, metrics in sorted(payload.get("by_load_path", {}).items()):
        for target, raw_metric, calibrated_metric, direction in CALIBRATION_PAIRS:
            raw = metrics.get(raw_metric)
            calibrated = metrics.get(calibrated_metric)
            if not raw or not calibrated:
                continue
            raw_mean = float(raw["mean"])
            calibrated_mean = float(calibrated["mean"])
            gain = calibrated_mean - raw_mean if direction == "higher" else raw_mean - calibrated_mean
            base = _base_row(metadata, protocol_name, sparse_config, load_path)
            base.update(
                {
                    "Target": target,
                    "Metric": raw_metric.replace(f"{target}_", ""),
                    "Direction": direction,
                    "Raw mean": _format_float(raw_mean),
                    "Calibrated mean": _format_float(calibrated_mean),
                    "Gain": _format_float(gain),
                    "Gain %": _format_float(100.0 * gain / abs(raw_mean)) if abs(raw_mean) > 1.0e-12 else "",
                    "Raw": _format_stat(raw),
                    "Calibrated": _format_stat(calibrated),
                    "Improved": "yes" if gain > 0.0 else "no",
                }
            )
            rows.append(base)
    return rows


def _gain_aggregate_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    groups: dict[tuple[str, str, str, str], list[dict[str, str]]] = {}
    for row in rows:
        key = (row["Target"], row["Metric"], row["Direction"], row["Sparse config"])
        groups.setdefault(key, []).append(row)
    output = []
    for key, items in sorted(groups.items()):
        gains = [float(item["Gain"]) for item in items if item["Gain"]]
        output.append(
            {
                "Evidence tier": items[0]["Evidence tier"],
                "Protocol": items[0]["Protocol"],
                "Sparse config": key[3],
                "Target": key[0],
                "Metric": key[1],
                "Direction": key[2],
                "Gain mean": _format_float(_mean(gains)),
                "Gain std": _format_float(_std(gains)),
                "Gain median": _format_float(_median(gains)),
                "Gain IQR": _format_float(_iqr(gains)),
                "Improved paths": str(sum(1 for item in items if item["Improved"] == "yes")),
                "Paths": str(len(items)),
                "Eval paths": ",".join(item["Eval path"] for item in items),
            }
        )
    return output


def _format_stat(stats: dict | None) -> str:
    if not stats:
        return ""
    return f"{stats['mean']:.4g} +/- {stats['std']:.2g}; med {stats['median']:.4g}, IQR {stats['iqr']:.2g}"


def _format_float(value: float | None) -> str:
    if value is None:
        return ""
    return f"{float(value):.6g}"


def _mean(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def _std(values: list[float]) -> float | None:
    if not values:
        return None
    if len(values) == 1:
        return 0.0
    avg = _mean(values)
    assert avg is not None
    return (sum((value - avg) ** 2 for value in values) / (len(values) - 1)) ** 0.5


def _median(values: list[float]) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    center = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[center]
    return 0.5 * (ordered[center - 1] + ordered[center])


def _iqr(values: list[float]) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    return _quantile(ordered, 0.75) - _quantile(ordered, 0.25)


def _quantile(ordered: list[float], q: float) -> float:
    if len(ordered) == 1:
        return ordered[0]
    position = q * (len(ordered) - 1)
    left = int(position)
    right = min(left + 1, len(ordered) - 1)
    weight = position - left
    return ordered[left] * (1.0 - weight) + ordered[right] * weight


def _write_rows(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _write_markdown(path: Path, rows: list[dict[str, str]], title: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    headers = list(rows[0])
    lines = [
        f"# {title}",
        "",
        "Expedited current main table generated from completed 50-epoch, 5-seed calibrated sparse-DT posterior results. "
        "The full 9-condition formal campaign is still running.",
        "",
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(header, "")).replace("|", "\\|") for header in headers) + " |")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
