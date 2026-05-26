from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

import torch


PROJECT_ROOT = Path(__file__).resolve().parents[2]
GENERATOR = PROJECT_ROOT / "12_reproducibility" / "scripts" / "generate_complex_j2_path_dataset.py"
SUMMARIZER = PROJECT_ROOT / "12_reproducibility" / "scripts" / "summarize_j2_complex_dataset.py"
SUITE = PROJECT_ROOT / "12_reproducibility" / "scripts" / "run_level6_complex_j2_benchmark_suite.py"

DATA_ROOT = PROJECT_ROOT / "05_data_pipeline" / "processed" / "level6_complex_j2_benchmark_formal"
REPORT_ROOT = PROJECT_ROOT / "10_results" / "reports" / "level6_complex_j2_benchmark_formal"
PAPER_TABLE = PROJECT_ROOT / "11_paper" / "tables" / "level6_complex_j2_benchmark_main_table"

ALL_PATH_FAMILIES = "monotonic,unload_reload,cyclic,nonproportional,random_amplitude,pre_stress"
FULL_GEOMETRIES = "multi_hole,notch,curved_hole,random_holes,crack_tip,stress_concentration"
REPRESENTATIVE_MESH = "14x11"
FULL_T6_MESHES = "14x11,18x14,22x17"
DEFAULT_MODELS = (
    "hgo_qp_true_j2,hgo_qp_thermo_hard,hgo_qp_dual_reversal_active,"
    "hano_faithful,incde,tinn,static_gno_sequence,static_fno_sequence,static_deeponet_sequence"
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Generate, summarize, and run the formal Level-6 path-family x geometry-family "
            "x mesh-family J2 benchmark main table."
        )
    )
    parser.add_argument("--data-root", type=Path, default=DATA_ROOT)
    parser.add_argument("--report-root", type=Path, default=REPORT_ROOT)
    parser.add_argument(
        "--matrix",
        choices=("representative", "full"),
        default="representative",
        help=(
            "representative uses six geometry families at one T6 mesh size for a paper main-table "
            "slice; full uses the complete Level-6 preset with three mesh sizes."
        ),
    )
    parser.add_argument(
        "--stages",
        default="data,summary,table",
        help="Comma-separated stages: data, summary, table.",
    )
    parser.add_argument("--mesh-kinds", default=FULL_GEOMETRIES)
    parser.add_argument("--mesh-sizes", default=None)
    parser.add_argument("--train-samples", type=int, default=128)
    parser.add_argument("--eval-samples", type=int, default=40)
    parser.add_argument("--load-steps", type=int, default=12)
    parser.add_argument("--max-newton-steps", type=int, default=24)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument(
        "--samples-per-shard",
        type=int,
        default=16,
        help="Generate formal train/test NPZ files through resumable sample shards.",
    )
    parser.add_argument("--models", default=DEFAULT_MODELS)
    parser.add_argument(
        "--cases",
        default="all",
        help="Case directories for the table stage, or 'all' to scan generated data root.",
    )
    parser.add_argument("--protocols", default="strict,reversal_curriculum,family_upper_bound")
    parser.add_argument("--seeds", default="20260517,20260518,20260519,20260520,20260521")
    parser.add_argument("--epochs", type=int, default=50)
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--eval-batch-size", type=int, default=4)
    parser.add_argument("--hidden-dim", type=int, default=96)
    parser.add_argument("--message-passing-layers", type=int, default=3)
    parser.add_argument("--learning-rate", type=float, default=1.0e-3)
    parser.add_argument("--grad-clip-norm", type=float, default=10.0)
    parser.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    parser.add_argument("--fem-training-residual-weight", type=float, default=5.0e-5)
    parser.add_argument("--fem-training-energy-weight", type=float, default=5.0e-6)
    parser.add_argument("--fem-training-solver-weight", type=float, default=1.0e-5)
    parser.add_argument("--fem-training-solver-mode", choices=("linearized", "dense_newton"), default="linearized")
    parser.add_argument("--fem-training-newton-damping", type=float, default=1.0)
    parser.add_argument("--fem-training-newton-steps", type=int, default=1)
    parser.add_argument("--fem-training-newton-line-search", action="store_true")
    parser.add_argument("--fem-training-newton-line-search-dampings", default="1.0,0.5,0.25,0.125")
    parser.add_argument("--fem-training-newton-convergence-tol", type=float, default=1.0e-3)
    parser.add_argument("--fem-training-tangent-regularization", type=float, default=1.0e-6)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force-regenerate", action="store_true")
    parser.add_argument("--aggregate-only", action="store_true")
    parser.add_argument("--no-skip-existing", action="store_true")
    args = parser.parse_args()

    stages = _parse_stages(args.stages)
    if "data" in stages:
        _run(_data_command(args), args.dry_run)
    if "summary" in stages:
        _run(_summary_command(args), args.dry_run)
    if "table" in stages:
        _run(_table_command(args), args.dry_run)


