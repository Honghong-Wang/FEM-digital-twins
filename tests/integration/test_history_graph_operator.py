from __future__ import annotations

import torch

from pcgno_dt.data.datasets import PathOperatorTensorDataset
from pcgno_dt.evaluation.path_history import evaluate_reversal_memory_errors
from pcgno_dt.evaluation.path_history import evaluate_qp_reversal_memory_errors
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
from pcgno_dt.numerics.j2plasticity2d import generate_j2_plasticity_fem_snapshots
from pcgno_dt.training.path_losses import PathLossWeights, history_graph_operator_loss


def test_history_graph_operator_advances_j2_path_history() -> None:
    data = generate_j2_plasticity_fem_snapshots(
        n_samples=2,
        split="train",
        seed=11,
        nx=3,
        ny=3,
        load_steps=3,
        max_newton_steps=10,
    )
    tensors = {key: value for key, value in data.items() if isinstance(value, torch.Tensor)}
    tensors["material_history_sequence"] = torch.as_tensor(data["material_history_sequence"], dtype=torch.float32)
    tensors["plastic_strain_sequence"] = torch.as_tensor(data["plastic_strain_sequence"], dtype=torch.float32)
    dataset = PathOperatorTensorDataset(tensors)
    batch = {key: value for key, value in dataset[:2].items()}
    connectivity = torch.as_tensor(data["connectivity"], dtype=torch.long)
    model = HistoryGraphOperator(
        HistoryGraphOperatorConfig(
            num_parameters=batch["params"].shape[-1],
            num_fields=batch["fields_sequence"].shape[-1],
            spatial_dim=batch["coords"].shape[-1],
            history_dim=batch["material_history_sequence"].shape[-1],
            hidden_dim=24,
            num_message_passing_layers=1,
            k_neighbors=4,
        )
    )

    outputs = model(
        batch["coords"],
        batch["params"],
        batch["forcing_sequence"],
        connectivity=connectivity,
        teacher_history=batch["material_history_sequence"],
        teacher_forcing_ratio=0.25,
    )
    assert outputs["mean_sequence"].shape == batch["fields_sequence"].shape
    assert outputs["history_sequence"].shape == batch["material_history_sequence"].shape
    assert outputs["logvar_sequence"].shape == batch["fields_sequence"].shape

    losses = history_graph_operator_loss(outputs, batch)
    assert torch.isfinite(losses["total"])
    increment_losses = history_graph_operator_loss(
        outputs,
        batch,
        PathLossWeights(
            history_increment=0.25,
            eqp_increment=0.1,
            plastic_work_increment=0.1,
            yield_flag=0.05,
            yield_surface=0.1,
            elastic_overstress=0.1,
            plastic_work_lower_bound=0.1,
        ),
    )
    assert torch.isfinite(increment_losses["history_increment"])
    assert torch.isfinite(increment_losses["eqp_increment"])
    assert torch.isfinite(increment_losses["plastic_work_increment"])
    assert torch.isfinite(increment_losses["yield_flag"])
    assert torch.isfinite(increment_losses["yield_surface"])
    assert torch.isfinite(increment_losses["elastic_overstress"])
    assert torch.isfinite(increment_losses["plastic_work_lower_bound"])
    losses["total"].backward()
    assert any(parameter.grad is not None for parameter in model.parameters())

    free_outputs = model(
        batch["coords"],
        batch["params"],
        batch["forcing_sequence"],
        connectivity=connectivity,
        teacher_forcing_ratio=0.0,
    )
    history = free_outputs["history_sequence"]
    assert torch.all(history[:, 1:, :, 0] + 1.0e-7 >= history[:, :-1, :, 0])
    assert torch.all(history[:, 1:, :, 1] + 1.0e-7 >= history[:, :-1, :, 1])
    assert torch.all(history[..., 2] >= 0.0)
    assert torch.all((history[..., 3] >= 0.0) & (history[..., 3] <= 1.0))
    reversal_metrics = evaluate_reversal_memory_errors(
        free_outputs["history_sequence"],
        batch["material_history_sequence"],
        batch["forcing_sequence"],
    )
    assert torch.isfinite(reversal_metrics["reversal_history_increment_relative_l2"])


