from __future__ import annotations

import torch

from pcgno_dt.data.synthetic import generate_operator_dataset
from pcgno_dt.models.pcgno import PCGNOConfig, PhysicsConstrainedGenerativeNeuralOperator
from pcgno_dt.physics.structural import NonlinearElasticBarProblem
from pcgno_dt.physics.thermo_mechanical import ThermoMechanicalBarProblem
from pcgno_dt.training.losses import physics_constrained_loss


def test_nonlinear_structural_family_uses_common_operator_protocol() -> None:
    problem = NonlinearElasticBarProblem(num_points=48)
    data = generate_operator_dataset(problem, n_samples=4, split="train", seed=11)
    residual = problem.residual(
        data["params"],
        data["fields"],
        forcing=data["forcing"],
        use_finite_difference=False,
    )
    boundary = problem.boundary_residual(data["params"], data["fields"])

    assert data["coords"].shape == (4, 48, 1)
    assert data["fields"].shape == (4, 48, 1)
    assert data["forcing"].shape == (4, 48, 1)
    assert torch.max(torch.abs(residual)).item() < 1.0e-6
    assert torch.max(torch.abs(boundary)).item() < 1.0e-6


def test_thermo_mechanical_family_uses_common_operator_protocol() -> None:
    problem = ThermoMechanicalBarProblem(num_points=48)
    data = generate_operator_dataset(problem, n_samples=4, split="ood_material", seed=13)
    residual = problem.residual(
        data["params"],
        data["fields"],
        forcing=data["forcing"],
        use_finite_difference=False,
    )
    boundary = problem.boundary_residual(data["params"], data["fields"])

    assert data["coords"].shape == (4, 48, 1)
    assert data["fields"].shape == (4, 48, 2)
    assert data["forcing"].shape == (4, 48, 2)
    assert torch.max(torch.abs(residual)).item() < 1.0e-6
    assert torch.max(torch.abs(boundary)).item() < 1.0e-6


def test_physics_constrained_loss_accepts_structural_problem() -> None:
    problem = NonlinearElasticBarProblem(num_points=24)
    data = generate_operator_dataset(problem, n_samples=3, split="test", seed=17)
    batch = {key: value for key, value in data.items() if isinstance(value, torch.Tensor)}
    model = PhysicsConstrainedGenerativeNeuralOperator(
        PCGNOConfig(
            num_parameters=problem.num_parameters,
            num_fields=problem.num_fields,
            hidden_dim=24,
            latent_dim=4,
        )
    )

    outputs = model(batch["coords"], batch["params"], n_samples=2)
    losses = physics_constrained_loss(outputs, batch, problem)
    losses["total"].backward()
    assert torch.isfinite(losses["total"])
