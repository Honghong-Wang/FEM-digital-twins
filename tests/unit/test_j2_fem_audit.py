from __future__ import annotations

import torch

from pcgno_dt.physics.j2_fem_audit import (
    _audit_step_indices,
    _dense_newton_update_loss,
    j2_fem_audit_loss,
    j2_fem_residual_energy,
    j2_fem_training_loss,
)


def test_j2_fem_audit_supports_t3_and_masks_fixed_edge() -> None:
    coords = torch.tensor([[[0.0, 0.0], [1.0, 0.0], [0.0, 1.0]]])
    fields = torch.tensor([[[0.0, 0.0], [0.01, 0.0], [0.0, -0.005]]])
    forcing = torch.zeros_like(fields)
    params = torch.tensor([[100.0, 0.30, 0.10, 1.0, 0.0, 0.0]])
    connectivity = torch.tensor([[0, 1, 2]])
    plastic = torch.zeros(1, 1, 4)
    history = torch.zeros(1, 1, 5)

    audit = j2_fem_residual_energy(coords, params, fields, forcing, connectivity, plastic, history)

    assert audit["residual"].shape == fields.shape
    assert audit["energy"].shape == (1,)
    assert audit["residual_rms"].shape == (1,)
    assert torch.isfinite(audit["residual"]).all()
    assert torch.isfinite(audit["energy"]).all()
    assert torch.allclose(audit["residual"][:, [0, 2]], torch.zeros(1, 2, 2), atol=1.0e-12)


def test_j2_fem_audit_loss_supports_t6_path_sequence() -> None:
    coords = torch.tensor(
        [
            [
                [0.0, 0.0],
                [1.0, 0.0],
                [0.0, 1.0],
                [0.5, 0.0],
                [0.5, 0.5],
                [0.0, 0.5],
            ]
        ]
    )
    connectivity = torch.tensor([[0, 1, 2, 3, 4, 5]])
    params = torch.tensor([[100.0, 0.30, 0.10, 1.0, 0.0, 0.0]])
    base_fields = torch.stack([0.01 * coords[..., 0], -0.005 * coords[..., 1]], dim=-1)
    fields_sequence = torch.stack([0.5 * base_fields, base_fields], dim=1)
    prediction = 1.05 * fields_sequence
    forcing_sequence = torch.zeros_like(fields_sequence)
    plastic_sequence = torch.zeros(1, 2, 1, 4)
    history_sequence = torch.zeros(1, 2, 1, 5)
    plastic_qp_sequence = torch.zeros(1, 2, 1, 3, 6)
    history_qp_sequence = torch.zeros(1, 2, 1, 3, 5)
    outputs = {"mean_sequence": prediction}
    batch = {
        "coords": coords,
        "params": params,
        "fields_sequence": fields_sequence,
        "forcing_sequence": forcing_sequence,
        "plastic_strain_sequence": plastic_sequence,
        "plastic_strain_qp_sequence": plastic_qp_sequence,
        "material_history_sequence": history_sequence,
        "material_history_qp_sequence": history_qp_sequence,
    }

    losses = j2_fem_audit_loss(
        outputs,
        batch,
        connectivity,
        residual_weight=0.5,
        energy_weight=0.1,
        every_step=True,
    )

    assert set(losses) == {
        "fem_residual",
        "fem_energy",
        "fem_solver_linearized_residual",
        "target_fem_residual",
        "total",
    }
    assert torch.isfinite(losses["total"])
    assert losses["total"].ndim == 0


