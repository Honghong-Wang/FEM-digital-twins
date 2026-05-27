from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
FIVE_SEED_SUITE = PROJECT_ROOT / "12_reproducibility" / "scripts" / "run_j2_sparse_dt_assimilation_5seed_suite.py"
ALL_PATHS = "monotonic,unload_reload,cyclic,nonproportional,random_amplitude,pre_stress"
PROTOCOLS = {
    "strict_path_ood": ("monotonic", "unload_reload,cyclic,nonproportional,random_amplitude,pre_stress"),
    "reversal_curriculum": ("monotonic,unload_reload,cyclic", "cyclic,nonproportional,random_amplitude,pre_stress"),
    "family_upper_bound": (ALL_PATHS, ALL_PATHS),
}
DEFAULT_SPARSE_CONFIGS = "s2_t2:2:2:0.001,s4_t2:4:2:0.001,s6_t3:6:3:0.001"
TABLE_METRICS = (
    "sparse_observation_relative_l2",
    "rollout_displacement_relative_l2",
    "material_parameter_relative_l2",
    "material_parameter_posterior_std",
    "material_parameter_coverage_95",
    "material_parameter_ece",
    "material_parameter_nll",
    "calibrated_material_parameter_coverage_95",
    "calibrated_material_parameter_ece",
    "calibrated_material_parameter_nll",
    "calibrated_material_parameter_spread_scale",
    "calibrated_material_parameter_posterior_std",
    "history_relative_l2",
    "history_final_relative_l2",
    "history_posterior_std",
    "history_coverage_95",
    "history_ece",
    "history_nll",
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
    "posterior_calibration_num_calibration",
    "posterior_calibration_num_test",
    "inversion_final_loss",
)

