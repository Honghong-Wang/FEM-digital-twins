from __future__ import annotations

import torch

from pcgno_dt.physics.j2_return import (
    DifferentiableJ2PlaneStrainReturnMapping,
    DifferentiableJ2ReturnMapping,
    TrueDifferentiableJ2PlaneStrainReturnMapping,
    j2_yield_residual,
)


def test_differentiable_j2_return_mapping_enforces_scalar_admissibility() -> None:
    layer = DifferentiableJ2ReturnMapping()
    previous = torch.zeros(2, 3, 5, requires_grad=False)
    raw = torch.zeros(2, 3, 5, requires_grad=True)
    raw.data[..., 4] = 2.0
    params = torch.tensor(
        [
            [100.0, 0.30, 0.10, 1.0, 0.0, 0.0],
            [120.0, 0.28, 0.12, 2.0, 0.0, 0.0],
        ],
        dtype=torch.float32,
    )

    projected = layer(previous, raw, params)
    residual = j2_yield_residual(projected, params)
    assert projected.shape == previous.shape
    assert torch.all(projected[..., 0] >= 0.0)
    assert torch.all(projected[..., 1] >= 0.0)
    assert torch.all(projected[..., 2] >= 0.0)
    assert torch.all((projected[..., 3] >= 0.0) & (projected[..., 3] <= 1.0))
    assert torch.all(projected[..., 4] >= 0.0)
    assert torch.max(residual).item() < 1.0e-4

    loss = projected[..., :5].sum()
    loss.backward()
    assert raw.grad is not None
    assert torch.isfinite(raw.grad).all()


def test_plane_strain_j2_return_mapping_uses_trial_stress_and_updates_tensor_history() -> None:
    layer = DifferentiableJ2PlaneStrainReturnMapping()
    strain = torch.tensor([[[0.0040, -0.0010, 0.0010]]], requires_grad=True)
    plastic_old = torch.zeros(1, 1, 3, 3)
    previous_history = torch.zeros(1, 1, 5)
    params = torch.tensor([[100.0, 0.30, 0.10, 1.0, 0.0, 0.0]])

    state = layer(strain, plastic_old, previous_history, params)
    residual = j2_yield_residual(state.history, params)

    assert state.history.shape == previous_history.shape
    assert state.plastic_strain.shape == plastic_old.shape
    assert state.stress_voigt.shape == (1, 1, 3)
    assert state.algorithmic_tangent.shape == (1, 1, 3, 3)
    assert state.yield_function.shape == (1, 1)
    assert torch.all(state.history[..., 2] >= 0.0)
    assert torch.max(residual).item() < 1.0e-4
    assert torch.linalg.norm(state.plastic_strain).item() > 0.0

    state.history[..., :5].sum().backward()
    assert strain.grad is not None
    assert torch.isfinite(strain.grad).all()


def test_true_j2_return_mapping_supports_multi_qp_and_implicit_gradients() -> None:
    layer = TrueDifferentiableJ2PlaneStrainReturnMapping()
    strain = torch.tensor(
        [[[[0.0040, -0.0010, 0.0010], [0.0030, -0.0005, 0.0000], [0.0050, -0.0015, 0.0015]]]],
        requires_grad=True,
    )
    plastic_old = torch.zeros(1, 1, 3, 3, 3)
    previous_history = torch.zeros(1, 1, 3, 5)
    params = torch.tensor([[100.0, 0.30, 0.10, 1.0, 0.0, 0.0]])

    state = layer(strain, plastic_old, previous_history, params)
    residual = j2_yield_residual(state.history, params)

    assert state.history.shape == previous_history.shape
    assert state.plastic_strain.shape == plastic_old.shape
    assert state.stress_voigt.shape == (1, 1, 3, 3)
    assert state.algorithmic_tangent.shape == (1, 1, 3, 3, 3)
    assert state.plastic_multiplier.shape == (1, 1, 3)
    assert state.consistency_residual.shape == (1, 1, 3)
    assert torch.all(state.history[..., 2] >= 0.0)
    active = state.plastic_multiplier > 0.0
    assert torch.max(residual[active]).item() < 1.0e-4
    assert torch.max(state.consistency_residual[active].abs()).item() < 1.0e-4

    loss = state.stress_voigt.square().mean() + state.history[..., :5].sum()
    loss.backward()
    assert strain.grad is not None
    assert torch.isfinite(strain.grad).all()


