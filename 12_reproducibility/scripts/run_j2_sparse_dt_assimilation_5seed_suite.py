from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RUNNER = PROJECT_ROOT / "12_reproducibility" / "scripts" / "run_j2_sparse_digital_twin_assimilation.py"
PRIMARY_METRICS = (
    "sparse_observation_relative_l2",
    "rollout_displacement_relative_l2",
    "material_parameter_relative_l2",
    "material_parameter_mae",
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
    "posterior_calibration_num_calibration",
    "posterior_calibration_num_test",
    "inversion_final_loss",
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Run and aggregate a 5-seed sparse-observation digital-twin assimilation suite "
            "for J2 path-dependent FEM data."
        )
    )
    parser.add_argument("--seeds", default="20260517,20260518,20260519,20260520,20260521")
    parser.add_argument("--epochs", type=int, default=50)
    parser.add_argument("--train-samples", type=int, default=32)
    parser.add_argument("--eval-samples", type=int, default=8)
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--eval-batch-size", type=int, default=2)
    parser.add_argument("--hidden-dim", type=int, default=96)
    parser.add_argument("--message-passing-layers", type=int, default=3)
    parser.add_argument("--model-kind", choices=("history_gno", "thermo_hard_hgo"), default="thermo_hard_hgo")
    parser.add_argument("--train-load-paths", default="monotonic,unload_reload,cyclic")
    parser.add_argument("--eval-load-paths", default="cyclic,nonproportional,random_amplitude,pre_stress")
    parser.add_argument("--nx", type=int, default=8)
    parser.add_argument("--ny", type=int, default=6)
    parser.add_argument("--mesh-kind", default="multi_hole")
    parser.add_argument("--geometry-perturbation", type=float, default=0.10)
    parser.add_argument("--load-steps", type=int, default=8)
    parser.add_argument("--max-newton-steps", type=int, default=14)
    parser.add_argument("--num-sensors", type=int, default=6)
    parser.add_argument("--num-observation-steps", type=int, default=3)
    parser.add_argument("--observation-noise-std", type=float, default=1.0e-3)
    parser.add_argument("--inversion-steps", type=int, default=120)
    parser.add_argument("--inversion-learning-rate", type=float, default=2.0e-2)
    parser.add_argument("--num-posterior-chains", type=int, default=8)
    parser.add_argument("--calibrate-posterior", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--calibration-target-coverage", type=float, default=0.95)
    parser.add_argument("--calibration-max-scale", type=float, default=1.0e4)
    parser.add_argument("--calibration-search-steps", type=int, default=32)
    parser.add_argument(
        "--posterior-calibration-mode",
        choices=("split_conformal", "batch_oracle"),
        default="split_conformal",
    )
    parser.add_argument("--calibration-fraction", type=float, default=0.5)
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--force-regenerate-data", action="store_true")
    parser.add_argument("--force-rerun", action="store_true")
    parser.add_argument("--aggregate-only", action="store_true")
    parser.add_argument(
        "--shared-data-root",
        type=Path,
        default=PROJECT_ROOT / "05_data_pipeline" / "processed" / "j2_sparse_dt_assimilation_formal_shared",
        help="Shared split root reused across seeds so only model initialization/optimization seed changes.",
    )
    parser.add_argument(
        "--report-dir",
        type=Path,
        default=PROJECT_ROOT / "10_results" / "reports" / "j2_sparse_dt_assimilation_5seed",
    )
    parser.add_argument(
        "--summary-json",
        type=Path,
        default=PROJECT_ROOT / "10_results" / "reports" / "j2_sparse_dt_assimilation_5seed_summary.json",
    )
    parser.add_argument(
        "--summary-csv",
        type=Path,
        default=PROJECT_ROOT / "11_paper" / "tables" / "j2_sparse_dt_assimilation_5seed_summary.csv",
    )
    parser.add_argument(
        "--summary-md",
        type=Path,
        default=PROJECT_ROOT / "11_paper" / "tables" / "j2_sparse_dt_assimilation_5seed_summary.md",
    )
    parser.add_argument(
        "--per-seed-csv",
        type=Path,
        default=PROJECT_ROOT / "11_paper" / "tables" / "j2_sparse_dt_assimilation_5seed_per_seed.csv",
    )
    args = parser.parse_args()

    seeds = _parse_ints(args.seeds)
    if not args.aggregate_only:
        for index, seed in enumerate(seeds):
            _run_seed(args, seed, regenerate_data=args.force_regenerate_data and index == 0)
    summary, per_seed_rows = _aggregate(args.report_dir, seeds)
    summary["metadata"] = {
        "seeds": list(seeds),
        "epochs": args.epochs,
        "train_samples": args.train_samples,
        "eval_samples": args.eval_samples,
        "train_load_paths": args.train_load_paths.split(","),
        "eval_load_paths": args.eval_load_paths.split(","),
        "mesh_kind": args.mesh_kind,
        "grid_shape": [args.nx, args.ny],
        "load_steps": args.load_steps,
        "num_sensors": args.num_sensors,
        "num_observation_steps": args.num_observation_steps,
        "num_posterior_chains": args.num_posterior_chains,
        "calibrate_posterior": args.calibrate_posterior,
        "calibration_target_coverage": args.calibration_target_coverage,
        "calibration_max_scale": args.calibration_max_scale,
        "posterior_calibration_mode": args.posterior_calibration_mode,
        "calibration_fraction": args.calibration_fraction,
        "inversion_steps": args.inversion_steps,
        "shared_data_root": str(args.shared_data_root),
        "report_dir": str(args.report_dir),
    }
    args.summary_json.parent.mkdir(parents=True, exist_ok=True)
    args.summary_json.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    _write_summary_csv(args.summary_csv, summary)
    _write_summary_md(args.summary_md, summary)
    _write_per_seed_csv(args.per_seed_csv, per_seed_rows)
    print(json.dumps(summary["by_load_path"], indent=2))
    print(f"wrote {args.summary_json}")
    print(f"wrote {args.summary_csv}")
    print(f"wrote {args.summary_md}")
    print(f"wrote {args.per_seed_csv}")


def _run_seed(args: argparse.Namespace, seed: int, regenerate_data: bool) -> None:
    out = args.report_dir / f"seed_{seed}.json"
    if out.exists() and not args.force_rerun:
        print(f"skip existing {out}")
        return
    command = [
        sys.executable,
        str(RUNNER),
        "--data-root",
        str(args.shared_data_root),
        "--train-load-paths",
        args.train_load_paths,
        "--eval-load-paths",
        args.eval_load_paths,
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
        str(args.num_sensors),
        "--num-observation-steps",
        str(args.num_observation_steps),
        "--observation-noise-std",
        str(args.observation_noise_std),
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
        args.posterior_calibration_mode,
        "--calibration-fraction",
        str(args.calibration_fraction),
        "--seed",
        str(seed),
        "--device",
        args.device,
        "--out",
        str(out),
        "--csv-out",
        str(out.with_suffix(".csv")),
    ]
    if regenerate_data:
        command.append("--force-regenerate")
    if not args.calibrate_posterior:
        command.append("--no-calibrate-posterior")
    print(f"running sparse DT assimilation seed={seed}")
    subprocess.run(command, cwd=PROJECT_ROOT, check=True)


def _aggregate(report_dir: Path, seeds: tuple[int, ...]) -> tuple[dict, list[dict[str, str]]]:
    payloads = []
    for seed in seeds:
        path = report_dir / f"seed_{seed}.json"
        if not path.exists():
            raise FileNotFoundError(path)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payloads.append((seed, payload))
    load_paths = sorted({load_path for _, payload in payloads for load_path in payload["evaluations"]})
    summary = {"by_load_path": {}}
    per_seed_rows = []
    for load_path in load_paths:
        summary["by_load_path"][load_path] = {}
        for metric in PRIMARY_METRICS:
            values = [
                float(payload["evaluations"][load_path][metric])
                for _, payload in payloads
                if metric in payload["evaluations"].get(load_path, {})
            ]
            if values:
                summary["by_load_path"][load_path][metric] = _distribution(values)
        for seed, payload in payloads:
            metrics = payload["evaluations"].get(load_path, {})
            row = {"seed": str(seed), "load_path": load_path}
            row.update({metric: _format_float(metrics.get(metric)) for metric in PRIMARY_METRICS})
            per_seed_rows.append(row)
    return summary, per_seed_rows


def _distribution(values: list[float]) -> dict[str, float]:
    ordered = sorted(values)
    n = len(ordered)
    mean = sum(ordered) / n
    variance = sum((value - mean) ** 2 for value in ordered) / max(n - 1, 1)
    q1 = _quantile(ordered, 0.25)
    q2 = _quantile(ordered, 0.50)
    q3 = _quantile(ordered, 0.75)
    return {
        "mean": mean,
        "std": variance ** 0.5,
        "median": q2,
        "iqr": q3 - q1,
        "min": ordered[0],
        "max": ordered[-1],
        "n": n,
    }


def _quantile(ordered: list[float], q: float) -> float:
    if len(ordered) == 1:
        return ordered[0]
    position = q * (len(ordered) - 1)
    left = int(position)
    right = min(left + 1, len(ordered) - 1)
    weight = position - left
    return ordered[left] * (1.0 - weight) + ordered[right] * weight


def _write_summary_csv(path: Path, summary: dict) -> None:
    rows = []
    for load_path, metrics in summary["by_load_path"].items():
        for metric, stats in metrics.items():
            rows.append(
                {
                    "load_path": load_path,
                    "metric": metric,
                    "mean": stats["mean"],
                    "std": stats["std"],
                    "median": stats["median"],
                    "iqr": stats["iqr"],
                    "min": stats["min"],
                    "max": stats["max"],
                    "n": stats["n"],
                }
            )
    _write_rows(path, rows)


def _write_summary_md(path: Path, summary: dict) -> None:
    rows = []
    for load_path, metrics in summary["by_load_path"].items():
        row = {"Load path": load_path}
        for metric in PRIMARY_METRICS:
            row[metric] = _format_stat(metrics.get(metric))
        rows.append(row)
    _write_markdown(path, rows)


def _write_per_seed_csv(path: Path, rows: list[dict[str, str]]) -> None:
    _write_rows(path, rows)


def _write_rows(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    headers = list(rows[0])
    lines = [
        "# J2 Sparse-Observation Digital-Twin Assimilation 5-Seed Summary",
        "",
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(row.get(header, "") for header in headers) + " |")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def _format_stat(stats: dict | None) -> str:
    if not stats:
        return ""
    return f"{stats['mean']:.4g} +/- {stats['std']:.2g}; med {stats['median']:.4g}, IQR {stats['iqr']:.2g}"


def _format_float(value: object) -> str:
    if value is None:
        return ""
    return f"{float(value):.10g}"


def _parse_ints(value: str) -> tuple[int, ...]:
    parsed = tuple(int(item.strip()) for item in value.split(",") if item.strip())
    if not parsed:
        raise argparse.ArgumentTypeError("at least one seed is required")
    return parsed


if __name__ == "__main__":
    main()
