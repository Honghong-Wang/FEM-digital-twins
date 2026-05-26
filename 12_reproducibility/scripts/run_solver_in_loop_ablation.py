from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
BASELINE_SCRIPT = PROJECT_ROOT / "12_reproducibility" / "scripts" / "run_j2_path_dependent_baseline_table.py"
DEFAULT_DATA_ROOT = PROJECT_ROOT / "05_data_pipeline" / "processed" / "level6_benchmark_matrix_smoke" / "multi_hole_6x5"
DEFAULT_OUT_ROOT = PROJECT_ROOT / "10_results" / "reports" / "solver_in_loop_ablation"
DEFAULT_TABLE_ROOT = PROJECT_ROOT / "11_paper" / "tables"

ABLATION_CONFIGS = (
    {
        "name": "no_solver_loss",
        "label": "No solver loss",
        "solver_weight": 0.0,
        "solver_mode": "dense_newton",
        "newton_damping": 1.0,
        "newton_steps": 1,
        "line_search": False,
        "line_search_dampings": "1.0,0.5,0.25,0.125",
        "regularization": 1.0e-6,
    },
    {
        "name": "tangent_linearized_solver_loss",
        "label": "Tangent-linearized solver loss",
        "solver_weight": 1.0e-5,
        "solver_mode": "linearized",
        "newton_damping": 1.0,
        "newton_steps": 1,
        "line_search": False,
        "line_search_dampings": "1.0,0.5,0.25,0.125",
        "regularization": 1.0e-6,
    },
    {
        "name": "one_step_dense_newton",
        "label": "One-step dense Newton",
        "solver_weight": 1.0e-5,
        "solver_mode": "dense_newton",
        "newton_damping": 1.0,
        "newton_steps": 1,
        "line_search": False,
        "line_search_dampings": "1.0,0.5,0.25,0.125",
        "regularization": 1.0e-6,
    },
    {
        "name": "multi_step_damped_newton",
        "label": "Multi-step damped Newton",
        "solver_weight": 1.0e-5,
        "solver_mode": "dense_newton",
        "newton_damping": 0.5,
        "newton_steps": 3,
        "line_search": False,
        "line_search_dampings": "1.0,0.5,0.25,0.125",
        "regularization": 1.0e-6,
    },
    {
        "name": "multi_step_line_search_newton",
        "label": "Multi-step line-search Newton",
        "solver_weight": 1.0e-5,
        "solver_mode": "dense_newton",
        "newton_damping": 1.0,
        "newton_steps": 3,
        "line_search": True,
        "line_search_dampings": "1.0,0.5,0.25,0.125",
        "regularization": 1.0e-6,
    },
)

REPORT_METRICS = (
    ("displacement_relative_l2", "rollout disp rel L2"),
    ("final_displacement_relative_l2", "final disp rel L2"),
    ("qp_history_relative_l2", "QP history rel L2"),
    ("qp_history_increment_relative_l2", "QP history-inc rel L2"),
    ("qp_reversal_eqp_increment_relative_l2", "QP reversal eqp-inc rel L2"),
    ("qp_reversal_plastic_work_increment_relative_l2", "QP reversal work-inc rel L2"),
    ("qp_reversal_yield_flag_mae", "QP reversal yield MAE"),
    ("fem_residual_relative_rms", "FEM residual rel RMS"),
    ("fem_energy_relative_error", "FEM energy rel err"),
    ("fem_solver_linearized_residual_relative_rms", "FEM tangent-solver rel RMS"),
    ("fem_newton_initial_residual_relative_rms", "Newton initial residual rel RMS"),
    ("fem_newton_final_residual_relative_rms", "Newton final residual rel RMS"),
    ("fem_newton_residual_ratio", "Newton residual ratio"),
    ("fem_newton_residual_decrease_fraction", "Newton residual decrease"),
    ("fem_newton_step_residual_decrease_fraction", "Newton step residual decrease"),
    ("fem_newton_step1_residual_ratio", "Newton step1 residual ratio"),
    ("fem_newton_step2_residual_ratio", "Newton step2 residual ratio"),
    ("fem_newton_step3_residual_ratio", "Newton step3 residual ratio"),
    ("fem_newton_step1_residual_decrease_fraction", "Newton step1 residual decrease"),
    ("fem_newton_step2_residual_decrease_fraction", "Newton step2 residual decrease"),
    ("fem_newton_step3_residual_decrease_fraction", "Newton step3 residual decrease"),
    ("fem_newton_correction_relative_norm", "Newton correction rel norm"),
    ("fem_newton_accepted_damping", "Newton accepted damping"),
    ("fem_newton_convergence_rate", "Newton convergence rate"),
    ("fem_newton_failure_rate", "Newton failure rate"),
)