def test_thermo_hard_history_graph_operator_projects_j2_history() -> None:
    data = generate_j2_plasticity_fem_snapshots(
        n_samples=1,
        split="train",
        seed=12,
        nx=3,
        ny=3,
        load_steps=3,
        max_newton_steps=8,
    )
    tensors = {key: value for key, value in data.items() if isinstance(value, torch.Tensor)}
    tensors["material_history_sequence"] = torch.as_tensor(data["material_history_sequence"], dtype=torch.float32)
    tensors["plastic_strain_sequence"] = torch.as_tensor(data["plastic_strain_sequence"], dtype=torch.float32)
    dataset = PathOperatorTensorDataset(tensors)
    batch = {key: value for key, value in dataset[:1].items()}
    connectivity = torch.as_tensor(data["connectivity"], dtype=torch.long)
    model = HistoryGraphOperator(
        HistoryGraphOperatorConfig(
            num_parameters=batch["params"].shape[-1],
            num_fields=batch["fields_sequence"].shape[-1],
            spatial_dim=batch["coords"].shape[-1],
            history_dim=batch["material_history_sequence"].shape[-1],
            hidden_dim=16,
            num_message_passing_layers=1,
            k_neighbors=4,
            thermo_hard_j2_return=True,
        )
    )
    outputs = model(
        batch["coords"],
        batch["params"],
        batch["forcing_sequence"],
        connectivity=connectivity,
        teacher_plastic_strain=batch["plastic_strain_sequence"],
    )
    history = outputs["history_sequence"]
    params = batch["params"]
    flow_stress = params[:, None, None, 2] + params[:, None, None, 3].clamp_min(0.0) * history[..., 0]
    assert outputs["plastic_strain_sequence"].shape[:4] == (*batch["material_history_sequence"].shape[:3], 3)
    assert outputs["j2_stress_sequence"].shape == (*batch["material_history_sequence"].shape[:3], 3)
    assert outputs["j2_algorithmic_tangent_sequence"].shape == (*batch["material_history_sequence"].shape[:3], 3, 3)
    assert outputs["j2_yield_function_sequence"].shape == batch["material_history_sequence"].shape[:3]
    assert torch.all(history[:, 1:, :, 0] + 1.0e-7 >= history[:, :-1, :, 0])
    assert torch.all(history[:, 1:, :, 1] + 1.0e-7 >= history[:, :-1, :, 1])
    assert torch.all(history[..., 2] >= 0.0)
    assert torch.all(history[..., 4] <= flow_stress + 1.0e-4)


def test_qp_thermo_hard_history_graph_operator_predicts_quadrature_history() -> None:
    data = generate_j2_plasticity_fem_snapshots(
        n_samples=1,
        split="train",
        seed=121,
        nx=3,
        ny=3,
        load_steps=3,
        max_newton_steps=8,
    )
    tensors = {key: torch.as_tensor(value, dtype=torch.float32) for key, value in data.items() if isinstance(value, torch.Tensor)}
    tensors["material_history_sequence"] = torch.as_tensor(data["material_history_sequence"], dtype=torch.float32)
    tensors["material_history_qp_sequence"] = torch.as_tensor(data["material_history_qp_sequence"], dtype=torch.float32)
    tensors["plastic_strain_sequence"] = torch.as_tensor(data["plastic_strain_sequence"], dtype=torch.float32)
    dataset = PathOperatorTensorDataset(tensors)
    batch = {key: value for key, value in dataset[:1].items()}
    connectivity = torch.as_tensor(data["connectivity"], dtype=torch.long)
    n_qp = int(batch["material_history_qp_sequence"].shape[-2])
    model = HistoryGraphOperator(
        HistoryGraphOperatorConfig(
            num_parameters=batch["params"].shape[-1],
            num_fields=batch["fields_sequence"].shape[-1],
            spatial_dim=batch["coords"].shape[-1],
            history_dim=batch["material_history_sequence"].shape[-1],
            hidden_dim=16,
            num_message_passing_layers=1,
            k_neighbors=4,
            thermo_hard_j2_return=True,
            predict_qp_history=True,
            num_quadrature_points=n_qp,
        )
    )

    outputs = model(
        batch["coords"],
        batch["params"],
        batch["forcing_sequence"],
        connectivity=connectivity,
        teacher_history=batch["material_history_sequence"],
        teacher_qp_history=batch["material_history_qp_sequence"],
        teacher_forcing_ratio=0.25,
    )

    assert outputs["history_qp_sequence"].shape == batch["material_history_qp_sequence"].shape
    assert outputs["history_sequence"].shape == batch["material_history_sequence"].shape
    losses = history_graph_operator_loss(
        outputs,
        batch,
        PathLossWeights(qp_history=1.0, qp_history_increment=0.25, calibration=0.0),
    )
    assert torch.isfinite(losses["qp_history"])
    assert torch.isfinite(losses["qp_history_increment"])
    losses["total"].backward()
    assert any(parameter.grad is not None for parameter in model.parameters())