def test_j2_fem_audit_loss_uses_predicted_history_when_available() -> None:
    coords = torch.tensor([[[0.0, 0.0], [1.0, 0.0], [0.0, 1.0]]])
    connectivity = torch.tensor([[0, 1, 2]])
    params = torch.tensor([[100.0, 0.30, 0.10, 10.0, 0.0, 0.0]])
    fields_sequence = torch.tensor([[[[0.0, 0.0], [0.01, 0.0], [0.0, -0.005]]]])
    forcing_sequence = torch.zeros_like(fields_sequence)
    plastic_sequence = torch.zeros(1, 1, 1, 4)
    history_sequence = torch.zeros(1, 1, 1, 5)
    batch = {
        "coords": coords,
        "params": params,
        "fields_sequence": fields_sequence,
        "forcing_sequence": forcing_sequence,
        "plastic_strain_sequence": plastic_sequence,
        "material_history_sequence": history_sequence,
    }
    base_outputs = {"mean_sequence": fields_sequence, "history_sequence": history_sequence}
    shifted_history = history_sequence.clone()
    shifted_history[..., 0] = 1.0
    shifted_outputs = {"mean_sequence": fields_sequence, "history_sequence": shifted_history}

    base_loss = j2_fem_audit_loss(base_outputs, batch, connectivity, energy_weight=1.0)
    shifted_loss = j2_fem_audit_loss(shifted_outputs, batch, connectivity, energy_weight=1.0)

    assert shifted_loss["fem_energy"] > base_loss["fem_energy"]


def test_j2_fem_audit_reversal_step_policy_selects_turning_points() -> None:
    forcing = torch.zeros(1, 8, 4, 2)
    signal = torch.tensor([0.25, 0.5, 1.0, 0.2, -0.5, 0.2, 1.0, 0.0])
    forcing[0, :, :, 0] = signal[:, None]

    assert _audit_step_indices(forcing, step_policy="final") == (7,)
    assert _audit_step_indices(forcing, step_policy="all") == tuple(range(8))
    assert _audit_step_indices(forcing, step_policy="reversal") == (2, 4, 6)
    assert _audit_step_indices(forcing, step_policy="reversal_final") == (2, 4, 6, 7)


def test_j2_fem_training_loss_backpropagates_all_step_residual_and_energy() -> None:
    coords = torch.tensor([[[0.0, 0.0], [1.0, 0.0], [0.0, 1.0]]])
    connectivity = torch.tensor([[0, 1, 2]])
    params = torch.tensor([[100.0, 0.30, 0.10, 1.0, 0.0, 0.0]])
    base_fields = torch.tensor([[[0.0, 0.0], [0.01, 0.0], [0.0, -0.005]]])
    fields_sequence = torch.stack([0.5 * base_fields, base_fields], dim=1)
    prediction = (1.1 * fields_sequence).clone().requires_grad_(True)
    forcing_sequence = torch.zeros_like(fields_sequence)
    plastic_sequence = torch.zeros(1, 2, 1, 4)
    history_sequence = torch.zeros(1, 2, 1, 5)
    outputs = {"mean_sequence": prediction, "plastic_strain_sequence": plastic_sequence, "history_sequence": history_sequence}
    batch = {
        "coords": coords,
        "params": params,
        "fields_sequence": fields_sequence,
        "forcing_sequence": forcing_sequence,
        "plastic_strain_sequence": plastic_sequence,
        "material_history_sequence": history_sequence,
    }

    losses = j2_fem_training_loss(
        outputs,
        batch,
        connectivity,
        residual_weight=0.5,
        energy_weight=0.1,
        step_policy="all",
    )
    losses["total"].backward()

    assert torch.isfinite(losses["fem_residual"])
    assert torch.isfinite(losses["fem_energy"])
    assert prediction.grad is not None
    assert torch.isfinite(prediction.grad).all()
    assert prediction.grad.abs().sum() > 0.0

    dense_prediction = (1.2 * fields_sequence).clone().requires_grad_(True)
    dense_outputs = {**outputs, "mean_sequence": dense_prediction}
    dense_losses = j2_fem_training_loss(
        dense_outputs,
        batch,
        connectivity,
        residual_weight=0.0,
        energy_weight=0.0,
        solver_weight=1.0,
        solver_mode="dense_newton",
        step_policy="all",
    )
    dense_losses["total"].backward()

    assert torch.isfinite(dense_losses["fem_solver_linearized_residual"])
    assert dense_prediction.grad is not None
    assert torch.isfinite(dense_prediction.grad).all()


