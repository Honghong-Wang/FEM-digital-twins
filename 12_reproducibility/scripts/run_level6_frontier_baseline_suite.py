from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

import torch


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SUITE = PROJECT_ROOT / "12_reproducibility" / "scripts" / "run_level6_complex_j2_benchmark_suite.py"

DEFAULT_DATA_ROOT = PROJECT_ROOT / "05_data_pipeline" / "processed" / "level6_complex_j2_benchmark_formal_3geom"
DEFAULT_OUT_ROOT = PROJECT_ROOT / "10_results" / "reports" / "level6_frontier_baseline_suite"
DEFAULT_PAPER_TABLE = PROJECT_ROOT / "11_paper" / "tables" / "level6_frontier_baseline_table"

FRONTIER_MODELS = (
    "hano_faithful",
    "incde",
    "tinn",
    "static_gno_sequence",
    "static_fno_sequence",
    "static_deeponet_sequence",
)
REPRESENTATIVE_CASES = (
    "multi_hole_14x11",
    "notch_14x11",
    "curved_hole_14x11",
    "random_holes_14x11",
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Run faithful frontier baselines for the Level-6 J2 path-dependent benchmark. "
            "The suite compares faithful HANO, INCDE-style, TINN-style, and static "
            "GNO/FNO/DeepONet sequence baselines under the same cases, protocols, seeds, "
            "epochs, and path-OOD metrics."
        )
    )
    parser.add_argument("--data-root", type=Path, default=DEFAULT_DATA_ROOT)
    parser.add_argument("--cases", default=",".join(REPRESENTATIVE_CASES))
    parser.add_argument("--models", default=",".join(FRONTIER_MODELS))
    parser.add_argument("--protocols", default="strict,reversal_curriculum,family_upper_bound")
    parser.add_argument(
        "--eval-load-paths",
        default="monotonic,unload_reload,cyclic,nonproportional,random_amplitude,pre_stress",
    )
    parser.add_argument("--seeds", default="20260517,20260518,20260519,20260520,20260521")
    parser.add_argument("--epochs", type=int, default=50)
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--eval-batch-size", type=int, default=4)
    parser.add_argument("--hidden-dim", type=int, default=96)
    parser.add_argument("--message-passing-layers", type=int, default=3)
    parser.add_argument("--learning-rate", type=float, default=1.0e-3)
    parser.add_argument("--grad-clip-norm", type=float, default=10.0)
    parser.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    parser.add_argument("--out-root", type=Path, default=DEFAULT_OUT_ROOT)
    parser.add_argument("--paper-table-stem", type=Path, default=DEFAULT_PAPER_TABLE)
    parser.add_argument(
        "--tinn-residual-weight",
        type=float,
        default=5.0e-5,
        help="FEM residual training weight applied only to the TINN-style thermo baseline.",
    )
    parser.add_argument(
        "--tinn-energy-weight",
        type=float,
        default=5.0e-6,
        help="FEM energy training weight applied only to the TINN-style thermo baseline.",
    )
    parser.add_argument(
        "--tinn-solver-weight",
        type=float,
        default=1.0e-5,
        help="Tangent/Newton solver training weight applied only to the TINN-style thermo baseline.",
    )
    parser.add_argument("--fem-training-solver-mode", choices=("linearized", "dense_newton"), default="linearized")
    parser.add_argument("--fem-training-newton-damping", type=float, default=1.0)
    parser.add_argument("--fem-training-newton-steps", type=int, default=1)
    parser.add_argument("--fem-training-newton-line-search", action="store_true")
    parser.add_argument("--fem-training-newton-line-search-dampings", default="1.0,0.5,0.25,0.125")
    parser.add_argument("--fem-training-newton-convergence-tol", type=float, default=1.0e-3)
    parser.add_argument("--fem-training-tangent-regularization", type=float, default=1.0e-6)
    parser.add_argument("--aggregate-only", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--no-skip-existing", action="store_true")
    args = parser.parse_args()

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
        str(args.tinn_residual_weight),
        "--fem-training-energy-weight",
        str(args.tinn_energy_weight),
        "--fem-training-solver-weight",
        str(args.tinn_solver_weight),
        "--fem-training-models",
        "tinn",
        "--fem-training-step-policy",
        "all",
        "--fem-training-solver-mode",
        args.fem_training_solver_mode,
        "--fem-training-newton-damping",
        str(args.fem_training_newton_damping),
        "--fem-training-newton-steps",
        str(args.fem_training_newton_steps),
        "--fem-training-newton-line-search-dampings",
        args.fem_training_newton_line_search_dampings,
        "--fem-training-newton-convergence-tol",
        str(args.fem_training_newton_convergence_tol),
        "--fem-training-tangent-regularization",
        str(args.fem_training_tangent_regularization),
        "--fem-audit-step-policy",
        "all",
        "--fem-audit-metrics",
        "--out-root",
        str(args.out_root),
        "--paper-csv-out",
        str(args.paper_table_stem.with_suffix(".csv")),
        "--paper-md-out",
        str(args.paper_table_stem.with_suffix(".md")),
    ]
    if args.fem_training_newton_line_search:
        command.append("--fem-training-newton-line-search")
    if args.aggregate_only:
        command.append("--aggregate-only")
    if args.no_skip_existing:
        command.append("--no-skip-existing")
    if args.dry_run:
        command.append("--dry-run")

    subprocess.run(command, cwd=PROJECT_ROOT, check=True)


if __name__ == "__main__":
    main()
