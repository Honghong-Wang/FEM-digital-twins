from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
BASELINE_SCRIPT = PROJECT_ROOT / "12_reproducibility" / "scripts" / "run_j2_path_dependent_baseline_table.py"
ALL_PATH_FAMILIES = "monotonic,unload_reload,cyclic,nonproportional,random_amplitude,pre_stress"
PROTOCOL_TRAIN_PATHS = {
    "strict": "monotonic",
    "reversal_curriculum": "monotonic,unload_reload,cyclic",
    "family_upper_bound": ALL_PATH_FAMILIES,
}
REPORT_PATHS = (
    "monotonic",
    "unload_reload",
    "cyclic",
    "nonproportional",
    "random_amplitude",
    "pre_stress",
)
REPORT_METRICS = (
    ("displacement_relative_l2", "disp rel L2"),
    ("history_relative_l2", "history rel L2"),
    ("history_increment_relative_l2", "history-inc rel L2"),
    ("qp_history_relative_l2", "QP history rel L2"),
    ("qp_history_increment_relative_l2", "QP history-inc rel L2"),
    ("qp_reversal_plastic_scalar_increment_relative_l2", "QP reversal scalar-inc rel L2"),
    ("qp_reversal_eqp_increment_relative_l2", "QP reversal eqp-inc rel L2"),
    ("qp_reversal_plastic_work_increment_relative_l2", "QP reversal work-inc rel L2"),
    ("qp_reversal_yield_flag_mae", "QP reversal yield MAE"),
    ("reversal_history_increment_relative_l2", "reversal hist-inc rel L2"),
    ("predicted_yield_surface_relative_rms", "yield RMS"),
    ("predicted_plastic_work_lower_bound_target_normalized_violation", "work viol target-norm"),
    ("j2_qp_active_consistency_residual_relative_rms", "J2 QP active consistency rel RMS"),
    ("fem_residual_relative_rms", "FEM residual rel RMS"),
    ("fem_energy_relative_error", "FEM energy rel err"),
    ("fem_solver_linearized_residual_relative_rms", "FEM tangent-solver rel RMS"),
    ("fem_newton_residual_ratio", "Newton residual ratio"),
    ("fem_newton_residual_decrease_fraction", "Newton residual decrease"),
    ("fem_newton_correction_relative_norm", "Newton correction norm"),
    ("fem_newton_step1_residual_ratio", "Newton step1 residual ratio"),
    ("fem_newton_step2_residual_ratio", "Newton step2 residual ratio"),
    ("fem_newton_step3_residual_ratio", "Newton step3 residual ratio"),
    ("fem_newton_accepted_damping", "Newton accepted damping"),
    ("fem_newton_convergence_rate", "Newton convergence"),
    ("fem_newton_failure_rate", "Newton failure"),
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Run the Level-6 J2 benchmark matrix over path families, geometry families, "
            "and mesh-size families. The data root should contain case directories such as "
            "multi_hole_16x12/<load-path>/<split>.npz."
        )
    )
    parser.add_argument(
        "--data-root",
        type=Path,
        default=PROJECT_ROOT / "05_data_pipeline" / "processed" / "level6_complex_j2_benchmark",
    )
    parser.add_argument(
        "--cases",
        type=str,
        default="all",
        help="Comma-separated case directories, or 'all' to scan directories under data-root.",
    )
    parser.add_argument(
        "--models",
        type=str,
        default=(
            "hgo_qp_true_j2,hgo_qp_thermo_hard,hgo_thermo_hard,hgo_data,"
            "hano_faithful,incde,tinn,static_gno_sequence,static_fno_sequence,static_deeponet_sequence"
        ),
    )
    parser.add_argument("--seeds", type=str, default="20260517,20260518,20260519,20260520,20260521")
    parser.add_argument("--epochs", type=int, default=50)
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--eval-batch-size", type=int, default=4)
    parser.add_argument("--hidden-dim", type=int, default=96)
    parser.add_argument("--message-passing-layers", type=int, default=3)
    parser.add_argument("--learning-rate", type=float, default=1.0e-3)
    parser.add_argument("--grad-clip-norm", type=float, default=10.0)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--fem-audit-loss-weight", type=float, default=0.0)
    parser.add_argument("--fem-audit-energy-weight", type=float, default=0.0)
    parser.add_argument("--fem-audit-solver-weight", type=float, default=0.0)
    parser.add_argument("--fem-audit-every-step", action="store_true")
    parser.add_argument(
        "--fem-audit-step-policy",
        choices=("final", "all", "reversal", "reversal_final"),
        default="all",
    )
    parser.add_argument("--fem-audit-metrics", action="store_true")
    parser.add_argument("--fem-audit-models", type=str, default="hgo_qp_true_j2,hgo_qp_thermo_hard,tinn")
    parser.add_argument("--fem-training-residual-weight", type=float, default=None)
    parser.add_argument("--fem-training-energy-weight", type=float, default=None)
    parser.add_argument("--fem-training-solver-weight", type=float, default=None)
    parser.add_argument("--fem-training-solver-mode", choices=("linearized", "dense_newton"), default="linearized")
    parser.add_argument("--fem-training-newton-damping", type=float, default=1.0)
    parser.add_argument("--fem-training-newton-steps", type=int, default=1)
    parser.add_argument("--fem-training-newton-line-search", action="store_true")
    parser.add_argument("--fem-training-newton-line-search-dampings", default="1.0,0.5,0.25,0.125")
    parser.add_argument("--fem-training-newton-convergence-tol", type=float, default=1.0e-3)
    parser.add_argument("--fem-training-tangent-regularization", type=float, default=1.0e-6)
    parser.add_argument(
        "--fem-training-step-policy",
        choices=("final", "all", "reversal", "reversal_final"),
        default=None,
    )
    parser.add_argument("--fem-training-models", type=str, default=None)
    parser.add_argument(
        "--protocols",
        type=str,
        default="strict,reversal_curriculum,family_upper_bound",
        help="Protocols: strict, reversal_curriculum, family_upper_bound.",
    )
    parser.add_argument(
        "--eval-load-paths",
        type=str,
        default=ALL_PATH_FAMILIES,
        help="Comma-separated path families to evaluate.",
    )
    parser.add_argument(
        "--out-root",
        type=Path,
        default=PROJECT_ROOT / "10_results" / "reports" / "level6_complex_j2_benchmark_suite",
    )
    parser.add_argument(
        "--paper-csv-out",
        type=Path,
        default=PROJECT_ROOT / "11_paper" / "tables" / "level6_complex_j2_benchmark_main_table.csv",
    )
    parser.add_argument(
        "--paper-md-out",
        type=Path,
        default=PROJECT_ROOT / "11_paper" / "tables" / "level6_complex_j2_benchmark_main_table.md",
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--skip-existing",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Skip case/protocol runs whose summary.json already exists and aggregate them into the main table.",
    )
    parser.add_argument(
        "--aggregate-only",
        action="store_true",
        help="Only aggregate existing case/protocol summary.json files into the main table.",
    )
    args = parser.parse_args()

    cases = _resolve_cases(args.data_root, args.cases)
    protocols = _parse_protocols(args.protocols)
    rows = []
    for case in cases:
        for protocol_name, train_paths in protocols.items():
            out_dir = args.out_root / case.name / protocol_name
            command = _baseline_command(case, train_paths, out_dir, args)
            if args.dry_run:
                print(" ".join(command))
                continue
            summary_path = out_dir / "summary.json"
            if args.aggregate_only:
                if summary_path.exists():
                    rows.extend(_summary_rows(case.name, protocol_name, summary_path))
                else:
                    print(f"[missing] {summary_path}")
                continue
            if args.skip_existing and summary_path.exists():
                print(f"[skip] {case.name}/{protocol_name}: {summary_path} exists")
            else:
                out_dir.mkdir(parents=True, exist_ok=True)
                subprocess.run(command, check=True, cwd=PROJECT_ROOT)
            rows.extend(_summary_rows(case.name, protocol_name, summary_path))
    if not args.dry_run:
        summary_csv = args.out_root / "level6_complex_j2_benchmark_summary.csv"
        summary_md = args.out_root / "level6_complex_j2_benchmark_summary.md"
        _write_rows(summary_csv, rows)
        _write_markdown(summary_md, rows)
        _write_rows(args.paper_csv_out, rows)
        _write_markdown(args.paper_md_out, rows)
        print(f"wrote {summary_csv}")
        print(f"wrote {summary_md}")
        print(f"wrote {args.paper_csv_out}")
        print(f"wrote {args.paper_md_out}")


