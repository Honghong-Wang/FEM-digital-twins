from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

import torch
from torch import nn
from torch.utils.data import DataLoader

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pcgno_dt.data.datasets import PathOperatorTensorDataset
from pcgno_dt.data.fem import load_fem_path_snapshots
from pcgno_dt.evaluation.path_history import (
    evaluate_j2_path_history_consistency,
    evaluate_qp_reversal_memory_errors,
    evaluate_reversal_memory_errors,
)
from pcgno_dt.models.history_gno import HistoryGraphOperator, HistoryGraphOperatorConfig
from pcgno_dt.models.path_frontier import (
    ControlledPathOperator,
    ControlledPathOperatorConfig,
    FaithfulHANOOperator,
    FaithfulHANOOperatorConfig,
    NeuralCDEPathOperator,
    NeuralCDEPathOperatorConfig,
    WindowedHistoryOperator,
    WindowedHistoryOperatorConfig,
)
from pcgno_dt.numerics.baselines import (
    DeepONetBaseline,
    FNOBaseline,
    MeshGraphOperatorBaseline,
    MeshSampledFNOBaseline,
)
from pcgno_dt.numerics.j2plasticity2d import J2_LOAD_PATHS
from pcgno_dt.physics.j2_fem_audit import j2_fem_audit_loss, j2_fem_training_loss
from pcgno_dt.training.path_losses import PathLossWeights, history_graph_operator_loss


SUPPORTED_LOAD_PATHS = J2_LOAD_PATHS
DEFAULT_MODELS = (
    "hgo_thermo",
    "hgo_thermo_hard",
    "hgo_qp_thermo_hard",
    "hgo_data",
    "hano_faithful",
    "hano_style",
    "incde",
    "tinn",
    "static_gno_sequence",
    "static_fno_sequence",
    "static_deeponet_sequence",
)
SUPPORTED_MODELS = (
    *DEFAULT_MODELS,
    "hano",
    "hgo_qp_true_j2",
    "hgo_qp_thermo_hard_qpaware",
    "hgo_qp_thermo_hard_qpaware_active",
    "hgo_qp_dual_active",
    "hgo_qp_dual_sparse_active",
    "hgo_qp_dual_reversal_active",
    "hgo_qp_memory_attack",
    "hgo_qp_plastic_corrector",
)
DEFAULT_FEM_TRAINING_MODELS = (
    "hgo_qp_true_j2",
    "hgo_qp_thermo_hard",
    "hgo_qp_thermo_hard_qpaware",
    "hgo_qp_thermo_hard_qpaware_active",
    "hgo_qp_plastic_corrector",
    "hgo_qp_dual_active",
    "hgo_qp_dual_sparse_active",
    "hgo_qp_dual_reversal_active",
    "hgo_qp_memory_attack",
    "hgo_thermo_hard",
    "tinn",
)
HISTORY_CHANNELS = {
    "eq_plastic_strain": 0,
    "plastic_work": 1,
    "plastic_multiplier_increment": 2,
    "yield_flag": 3,
    "von_mises": 4,
}
TABLE_METRICS = (
    ("displacement_relative_l2", "Cyclic disp. rel. L2"),
    ("history_relative_l2", "Cyclic history rel. L2"),
    ("history_increment_relative_l2", "History-increment rel. L2"),
    ("qp_history_relative_l2", "QP history rel. L2"),
    ("qp_history_increment_relative_l2", "QP history-inc. rel. L2"),
    ("qp_eq_plastic_strain_relative_l2", "QP eqp rel. L2"),
    ("qp_plastic_work_relative_l2", "QP plastic-work rel. L2"),
    ("qp_von_mises_relative_l2", "QP von-Mises rel. L2"),
    ("qp_reversal_plastic_scalar_increment_relative_l2", "QP reversal scalar-inc. rel. L2"),
    ("qp_reversal_eqp_increment_relative_l2", "QP reversal eqp-inc. rel. L2"),
    ("qp_reversal_plastic_work_increment_relative_l2", "QP reversal work-inc. rel. L2"),
    ("qp_reversal_yield_flag_mae", "QP reversal yield MAE"),
    ("qp_inactive_false_plasticity", "QP inactive false plasticity"),
    ("j2_qp_consistency_residual_relative_rms", "True-J2 consistency rel. RMS"),
    ("j2_qp_active_consistency_residual_relative_rms", "True-J2 active consistency rel. RMS"),
    ("j2_qp_plastic_multiplier_negative_violation", "True-J2 negative dgamma"),
    ("j2_qp_active_fraction", "True-J2 active QP frac."),
    ("eq_plastic_strain_increment_relative_l2", "Eqp increment rel. L2"),
    ("plastic_work_increment_relative_l2", "Plastic-work inc. rel. L2"),
    ("reversal_history_increment_relative_l2", "Reversal hist-inc. rel. L2"),
    ("reversal_yield_flag_mae", "Reversal yield-flag MAE"),
    ("predicted_yield_surface_relative_rms", "Yield-surface RMS"),
    ("predicted_plastic_work_lower_bound_absolute_violation", "Plastic-work violation abs."),
    (
        "predicted_plastic_work_lower_bound_target_normalized_violation",
        "Plastic-work violation target-norm.",
    ),
    ("predicted_plastic_work_lower_bound_relative_violation", "Plastic-work violation pred-norm."),
    ("hano_strain_relative_l2", "HANO strain rel. L2"),
    ("hano_stress_relative_l2", "HANO stress rel. L2"),
    ("fem_residual_relative_rms", "FEM residual rel. RMS"),
    ("fem_energy_relative_error", "FEM energy rel. err."),
    ("fem_solver_linearized_residual_relative_rms", "FEM tangent-solver rel. RMS"),
    ("fem_newton_initial_residual_relative_rms", "Newton initial residual rel. RMS"),
    ("fem_newton_final_residual_relative_rms", "Newton final residual rel. RMS"),
    ("fem_newton_residual_ratio", "Newton residual ratio"),
    ("fem_newton_residual_decrease_fraction", "Newton residual decrease frac."),
    ("fem_newton_step_residual_decrease_fraction", "Newton step decrease frac."),
    ("fem_newton_step1_residual_ratio", "Newton step 1 residual ratio"),
    ("fem_newton_step2_residual_ratio", "Newton step 2 residual ratio"),
    ("fem_newton_step3_residual_ratio", "Newton step 3 residual ratio"),
    ("fem_newton_step1_residual_decrease_fraction", "Newton step 1 decrease frac."),
    ("fem_newton_step2_residual_decrease_fraction", "Newton step 2 decrease frac."),
    ("fem_newton_step3_residual_decrease_fraction", "Newton step 3 decrease frac."),
    ("fem_newton_correction_relative_norm", "Newton correction rel. norm"),
    ("fem_newton_accepted_damping", "Newton accepted damping"),
    ("fem_newton_convergence_rate", "Newton convergence rate"),
    ("fem_newton_failure_rate", "Newton failure rate"),
)
MODEL_LABELS = {
    "hgo_thermo": "HistoryGNO thermo-aware",
    "hgo_thermo_hard": "Thermo-hard HistoryGNO",
    "hgo_qp_thermo_hard": "QP-thermo-hard HistoryGNO",
    "hgo_qp_thermo_hard_qpaware": "QP-aware thermo-hard HistoryGNO",
    "hgo_qp_thermo_hard_qpaware_active": "QP-aware active-zone thermo-hard HistoryGNO",
    "hgo_qp_dual_active": "Dual-head active-QP HistoryGNO",
    "hgo_qp_dual_sparse_active": "Dual-head sparse-active QP HistoryGNO",
    "hgo_qp_dual_reversal_active": "Dual-head reversal-active QP-HistoryGNO",
    "hgo_qp_memory_attack": "QP-memory attack HistoryGNO",
    "hgo_qp_true_j2": "True differentiable J2 QP-HistoryGNO",
    "hgo_qp_plastic_corrector": "QP plastic-memory corrector HistoryGNO",
    "hgo_data": "HistoryGNO data-only",
    "hano_faithful": "Faithful HANO strain-stress spectral-window NO",
    "hano_style": "HANO-style window NO",
    "hano": "HANO-style window NO (legacy)",
    "incde": "INCDE-style Euler neural CDE",
    "tinn": "TINN-style thermo-projected neural CDE",
    "static_gno_sequence": "Non-recurrent GNO sequence",
    "static_fno_sequence": "Static FNO sequence",
    "static_deeponet_sequence": "Static DeepONet sequence",
}