def test_true_j2_consistent_tangent_matches_autograd_jacobian() -> None:
    layer = TrueDifferentiableJ2PlaneStrainReturnMapping()
    strain = torch.tensor([[[[0.0040, -0.0010, 0.0010]]]], dtype=torch.double, requires_grad=True)
    plastic_old = torch.zeros(1, 1, 1, 3, 3, dtype=torch.double)
    previous_history = torch.zeros(1, 1, 1, 5, dtype=torch.double)
    params = torch.tensor([[100.0, 0.30, 0.10, 1.0, 0.0, 0.0]], dtype=torch.double)

    state = layer(strain, plastic_old, previous_history, params)
    jacobian_rows = []
    for component in range(3):
        grad_output = torch.zeros_like(state.stress_voigt)
        grad_output[..., component] = 1.0
        gradient = torch.autograd.grad(
            state.stress_voigt,
            strain,
            grad_outputs=grad_output,
            retain_graph=True,
        )[0]
        jacobian_rows.append(gradient[0, 0, 0])
    autograd_tangent = torch.stack(jacobian_rows, dim=0)

    assert torch.allclose(state.algorithmic_tangent[0, 0, 0], autograd_tangent, atol=1.0e-8, rtol=1.0e-6)


def test_true_j2_multi_qp_consistent_tangent_matches_autograd_jacobian() -> None:
    layer = TrueDifferentiableJ2PlaneStrainReturnMapping()
    strain = torch.tensor(
        [[[[0.0040, -0.0010, 0.0010], [0.0035, -0.0012, 0.0007], [0.0050, -0.0015, 0.0015]]]],
        dtype=torch.double,
        requires_grad=True,
    )
    plastic_old = torch.zeros(1, 1, 3, 3, 3, dtype=torch.double)
    previous_history = torch.zeros(1, 1, 3, 5, dtype=torch.double)
    params = torch.tensor([[100.0, 0.30, 0.10, 1.0, 0.0, 0.0]], dtype=torch.double)

    state = layer(strain, plastic_old, previous_history, params)
    for qp in range(3):
        jacobian_rows = []
        for component in range(3):
            grad_output = torch.zeros_like(state.stress_voigt)
            grad_output[0, 0, qp, component] = 1.0
            gradient = torch.autograd.grad(
                state.stress_voigt,
                strain,
                grad_outputs=grad_output,
                retain_graph=True,
            )[0]
            jacobian_rows.append(gradient[0, 0, qp])
        autograd_tangent = torch.stack(jacobian_rows, dim=0)
        assert torch.allclose(
            state.algorithmic_tangent[0, 0, qp],
            autograd_tangent,
            atol=1.0e-8,
            rtol=1.0e-6,
        )


def test_true_j2_layer_gradcheck_active_branch() -> None:
    layer = TrueDifferentiableJ2PlaneStrainReturnMapping()
    strain = torch.tensor([[[[0.0040, -0.0010, 0.0010]]]], dtype=torch.double, requires_grad=True)
    plastic_old = torch.zeros(1, 1, 1, 3, 3, dtype=torch.double)
    previous_history = torch.zeros(1, 1, 1, 5, dtype=torch.double)
    params = torch.tensor([[100.0, 0.30, 0.10, 1.0, 0.0, 0.0]], dtype=torch.double)

    def stress_response(strain_value: torch.Tensor) -> torch.Tensor:
        return layer(strain_value, plastic_old, previous_history, params).stress_voigt

    assert torch.autograd.gradcheck(
        stress_response,
        (strain,),
        eps=1.0e-6,
        atol=1.0e-4,
        rtol=1.0e-3,
    )