COMPACT_METRICS = (
    "sparse_observation_relative_l2",
    "rollout_displacement_relative_l2",
    "material_parameter_relative_l2",
    "material_parameter_coverage_95",
    "calibrated_material_parameter_coverage_95",
    "material_parameter_ece",
    "calibrated_material_parameter_ece",
    "history_coverage_95",
    "calibrated_history_coverage_95",
    "history_ece",
    "calibrated_history_ece",
    "field_coverage_95",
    "calibrated_field_coverage_95",
    "field_ece",
    "calibrated_field_ece",
    "field_nll",
    "calibrated_field_nll",
    "calibrated_material_parameter_spread_scale",
    "calibrated_history_spread_scale",
    "calibrated_field_spread_scale",
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


@dataclass(frozen=True)
class SparseConfig:
    name: str
    sensors: int
    observation_steps: int
    noise_std: float


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Promote sparse-observation digital-twin posterior calibration to a main evidence table. "
            "The suite runs sparse sensor robustness and path-OOD assimilation conditions and aggregates "
            "material/history posterior coverage, NLL, and ECE."
        )
    )
    parser.add_argument("--protocols", default="strict_path_ood,reversal_curriculum,family_upper_bound")
    parser.add_argument("--sparse-configs", default=DEFAULT_SPARSE_CONFIGS)
    parser.add_argument("--seeds", default="20260517,20260518,20260519,20260520,20260521")
    parser.add_argument("--epochs", type=int, default=50)
    parser.add_argument("--train-samples", type=int, default=32)
    parser.add_argument("--eval-samples", type=int, default=8)
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--eval-batch-size", type=int, default=2)
    parser.add_argument("--hidden-dim", type=int, default=96)
    parser.add_argument("--message-passing-layers", type=int, default=3)
    parser.add_argument("--model-kind", choices=("history_gno", "thermo_hard_hgo"), default="thermo_hard_hgo")
    parser.add_argument("--nx", type=int, default=8)
    parser.add_argument("--ny", type=int, default=6)
    parser.add_argument("--mesh-kind", default="multi_hole")
    parser.add_argument("--geometry-perturbation", type=float, default=0.10)
    parser.add_argument("--load-steps", type=int, default=8)
    parser.add_argument("--max-newton-steps", type=int, default=14)
    parser.add_argument("--inversion-steps", type=int, default=120)
    parser.add_argument("--inversion-learning-rate", type=float, default=2.0e-2)
    parser.add_argument("--num-posterior-chains", type=int, default=8)
    parser.add_argument("--calibration-target-coverage", type=float, default=0.95)
    parser.add_argument("--calibration-max-scale", type=float, default=1.0e4)
    parser.add_argument("--calibration-search-steps", type=int, default=32)
    parser.add_argument("--calibration-fraction", type=float, default=0.5)
    parser.add_argument("--device", default="cuda")
    parser.add_argument(
        "--shared-data-root",
        type=Path,
        default=PROJECT_ROOT / "05_data_pipeline" / "processed" / "j2_sparse_dt_posterior_calibration_main",
    )
    parser.add_argument(
        "--report-root",
        type=Path,
        default=PROJECT_ROOT / "10_results" / "reports" / "j2_sparse_dt_posterior_calibration_main",
    )
    parser.add_argument(
        "--paper-csv-out",
        type=Path,
        default=PROJECT_ROOT / "11_paper" / "tables" / "j2_sparse_dt_posterior_calibration_main_table.csv",
    )
    parser.add_argument(
        "--paper-md-out",
        type=Path,
        default=PROJECT_ROOT / "11_paper" / "tables" / "j2_sparse_dt_posterior_calibration_main_table.md",
    )
    parser.add_argument(
        "--compact-csv-out",
        type=Path,
        default=PROJECT_ROOT / "11_paper" / "tables" / "j2_sparse_dt_posterior_calibration_compact_main.csv",
    )
    parser.add_argument(
        "--compact-md-out",
        type=Path,
        default=PROJECT_ROOT / "11_paper" / "tables" / "j2_sparse_dt_posterior_calibration_compact_main.md",
    )
    parser.add_argument(
        "--gain-csv-out",
        type=Path,
        default=PROJECT_ROOT / "11_paper" / "tables" / "j2_sparse_dt_posterior_calibration_gain_table.csv",
    )
    parser.add_argument(
        "--gain-md-out",
        type=Path,
        default=PROJECT_ROOT / "11_paper" / "tables" / "j2_sparse_dt_posterior_calibration_gain_table.md",
    )
    parser.add_argument(
        "--gain-aggregate-csv-out",
        type=Path,
        default=PROJECT_ROOT / "11_paper" / "tables" / "j2_sparse_dt_posterior_calibration_gain_aggregate.csv",
    )
    parser.add_argument(
        "--gain-aggregate-md-out",
        type=Path,
        default=PROJECT_ROOT / "11_paper" / "tables" / "j2_sparse_dt_posterior_calibration_gain_aggregate.md",
    )
    parser.add_argument("--force-rerun", action="store_true")
    parser.add_argument("--force-regenerate-data", action="store_true")
    parser.add_argument("--aggregate-only", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    protocols = _parse_protocols(args.protocols)
    sparse_configs = _parse_sparse_configs(args.sparse_configs)
    if not args.aggregate_only:
        for protocol_name, (train_paths, eval_paths) in protocols.items():
            for config in sparse_configs:
                _run_condition(args, protocol_name, train_paths, eval_paths, config)
    if args.dry_run:
        return
    rows = _aggregate_conditions(args, protocols, sparse_configs)
    compact_rows = _compact_rows(args, protocols, sparse_configs)
    gain_rows = _calibration_gain_rows(args, protocols, sparse_configs)
    gain_aggregate_rows = _aggregate_gain_rows(gain_rows)
    _write_rows(args.paper_csv_out, rows)
    _write_markdown(args.paper_md_out, rows)
    _write_rows(args.compact_csv_out, compact_rows)
    _write_markdown(args.compact_md_out, compact_rows, title="Posterior calibration compact main evidence")
    _write_rows(args.gain_csv_out, gain_rows)
    _write_markdown(args.gain_md_out, gain_rows, title="Posterior calibration raw-to-calibrated gain table")
    _write_rows(args.gain_aggregate_csv_out, gain_aggregate_rows)
    _write_markdown(
        args.gain_aggregate_md_out,
        gain_aggregate_rows,
        title="Posterior calibration gain aggregate by protocol and sparse sensor setting",
    )
    print(f"wrote {args.paper_csv_out}")
    print(f"wrote {args.paper_md_out}")
    print(f"wrote {args.compact_csv_out}")
    print(f"wrote {args.gain_aggregate_csv_out}")


def _run_condition(
    args: argparse.Namespace,
    protocol_name: str,
    train_paths: str,
    eval_paths: str,
    config: SparseConfig,
) -> None:
    condition_root = args.report_root / protocol_name / config.name
    summary_json = condition_root / "summary.json"
    print(
        "[posterior-calibration-main] "
        f"START protocol={protocol_name} sparse_config={config.name} "
        f"summary={summary_json}",
        flush=True,
    )
    command = [
        sys.executable,
        str(FIVE_SEED_SUITE),
        "--seeds",
        args.seeds,
        "--epochs",
        str(args.epochs),
        "--train-samples",
        str(args.train_samples),
        "--eval-samples",
        str(args.eval_samples),
        "--batch-size",
        str(args.batch_size),
        "--eval-batch-size",
        str(args.eval_batch_size),
        "--hidden-dim",
        str(args.hidden_dim),
        "--message-passing-layers",
        str(args.message_passing_layers),
        "--model-kind",
        args.model_kind,
        "--train-load-paths",
        train_paths,
        "--eval-load-paths",
        eval_paths,
        "--nx",
        str(args.nx),
        "--ny",
        str(args.ny),
        "--mesh-kind",
        args.mesh_kind,
        "--geometry-perturbation",
        str(args.geometry_perturbation),
        "--load-steps",
        str(args.load_steps),
        "--max-newton-steps",
        str(args.max_newton_steps),
        "--num-sensors",
        str(config.sensors),
        "--num-observation-steps",
        str(config.observation_steps),
        "--observation-noise-std",
        str(config.noise_std),
        "--inversion-steps",
        str(args.inversion_steps),
        "--inversion-learning-rate",
        str(args.inversion_learning_rate),
        "--num-posterior-chains",
        str(args.num_posterior_chains),
        "--calibration-target-coverage",
        str(args.calibration_target_coverage),
        "--calibration-max-scale",
        str(args.calibration_max_scale),
        "--calibration-search-steps",
        str(args.calibration_search_steps),
        "--posterior-calibration-mode",
        "split_conformal",
        "--calibration-fraction",
        str(args.calibration_fraction),
        "--device",
        args.device,
        "--shared-data-root",
        str(args.shared_data_root),
        "--report-dir",
        str(condition_root / "seeds"),
        "--summary-json",
        str(summary_json),
        "--summary-csv",
        str(condition_root / "summary.csv"),
        "--summary-md",
        str(condition_root / "summary.md"),
        "--per-seed-csv",
        str(condition_root / "per_seed.csv"),
    ]
    if args.force_rerun:
        command.append("--force-rerun")
    if args.force_regenerate_data:
        command.append("--force-regenerate-data")
    if args.dry_run:
        print(" ".join(command))
        return
    subprocess.run(command, cwd=PROJECT_ROOT, check=True)
    print(
        "[posterior-calibration-main] "
        f"DONE protocol={protocol_name} sparse_config={config.name} "
        f"summary_exists={summary_json.exists()}",
        flush=True,
    )


def _aggregate_conditions(
    args: argparse.Namespace,
    protocols: dict[str, tuple[str, str]],
    sparse_configs: tuple[SparseConfig, ...],
) -> list[dict[str, str]]:
    rows = []
    for protocol_name, (train_paths, _eval_paths) in protocols.items():
        train_set = set(_split_csv(train_paths))
        for config in sparse_configs:
            summary_path = args.report_root / protocol_name / config.name / "summary.json"
            if not summary_path.exists():
                if args.dry_run:
                    continue
                raise FileNotFoundError(summary_path)
            payload = json.loads(summary_path.read_text(encoding="utf-8"))
            for load_path, metrics in payload["by_load_path"].items():
                row = {
                    "Protocol": protocol_name,
                    "Train paths": train_paths,
                    "Eval path": load_path,
                    "Path OOD": "yes" if load_path not in train_set else "no",
                    "Sparse config": config.name,
                    "Sensors": str(config.sensors),
                    "Observed steps": str(config.observation_steps),
                    "Noise std": f"{config.noise_std:.3g}",
                }
                for metric in TABLE_METRICS:
                    row[metric] = _format_stat(metrics.get(metric))
                rows.append(row)
    return rows


def _compact_rows(
    args: argparse.Namespace,
    protocols: dict[str, tuple[str, str]],
    sparse_configs: tuple[SparseConfig, ...],
) -> list[dict[str, str]]:
    rows = []
    for protocol_name, (train_paths, _eval_paths) in protocols.items():
        train_set = set(_split_csv(train_paths))
        for config in sparse_configs:
            payload = _load_condition_summary(args, protocol_name, config)
            for load_path, metrics in payload["by_load_path"].items():
                row = {
                    "Protocol": protocol_name,
                    "Eval path": load_path,
                    "Path OOD": "yes" if load_path not in train_set else "no",
                    "Sparse config": config.name,
                    "Sensors": str(config.sensors),
                    "Observed steps": str(config.observation_steps),
                    "Noise std": f"{config.noise_std:.3g}",
                }
                for metric in COMPACT_METRICS:
                    row[_compact_label(metric)] = _format_stat(metrics.get(metric))
                rows.append(row)
    return rows


def _calibration_gain_rows(
    args: argparse.Namespace,
    protocols: dict[str, tuple[str, str]],
    sparse_configs: tuple[SparseConfig, ...],
) -> list[dict[str, str]]:
    rows = []
    for protocol_name, (train_paths, _eval_paths) in protocols.items():
        train_set = set(_split_csv(train_paths))
        for config in sparse_configs:
            payload = _load_condition_summary(args, protocol_name, config)
            for load_path, metrics in payload["by_load_path"].items():
                for target, raw_metric, calibrated_metric, direction in CALIBRATION_PAIRS:
                    raw_stats = metrics.get(raw_metric)
                    calibrated_stats = metrics.get(calibrated_metric)
                    if not raw_stats or not calibrated_stats:
                        continue
                    raw_mean = _stat_mean(raw_stats)
                    calibrated_mean = _stat_mean(calibrated_stats)
                    gain = _calibration_gain(raw_mean, calibrated_mean, direction)
                    rows.append(
                        {
                            "Protocol": protocol_name,
                            "Train paths": train_paths,
                            "Eval path": load_path,
                            "Path OOD": "yes" if load_path not in train_set else "no",
                            "Sparse config": config.name,
                            "Sensors": str(config.sensors),
                            "Observed steps": str(config.observation_steps),
                            "Target": target,
                            "Metric": raw_metric.replace(f"{target}_", ""),
                            "Direction": direction,
                            "Raw mean": _format_float(raw_mean),
                            "Calibrated mean": _format_float(calibrated_mean),
                            "Gain": _format_float(gain),
                            "Gain %": _format_float(_percent_gain(raw_mean, gain)),
                            "Raw": _format_stat(raw_stats),
                            "Calibrated": _format_stat(calibrated_stats),
                            "Improved": "yes" if gain is not None and gain > 0.0 else "no",
                        }
                    )
    return rows


def _aggregate_gain_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    groups: dict[tuple[str, str, str, str, str], list[dict[str, str]]] = {}
    for row in rows:
        key = (
            row["Protocol"],
            row["Sparse config"],
            row["Target"],
            row["Metric"],
            row["Direction"],
        )
        groups.setdefault(key, []).append(row)
    output = []
    for key, items in sorted(groups.items()):
        gains = [_as_float(item["Gain"]) for item in items]
        gains = [value for value in gains if value is not None]
        output.append(
            {
                "Protocol": key[0],
                "Sparse config": key[1],
                "Target": key[2],
                "Metric": key[3],
                "Direction": key[4],
                "Gain mean": _format_float(_mean(gains)),
                "Gain std": _format_float(_std(gains)),
                "Gain median": _format_float(_median(gains)),
                "Gain IQR": _format_float(_iqr(gains)),
                "Improved paths": str(sum(1 for item in items if item.get("Improved") == "yes")),
                "Paths": str(len(items)),
                "Eval paths": ",".join(sorted({item["Eval path"] for item in items})),
            }
        )
    return output


def _load_condition_summary(args: argparse.Namespace, protocol_name: str, config: SparseConfig) -> dict:
    summary_path = args.report_root / protocol_name / config.name / "summary.json"
    if not summary_path.exists():
        if args.dry_run:
            return {"by_load_path": {}}
        raise FileNotFoundError(summary_path)
    return json.loads(summary_path.read_text(encoding="utf-8"))


def _compact_label(metric: str) -> str:
    replacements = {
        "sparse_observation_relative_l2": "Sparse obs. L2",
        "rollout_displacement_relative_l2": "Rollout disp. L2",
        "material_parameter_relative_l2": "Material rel. L2",
        "material_parameter_coverage_95": "Param cov. raw",
        "calibrated_material_parameter_coverage_95": "Param cov. cal.",
        "material_parameter_ece": "Param ECE raw",
        "calibrated_material_parameter_ece": "Param ECE cal.",
        "history_coverage_95": "History cov. raw",
        "calibrated_history_coverage_95": "History cov. cal.",
        "history_ece": "History ECE raw",
        "calibrated_history_ece": "History ECE cal.",
        "field_coverage_95": "Field cov. raw",
        "calibrated_field_coverage_95": "Field cov. cal.",
        "field_ece": "Field ECE raw",
        "calibrated_field_ece": "Field ECE cal.",
        "field_nll": "Field NLL raw",
        "calibrated_field_nll": "Field NLL cal.",
        "calibrated_material_parameter_spread_scale": "Param spread scale",
        "calibrated_history_spread_scale": "History spread scale",
        "calibrated_field_spread_scale": "Field spread scale",
    }
    return replacements.get(metric, metric)


def _stat_mean(stats: dict | None) -> float | None:
    if not stats:
        return None
    try:
        return float(stats["mean"])
    except (KeyError, TypeError, ValueError):
        return None


def _calibration_gain(raw: float | None, calibrated: float | None, direction: str) -> float | None:
    if raw is None or calibrated is None:
        return None
    if direction == "higher":
        return calibrated - raw
    return raw - calibrated


def _percent_gain(raw: float | None, gain: float | None) -> float | None:
    if raw is None or gain is None or abs(raw) <= 1.0e-12:
        return None
    return 100.0 * gain / abs(raw)


def _as_float(value: str | None) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(value)
    except ValueError:
        return None


def _mean(values: list[float]) -> float | None:
    if not values:
        return None
    return sum(values) / len(values)


def _std(values: list[float]) -> float | None:
    if not values:
        return None
    if len(values) == 1:
        return 0.0
    avg = sum(values) / len(values)
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


def _parse_protocols(value: str) -> dict[str, tuple[str, str]]:
    parsed = {}
    for name in _split_csv(value):
        if name not in PROTOCOLS:
            raise argparse.ArgumentTypeError(f"unknown protocol {name!r}; options are {sorted(PROTOCOLS)}")
        parsed[name] = PROTOCOLS[name]
    if not parsed:
        raise argparse.ArgumentTypeError("at least one protocol is required")
    return parsed


def _parse_sparse_configs(value: str) -> tuple[SparseConfig, ...]:
    configs = []
    for item in _split_csv(value):
        parts = item.split(":")
        if len(parts) != 4:
            raise argparse.ArgumentTypeError(
                "sparse configs must be name:sensors:observation_steps:noise_std"
            )
        configs.append(SparseConfig(parts[0], int(parts[1]), int(parts[2]), float(parts[3])))
    if not configs:
        raise argparse.ArgumentTypeError("at least one sparse config is required")
    return tuple(configs)


def _split_csv(value: str) -> tuple[str, ...]:
    return tuple(item.strip() for item in value.split(",") if item.strip())


def _format_stat(stats: dict | None) -> str:
    if not stats:
        return ""
    return f"{stats['mean']:.4g} +/- {stats['std']:.2g}; med {stats['median']:.4g}, IQR {stats['iqr']:.2g}"


def _format_float(value: object) -> str:
    if value is None:
        return ""
    try:
        return f"{float(value):.6g}"
    except (TypeError, ValueError):
        return ""


def _write_rows(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _write_markdown(
    path: Path,
    rows: list[dict[str, str]],
    title: str = "Sparse-observation digital-twin posterior calibration main evidence",
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    headers = list(rows[0])
    lines = [
        f"# {title}",
        "",
        "This table promotes material/history posterior calibration from extended diagnostics to the main evidence chain.",
        "",
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(_md_cell(row.get(header, "")) for header in headers) + " |")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def _md_cell(value: str) -> str:
    return str(value).replace("|", "\\|")


if __name__ == "__main__":
    main()