class StaticSequenceOperator(nn.Module):
    """Non-recurrent sequence wrapper around a static neural operator baseline.

    It predicts each displacement step independently from coordinates, parameters, global load
    summary, and step fraction. A small element-level decoder predicts material history without
    seeing previous history, making it a useful foil for recurrent stateful operators.
    """

    def __init__(
        self,
        base: nn.Module,
        augmented_param_dim: int,
        spatial_dim: int,
        num_fields: int,
        history_dim: int,
        hidden_dim: int = 96,
        enforce_history_channels: bool = True,
    ) -> None:
        super().__init__()
        self.base = base
        self.history_dim = history_dim
        self.num_fields = num_fields
        self.enforce_history_channels = enforce_history_channels
        self.history_decoder = nn.Sequential(
            nn.Linear(spatial_dim + 2 * num_fields + augmented_param_dim, hidden_dim),
            nn.SiLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.SiLU(),
            nn.Linear(hidden_dim, history_dim),
        )

    def forward(
        self,
        coords: torch.Tensor,
        params: torch.Tensor,
        forcing_sequence: torch.Tensor,
        initial_history: torch.Tensor | None = None,
        connectivity: torch.Tensor | None = None,
        teacher_history: torch.Tensor | None = None,
        teacher_forcing_ratio: float = 0.0,
    ) -> dict[str, torch.Tensor]:
        del initial_history, teacher_history, teacher_forcing_ratio
        if forcing_sequence.ndim != 4:
            raise ValueError("forcing_sequence must have shape [batch, steps, nodes, fields]")
        batch_size, n_steps, _, _ = forcing_sequence.shape
        connectivity_local = _prepare_connectivity(connectivity, coords.device)
        displacement_steps = []
        history_steps = []
        logvar_steps = []
        for step in range(n_steps):
            forcing = forcing_sequence[:, step]
            augmented = _augment_params(params, forcing, step, n_steps)
            displacement = self.base(coords, augmented)["mean"]
            history = self._decode_history(coords, augmented, forcing, displacement, connectivity_local)
            displacement_steps.append(displacement)
            history_steps.append(history)
            logvar_steps.append(torch.zeros_like(displacement))
        return {
            "mean_sequence": torch.stack(displacement_steps, dim=1),
            "history_sequence": torch.stack(history_steps, dim=1),
            "logvar_sequence": torch.stack(logvar_steps, dim=1),
            "mean": displacement_steps[-1],
            "history": history_steps[-1],
            "logvar": logvar_steps[-1],
        }

    def _decode_history(
        self,
        coords: torch.Tensor,
        params_augmented: torch.Tensor,
        forcing: torch.Tensor,
        displacement: torch.Tensor,
        connectivity: torch.Tensor | None,
    ) -> torch.Tensor:
        element_coords = _nodes_to_elements(coords, connectivity)
        element_forcing = _nodes_to_elements(forcing, connectivity)
        element_displacement = _nodes_to_elements(displacement, connectivity)
        context = params_augmented.unsqueeze(1).expand(-1, element_coords.shape[1], -1)
        raw = self.history_decoder(
            torch.cat([element_coords, element_forcing, element_displacement, context], dim=-1)
        )
        raw = torch.nan_to_num(raw, nan=0.0, posinf=30.0, neginf=-30.0).clamp(-30.0, 30.0)
        if not self.enforce_history_channels or self.history_dim < 5:
            return raw
        history = raw.clone()
        history[..., 0] = torch.nn.functional.softplus(raw[..., 0])
        history[..., 1] = torch.nn.functional.softplus(raw[..., 1])
        history[..., 2] = torch.nn.functional.softplus(raw[..., 2])
        history[..., 3] = torch.sigmoid(raw[..., 3])
        history[..., 4] = torch.nn.functional.softplus(raw[..., 4])
        return history


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compare recurrent and static sequence baselines on a J2 path-OOD split."
    )
    parser.add_argument(
        "--data-root",
        type=Path,
        default=PROJECT_ROOT / "05_data_pipeline" / "processed" / "j2_complex_geometry_shared_path_fem2d",
    )
    parser.add_argument("--models", type=_parse_models, default=",".join(DEFAULT_MODELS))
    parser.add_argument("--train-load-paths", type=_parse_load_paths, default="monotonic")
    parser.add_argument(
        "--eval-load-paths",
        type=_parse_load_paths,
        default=",".join(SUPPORTED_LOAD_PATHS),
    )
    parser.add_argument(
        "--seeds",
        type=str,
        default=(
            "20260517,20260518,20260519,20260520,20260521,"
            "20260522,20260523,20260524,20260525,20260526"
        ),
    )
    parser.add_argument("--epochs", type=int, default=50)
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--eval-batch-size", type=int, default=4)
    parser.add_argument("--learning-rate", type=float, default=1.0e-3)
    parser.add_argument(
        "--grad-clip-norm",
        type=float,
        default=10.0,
        help="Global gradient norm clipping for multi-baseline training stability; set <=0 to disable.",
    )
    parser.add_argument("--hidden-dim", type=int, default=96)
    parser.add_argument("--message-passing-layers", type=int, default=3)
    parser.add_argument("--teacher-forcing-ratio", type=float, default=0.5)
    parser.add_argument(
        "--teacher-forcing-final-ratio",
        type=float,
        default=None,
        help="Optional final teacher-forcing ratio for linear rollout curriculum.",
    )
    parser.add_argument(
        "--teacher-forcing-warmup-epochs",
        type=int,
        default=0,
        help="Keep the initial teacher-forcing ratio for this many epochs before annealing.",
    )
    parser.add_argument(
        "--fem-audit-loss-weight",
        type=float,
        default=0.0,
        help="Legacy alias for --fem-training-residual-weight.",
    )
    parser.add_argument(
        "--fem-audit-energy-weight",
        type=float,
        default=0.0,
        help="Legacy alias for --fem-training-energy-weight.",
    )
    parser.add_argument(
        "--fem-audit-solver-weight",
        type=float,
        default=0.0,
        help="Legacy alias for --fem-training-solver-weight.",
    )
    parser.add_argument(
        "--fem-audit-every-step",
        action="store_true",
        help="Apply FEM audit loss on every rollout step instead of the final step only.",
    )
    parser.add_argument(
        "--fem-audit-step-policy",
        choices=("final", "all", "reversal", "reversal_final"),
        default="final",
        help=(
            "Step selection for matrix-free FEM audit. 'reversal_final' audits path "
            "turning points plus the final step, which is cheaper than all-step cyclic audit."
        ),
    )
    parser.add_argument(
        "--fem-audit-models",
        type=str,
        default="hgo_thermo_hard,tinn",
        help="Comma-separated models that receive FEM audit training loss.",
    )
    parser.add_argument(
        "--fem-training-residual-weight",
        type=float,
        default=None,
        help="Matrix-free J2 FEM residual loss weight used inside the training loop.",
    )
    parser.add_argument(
        "--fem-training-energy-weight",
        type=float,
        default=None,
        help="Matrix-free J2 total-potential-energy loss weight used inside the training loop.",
    )
    parser.add_argument(
        "--fem-training-solver-weight",
        type=float,
        default=None,
        help=(
            "Weight for the tangent-linearized solver-in-loop residual "
            "R(u_pred)+K_tangent(u_pred)(u_target-u_pred)."
        ),
    )
    parser.add_argument(
        "--fem-training-solver-mode",
        choices=("linearized", "dense_newton"),
        default="linearized",
        help="Use dense_newton to assemble K_tangent and backpropagate one damped Newton solve.",
    )
    parser.add_argument("--fem-training-newton-damping", type=float, default=1.0)
    parser.add_argument(
        "--fem-training-newton-steps",
        type=int,
        default=1,
        help="Number of damped dense Newton updates used by solver-in-loop training.",
    )
    parser.add_argument(
        "--fem-training-newton-line-search",
        action="store_true",
        help="Select a per-sample damping from --fem-training-newton-line-search-dampings by residual decrease.",
    )
    parser.add_argument(
        "--fem-training-newton-line-search-dampings",
        default="1.0,0.5,0.25,0.125",
        help="Comma-separated damping candidates for dense Newton line search.",
    )
    parser.add_argument("--fem-training-newton-convergence-tol", type=float, default=1.0e-3)
    parser.add_argument("--fem-training-tangent-regularization", type=float, default=1.0e-6)
    parser.add_argument(
        "--fem-training-step-policy",
        choices=("final", "all", "reversal", "reversal_final"),
        default=None,
        help="Training-step policy for FEM residual/energy loss. New training flags default to all steps.",
    )
    parser.add_argument(
        "--fem-training-models",
        type=str,
        default=None,
        help=(
            "Comma-separated models that receive FEM residual/energy training loss. "
            "Defaults to the legacy fem-audit-models list when omitted."
        ),
    )
    parser.add_argument(
        "--fem-audit-metrics",
        action="store_true",
        help="Report matrix-free J2 FEM residual/energy audit metrics during evaluation.",
    )
    parser.add_argument("--device", default="cpu")
    parser.add_argument(
        "--out",
        type=Path,
        default=PROJECT_ROOT / "10_results" / "reports" / "j2_path_dependent_baseline_table.json",
    )
    parser.add_argument(
        "--csv-out",
        type=Path,
        default=PROJECT_ROOT / "11_paper" / "tables" / "j2_path_dependent_baseline_table.csv",
    )
    parser.add_argument(
        "--md-out",
        type=Path,
        default=PROJECT_ROOT / "11_paper" / "tables" / "j2_path_dependent_baseline_table.md",
    )
    parser.add_argument(
        "--robust-csv-out",
        type=Path,
        default=PROJECT_ROOT / "11_paper" / "tables" / "j2_path_dependent_baseline_table_robust_stats.csv",
    )
    parser.add_argument(
        "--robust-md-out",
        type=Path,
        default=PROJECT_ROOT / "11_paper" / "tables" / "j2_path_dependent_baseline_table_robust_stats.md",
    )
    parser.add_argument(
        "--per-seed-csv-out",
        type=Path,
        default=PROJECT_ROOT / "11_paper" / "tables" / "j2_path_dependent_baseline_table_per_seed.csv",
    )
    parser.add_argument(
        "--per-seed-md-out",
        type=Path,
        default=PROJECT_ROOT / "11_paper" / "tables" / "j2_path_dependent_baseline_table_per_seed.md",
    )
    parser.add_argument(
        "--outlier-csv-out",
        type=Path,
        default=PROJECT_ROOT / "11_paper" / "tables" / "j2_path_dependent_baseline_table_outliers.csv",
    )
    parser.add_argument(
        "--outlier-md-out",
        type=Path,
        default=PROJECT_ROOT / "11_paper" / "tables" / "j2_path_dependent_baseline_table_outliers.md",
    )
    parser.add_argument(
        "--pathwise-csv-out",
        type=Path,
        default=PROJECT_ROOT / "11_paper" / "tables" / "j2_path_dependent_baseline_table_by_path.csv",
    )
    parser.add_argument(
        "--pathwise-md-out",
        type=Path,
        default=PROJECT_ROOT / "11_paper" / "tables" / "j2_path_dependent_baseline_table_by_path.md",
    )
    args = parser.parse_args()

    seeds = _parse_int_list(args.seeds)
    train_load_paths = _ensure_tuple(args.train_load_paths)
    eval_load_paths = _ensure_tuple(args.eval_load_paths)
    if "monotonic" not in eval_load_paths:
        eval_load_paths = ("monotonic", *eval_load_paths)
    models = _ensure_tuple(args.models)
    fem_training = _fem_training_config(args)

    results: dict[str, dict] = {}
    for model_name in models:
        seed_results = []
        for seed in seeds:
            print(f"running {model_name} seed={seed}")
            seed_results.append(_run_model_seed(model_name, seed, train_load_paths, eval_load_paths, args))
        results[model_name] = {
            "seeds": seed_results,
            "summary": _summarize_seed_results(seed_results),
        }
        print(json.dumps({model_name: results[model_name]["summary"]["cyclic_primary"]}, indent=2))

    payload = {
        "metadata": {
            "data_root": str(args.data_root),
            "models": list(models),
            "seeds": list(seeds),
            "train_load_paths": list(train_load_paths),
            "eval_load_paths": list(eval_load_paths),
            "epochs": args.epochs,
            "batch_size": args.batch_size,
            "eval_batch_size": args.eval_batch_size,
            "learning_rate": args.learning_rate,
            "grad_clip_norm": args.grad_clip_norm,
            "fem_training": {
                "residual_weight": fem_training["residual_weight"],
                "energy_weight": fem_training["energy_weight"],
                "solver_weight": fem_training["solver_weight"],
                "solver_mode": fem_training["solver_mode"],
                "step_policy": fem_training["step_policy"],
                "models": list(fem_training["models"]),
            },
        },
        "results": results,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    _write_table_csv(args.csv_out, payload)
    _write_table_markdown(args.md_out, payload)
    _write_robust_stats_csv(args.robust_csv_out, payload)
    _write_robust_stats_markdown(args.robust_md_out, payload)
    _write_per_seed_detail_csv(args.per_seed_csv_out, payload)
    _write_per_seed_detail_markdown(args.per_seed_md_out, payload)
    _write_outlier_diagnostics_csv(args.outlier_csv_out, payload)
    _write_outlier_diagnostics_markdown(args.outlier_md_out, payload)
    _write_pathwise_csv(args.pathwise_csv_out, payload)
    _write_pathwise_markdown(args.pathwise_md_out, payload)
    print(f"wrote {args.out}")
    print(f"wrote {args.csv_out}")
    print(f"wrote {args.md_out}")
    print(f"wrote {args.robust_csv_out}")
    print(f"wrote {args.robust_md_out}")
    print(f"wrote {args.per_seed_csv_out}")
    print(f"wrote {args.per_seed_md_out}")
    print(f"wrote {args.outlier_csv_out}")
    print(f"wrote {args.outlier_md_out}")
    print(f"wrote {args.pathwise_csv_out}")
    print(f"wrote {args.pathwise_md_out}")


def _run_model_seed(
    model_name: str,
    seed: int,
    train_load_paths: tuple[str, ...],
    eval_load_paths: tuple[str, ...],
    args: argparse.Namespace,
) -> dict:
    torch.manual_seed(seed)
    train = _load_training_splits(args.data_root, train_load_paths, args.device)
    train_connectivity = _connectivity_tensor(train, args.device)
    model = _make_model(model_name, train, args).to(args.device)
    train_loss_history = _train(model_name, model, train, train_connectivity, seed, args)
    evaluations = {}
    for load_path in eval_load_paths:
        loaded = _load_split(args.data_root, load_path, "test", args.device)
        evaluations[load_path] = _evaluate(model, loaded, _connectivity_tensor(loaded, args.device), args)
    return {
        "seed": seed,
        "train_final_loss": train_loss_history[-1],
        "train_loss_history": train_loss_history,
        "evaluations": evaluations,
    }


def _make_model(model_name: str, loaded: dict, args: argparse.Namespace) -> nn.Module:
    tensors = loaded["tensors"]
    num_parameters = int(tensors["params"].shape[-1])
    num_fields = int(tensors["fields_sequence"].shape[-1])
    spatial_dim = int(tensors["coords"].shape[-1])
    history_dim = int(tensors["material_history_sequence"].shape[-1])
    if model_name in {
        "hgo_thermo",
        "hgo_thermo_hard",
        "hgo_qp_thermo_hard",
        "hgo_qp_thermo_hard_qpaware",
        "hgo_qp_thermo_hard_qpaware_active",
        "hgo_qp_dual_active",
        "hgo_qp_dual_sparse_active",
        "hgo_qp_dual_reversal_active",
        "hgo_qp_memory_attack",
        "hgo_qp_plastic_corrector",
        "hgo_qp_true_j2",
        "hgo_data",
    }:
        predict_qp_history = model_name in {
            "hgo_qp_thermo_hard",
            "hgo_qp_thermo_hard_qpaware",
            "hgo_qp_thermo_hard_qpaware_active",
            "hgo_qp_dual_active",
            "hgo_qp_dual_sparse_active",
            "hgo_qp_dual_reversal_active",
            "hgo_qp_memory_attack",
            "hgo_qp_plastic_corrector",
            "hgo_qp_true_j2",
        }
        num_quadrature_points = (
            int(tensors["material_history_qp_sequence"].shape[-2])
            if predict_qp_history and "material_history_qp_sequence" in tensors
            else 1
        )
        return HistoryGraphOperator(
            HistoryGraphOperatorConfig(
                num_parameters=num_parameters,
                num_fields=num_fields,
                spatial_dim=spatial_dim,
                history_dim=history_dim,
                hidden_dim=args.hidden_dim,
                num_message_passing_layers=args.message_passing_layers,
                thermo_hard_j2_return=model_name
                in {
                    "hgo_thermo_hard",
                    "hgo_qp_thermo_hard",
                    "hgo_qp_thermo_hard_qpaware",
                    "hgo_qp_thermo_hard_qpaware_active",
                    "hgo_qp_dual_active",
                    "hgo_qp_dual_sparse_active",
                    "hgo_qp_dual_reversal_active",
                    "hgo_qp_memory_attack",
                    "hgo_qp_plastic_corrector",
                    "hgo_qp_true_j2",
                },
                predict_qp_history=predict_qp_history,
                num_quadrature_points=num_quadrature_points,
                qp_feature_conditioning=model_name
                in {
                    "hgo_qp_thermo_hard_qpaware",
                    "hgo_qp_thermo_hard_qpaware_active",
                    "hgo_qp_dual_active",
                    "hgo_qp_dual_sparse_active",
                    "hgo_qp_dual_reversal_active",
                    "hgo_qp_memory_attack",
                    "hgo_qp_plastic_corrector",
                },
                qp_dual_history_head=model_name
                in {
                    "hgo_qp_dual_active",
                    "hgo_qp_dual_sparse_active",
                    "hgo_qp_dual_reversal_active",
                    "hgo_qp_memory_attack",
                },
                qp_dual_sparse_initialization=model_name in {"hgo_qp_dual_sparse_active", "hgo_qp_memory_attack"},
                qp_plastic_memory_corrector=model_name
                in {
                    "hgo_qp_plastic_corrector",
                    "hgo_qp_dual_active",
                    "hgo_qp_dual_sparse_active",
                    "hgo_qp_dual_reversal_active",
                    "hgo_qp_memory_attack",
                },
                qp_plastic_increment_scale=1.0e-3 if model_name == "hgo_qp_memory_attack" else 1.0e-4,
                qp_plastic_gate_floor=5.0e-1
                if model_name == "hgo_qp_memory_attack"
                else 0.0
                if model_name
                in {
                    "hgo_qp_dual_active",
                    "hgo_qp_dual_sparse_active",
                    "hgo_qp_dual_reversal_active",
                }
                else 1.0e-2,
                qp_plastic_gate_power=2.5
                if model_name == "hgo_qp_dual_reversal_active"
                else 2.0
                if model_name in {"hgo_qp_dual_active", "hgo_qp_dual_sparse_active"}
                else 1.0,
                true_differentiable_j2_return=model_name == "hgo_qp_true_j2",
            )
        )
    if model_name == "hano_faithful":
        return FaithfulHANOOperator(
            FaithfulHANOOperatorConfig(
                num_parameters=num_parameters,
                num_fields=num_fields,
                spatial_dim=spatial_dim,
                history_dim=history_dim,
                hidden_dim=args.hidden_dim,
            )
        )
    if model_name in {"hano_style", "hano"}:
        return WindowedHistoryOperator(
            WindowedHistoryOperatorConfig(
                num_parameters=num_parameters,
                num_fields=num_fields,
                spatial_dim=spatial_dim,
                history_dim=history_dim,
                hidden_dim=args.hidden_dim,
            )
        )
    if model_name in {"incde", "tinn"}:
        return NeuralCDEPathOperator(
            NeuralCDEPathOperatorConfig(
                num_parameters=num_parameters,
                num_fields=num_fields,
                spatial_dim=spatial_dim,
                history_dim=history_dim,
                hidden_dim=args.hidden_dim,
                thermo_hard_j2_return=model_name == "tinn",
            )
        )

    augmented_param_dim = num_parameters + num_fields + 1
    if model_name == "static_gno_sequence":
        base = MeshGraphOperatorBaseline(
            augmented_param_dim,
            num_fields=num_fields,
            spatial_dim=spatial_dim,
            hidden_dim=args.hidden_dim,
            num_layers=args.message_passing_layers,
        )
    elif model_name == "static_deeponet_sequence":
        base = DeepONetBaseline(augmented_param_dim, num_fields=num_fields, spatial_dim=spatial_dim)
    elif model_name == "static_fno_sequence":
        grid_shape = _grid_shape_from_loaded(loaded)
        if tensors["coords"].shape[1] == grid_shape[0] * grid_shape[1]:
            base = FNOBaseline(
                augmented_param_dim,
                num_fields=num_fields,
                spatial_dim=spatial_dim,
                grid_shape=grid_shape,
            )
        else:
            base = MeshSampledFNOBaseline(
                augmented_param_dim,
                num_fields=num_fields,
                spatial_dim=spatial_dim,
                grid_shape=grid_shape,
            )
    else:
        raise ValueError(f"unknown model: {model_name}")
    return StaticSequenceOperator(
        base,
        augmented_param_dim=augmented_param_dim,
        spatial_dim=spatial_dim,
        num_fields=num_fields,
        history_dim=history_dim,
        hidden_dim=args.hidden_dim,
    )


def _fem_training_config(args: argparse.Namespace) -> dict[str, object]:
    uses_new_flags = (
        args.fem_training_residual_weight is not None
        or args.fem_training_energy_weight is not None
        or args.fem_training_solver_weight is not None
        or args.fem_training_step_policy is not None
        or args.fem_training_models is not None
    )
    residual_weight = (
        args.fem_training_residual_weight
        if args.fem_training_residual_weight is not None
        else args.fem_audit_loss_weight
    )
    energy_weight = (
        args.fem_training_energy_weight
        if args.fem_training_energy_weight is not None
        else args.fem_audit_energy_weight
    )
    solver_weight = (
        args.fem_training_solver_weight
        if args.fem_training_solver_weight is not None
        else args.fem_audit_solver_weight
    )
    if args.fem_training_step_policy is not None:
        step_policy = args.fem_training_step_policy
    elif uses_new_flags:
        step_policy = "all"
    elif args.fem_audit_every_step:
        step_policy = "all"
    else:
        step_policy = args.fem_audit_step_policy
    if args.fem_training_models is not None:
        models = _ensure_tuple(args.fem_training_models)
    elif uses_new_flags:
        models = DEFAULT_FEM_TRAINING_MODELS
    else:
        models = _ensure_tuple(args.fem_audit_models)
    return {
        "residual_weight": float(residual_weight),
        "energy_weight": float(energy_weight),
        "solver_weight": float(solver_weight),
        "solver_mode": str(args.fem_training_solver_mode),
        "newton_damping": float(args.fem_training_newton_damping),
        "newton_steps": int(args.fem_training_newton_steps),
        "newton_line_search": bool(args.fem_training_newton_line_search),
        "newton_line_search_dampings": _parse_float_list(args.fem_training_newton_line_search_dampings),
        "newton_convergence_tol": float(args.fem_training_newton_convergence_tol),
        "tangent_regularization": float(args.fem_training_tangent_regularization),
        "step_policy": str(step_policy),
        "models": tuple(models),
    }


def _train(
    model_name: str,
    model: nn.Module,
    loaded: dict,
    connectivity: torch.Tensor,
    seed: int,
    args: argparse.Namespace,
) -> list[float]:
    dataset = PathOperatorTensorDataset(loaded["tensors"])
    generator = torch.Generator()
    generator.manual_seed(seed)
    loader = DataLoader(dataset, batch_size=args.batch_size, shuffle=True, generator=generator)
    optimizer = torch.optim.Adam(model.parameters(), lr=args.learning_rate)
    weights = _loss_weights(model_name)
    fem_training = _fem_training_config(args)
    history = []
    model.train()
    for epoch in range(args.epochs):
        teacher_forcing_ratio = _teacher_forcing_ratio(epoch, args)
        running = 0.0
        n_seen = 0
        for batch in loader:
            batch = _move_batch(batch, args.device)
            optimizer.zero_grad()
            model_kwargs = {
                "connectivity": connectivity,
                "teacher_history": batch["material_history_sequence"],
                "teacher_forcing_ratio": (
                    teacher_forcing_ratio
                    if model_name.startswith("hgo_") or model_name in {"hano_faithful", "hano_style", "hano"}
                    else 0.0
                ),
            }
            if model_name.startswith("hgo_"):
                model_kwargs["teacher_plastic_strain"] = batch.get("plastic_strain_sequence")
                model_kwargs["teacher_qp_history"] = batch.get("material_history_qp_sequence")
            if model_name == "hano_faithful":
                model_kwargs["teacher_strain"] = batch.get("strain_sequence")
                model_kwargs["teacher_stress"] = batch.get("stress_sequence")
            outputs = model(
                batch["coords"],
                batch["params"],
                batch["forcing_sequence"],
                **model_kwargs,
            )
            losses = history_graph_operator_loss(outputs, batch, weights)
            if (
                (
                    fem_training["residual_weight"] > 0.0
                    or fem_training["energy_weight"] > 0.0
                    or fem_training["solver_weight"] > 0.0
                )
                and model_name in fem_training["models"]
            ):
                fem_losses = j2_fem_training_loss(
                    outputs,
                    batch,
                    connectivity,
                    residual_weight=fem_training["residual_weight"],
                    energy_weight=fem_training["energy_weight"],
                    solver_weight=fem_training["solver_weight"],
                    solver_mode=fem_training["solver_mode"],
                    newton_damping=fem_training["newton_damping"],
                    newton_steps=fem_training["newton_steps"],
                    newton_line_search=fem_training["newton_line_search"],
                    newton_line_search_dampings=fem_training["newton_line_search_dampings"],
                    newton_convergence_tol=fem_training["newton_convergence_tol"],
                    tangent_regularization=fem_training["tangent_regularization"],
                    step_policy=fem_training["step_policy"],
            )
                losses["total"] = losses["total"] + fem_losses["total"]
                losses.update({f"fem_training_{key}": value for key, value in fem_losses.items()})
            losses["total"].backward()
            if args.grad_clip_norm and args.grad_clip_norm > 0.0:
                torch.nn.utils.clip_grad_norm_(model.parameters(), float(args.grad_clip_norm))
            optimizer.step()
            batch_size = int(batch["params"].shape[0])
            running += float(losses["total"].detach().cpu()) * batch_size
            n_seen += batch_size
        history.append(running / max(n_seen, 1))
    return history


def _evaluate(
    model: nn.Module,
    loaded: dict,
    connectivity: torch.Tensor,
    args: argparse.Namespace,
) -> dict[str, float]:
    dataset = PathOperatorTensorDataset(loaded["tensors"])
    loader = DataLoader(dataset, batch_size=args.eval_batch_size, shuffle=False)
    weights = _eval_loss_weights()
    fem_training = _fem_training_config(args)
    accum: dict[str, float] = {}
    n_seen = 0
    model.eval()
    with torch.no_grad():
        for batch in loader:
            batch = _move_batch(batch, args.device)
            outputs = model(
                batch["coords"],
                batch["params"],
                batch["forcing_sequence"],
                connectivity=connectivity,
                teacher_forcing_ratio=0.0,
            )
            metrics = _path_prediction_metrics(
                outputs,
                batch,
                weights,
                connectivity if args.fem_audit_metrics else None,
                fem_audit_step_policy=args.fem_audit_step_policy,
                fem_solver_mode=fem_training["solver_mode"],
                fem_newton_damping=fem_training["newton_damping"],
                fem_newton_steps=fem_training["newton_steps"],
                fem_newton_line_search=fem_training["newton_line_search"],
                fem_newton_line_search_dampings=fem_training["newton_line_search_dampings"],
                fem_newton_convergence_tol=fem_training["newton_convergence_tol"],
                fem_tangent_regularization=fem_training["tangent_regularization"],
            )
            batch_size = int(batch["params"].shape[0])
            for key, value in metrics.items():
                accum[key] = accum.get(key, 0.0) + float(value.detach().cpu()) * batch_size
            n_seen += batch_size
    model.train()
    return {key: value / max(n_seen, 1) for key, value in sorted(accum.items())}


def _teacher_forcing_ratio(epoch: int, args: argparse.Namespace) -> float:
    initial = float(args.teacher_forcing_ratio)
    if args.teacher_forcing_final_ratio is None:
        return initial
    final = float(args.teacher_forcing_final_ratio)
    warmup = max(int(args.teacher_forcing_warmup_epochs), 0)
    if epoch < warmup:
        return initial
    anneal_epochs = max(int(args.epochs) - warmup - 1, 1)
    progress = min(max((epoch - warmup) / anneal_epochs, 0.0), 1.0)
    return (1.0 - progress) * initial + progress * final


def _path_prediction_metrics(
    outputs: dict[str, torch.Tensor],
    batch: dict[str, torch.Tensor],
    weights: PathLossWeights,
    connectivity: torch.Tensor | None = None,
    fem_audit_step_policy: str = "final",
    fem_solver_mode: str = "linearized",
    fem_newton_damping: float = 1.0,
    fem_newton_steps: int = 1,
    fem_newton_line_search: bool = False,
    fem_newton_line_search_dampings: tuple[float, ...] | None = None,
    fem_newton_convergence_tol: float = 1.0e-3,
    fem_tangent_regularization: float = 1.0e-6,
) -> dict[str, torch.Tensor]:
    losses = history_graph_operator_loss(outputs, batch, weights)
    prediction = outputs["mean_sequence"]
    target = batch["fields_sequence"]
    history_prediction = outputs["history_sequence"]
    history_target = batch["material_history_sequence"][..., : history_prediction.shape[-1]]
    metrics = {
        "total_loss": losses["total"],
        "displacement_relative_l2": _relative_rmse(prediction, target),
        "history_relative_l2": _relative_rmse(history_prediction, history_target),
        "history_increment_relative_l2": _relative_rmse(
            _path_increment(history_prediction),
            _path_increment(history_target),
        ),
        "final_displacement_relative_l2": _relative_rmse(prediction[:, -1], target[:, -1]),
        "final_history_relative_l2": _relative_rmse(history_prediction[:, -1], history_target[:, -1]),
    }
    qp_history_prediction = outputs.get("history_qp_sequence")
    qp_history_target = batch.get("material_history_qp_sequence")
    if qp_history_prediction is not None and qp_history_target is not None:
        qp_history_target = qp_history_target[..., : qp_history_prediction.shape[-1]]
        metrics["qp_history_relative_l2"] = _relative_rmse(qp_history_prediction, qp_history_target)
        metrics["qp_history_increment_relative_l2"] = _relative_rmse(
            _path_increment(qp_history_prediction),
            _path_increment(qp_history_target),
        )
        for name, channel in HISTORY_CHANNELS.items():
            if channel >= qp_history_prediction.shape[-1]:
                continue
            predicted_channel = qp_history_prediction[..., channel]
            target_channel = qp_history_target[..., channel]
            if name == "yield_flag":
                metrics[f"qp_{name}_mae"] = (predicted_channel - target_channel).abs().mean()
            else:
                metrics[f"qp_{name}_relative_l2"] = _relative_rmse(predicted_channel, target_channel)
                if name in {"eq_plastic_strain", "plastic_work"}:
                    metrics[f"qp_{name}_increment_relative_l2"] = _relative_rmse(
                        _path_increment(predicted_channel),
                        _path_increment(target_channel),
                    )
        metrics.update(
            evaluate_qp_reversal_memory_errors(
                qp_history_prediction,
                qp_history_target,
                batch["forcing_sequence"],
            )
        )
    metrics.update(_true_j2_qp_layer_metrics(outputs, batch))
    hano_strain = outputs.get("hano_strain_sequence")
    target_strain = batch.get("strain_sequence")
    if hano_strain is not None and target_strain is not None:
        target_strain = target_strain[..., : hano_strain.shape[-1]]
        metrics["hano_strain_relative_l2"] = _relative_rmse(hano_strain, target_strain)
    hano_stress = outputs.get("hano_stress_sequence")
    target_stress = batch.get("stress_sequence")
    if hano_stress is not None and target_stress is not None:
        target_stress = target_stress[..., : hano_stress.shape[-1]]
        metrics["hano_stress_relative_l2"] = _relative_rmse(hano_stress, target_stress)
    for name, channel in HISTORY_CHANNELS.items():
        if channel >= history_prediction.shape[-1]:
            continue
        predicted_channel = history_prediction[..., channel]
        target_channel = history_target[..., channel]
        if name == "yield_flag":
            metrics[f"{name}_mae"] = (predicted_channel - target_channel).abs().mean()
        else:
            metrics[f"{name}_relative_l2"] = _relative_rmse(predicted_channel, target_channel)
            if name in {"eq_plastic_strain", "plastic_work"}:
                metrics[f"{name}_increment_relative_l2"] = _relative_rmse(
                    _path_increment(predicted_channel),
                    _path_increment(target_channel),
                )

    target_consistency = evaluate_j2_path_history_consistency(batch)
    predicted_consistency = evaluate_j2_path_history_consistency(
        {
            "material_history_sequence": history_prediction,
            "target_material_history_sequence": history_target,
            "forcing_sequence": batch["forcing_sequence"],
            "params": batch["params"],
        }
    )
    reversal_metrics = evaluate_reversal_memory_errors(
        history_prediction,
        history_target,
        batch["forcing_sequence"],
    )
    metrics.update({f"target_{key}": value for key, value in target_consistency.items()})
    metrics.update({f"predicted_{key}": value for key, value in predicted_consistency.items()})
    metrics.update(reversal_metrics)
    if connectivity is not None and "plastic_strain_sequence" in batch:
        fem_metrics = j2_fem_audit_loss(
            outputs,
            batch,
            connectivity,
            residual_weight=1.0,
            energy_weight=1.0,
            solver_weight=1.0,
            solver_mode=fem_solver_mode,
            newton_damping=fem_newton_damping,
            newton_steps=fem_newton_steps,
            newton_line_search=fem_newton_line_search,
            newton_line_search_dampings=fem_newton_line_search_dampings,
            newton_convergence_tol=fem_newton_convergence_tol,
            tangent_regularization=fem_tangent_regularization,
            step_policy=fem_audit_step_policy,
        )
        metrics["fem_residual_relative_rms"] = fem_metrics["fem_residual"].sqrt()
        metrics["fem_energy_relative_error"] = fem_metrics["fem_energy"].sqrt()
        metrics["fem_solver_linearized_residual_relative_rms"] = fem_metrics[
            "fem_solver_linearized_residual"
        ].sqrt()
        metrics["target_fem_residual_relative_rms"] = fem_metrics["target_fem_residual"]
        if "fem_newton_initial_residual" in fem_metrics:
            metrics["fem_newton_initial_residual_relative_rms"] = fem_metrics["fem_newton_initial_residual"]
            metrics["fem_newton_final_residual_relative_rms"] = fem_metrics["fem_newton_final_residual"]
            metrics["fem_newton_residual_ratio"] = fem_metrics["fem_newton_residual_ratio"]
            metrics["fem_newton_residual_decrease_fraction"] = fem_metrics["fem_newton_residual_decrease_fraction"]
            metrics["fem_newton_step_residual_decrease_fraction"] = fem_metrics[
                "fem_newton_step_residual_decrease_fraction"
            ]
            metrics["fem_newton_correction_relative_norm"] = fem_metrics["fem_newton_correction_relative_norm"]
            metrics["fem_newton_accepted_damping"] = fem_metrics["fem_newton_accepted_damping"]
            metrics["fem_newton_convergence_rate"] = fem_metrics["fem_newton_convergence_rate"]
            metrics["fem_newton_failure_rate"] = fem_metrics["fem_newton_failure_rate"]
            for step_index in range(1, 4):
                ratio_key = f"fem_newton_step{step_index}_residual_ratio"
                decrease_key = f"fem_newton_step{step_index}_residual_decrease_fraction"
                if ratio_key in fem_metrics:
                    metrics[ratio_key] = fem_metrics[ratio_key]
                if decrease_key in fem_metrics:
                    metrics[decrease_key] = fem_metrics[decrease_key]
    return metrics


def _true_j2_qp_layer_metrics(
    outputs: dict[str, torch.Tensor],
    batch: dict[str, torch.Tensor],
    eps: float = 1.0e-12,
) -> dict[str, torch.Tensor]:
    residual = outputs.get("j2_qp_consistency_residual_sequence")
    multiplier = outputs.get("j2_qp_plastic_multiplier_sequence")
    if residual is None or multiplier is None:
        return {}
    if batch["params"].ndim != 2 or batch["params"].shape[-1] < 3:
        scale = residual.detach().abs().mean().clamp_min(eps)
    else:
        scale = batch["params"][:, None, None, None, 2].abs().clamp_min(eps)
    residual_rms = residual.square().mean().sqrt()
    active = multiplier > 0.0
    if bool(active.any()):
        active_residual_rms = residual[active].square().mean().sqrt()
    else:
        active_residual_rms = residual.new_tensor(0.0)
    tangent = outputs.get("j2_qp_algorithmic_tangent_sequence")
    if tangent is not None:
        tangent_norm = tangent.square().mean().sqrt()
    else:
        tangent_norm = residual.new_tensor(0.0)
    return {
        "j2_qp_consistency_residual_relative_rms": residual_rms / scale.square().mean().sqrt().clamp_min(eps),
        "j2_qp_active_consistency_residual_relative_rms": active_residual_rms
        / scale.square().mean().sqrt().clamp_min(eps),
        "j2_qp_consistency_residual_absolute_rms": residual_rms,
        "j2_qp_plastic_multiplier_negative_violation": torch.relu(-multiplier).mean(),
        "j2_qp_active_fraction": active.to(dtype=residual.dtype).mean(),
        "j2_qp_tangent_rms": tangent_norm,
    }


def _loss_weights(model_name: str) -> PathLossWeights:
    if model_name == "hgo_qp_memory_attack":
        return PathLossWeights(
            displacement=0.75,
            history=0.50,
            qp_history=1.0,
            qp_history_channel=2.0,
            qp_history_active=8.0,
            qp_plastic_scalar_active=10.0,
            qp_plastic_scalar_increment_active=12.0,
            qp_inactive_false_plasticity=5.0,
            qp_reversal_plastic_increment_active=12.0,
            qp_history_topk=8.0,
            qp_history_increment_topk=10.0,
            qp_reversal_topk_increment=12.0,
            qp_plastic_log_active=2.0,
            history_increment=0.25,
            qp_history_increment=1.0,
            qp_history_increment_channel=2.0,
            qp_history_increment_active=8.0,
            qp_yield_flag=4.0,
            eqp_increment=0.25,
            plastic_work_increment=0.25,
            yield_flag=0.20,
            yield_surface=0.001,
            elastic_overstress=0.001,
            plastic_work_lower_bound=0.001,
            calibration=0.0,
            qp_active_mask_mode="current_increment",
            qp_topk_fraction=0.20,
        )
    if model_name == "hgo_qp_dual_reversal_active":
        return PathLossWeights(
            qp_history=0.25,
            qp_history_channel=1.50,
            qp_history_active=6.0,
            qp_plastic_scalar_active=8.0,
            qp_plastic_scalar_increment_active=8.0,
            qp_inactive_false_plasticity=4.0,
            qp_reversal_plastic_increment_active=8.0,
            history_increment=0.25,
            qp_history_increment=0.50,
            qp_history_increment_channel=1.50,
            qp_history_increment_active=6.0,
            qp_yield_flag=3.0,
            eqp_increment=0.25,
            plastic_work_increment=0.25,
            yield_flag=0.20,
            yield_surface=0.001,
            elastic_overstress=0.001,
            plastic_work_lower_bound=0.001,
            calibration=0.0,
            qp_active_mask_mode="current_increment",
        )
    if model_name in {"hgo_qp_dual_active", "hgo_qp_dual_sparse_active"}:
        return PathLossWeights(
            qp_history=0.50,
            qp_history_channel=1.0,
            qp_history_active=2.0,
            qp_plastic_scalar_active=4.0,
            qp_plastic_scalar_increment_active=3.0,
            qp_inactive_false_plasticity=3.0,
            qp_reversal_plastic_increment_active=2.0,
            history_increment=0.25,
            qp_history_increment=0.50,
            qp_history_increment_channel=1.0,
            qp_history_increment_active=3.0,
            qp_yield_flag=2.0,
            eqp_increment=0.25,
            plastic_work_increment=0.25,
            yield_flag=0.20,
            yield_surface=0.001,
            elastic_overstress=0.001,
            plastic_work_lower_bound=0.001,
            calibration=0.0,
        )
    if model_name == "hgo_qp_plastic_corrector":
        return PathLossWeights(
            qp_history=1.0,
            qp_history_channel=2.0,
            qp_history_active=6.0,
            history_increment=0.25,
            qp_history_increment=0.50,
            qp_history_increment_channel=1.0,
            qp_history_increment_active=4.0,
            qp_yield_flag=2.0,
            eqp_increment=0.25,
            plastic_work_increment=0.25,
            yield_flag=0.20,
            yield_surface=0.001,
            elastic_overstress=0.001,
            plastic_work_lower_bound=0.001,
            calibration=0.0,
        )
    if model_name == "hgo_qp_thermo_hard_qpaware_active":
        return PathLossWeights(
            qp_history=1.0,
            qp_history_channel=1.0,
            qp_history_active=2.0,
            history_increment=0.25,
            qp_history_increment=0.25,
            qp_history_increment_channel=0.25,
            qp_history_increment_active=0.50,
            eqp_increment=0.10,
            plastic_work_increment=0.10,
            yield_flag=0.05,
            yield_surface=0.001,
            elastic_overstress=0.001,
            plastic_work_lower_bound=0.001,
            calibration=0.0,
        )
    if model_name == "hgo_qp_thermo_hard_qpaware":
        return PathLossWeights(
            qp_history=1.0,
            qp_history_channel=1.0,
            history_increment=0.25,
            qp_history_increment=0.25,
            qp_history_increment_channel=0.25,
            eqp_increment=0.10,
            plastic_work_increment=0.10,
            yield_flag=0.05,
            yield_surface=0.001,
            elastic_overstress=0.001,
            plastic_work_lower_bound=0.001,
            calibration=0.0,
        )
    if model_name in {"hgo_qp_thermo_hard", "hgo_qp_true_j2"}:
        return PathLossWeights(
            qp_history=1.0,
            history_increment=0.25,
            qp_history_increment=0.25,
            eqp_increment=0.10,
            plastic_work_increment=0.10,
            yield_flag=0.05,
            yield_surface=0.001,
            elastic_overstress=0.001,
            plastic_work_lower_bound=0.001,
            calibration=0.0,
        )
    if model_name == "hano_faithful":
        return PathLossWeights(
            history_increment=0.25,
            eqp_increment=0.10,
            plastic_work_increment=0.10,
            yield_flag=0.05,
            yield_surface=0.001,
            elastic_overstress=0.001,
            plastic_work_lower_bound=0.001,
            hano_strain=0.25,
            hano_stress=0.25,
            calibration=0.0,
        )
    if model_name in {"hgo_thermo", "hgo_thermo_hard", "hano_style", "hano", "tinn"}:
        return PathLossWeights(
            history_increment=0.25,
            eqp_increment=0.10,
            plastic_work_increment=0.10,
            yield_flag=0.05,
            yield_surface=0.001,
            elastic_overstress=0.001,
            plastic_work_lower_bound=0.001,
            calibration=0.0,
        )
    return PathLossWeights(
        calibration=0.0,
        eqp_monotonicity=0.0,
        plastic_work_monotonicity=0.0,
        plastic_multiplier_nonnegative=0.0,
        yield_bounds=0.0,
    )


def _eval_loss_weights() -> PathLossWeights:
    return PathLossWeights(
        history_increment=0.25,
        eqp_increment=0.10,
        plastic_work_increment=0.10,
        yield_flag=0.05,
        yield_surface=0.001,
        elastic_overstress=0.001,
        plastic_work_lower_bound=0.001,
        calibration=0.0,
    )


def _load_split(data_root: Path, load_path: str, split: str, device: str) -> dict:
    return load_fem_path_snapshots(data_root / load_path / f"{split}.npz", device=device)


def _load_training_splits(data_root: Path, load_paths: tuple[str, ...], device: str) -> dict:
    loaded_splits = [_load_split(data_root, load_path, "train", device) for load_path in load_paths]
    if len(loaded_splits) == 1:
        return loaded_splits[0]
    base = loaded_splits[0]
    tensors: dict[str, torch.Tensor] = {}
    for key, first_value in base["tensors"].items():
        if not isinstance(first_value, torch.Tensor) or first_value.ndim == 0:
            continue
        parts = []
        compatible = True
        for loaded in loaded_splits:
            value = loaded["tensors"].get(key)
            if value is None or not isinstance(value, torch.Tensor) or value.ndim == 0:
                compatible = False
                break
            if tuple(value.shape[1:]) != tuple(first_value.shape[1:]):
                compatible = False
                break
            parts.append(value)
        if compatible:
            tensors[key] = torch.cat(parts, dim=0)
    return {"tensors": tensors, "metadata": base["metadata"], "extra": base["extra"]}


def _summarize_seed_results(seed_results: list[dict]) -> dict:
    load_paths = sorted({load_path for result in seed_results for load_path in result["evaluations"]})
    summary: dict[str, object] = {
        "num_seeds": len(seed_results),
        "train_final_loss": _distribution_stats([result["train_final_loss"] for result in seed_results]),
        "by_load_path": {},
        "cyclic_primary": {},
    }
    by_load_path = summary["by_load_path"]
    for load_path in load_paths:
        metric_names = sorted(
            {metric for result in seed_results for metric in result["evaluations"].get(load_path, {})}
        )
        by_load_path[load_path] = {
            metric: _distribution_stats(
                [
                    result["evaluations"][load_path][metric]
                    for result in seed_results
                    if metric in result["evaluations"].get(load_path, {})
                ]
            )
            for metric in metric_names
        }
    summary["cyclic_primary"] = {
        metric: by_load_path["cyclic"][metric]
        for metric, _ in TABLE_METRICS
        if metric in by_load_path.get("cyclic", {})
    }
    return summary


def _write_table_csv(path: Path, payload: dict) -> None:
    rows = _table_rows(payload)
    fieldnames = list(rows[0]) if rows else []
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _write_table_markdown(path: Path, payload: dict) -> None:
    rows = _table_rows(payload)
    if not rows:
        raise ValueError("no rows to write")
    headers = list(rows[0])
    eval_paths = ", ".join(payload["metadata"].get("eval_load_paths", []))
    lines = [
        "# J2 Path-Dependent Baseline Table",
        "",
        f"Data root: `{payload['metadata']['data_root']}`",
        f"Train load paths: `{', '.join(payload['metadata']['train_load_paths'])}`",
        f"Primary table: cyclic path, {payload['metadata']['epochs']} epochs, {len(payload['metadata']['seeds'])} seeds",
        f"Evaluated paths stored in JSON: `{eval_paths}`",
        "",
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---", *["---:" for _ in headers[1:]]]) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(row.get(header, "") for header in headers) + " |")
    lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _write_robust_stats_csv(path: Path, payload: dict) -> None:
    _write_rows_csv(path, _robust_stat_rows(payload))


def _write_robust_stats_markdown(path: Path, payload: dict) -> None:
    rows = _robust_stat_rows(payload)
    eval_paths = ", ".join(payload["metadata"].get("eval_load_paths", []))
    lines = [
        "# J2 Path-Dependent Baseline Robust Statistics",
        "",
        "Each row reports both mean/std and robust median/IQR statistics on the cyclic primary test path.",
        f"All evaluated paths are stored in JSON: `{eval_paths}`.",
        "",
    ]
    lines.extend(_markdown_table(rows))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _write_per_seed_detail_csv(path: Path, payload: dict) -> None:
    _write_rows_csv(path, _per_seed_rows(payload))


def _write_per_seed_detail_markdown(path: Path, payload: dict) -> None:
    rows = _per_seed_rows(payload)
    eval_paths = ", ".join(payload["metadata"].get("eval_load_paths", []))
    lines = [
        "# J2 Path-Dependent Baseline Per-Seed Details",
        "",
        "Per-seed cyclic-primary metrics for diagnosing stochastic training stability and outliers.",
        f"All evaluated paths are stored in JSON: `{eval_paths}`.",
        "",
    ]
    lines.extend(_markdown_table(rows))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _write_outlier_diagnostics_csv(path: Path, payload: dict) -> None:
    _write_rows_csv(path, _outlier_rows(payload))


def _write_outlier_diagnostics_markdown(path: Path, payload: dict) -> None:
    rows = _outlier_rows(payload)
    eval_paths = ", ".join(payload["metadata"].get("eval_load_paths", []))
    lines = [
        "# J2 Path-Dependent Baseline Outlier Diagnostics",
        "",
        "Outliers are detected on cyclic-primary metrics using a 1.5 IQR rule when IQR is nonzero, "
        "otherwise a 3 sigma rule is used.",
        f"All evaluated paths are stored in JSON: `{eval_paths}`.",
        "",
    ]
    if rows:
        lines.extend(_markdown_table(rows))
    else:
        lines.append("No outliers detected for the configured table metrics.")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _write_pathwise_csv(path: Path, payload: dict) -> None:
    _write_rows_csv(path, _pathwise_rows(payload))


def _write_pathwise_markdown(path: Path, payload: dict) -> None:
    rows = _pathwise_rows(payload)
    lines = [
        "# J2 Path-Dependent Baseline Pathwise Table",
        "",
        f"Data root: `{payload['metadata']['data_root']}`",
        f"Train load paths: `{', '.join(payload['metadata']['train_load_paths'])}`",
        f"Evaluated paths: `{', '.join(payload['metadata'].get('eval_load_paths', []))}`",
        f"Protocol: {payload['metadata']['epochs']} epochs, {len(payload['metadata']['seeds'])} seeds",
        "",
    ]
    lines.extend(_markdown_table(rows))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _table_rows(payload: dict) -> list[dict[str, str]]:
    rows = []
    for model_name, result in payload["results"].items():
        summary = result["summary"]
        row = {
            "Model": MODEL_LABELS.get(model_name, model_name),
            "Seeds": str(summary["num_seeds"]),
        }
        cyclic = summary["cyclic_primary"]
        for metric, label in TABLE_METRICS:
            row[label] = _format_stat(cyclic.get(metric))
        rows.append(row)
    return rows


def _pathwise_rows(payload: dict) -> list[dict[str, str]]:
    rows = []
    eval_paths = payload["metadata"].get("eval_load_paths", [])
    for model_name, result in payload["results"].items():
        summary = result["summary"]
        by_load_path = summary.get("by_load_path", {})
        for load_path in eval_paths:
            path_summary = by_load_path.get(load_path, {})
            if not path_summary:
                continue
            row = {
                "Model": MODEL_LABELS.get(model_name, model_name),
                "Load path": load_path,
                "Seeds": str(summary["num_seeds"]),
            }
            for metric, label in TABLE_METRICS:
                row[_pathwise_metric_label(label)] = _format_stat(path_summary.get(metric))
            rows.append(row)
    return rows


def _pathwise_metric_label(label: str) -> str:
    if label == "Cyclic disp. rel. L2":
        return "Disp. rel. L2"
    if label == "Cyclic history rel. L2":
        return "History rel. L2"
    if label.startswith("Cyclic "):
        return label[len("Cyclic ") :]
    return label


def _robust_stat_rows(payload: dict) -> list[dict[str, str]]:
    rows = []
    for model_name, result in payload["results"].items():
        cyclic = result["summary"]["cyclic_primary"]
        for metric, label in TABLE_METRICS:
            stats = cyclic.get(metric)
            if stats is None:
                continue
            rows.append(
                {
                    "Model": MODEL_LABELS.get(model_name, model_name),
                    "Metric": label,
                    "Mean": _format_float(stats["mean"]),
                    "Std": _format_float(stats["std"]),
                    "Median": _format_float(stats["median"]),
                    "Q1": _format_float(stats["q1"]),
                    "Q3": _format_float(stats["q3"]),
                    "IQR": _format_float(stats["iqr"]),
                    "Min": _format_float(stats["min"]),
                    "Max": _format_float(stats["max"]),
                    "N": str(stats["n"]),
                }
            )
    return rows


def _per_seed_rows(payload: dict) -> list[dict[str, str]]:
    rows = []
    for model_name, result in payload["results"].items():
        for seed_result in result["seeds"]:
            cyclic = seed_result["evaluations"].get("cyclic", {})
            row = {
                "Model": MODEL_LABELS.get(model_name, model_name),
                "Seed": str(seed_result["seed"]),
                "Train final loss": _format_float(seed_result["train_final_loss"]),
            }
            for metric, label in TABLE_METRICS:
                if metric in cyclic:
                    row[label] = _format_float(cyclic[metric])
            rows.append(row)
    return rows


def _outlier_rows(payload: dict) -> list[dict[str, str]]:
    rows = []
    for model_name, result in payload["results"].items():
        seed_results = result["seeds"]
        for metric, label in TABLE_METRICS:
            seed_values = [
                (seed_result["seed"], seed_result["evaluations"]["cyclic"][metric])
                for seed_result in seed_results
                if metric in seed_result["evaluations"].get("cyclic", {})
            ]
            if len(seed_values) < 3:
                continue
            stats = _distribution_stats([value for _, value in seed_values])
            outliers, lower, upper, rule = _detect_outliers(seed_values, stats)
            if not outliers:
                continue
            rows.append(
                {
                    "Model": MODEL_LABELS.get(model_name, model_name),
                    "Metric": label,
                    "Rule": rule,
                    "Lower": _format_float(lower),
                    "Upper": _format_float(upper),
                    "Outlier count": str(len(outliers)),
                    "Outlier seeds": "; ".join(
                        f"{seed}={_format_float(value)}" for seed, value in outliers
                    ),
                    "Mean": _format_float(stats["mean"]),
                    "Std": _format_float(stats["std"]),
                    "Median": _format_float(stats["median"]),
                    "IQR": _format_float(stats["iqr"]),
                    "Min": _format_float(stats["min"]),
                    "Max": _format_float(stats["max"]),
                }
            )
    return rows


def _format_stat(stats: dict | None) -> str:
    if stats is None:
        return ""
    return f"{stats['mean']:.4f} +/- {stats['std']:.4f}"


def _format_float(value: float) -> str:
    return f"{float(value):.6g}"


def _write_rows_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames = _union_fieldnames(rows)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def _markdown_table(rows: list[dict[str, str]]) -> list[str]:
    if not rows:
        return []
    headers = _union_fieldnames(rows)
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---", *["---:" for _ in headers[1:]]]) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(row.get(header, "") for header in headers) + " |")
    return lines


def _union_fieldnames(rows: list[dict[str, str]]) -> list[str]:
    fieldnames = list(rows[0])
    seen = set(fieldnames)
    for row in rows[1:]:
        for field in row:
            if field not in seen:
                seen.add(field)
                fieldnames.append(field)
    return fieldnames


def _detect_outliers(
    seed_values: list[tuple[int, float]],
    stats: dict[str, float],
    eps: float = 1.0e-12,
) -> tuple[list[tuple[int, float]], float, float, str]:
    if stats["iqr"] > eps:
        lower = stats["q1"] - 1.5 * stats["iqr"]
        upper = stats["q3"] + 1.5 * stats["iqr"]
        rule = "1.5*IQR"
    elif stats["std"] > eps:
        lower = stats["mean"] - 3.0 * stats["std"]
        upper = stats["mean"] + 3.0 * stats["std"]
        rule = "3*sigma"
    else:
        return [], stats["mean"], stats["mean"], "constant"
    outliers = [(seed, value) for seed, value in seed_values if value < lower or value > upper]
    return outliers, lower, upper, rule


def _augment_params(params: torch.Tensor, forcing: torch.Tensor, step: int, n_steps: int) -> torch.Tensor:
    global_load = forcing.mean(dim=1)
    step_fraction = params.new_full((params.shape[0], 1), float(step + 1) / max(n_steps, 1))
    return torch.cat([params, global_load, step_fraction], dim=-1)


def _connectivity_tensor(loaded: dict, device: str | torch.device) -> torch.Tensor:
    return torch.as_tensor(loaded["extra"]["connectivity"], dtype=torch.long, device=device)


def _grid_shape_from_loaded(loaded: dict) -> tuple[int, int]:
    values = torch.as_tensor(loaded["extra"]["grid_shape"]).reshape(-1).tolist()
    if len(values) >= 2 and int(values[0]) > 0 and int(values[1]) > 0:
        return int(values[0]), int(values[1])
    n_nodes = int(loaded["tensors"]["coords"].shape[1])
    return n_nodes, 1


def _prepare_connectivity(connectivity: torch.Tensor | None, device: torch.device) -> torch.Tensor | None:
    if connectivity is None:
        return None
    return torch.as_tensor(connectivity, dtype=torch.long, device=device)


def _nodes_to_elements(values: torch.Tensor, connectivity: torch.Tensor | None) -> torch.Tensor:
    if connectivity is None:
        return values
    element_values = values.index_select(dim=1, index=connectivity.reshape(-1))
    element_values = element_values.view(values.shape[0], connectivity.shape[0], connectivity.shape[1], values.shape[-1])
    return element_values.mean(dim=2)


def _path_increment(values: torch.Tensor) -> torch.Tensor:
    if values.shape[1] < 2:
        return values.new_zeros(values.shape[0], 0, *values.shape[2:])
    return values[:, 1:] - values[:, :-1]


def _relative_rmse(prediction: torch.Tensor, target: torch.Tensor, eps: float = 1.0e-12) -> torch.Tensor:
    if prediction.numel() == 0:
        return target.new_tensor(0.0)
    error = prediction - target
    return error.square().mean().sqrt() / target.square().mean().sqrt().clamp_min(eps)


def _distribution_stats(values: list[float]) -> dict[str, float]:
    tensor = torch.tensor(values, dtype=torch.float64)
    std = tensor.std(unbiased=False) if tensor.numel() > 1 else tensor.new_tensor(0.0)
    q1 = torch.quantile(tensor, 0.25) if tensor.numel() > 1 else tensor[0]
    median = torch.quantile(tensor, 0.50) if tensor.numel() > 1 else tensor[0]
    q3 = torch.quantile(tensor, 0.75) if tensor.numel() > 1 else tensor[0]
    return {
        "mean": float(tensor.mean()),
        "std": float(std),
        "median": float(median),
        "q1": float(q1),
        "q3": float(q3),
        "iqr": float(q3 - q1),
        "min": float(tensor.min()),
        "max": float(tensor.max()),
        "n": int(tensor.numel()),
    }


def _move_batch(batch: dict[str, torch.Tensor], device: str | torch.device) -> dict[str, torch.Tensor]:
    return {key: value.to(device) if isinstance(value, torch.Tensor) else value for key, value in batch.items()}


def _parse_load_paths(value: str | tuple[str, ...] | list[str]) -> tuple[str, ...]:
    parsed = _ensure_tuple(value)
    unknown = sorted(set(parsed).difference(SUPPORTED_LOAD_PATHS))
    if unknown:
        raise argparse.ArgumentTypeError(f"unknown load paths {unknown}; options are {list(SUPPORTED_LOAD_PATHS)}")
    if not parsed:
        raise argparse.ArgumentTypeError("at least one load path is required")
    return parsed


def _parse_models(value: str | tuple[str, ...] | list[str]) -> tuple[str, ...]:
    parsed = _ensure_tuple(value)
    unknown = sorted(set(parsed).difference(SUPPORTED_MODELS))
    if unknown:
        raise argparse.ArgumentTypeError(f"unknown models {unknown}; options are {list(SUPPORTED_MODELS)}")
    if not parsed:
        raise argparse.ArgumentTypeError("at least one model is required")
    return parsed


def _parse_int_list(value: str) -> tuple[int, ...]:
    parsed = tuple(int(item.strip()) for item in value.split(",") if item.strip())
    if not parsed:
        raise argparse.ArgumentTypeError("at least one seed is required")
    return parsed


def _parse_float_list(value: str | tuple[float, ...] | list[float]) -> tuple[float, ...]:
    if isinstance(value, (tuple, list)):
        parsed = tuple(float(item) for item in value)
    else:
        parsed = tuple(float(item.strip()) for item in str(value).split(",") if item.strip())
    if not parsed:
        raise argparse.ArgumentTypeError("at least one float value is required")
    if any(item <= 0.0 for item in parsed):
        raise argparse.ArgumentTypeError("Newton damping candidates must be positive")
    return parsed


def _ensure_tuple(value: str | tuple[str, ...] | list[str]) -> tuple[str, ...]:
    if isinstance(value, (tuple, list)):
        return tuple(str(item).strip() for item in value if str(item).strip())
    return tuple(item.strip() for item in str(value).split(",") if item.strip())


if __name__ == "__main__":
    main()