def test_qp_aware_history_graph_operator_conditions_on_quadrature_state() -> None:
    data = generate_j2_plasticity_fem_snapshots(
        n_samples=1,
        split="train",
        seed=123,
        nx=3,
        ny=3,
        load_steps=3,
        max_newton_steps=8,
    )
    tensors = {key: torch.as_tensor(value, dtype=torch.float32) for key, value in data.items() if isinstance(value, torch.Tensor)}
    tensors["material_history_sequence"] = torch.as_tensor(data["material_history_sequence"], dtype=torch.float32)
    tensors["material_history_qp_sequence"] = torch.as_tensor(data["material_history_qp_sequence"], dtype=torch.float32)
    tensors["plastic_strain_sequence"] = torch.as_tensor(data["plastic_strain_sequence"], dtype=torch.float32)
    dataset = PathOperatorTensorDataset(tensors)
    batch = {key: value for key, value in dataset[:1].items()}
    connectivity = torch.as_tensor(data["connectivity"], dtype=torch.long)
    n_qp = int(batch["material_history_qp_sequence"].shape[-2])
    model = HistoryGraphOperator(
        HistoryGraphOperatorConfig(
            num_parameters=batch["params"].shape[-1],
            num_fields=batch["fields_sequence"].shape[-1],
            spatial_dim=batch["coords"].shape[-1],
            history_dim=batch["material_history_sequence"].shape[-1],
            hidden_dim=16,
            num_message_passing_layers=1,
            k_neighbors=4,
            thermo_hard_j2_return=True,
            predict_qp_history=True,
            num_quadrature_points=n_qp,
            qp_feature_conditioning=True,
        )
    )

    outputs = model(
        batch["coords"],
        batch["params"],
        batch["forcing_sequence"],
        connectivity=connectivity,
        teacher_history=batch["material_history_sequence"],
        teacher_qp_history=batch["material_history_qp_sequence"],
        teacher_forcing_ratio=0.25,
    )

    assert outputs["history_qp_sequence"].shape == batch["material_history_qp_sequence"].shape
    losses = history_graph_operator_loss(
        outputs,
        batch,
        PathLossWeights(
            qp_history=1.0,
            qp_history_channel=1.0,
            qp_history_active=1.0,
            qp_history_increment=0.25,
            qp_history_increment_channel=0.25,
            qp_history_increment_active=0.25,
            calibration=0.0,
        ),
    )
    assert torch.isfinite(losses["qp_history_channel"])
    assert torch.isfinite(losses["qp_history_increment_channel"])
    assert torch.isfinite(losses["qp_history_active"])
    assert torch.isfinite(losses["qp_history_increment_active"])
    losses["total"].backward()
    assert any(parameter.grad is not None for parameter in model.qp_conditioned_history_head.parameters())