def test_j2_fem_training_loss_uses_consistent_tangent_for_solver_loop() -> None:
    coords = torch.tensor([[[0.0, 0.0], [1.0, 0.0], [0.0, 1.0]]])
    connectivity = torch.tensor([[0, 1, 2]])
    params = torch.tensor([[100.0, 0.30, 0.10, 1.0, 0.0, 0.0]])
    fields_sequence = torch.tensor([[[[0.0, 0.0], [0.01, 0.0], [0.0, -0.005]]]])
    prediction = (1.2 * fields_sequence).clone().requires_grad_(True)
    forcing_sequence = torch.zeros_like(fields_sequence)
    plastic_qp_sequence = torch.zeros(1, 1, 1, 1, 4)
    history_qp_sequence = torch.zeros(1, 1, 1, 1, 5)
    stress_qp_sequence = torch.ones(1, 1, 1, 1, 3)
    tangent_qp_sequence = torch.eye(3).reshape(1, 1, 1, 1, 3, 3).expand(1, 1, 1, 1, 3, 3).clone()
    outputs = {
        "mean_sequence": prediction,
        "plastic_strain_qp_sequence": plastic_qp_sequence,
        "history_qp_sequence": history_qp_sequence,
        "j2_qp_stress_sequence": stress_qp_sequence,
        "j2_qp_algorithmic_tangent_sequence": tangent_qp_sequence,
    }
    batch = {
        "coords": coords,
        "params": params,
        "fields_sequence": fields_sequence,
        "forcing_sequence": forcing_sequence,
        "plastic_strain_qp_sequence": plastic_qp_sequence,
        "material_history_qp_sequence": history_qp_sequence,
        "stress_sequence": stress_qp_sequence,
    }

    losses = j2_fem_training_loss(
        outputs,
        batch,
        connectivity,
        residual_weight=0.0,
        energy_weight=0.0,
        solver_weight=1.0,
        step_policy="all",
    )
    losses["total"].backward()

    assert torch.isfinite(losses["fem_solver_linearized_residual"])
    assert losses["fem_solver_linearized_residual"] > 0.0
    assert prediction.grad is not None
    assert torch.isfinite(prediction.grad).all()
    assert prediction.grad.abs().sum() > 0.0


def test_dense_newton_update_loss_supports_multiple_damped_steps() -> None:
    prediction = torch.tensor([[[1.0, -0.5], [0.2, 0.1]]], requires_grad=True)
    target = torch.zeros_like(prediction)
    residual = prediction.detach().clone()
    dofs = residual.numel()
    tangent = torch.eye(dofs).reshape(1, dofs, dofs)

    one_step = _dense_newton_update_loss(
        tangent,
        residual,
        prediction,
        target,
        damping=0.5,
        steps=1,
        regularization=0.0,
        eps=1.0e-12,
    )
    three_steps = _dense_newton_update_loss(
        tangent,
        residual,
        prediction,
        target,
        damping=0.5,
        steps=3,
        regularization=0.0,
        eps=1.0e-12,
    )

    assert torch.isfinite(one_step["loss"])
    assert torch.isfinite(three_steps["loss"])
    assert three_steps["loss"] < one_step["loss"]
    assert three_steps["residual_ratio"].mean() < one_step["residual_ratio"].mean()


def test_dense_newton_line_search_reports_damping_and_rates() -> None:
    prediction = torch.tensor([[[1.0, 0.0], [0.0, 0.0]]], requires_grad=True)
    target = torch.zeros_like(prediction)
    residual = prediction.detach().clone()
    dofs = residual.numel()
    tangent = torch.eye(dofs).reshape(1, dofs, dofs)

    diagnostics = _dense_newton_update_loss(
        tangent,
        residual,
        prediction,
        target,
        damping=1.0,
        steps=2,
        line_search=True,
        line_search_dampings=(1.0, 0.5, 0.25),
        regularization=0.0,
        eps=1.0e-12,
    )

    assert diagnostics["accepted_damping"].shape == (1,)
    assert torch.isfinite(diagnostics["residual_decrease_fraction"]).all()
    assert diagnostics["converged"].item() == 1.0
    assert diagnostics["failed"].item() == 0.0
