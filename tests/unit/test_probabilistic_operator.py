from __future__ import annotations

import torch

from pcgno_dt.data.synthetic import generate_coupled_pde_dataset
from pcgno_dt.models.pcgno import PCGNOConfig, PhysicsConstrainedGenerativeNeuralOperator
from pcgno_dt.physics.manufactured import CoupledPDEProblem
from pcgno_dt.training.losses import PhysicsLossWeights, physics_constrained_loss
from pcgno_dt.uq.calibration import expected_calibration_error, predictive_interval


def test_pcgno_outputs_probabilistic_fields_and_loss_backward() -> None:
    problem = CoupledPDEProblem(num_points=32)
    data = generate_coupled_pde_dataset(problem, n_samples=4, split="train", seed=3)
    batch = {key: value for key, value in data.items() if isinstance(value, torch.Tensor)}
    model = PhysicsConstrainedGenerativeNeuralOperator(
        PCGNOConfig(num_parameters=problem.num_parameters, hidden_dim=24, latent_dim=4)
    )

    outputs = model(batch["coords"], batch["params"], n_samples=5)
    assert outputs["mean"].shape == batch["fields"].shape
    assert outputs["logvar"].shape == batch["fields"].shape
    assert outputs["samples"].shape == (4, 5, 32, problem.num_fields)

    losses = physics_constrained_loss(outputs, batch, problem)
    mse_losses = physics_constrained_loss(outputs, batch, problem, PhysicsLossWeights(data_loss_mode="mse"))
    assert torch.isfinite(mse_losses["data"])
    assert torch.isfinite(mse_losses["calibration"])
    losses["total"].backward()

    lower, upper = predictive_interval(outputs["samples"], level=0.8)
    assert lower.shape == batch["fields"].shape
    assert upper.shape == batch["fields"].shape
    assert torch.isfinite(expected_calibration_error(outputs["samples"], batch["fields"]))