def test_dual_head_qp_history_graph_operator_exposes_active_scalar_gradients() -> None:
    data = generate_j2_plasticity_fem_snapshots(
        n_samples=1,
        split="train",
        seed=124,
        nx=3,
        ny=3,
        load_steps=4,
        load_path="cyclic",
        max_newton_steps=8,
    )
    tensors = {key: torch.as_tensor(value, dtype=torch.float32) for key, value in data.items() if isinstance(value, torch.Tensor)}
    tensors["material_history_sequence"] = torch.as_tensor(data["material_history_sequence"], dtype=torch.float32)
    tensors["material_history_qp_sequence"] = torch.as_tensor(data["material_history_qp_sequence"], dtype=torch.float32)
    tensors["plastic_strain_sequence"] = torch.as_tensor(data["plastic_strain_sequence"], dtype=torch.float32)
    dataset = PathOperatorTensorDataset(tensors)
    batch = {key: value for key, value in dataset[:1].items()}
    connectivity = torch.as_tensor(data["connectivity"], dtype=torch.long)
    n_qp = int(batch["material_history_qp_sequence"].shape[-2])
    model = HistoryGraphOperator(
        HistoryGraphOperatorConfig(
            num_parameters=batch["params"].shape[-1],
            num_fields=batch["fields_sequence"].shape[-1],
            spatial_dim=batch["coords"].shape[-1],
            history_dim=batch["material_history_sequence"].shape[-1],
            hidden_dim=16,
            num_message_passing_layers=1,
            k_neighbors=4,
            thermo_hard_j2_return=True,
            predict_qp_history=True,
            num_quadrature_points=n_qp,
            qp_feature_conditioning=True,
            qp_dual_history_head=True,
            qp_plastic_memory_corrector=True,
        )
    )

    outputs = model(
        batch["coords"],
        batch["params"],
        batch["forcing_sequence"],
        connectivity=connectivity,
        teacher_history=batch["material_history_sequence"],
        teacher_qp_history=batch["material_history_qp_sequence"],
        teacher_forcing_ratio=0.25,
    )

    assert outputs["history_qp_sequence"].shape == batch["material_history_qp_sequence"].shape
    losses = history_graph_operator_loss(
        outputs,
        batch,
        PathLossWeights(
            qp_plastic_scalar_active=1.0,
            qp_plastic_scalar_increment_active=1.0,
            qp_inactive_false_plasticity=0.25,
            qp_reversal_plastic_increment_active=1.0,
            calibration=0.0,
        ),
    )
    assert torch.isfinite(losses["qp_plastic_scalar_active"])
    assert torch.isfinite(losses["qp_plastic_scalar_increment_active"])
    assert torch.isfinite(losses["qp_inactive_false_plasticity"])
    assert torch.isfinite(losses["qp_reversal_plastic_increment_active"])
    losses["total"].backward()
    assert any(parameter.grad is not None for parameter in model.qp_plastic_scalar_head.parameters())
    assert any(parameter.grad is not None for parameter in model.qp_stress_consistency_head.parameters())

    reversal_metrics = evaluate_qp_reversal_memory_errors(
        outputs["history_qp_sequence"].detach(),
        batch["material_history_qp_sequence"],
        batch["forcing_sequence"],
    )
    assert torch.isfinite(reversal_metrics["qp_reversal_plastic_scalar_increment_relative_l2"])