HIGHER_IS_BETTER = {
    "fem_newton_residual_decrease_fraction",
    "fem_newton_step_residual_decrease_fraction",
    "fem_newton_convergence_rate",
    "fem_newton_step1_residual_decrease_fraction",
    "fem_newton_step2_residual_decrease_fraction",
    "fem_newton_step3_residual_decrease_fraction",
}


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Run solver-in-loop ablations for J2 path-dependent operators. The four "
            "default arms isolate no solver loss, tangent-linearized solver loss, "
            "one-step dense Newton, and multi-step damped Newton."
        )
    )
    parser.add_argument("--data-root", type=Path, default=DEFAULT_DATA_ROOT)
    parser.add_argument("--out-root", type=Path, default=DEFAULT_OUT_ROOT)
    parser.add_argument("--models", default="hgo_qp_true_j2")
    parser.add_argument("--train-load-paths", default="monotonic")
    parser.add_argument(
        "--eval-load-paths",
        default="monotonic,unload_reload,cyclic,nonproportional,random_amplitude,pre_stress",
    )
    parser.add_argument(
        "--filter-existing-eval-paths",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Drop eval load paths that do not have test.npz under data-root.",
    )
    parser.add_argument("--seeds", default="20260517,20260518,20260519,20260520,20260521")
    parser.add_argument("--epochs", type=int, default=50)
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--eval-batch-size", type=int, default=4)
    parser.add_argument("--hidden-dim", type=int, default=96)
    parser.add_argument("--message-passing-layers", type=int, default=3)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--residual-weight", type=float, default=5.0e-5)
    parser.add_argument("--energy-weight", type=float, default=5.0e-6)
    parser.add_argument("--solver-weight", type=float, default=1.0e-5)
    parser.add_argument("--include-regularization-sweep", action="store_true")
    parser.add_argument("--regularization-sweep", default="1e-8,1e-6,1e-4")
    parser.add_argument("--step-policy", choices=("final", "all", "reversal", "reversal_final"), default="all")
    parser.add_argument("--fem-training-models", default="hgo_qp_true_j2,hgo_qp_thermo_hard,tinn")
    parser.add_argument("--learning-rate", type=float, default=1.0e-3)
    parser.add_argument("--aggregate-only", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--skip-existing", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument(
        "--table-csv-out",
        type=Path,
        default=DEFAULT_TABLE_ROOT / "solver_in_loop_ablation_table.csv",
    )
    parser.add_argument(
        "--table-md-out",
        type=Path,
        default=DEFAULT_TABLE_ROOT / "solver_in_loop_ablation_table.md",
    )
    parser.add_argument(
        "--reduction-csv-out",
        type=Path,
        default=DEFAULT_TABLE_ROOT / "solver_in_loop_ablation_reduction.csv",
    )
    parser.add_argument(
        "--reduction-md-out",
        type=Path,
        default=DEFAULT_TABLE_ROOT / "solver_in_loop_ablation_reduction.md",
    )
    args = parser.parse_args()
    if args.filter_existing_eval_paths:
        args.eval_load_paths = _existing_eval_paths(args.data_root, args.eval_load_paths)

    rows = []
    for config in _ablation_configs(args):
        config = dict(config)
        if config["solver_weight"] > 0.0:
            config["solver_weight"] = float(args.solver_weight)
        out_dir = args.out_root / str(config["name"])
        summary_path = out_dir / "summary.json"
        if not args.aggregate_only and (not args.skip_existing or not summary_path.exists()):
            out_dir.mkdir(parents=True, exist_ok=True)
            command = _baseline_command(args, config, out_dir)
            if args.dry_run:
                print(" ".join(command))
            else:
                subprocess.run(command, cwd=PROJECT_ROOT, check=True)
        if summary_path.exists():
            rows.extend(_summary_rows(config, summary_path))
        elif args.aggregate_only or not args.dry_run:
            print(f"[missing] {summary_path}")

    reduction_rows = _reduction_rows(rows)
    if not args.dry_run:
        _write_rows(args.table_csv_out, rows)
        _write_markdown(args.table_md_out, rows)
        _write_rows(args.reduction_csv_out, reduction_rows)
        _write_markdown(args.reduction_md_out, reduction_rows)
        print(f"wrote {args.table_csv_out}")
        print(f"wrote {args.table_md_out}")
        print(f"wrote {args.reduction_csv_out}")
        print(f"wrote {args.reduction_md_out}")