def _data_command(args: argparse.Namespace) -> list[str]:
    mesh_sizes = args.mesh_sizes
    if mesh_sizes is None:
        mesh_sizes = FULL_T6_MESHES if args.matrix == "full" else REPRESENTATIVE_MESH
    command = [
        sys.executable,
        str(GENERATOR),
        "--out-dir",
        str(args.data_root),
        "--mesh-kinds",
        args.mesh_kinds,
        "--mesh-sizes",
        mesh_sizes,
        "--train-samples",
        str(args.train_samples),
        "--eval-samples",
        str(args.eval_samples),
        "--load-steps",
        str(args.load_steps),
        "--max-newton-steps",
        str(args.max_newton_steps),
        "--load-paths",
        ALL_PATH_FAMILIES,
        "--splits",
        "train,test",
        "--element-order",
        "quadratic",
        "--quadrature-order",
        "2",
        "--solver-backend",
        "auto",
        "--workers",
        str(args.workers),
        "--samples-per-shard",
        str(args.samples_per_shard),
        "--no-export-tangent-sequence",
        "--no-export-final-tangent",
    ]
    if args.force_regenerate:
        command.append("--force-regenerate")
    return command


def _summary_command(args: argparse.Namespace) -> list[str]:
    return [
        sys.executable,
        str(SUMMARIZER),
        "--data-root",
        str(args.data_root),
        "--csv-out",
        str(args.report_root / "level6_formal_dataset_summary.csv"),
        "--md-out",
        str(args.report_root / "level6_formal_dataset_summary.md"),
        "--case-csv-out",
        str(args.report_root / "level6_formal_dataset_case_summary.csv"),
        "--case-md-out",
        str(args.report_root / "level6_formal_dataset_case_summary.md"),
        "--title",
        "Level-6 Formal Benchmark Matrix Summary",
    ]


def _table_command(args: argparse.Namespace) -> list[str]:
    command = [
        sys.executable,
        str(SUITE),
        "--data-root",
        str(args.data_root),
        "--cases",
        args.cases,
        "--models",
        args.models,
        "--protocols",
        args.protocols,
        "--eval-load-paths",
        ALL_PATH_FAMILIES,
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
        str(args.fem_training_residual_weight),
        "--fem-training-energy-weight",
        str(args.fem_training_energy_weight),
        "--fem-training-solver-weight",
        str(args.fem_training_solver_weight),
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
        "--fem-training-step-policy",
        "all",
        "--fem-audit-step-policy",
        "all",
        "--fem-audit-metrics",
        "--out-root",
        str(args.report_root / "main_table_runs"),
        "--paper-csv-out",
        str(PAPER_TABLE.with_suffix(".csv")),
        "--paper-md-out",
        str(PAPER_TABLE.with_suffix(".md")),
    ]
    if args.fem_training_newton_line_search:
        command.append("--fem-training-newton-line-search")
    if args.aggregate_only:
        command.append("--aggregate-only")
    if args.no_skip_existing:
        command.append("--no-skip-existing")
    return command


def _parse_stages(value: str) -> tuple[str, ...]:
    stages = tuple(item.strip() for item in value.split(",") if item.strip())
    allowed = {"data", "summary", "table"}
    unknown = sorted(set(stages).difference(allowed))
    if unknown:
        raise ValueError(f"unknown stages {unknown}; options are {sorted(allowed)}")
    if not stages:
        raise ValueError("at least one stage is required")
    return stages


def _run(command: list[str], dry_run: bool) -> None:
    if dry_run:
        print(" ".join(command))
        return
    subprocess.run(command, cwd=PROJECT_ROOT, check=True)


if __name__ == "__main__":
    main()