def test_true_j2_qp_history_graph_operator_exports_qp_tangent_and_history() -> None:
    data = generate_j2_plasticity_fem_snapshots(
        n_samples=1,
        split="train",
        seed=122,
        nx=3,
        ny=3,
        load_steps=3,
        max_newton_steps=8,
    )
    tensors = {key: torch.as_tensor(value, dtype=torch.float32) for key, value in data.items() if isinstance(value, torch.Tensor)}
    tensors["material_history_sequence"] = torch.as_tensor(data["material_history_sequence"], dtype=torch.float32)
    tensors["material_history_qp_sequence"] = torch.as_tensor(data["material_history_qp_sequence"], dtype=torch.float32)
    tensors["plastic_strain_sequence"] = torch.as_tensor(data["plastic_strain_sequence"], dtype=torch.float32)
    dataset = PathOperatorTensorDataset(tensors)
    batch = {key: value for key, value in dataset[:1].items()}
    connectivity = torch.as_tensor(data["connectivity"], dtype=torch.long)
    n_qp = int(batch["material_history_qp_sequence"].shape[-2])
    model = HistoryGraphOperator(
        HistoryGraphOperatorConfig(
            num_parameters=batch["params"].shape[-1],
            num_fields=batch["fields_sequence"].shape[-1],
            spatial_dim=batch["coords"].shape[-1],
            history_dim=batch["material_history_sequence"].shape[-1],
            hidden_dim=16,
            num_message_passing_layers=1,
            k_neighbors=4,
            thermo_hard_j2_return=True,
            predict_qp_history=True,
            num_quadrature_points=n_qp,
            true_differentiable_j2_return=True,
        )
    )

    outputs = model(
        batch["coords"],
        batch["params"],
        batch["forcing_sequence"],
        connectivity=connectivity,
        teacher_history=batch["material_history_sequence"],
        teacher_qp_history=batch["material_history_qp_sequence"],
        teacher_plastic_strain=batch["plastic_strain_sequence"],
        teacher_forcing_ratio=0.25,
    )

    assert outputs["history_qp_sequence"].shape == batch["material_history_qp_sequence"].shape
    assert outputs["plastic_strain_qp_sequence"].shape[-3:] == (n_qp, 3, 3)
    assert outputs["j2_qp_stress_sequence"].shape == (*batch["material_history_qp_sequence"].shape[:-1], 3)
    assert outputs["j2_qp_algorithmic_tangent_sequence"].shape == (*batch["material_history_qp_sequence"].shape[:-1], 3, 3)
    assert outputs["j2_qp_yield_function_sequence"].shape == batch["material_history_qp_sequence"].shape[:-1]
    assert outputs["j2_qp_trial_yield_function_sequence"].shape == batch["material_history_qp_sequence"].shape[:-1]
    assert outputs["j2_qp_trial_von_mises_sequence"].shape == batch["material_history_qp_sequence"].shape[:-1]
    assert outputs["j2_qp_plastic_multiplier_sequence"].shape == batch["material_history_qp_sequence"].shape[:-1]
    assert outputs["j2_qp_consistency_residual_sequence"].shape == batch["material_history_qp_sequence"].shape[:-1]
    loss = outputs["mean_sequence"].square().mean() + outputs["history_qp_sequence"][..., :5].mean()
    loss.backward()
    assert any(parameter.grad is not None for parameter in model.parameters())


def test_controlled_path_frontier_baselines_share_path_operator_interface() -> None:
    data = generate_j2_plasticity_fem_snapshots(
        n_samples=1,
        split="train",
        seed=13,
        nx=3,
        ny=3,
        load_steps=3,
        max_newton_steps=8,
    )
    tensors = {key: value for key, value in data.items() if isinstance(value, torch.Tensor)}
    tensors["material_history_sequence"] = torch.as_tensor(data["material_history_sequence"], dtype=torch.float32)
    tensors["plastic_strain_sequence"] = torch.as_tensor(data["plastic_strain_sequence"], dtype=torch.float32)
    dataset = PathOperatorTensorDataset(tensors)
    batch = {key: value for key, value in dataset[:1].items()}
    connectivity = torch.as_tensor(data["connectivity"], dtype=torch.long)
    model = ControlledPathOperator(
        ControlledPathOperatorConfig(
            num_parameters=batch["params"].shape[-1],
            num_fields=batch["fields_sequence"].shape[-1],
            spatial_dim=batch["coords"].shape[-1],
            history_dim=batch["material_history_sequence"].shape[-1],
            hidden_dim=16,
            thermo_hard_j2_return=True,
        )
    )
    outputs = model(
        batch["coords"],
        batch["params"],
        batch["forcing_sequence"],
        connectivity=connectivity,
    )
    assert outputs["mean_sequence"].shape == batch["fields_sequence"].shape
    assert outputs["history_sequence"].shape == batch["material_history_sequence"].shape
    losses = history_graph_operator_loss(outputs, batch)
    assert torch.isfinite(losses["total"])