def _baseline_command(args: argparse.Namespace, config: dict[str, object], out_dir: Path) -> list[str]:
    command = [
        sys.executable,
        str(BASELINE_SCRIPT),
        "--data-root",
        str(args.data_root),
        "--models",
        str(args.models),
        "--train-load-paths",
        str(args.train_load_paths),
        "--eval-load-paths",
        str(args.eval_load_paths),
        "--seeds",
        str(args.seeds),
        "--epochs",
        str(args.epochs),
        "--batch-size",
        str(args.batch_size),
        "--eval-batch-size",
        str(args.eval_batch_size),
        "--hidden-dim",
        str(args.hidden_dim),
        "--message-passing-layers",
        str(args.message_passing_layers),
        "--learning-rate",
        str(args.learning_rate),
        "--device",
        str(args.device),
        "--fem-training-residual-weight",
        str(args.residual_weight),
        "--fem-training-energy-weight",
        str(args.energy_weight),
        "--fem-training-solver-weight",
        str(config["solver_weight"]),
        "--fem-training-solver-mode",
        str(config["solver_mode"]),
        "--fem-training-newton-damping",
        str(config["newton_damping"]),
        "--fem-training-newton-steps",
        str(config["newton_steps"]),
        "--fem-training-newton-line-search-dampings",
        str(config["line_search_dampings"]),
        "--fem-training-tangent-regularization",
        str(config["regularization"]),
        "--fem-training-step-policy",
        str(args.step_policy),
        "--fem-training-models",
        str(args.fem_training_models),
        "--fem-audit-step-policy",
        "all",
        "--fem-audit-metrics",
        "--out",
        str(out_dir / "summary.json"),
        "--csv-out",
        str(out_dir / "table.csv"),
        "--md-out",
        str(out_dir / "table.md"),
        "--robust-csv-out",
        str(out_dir / "robust.csv"),
        "--robust-md-out",
        str(out_dir / "robust.md"),
        "--per-seed-csv-out",
        str(out_dir / "per_seed.csv"),
        "--per-seed-md-out",
        str(out_dir / "per_seed.md"),
        "--outlier-csv-out",
        str(out_dir / "outliers.csv"),
        "--outlier-md-out",
        str(out_dir / "outliers.md"),
        "--pathwise-csv-out",
        str(out_dir / "by_path.csv"),
        "--pathwise-md-out",
        str(out_dir / "by_path.md"),
    ]
    if bool(config.get("line_search", False)):
        command.append("--fem-training-newton-line-search")
    return command


def _ablation_configs(args: argparse.Namespace) -> list[dict[str, object]]:
    configs = [dict(config) for config in ABLATION_CONFIGS]
    if args.include_regularization_sweep:
        for regularization in _float_values(args.regularization_sweep):
            configs.append(
                {
                    "name": f"line_search_reg_{regularization:g}".replace("-", "m").replace(".", "p"),
                    "label": f"Line-search Newton reg={regularization:g}",
                    "solver_weight": 1.0e-5,
                    "solver_mode": "dense_newton",
                    "newton_damping": 1.0,
                    "newton_steps": 3,
                    "line_search": True,
                    "line_search_dampings": "1.0,0.5,0.25,0.125",
                    "regularization": regularization,
                }
            )
    return configs


def _existing_eval_paths(data_root: Path, value: str) -> str:
    requested = [item.strip() for item in value.split(",") if item.strip()]
    existing = [item for item in requested if (data_root / item / "test.npz").exists()]
    if not existing:
        raise FileNotFoundError(f"no requested eval load paths have test.npz under {data_root}")
    missing = sorted(set(requested).difference(existing))
    if missing:
        print(f"[filter] missing eval load paths under {data_root}: {', '.join(missing)}")
    return ",".join(existing)


