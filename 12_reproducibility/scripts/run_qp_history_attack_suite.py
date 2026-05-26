from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from pathlib import Path

import torch


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RUNNER = PROJECT_ROOT / "12_reproducibility" / "scripts" / "run_j2_path_dependent_baseline_table.py"
DATA_ROOT = PROJECT_ROOT / "05_data_pipeline" / "processed" / "level4_formal_complex_j2_t6_8step_qp_9case"
REPORT_DIR = PROJECT_ROOT / "10_results" / "reports" / "qp_history_attack"

DEFAULT_CASES = (
    "notch_16x12",
    "curved_hole_16x12",
    "multi_hole_16x12",
)
PROTOCOL_TRAIN_LOAD_PATHS = {
    "strict": "monotonic",
    "reversal_curriculum": "monotonic,unload_reload,cyclic",
    "upper_bound": "monotonic,unload_reload,cyclic,nonproportional",
}
EVAL_LOAD_PATHS = "monotonic,unload_reload,cyclic,nonproportional"
PRIMARY_METRICS = (
    "qp_history_relative_l2",
    "qp_history_increment_relative_l2",
    "qp_eq_plastic_strain_relative_l2",
    "qp_plastic_work_relative_l2",
    "qp_reversal_plastic_scalar_increment_relative_l2",
    "qp_reversal_eqp_increment_relative_l2",
    "qp_reversal_plastic_work_increment_relative_l2",
    "qp_reversal_yield_flag_mae",
    "qp_inactive_false_plasticity",
    "j2_qp_active_consistency_residual_relative_rms",
    "fem_residual_relative_rms",
    "fem_energy_relative_error",
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Run the QP-history attack suite: dual-head QP-HGO, current-increment active-QP "
            "losses, yield-aware weighting, and reversal/cyclic curriculum protocols."
        )
    )
    parser.add_argument("--data-root", type=Path, default=DATA_ROOT)
    parser.add_argument("--cases", default=",".join(DEFAULT_CASES), help="Comma-separated case directories.")
    parser.add_argument(
        "--protocols",
        default="strict,reversal_curriculum,upper_bound",
        help=f"Comma-separated protocols from {tuple(PROTOCOL_TRAIN_LOAD_PATHS)}.",
    )
    parser.add_argument(
        "--models",
        default="hgo_qp_memory_attack,hgo_qp_dual_reversal_active,hgo_qp_plastic_corrector,hgo_qp_dual_active",
        help="Comma-separated baseline-table model names.",
    )
    parser.add_argument("--epochs", type=int, default=50)
    parser.add_argument("--seeds", default="20260517,20260518,20260519,20260520,20260521")
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--eval-batch-size", type=int, default=8)
    parser.add_argument("--hidden-dim", type=int, default=96)
    parser.add_argument("--message-passing-layers", type=int, default=3)
    parser.add_argument("--learning-rate", type=float, default=1.0e-3)
    parser.add_argument("--teacher-forcing-ratio", type=float, default=0.8)
    parser.add_argument("--teacher-forcing-final-ratio", type=float, default=0.05)
    parser.add_argument("--teacher-forcing-warmup-epochs", type=int, default=5)
    parser.add_argument("--fem-training-residual-weight", type=float, default=5.0e-5)
    parser.add_argument("--fem-training-energy-weight", type=float, default=5.0e-6)
    parser.add_argument("--fem-training-solver-weight", type=float, default=1.0e-5)
    parser.add_argument("--fem-training-solver-mode", choices=("linearized", "dense_newton"), default="linearized")
    parser.add_argument(
        "--disable-fem-training",
        action="store_true",
        help="Train only with data/history/thermo losses while still reporting FEM audit metrics.",
    )
    parser.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    parser.add_argument("--report-dir", type=Path, default=REPORT_DIR)
    parser.add_argument("--summary-csv", type=Path, default=REPORT_DIR / "qp_history_attack_summary.csv")
    parser.add_argument("--summary-json", type=Path, default=REPORT_DIR / "qp_history_attack_summary.json")
    parser.add_argument("--force", action="store_true", help="Re-run existing case/protocol outputs.")
    parser.add_argument("--aggregate-only", action="store_true")
    args = parser.parse_args()

    cases = _parse_items(args.cases)
    protocols = _parse_items(args.protocols)
    unknown_protocols = sorted(set(protocols).difference(PROTOCOL_TRAIN_LOAD_PATHS))
    if unknown_protocols:
        raise ValueError(f"unknown protocols {unknown_protocols}; options are {tuple(PROTOCOL_TRAIN_LOAD_PATHS)}")
    args.report_dir.mkdir(parents=True, exist_ok=True)

    outputs: list[Path] = []
    for case in cases:
        for protocol in protocols:
            out_json = args.report_dir / f"qp_history_attack_{protocol}_{case}.json"
            outputs.append(out_json)
            if args.aggregate_only:
                continue
            _run_case_protocol(args, case, protocol, out_json)

    summary_rows = _aggregate(outputs)
    _write_summary_csv(args.summary_csv, summary_rows)
    args.summary_json.parent.mkdir(parents=True, exist_ok=True)
    args.summary_json.write_text(json.dumps(summary_rows, indent=2), encoding="utf-8")
    print(f"wrote {args.summary_csv}")
    print(f"wrote {args.summary_json}")