def test_hano_and_incde_frontier_baselines_share_path_operator_interface() -> None:
    data = generate_j2_plasticity_fem_snapshots(
        n_samples=1,
        split="train",
        seed=14,
        nx=3,
        ny=3,
        load_steps=3,
        max_newton_steps=8,
    )
    tensors = {key: value for key, value in data.items() if isinstance(value, torch.Tensor)}
    tensors["material_history_sequence"] = torch.as_tensor(data["material_history_sequence"], dtype=torch.float32)
    tensors["strain_sequence"] = torch.as_tensor(data["strain_sequence"], dtype=torch.float32)
    tensors["stress_sequence"] = torch.as_tensor(data["stress_sequence"], dtype=torch.float32)
    dataset = PathOperatorTensorDataset(tensors)
    batch = {key: value for key, value in dataset[:1].items()}
    connectivity = torch.as_tensor(data["connectivity"], dtype=torch.long)
    configs_and_models = [
        (
            FaithfulHANOOperator,
            FaithfulHANOOperatorConfig(
                num_parameters=batch["params"].shape[-1],
                num_fields=batch["fields_sequence"].shape[-1],
                spatial_dim=batch["coords"].shape[-1],
                history_dim=batch["material_history_sequence"].shape[-1],
                hidden_dim=16,
                window_size=2,
                num_attention_heads=1,
                num_spectral_modes=2,
            ),
        ),
        (
            WindowedHistoryOperator,
            WindowedHistoryOperatorConfig(
                num_parameters=batch["params"].shape[-1],
                num_fields=batch["fields_sequence"].shape[-1],
                spatial_dim=batch["coords"].shape[-1],
                history_dim=batch["material_history_sequence"].shape[-1],
                hidden_dim=16,
                window_size=2,
            ),
        ),
        (
            NeuralCDEPathOperator,
            NeuralCDEPathOperatorConfig(
                num_parameters=batch["params"].shape[-1],
                num_fields=batch["fields_sequence"].shape[-1],
                spatial_dim=batch["coords"].shape[-1],
                history_dim=batch["material_history_sequence"].shape[-1],
                hidden_dim=16,
                thermo_hard_j2_return=True,
            ),
        ),
    ]
    for model_cls, config in configs_and_models:
        model = model_cls(config)
        model_kwargs = {
            "connectivity": connectivity,
            "teacher_history": batch["material_history_sequence"],
            "teacher_forcing_ratio": 0.25,
        }
        if model_cls is FaithfulHANOOperator:
            model_kwargs["teacher_strain"] = batch.get("strain_sequence")
            model_kwargs["teacher_stress"] = batch.get("stress_sequence")
        outputs = model(
            batch["coords"],
            batch["params"],
            batch["forcing_sequence"],
            **model_kwargs,
        )
        assert outputs["mean_sequence"].shape == batch["fields_sequence"].shape
        assert outputs["history_sequence"].shape == batch["material_history_sequence"].shape
        losses = history_graph_operator_loss(outputs, batch)
        assert torch.isfinite(losses["total"])
        if "hano_strain_sequence" in outputs:
            assert outputs["hano_strain_sequence"].shape == batch["strain_sequence"].shape
            assert outputs["hano_stress_sequence"].shape == batch["stress_sequence"].shape
            supervised_losses = history_graph_operator_loss(
                outputs,
                batch,
                PathLossWeights(hano_strain=0.25, hano_stress=0.25, calibration=0.0),
            )
            assert torch.isfinite(supervised_losses["hano_strain"])
            assert torch.isfinite(supervised_losses["hano_stress"])