def _resolve_cases(data_root: Path, value: str) -> list[Path]:
    if value.strip().lower() == "all":
        cases = sorted(path for path in data_root.iterdir() if path.is_dir())
    else:
        cases = [data_root / item.strip() for item in value.split(",") if item.strip()]
    missing = [str(case) for case in cases if not case.exists()]
    if missing:
        raise FileNotFoundError(f"missing Level-6 case directories: {missing}")
    return cases


def _parse_protocols(value: str) -> dict[str, str]:
    protocols = {}
    for name in (item.strip() for item in value.split(",") if item.strip()):
        if name not in PROTOCOL_TRAIN_PATHS:
            raise argparse.ArgumentTypeError(
                f"unknown protocol {name!r}; options are {sorted(PROTOCOL_TRAIN_PATHS)}"
            )
        protocols[name] = PROTOCOL_TRAIN_PATHS[name]
    if not protocols:
        raise argparse.ArgumentTypeError("at least one protocol is required")
    return protocols


def _baseline_command(case: Path, train_paths: str, out_dir: Path, args: argparse.Namespace) -> list[str]:
    fem_residual_weight = (
        args.fem_training_residual_weight
        if args.fem_training_residual_weight is not None
        else args.fem_audit_loss_weight
    )
    fem_energy_weight = (
        args.fem_training_energy_weight
        if args.fem_training_energy_weight is not None
        else args.fem_audit_energy_weight
    )
    fem_solver_weight = (
        args.fem_training_solver_weight
        if args.fem_training_solver_weight is not None
        else args.fem_audit_solver_weight
    )
    fem_step_policy = args.fem_training_step_policy
    if fem_step_policy is None:
        fem_step_policy = "all" if args.fem_audit_every_step else args.fem_audit_step_policy
    fem_models = args.fem_training_models if args.fem_training_models is not None else args.fem_audit_models
    command = [
        sys.executable,
        str(BASELINE_SCRIPT),
        "--data-root",
        str(case),
        "--models",
        args.models,
        "--train-load-paths",
        train_paths,
        "--eval-load-paths",
        args.eval_load_paths,
        "--seeds",
        args.seeds,
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
        "--grad-clip-norm",
        str(args.grad_clip_norm),
        "--device",
        args.device,
        "--fem-training-residual-weight",
        str(fem_residual_weight),
        "--fem-training-energy-weight",
        str(fem_energy_weight),
        "--fem-training-solver-weight",
        str(fem_solver_weight),
        "--fem-training-solver-mode",
        args.fem_training_solver_mode,
        "--fem-training-newton-damping",
        str(args.fem_training_newton_damping),
        "--fem-training-newton-steps",
        str(args.fem_training_newton_steps),
        "--fem-training-newton-line-search-dampings",
        str(args.fem_training_newton_line_search_dampings),
        "--fem-training-newton-convergence-tol",
        str(args.fem_training_newton_convergence_tol),
        "--fem-training-tangent-regularization",
        str(args.fem_training_tangent_regularization),
        "--fem-training-models",
        fem_models,
        "--fem-training-step-policy",
        fem_step_policy,
        "--fem-audit-step-policy",
        "all" if args.fem_audit_every_step else args.fem_audit_step_policy,
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
    if args.fem_training_newton_line_search:
        command.append("--fem-training-newton-line-search")
    if args.fem_audit_metrics:
        command.append("--fem-audit-metrics")
    return command


def _summary_rows(case_name: str, protocol_name: str, summary_path: Path) -> list[dict[str, str]]:
    payload = json.loads(summary_path.read_text(encoding="utf-8"))
    rows = []
    for model_name, result in payload["results"].items():
        by_path = result["summary"].get("by_load_path", {})
        row = {
            "Case": case_name,
            "Protocol": protocol_name,
            "Model": model_name,
            "Seeds": str(result["summary"]["num_seeds"]),
        }
        for path_name in REPORT_PATHS:
            path_stats = by_path.get(path_name, {})
            for metric, label in REPORT_METRICS:
                row[f"{path_name} {label}"] = _format_stat(path_stats.get(metric))
        rows.append(row)
    return rows


def _format_stat(stats: dict | None) -> str:
    if not stats:
        return ""
    mean = stats.get("mean")
    std = stats.get("std")
    median = stats.get("median")
    iqr = stats.get("iqr")
    if mean is None:
        return ""
    if median is None:
        return f"{mean:.4g} +- {std:.2g}"
    return f"{mean:.4g} +- {std:.2g}; med {median:.4g}, IQR {iqr:.2g}"


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


if __name__ == "__main__":
    main()