def _summary_rows(config: dict[str, object], summary_path: Path) -> list[dict[str, str]]:
    payload = json.loads(summary_path.read_text(encoding="utf-8"))
    rows = []
    for model_name, result in sorted(payload.get("results", {}).items()):
        by_path = result.get("summary", {}).get("by_load_path", {})
        seeds = str(result.get("summary", {}).get("num_seeds", ""))
        for load_path, path_stats in sorted(by_path.items()):
            for metric, label in REPORT_METRICS:
                stats = path_stats.get(metric)
                if not stats or stats.get("mean") is None:
                    continue
                rows.append(
                    {
                        "Ablation": str(config["label"]),
                        "Ablation id": str(config["name"]),
                        "Solver mode": str(config["solver_mode"]),
                        "Newton damping": str(config["newton_damping"]),
                        "Newton steps": str(config["newton_steps"]),
                        "Line search": str(bool(config.get("line_search", False))),
                        "Regularization": str(config.get("regularization", "")),
                        "Model": model_name,
                        "Load path": load_path,
                        "Metric": metric,
                        "Metric label": label,
                        "Mean": _format_float(stats.get("mean")),
                        "Std": _format_float(stats.get("std")),
                        "Median": _format_float(stats.get("median")),
                        "IQR": _format_float(stats.get("iqr")),
                        "Seeds": seeds,
                        "Source": str(summary_path),
                    }
                )
    return rows


def _reduction_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    index = {
        (row["Ablation id"], row["Model"], row["Load path"], row["Metric"]): row
        for row in rows
    }
    baseline_id = "no_solver_loss"
    output = []
    for row in rows:
        if row["Ablation id"] == baseline_id:
            continue
        base = index.get((baseline_id, row["Model"], row["Load path"], row["Metric"]))
        if base is None:
            continue
        base_mean = _as_float(base["Mean"])
        cand_mean = _as_float(row["Mean"])
        base_median = _as_float(base["Median"])
        cand_median = _as_float(row["Median"])
        output.append(
            {
                "Ablation": row["Ablation"],
                "Model": row["Model"],
                "Load path": row["Load path"],
                "Metric": row["Metric"],
                "No-solver mean": _format_float(base_mean),
                "Ablation mean": _format_float(cand_mean),
                "Mean improvement": _format_float(_improvement(base_mean, cand_mean, row["Metric"])),
                "Mean improvement %": _format_float(_improvement_percent(base_mean, cand_mean, row["Metric"])),
                "Mean improved": _improved(base_mean, cand_mean, row["Metric"]),
                "No-solver median": _format_float(base_median),
                "Ablation median": _format_float(cand_median),
                "Median improvement": _format_float(_improvement(base_median, cand_median, row["Metric"])),
                "Median improvement %": _format_float(_improvement_percent(base_median, cand_median, row["Metric"])),
                "Median improved": _improved(base_median, cand_median, row["Metric"]),
            }
        )
    return output


def _write_rows(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames = list(rows[0])
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    headers = list(rows[0])
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(row.get(header, "") for header in headers) + " |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _as_float(value: str | None) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(value)
    except ValueError:
        return None


def _improvement(reference: float | None, candidate: float | None, metric: str) -> float | None:
    if reference is None or candidate is None:
        return None
    if metric in HIGHER_IS_BETTER:
        return candidate - reference
    return reference - candidate


def _improvement_percent(reference: float | None, candidate: float | None, metric: str) -> float | None:
    if reference is None or candidate is None or abs(reference) <= 1.0e-12:
        return None
    return 100.0 * _improvement(reference, candidate, metric) / abs(reference)


def _improved(reference: float | None, candidate: float | None, metric: str) -> str:
    if reference is None or candidate is None:
        return ""
    if metric in HIGHER_IS_BETTER:
        return "yes" if candidate > reference else "no"
    return "yes" if candidate < reference else "no"


def _float_values(value: str) -> tuple[float, ...]:
    parsed = tuple(float(item.strip()) for item in value.split(",") if item.strip())
    if not parsed:
        raise argparse.ArgumentTypeError("at least one float value is required")
    return parsed


def _format_float(value: object) -> str:
    if value is None:
        return ""
    try:
        return f"{float(value):.6g}"
    except (TypeError, ValueError):
        return ""


if __name__ == "__main__":
    main()