def _run_case_protocol(args: argparse.Namespace, case: str, protocol: str, out_json: Path) -> None:
    case_root = args.data_root / case
    if not case_root.exists():
        raise FileNotFoundError(case_root)
    if out_json.exists() and not args.force:
        print(f"[skip] {case}/{protocol}: {out_json} exists")
        return

    stem = out_json.with_suffix("").name
    command = [
        sys.executable,
        str(RUNNER),
        "--data-root",
        _path_arg(case_root),
        "--models",
        args.models,
        "--train-load-paths",
        PROTOCOL_TRAIN_LOAD_PATHS[protocol],
        "--eval-load-paths",
        EVAL_LOAD_PATHS,
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
        "--teacher-forcing-ratio",
        str(args.teacher_forcing_ratio),
        "--teacher-forcing-final-ratio",
        str(args.teacher_forcing_final_ratio),
        "--teacher-forcing-warmup-epochs",
        str(args.teacher_forcing_warmup_epochs),
        "--fem-audit-metrics",
        "--device",
        args.device,
        "--out",
        _path_arg(out_json),
        "--csv-out",
        _path_arg(args.report_dir / f"{stem}.csv"),
        "--md-out",
        _path_arg(args.report_dir / f"{stem}.md"),
        "--robust-csv-out",
        _path_arg(args.report_dir / f"{stem}_robust.csv"),
        "--robust-md-out",
        _path_arg(args.report_dir / f"{stem}_robust.md"),
        "--per-seed-csv-out",
        _path_arg(args.report_dir / f"{stem}_per_seed.csv"),
        "--per-seed-md-out",
        _path_arg(args.report_dir / f"{stem}_per_seed.md"),
        "--outlier-csv-out",
        _path_arg(args.report_dir / f"{stem}_outliers.csv"),
        "--outlier-md-out",
        _path_arg(args.report_dir / f"{stem}_outliers.md"),
        "--pathwise-csv-out",
        _path_arg(args.report_dir / f"{stem}_by_path.csv"),
        "--pathwise-md-out",
        _path_arg(args.report_dir / f"{stem}_by_path.md"),
    ]
    if not args.disable_fem_training:
        command.extend(
            [
                "--fem-training-residual-weight",
                str(args.fem_training_residual_weight),
                "--fem-training-energy-weight",
                str(args.fem_training_energy_weight),
                "--fem-training-solver-weight",
                str(args.fem_training_solver_weight),
                "--fem-training-solver-mode",
                args.fem_training_solver_mode,
                "--fem-training-step-policy",
                "all",
                "--fem-training-models",
                args.models,
            ]
        )
    print(f"[run] {case}/{protocol}: epochs={args.epochs}, seeds={args.seeds}, models={args.models}")
    subprocess.run(command, cwd=PROJECT_ROOT, check=True)


def _aggregate(paths: list[Path]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for path in paths:
        if not path.exists():
            continue
        with path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        stem = path.stem.replace("qp_history_attack_", "")
        protocol, case = _split_protocol_case(stem)
        for model_name, result in payload.get("results", {}).items():
            summary = result.get("summary", {})
            by_load_path = summary.get("by_load_path", {})
            for load_path, metrics in by_load_path.items():
                for metric in PRIMARY_METRICS:
                    stats = metrics.get(metric)
                    if not stats:
                        continue
                    rows.append(
                        {
                            "Case": case,
                            "Protocol": protocol,
                            "Model": model_name,
                            "Load path": load_path,
                            "Metric": metric,
                            "Mean": _fmt(stats.get("mean")),
                            "Std": _fmt(stats.get("std")),
                            "Median": _fmt(stats.get("median")),
                            "IQR": _fmt(stats.get("iqr")),
                            "N": str(stats.get("n", "")),
                        }
                    )
    return rows


def _split_protocol_case(stem: str) -> tuple[str, str]:
    for protocol in sorted(PROTOCOL_TRAIN_LOAD_PATHS, key=len, reverse=True):
        prefix = f"{protocol}_"
        if stem.startswith(prefix):
            return protocol, stem[len(prefix) :]
    return "unknown", stem


def _write_summary_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _parse_items(value: str) -> tuple[str, ...]:
    items = tuple(item.strip() for item in value.split(",") if item.strip())
    if not items:
        raise ValueError("at least one item is required")
    return items


def _path_arg(path: Path) -> str:
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(resolved)


def _fmt(value: object) -> str:
    if value is None:
        return ""
    return f"{float(value):.6g}"


if __name__ == "__main__":
    main()
