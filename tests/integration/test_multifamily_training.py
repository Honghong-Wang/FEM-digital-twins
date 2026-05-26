from __future__ import annotations

import torch

from pcgno_dt.data.datasets import OperatorTensorDataset
from pcgno_dt.data.multifamily import build_multifamily_tensors
from pcgno_dt.data.synthetic import generate_operator_dataset
from pcgno_dt.evaluation.comparison import evaluate_prediction
from pcgno_dt.models.pcgno import PCGNOConfig, PhysicsConstrainedGenerativeNeuralOperator
from pcgno_dt.physics.structural import NonlinearElasticBarProblem
from pcgno_dt.physics.thermo_mechanical import ThermoMechanicalBarProblem
from pcgno_dt.training.losses import multifamily_physics_constrained_loss


def test_multifamily_padding_masks_and_physics_loss() -> None:
    structural = NonlinearElasticBarProblem(num_points=24)
    thermo = ThermoMechanicalBarProblem(num_points=24)
    structural_data = generate_operator_dataset(structural, n_samples=3, split="train", seed=21)
    thermo_data = generate_operator_dataset(thermo, n_samples=3, split="train", seed=22)
    tensors, spec = build_multifamily_tensors([structural_data, thermo_data])
    dataset = OperatorTensorDataset(tensors)

    assert len(dataset) == 6
    assert spec.max_parameters == thermo.num_parameters
    assert spec.max_fields == thermo.num_fields
    assert tensors["params"].shape == (6, spec.max_parameters)
    assert tensors["fields"].shape == (6, spec.num_points, spec.max_fields)
    assert torch.all(tensors["field_mask"][:3, :, 1] == 0.0)
    assert torch.all(tensors["field_mask"][3:, :, 1] == 1.0)

    model = PhysicsConstrainedGenerativeNeuralOperator(
        PCGNOConfig(
            num_parameters=spec.max_parameters,
            num_fields=spec.max_fields,
            hidden_dim=24,
            latent_dim=4,
        )
    )
    outputs = model(tensors["coords"], tensors["params"], n_samples=4)
    losses = multifamily_physics_constrained_loss(
        outputs,
        tensors,
        problems_by_family={0: structural, 1: thermo},
    )
    losses["total"].backward()
    assert torch.isfinite(losses["total"])

    metrics = evaluate_prediction(
        outputs["mean"],
        tensors["fields"],
        outputs["samples"],
        field_mask=tensors["field_mask"],
    )
    assert {"relative_l2", "max_abs_error", "coverage_95", "ece"}.issubset(metrics)
    assert {"crps", "sharpness", "interval_width_95"}.issubset(metrics)
    assert torch.isfinite(metrics["relative_l2"])
