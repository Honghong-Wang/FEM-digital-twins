from __future__ import annotations

import torch

from pcgno_dt.data.synthetic import generate_coupled_pde_dataset, sparse_observations
from pcgno_dt.evaluation.comparison import evaluate_prediction
from pcgno_dt.models.pcgno import PCGNOConfig, PhysicsConstrainedGenerativeNeuralOperator
from pcgno_dt.numerics.baselines import (
    BaselineRegistry,
    DeepONetBaseline,
    FNOBaseline,
    HighFidelityManufacturedBaseline,
    PINNBaseline,
    PODROMBaseline,
)
from pcgno_dt.physics.manufactured import CoupledPDEProblem


def test_minimal_operator_pipeline_and_baselines() -> None:
    problem = CoupledPDEProblem(num_points=32)
    train = generate_coupled_pde_dataset(problem, n_samples=10, split="train", seed=4)
    test = generate_coupled_pde_dataset(problem, n_samples=3, split="ood_loading", seed=5)

    fem = HighFidelityManufacturedBaseline(problem)
    fem_prediction = fem.predict(test["coords"], test["params"])
    fem_metrics = evaluate_prediction(fem_prediction, test["fields"])
    assert fem_metrics["relative_l2"].item() < 1.0e-6

    rom = PODROMBaseline(rank=4).fit(train["params"], train["fields"])
    rom_prediction = rom.predict(test["coords"], test["params"])
    assert rom_prediction.shape == test["fields"].shape

    model = PhysicsConstrainedGenerativeNeuralOperator(
        PCGNOConfig(num_parameters=problem.num_parameters, hidden_dim=24, latent_dim=4)
    )
    outputs = model(test["coords"], test["params"], n_samples=4)
    metrics = evaluate_prediction(outputs["mean"], test["fields"], outputs["samples"])
    assert {"relative_l2", "max_abs_error", "coverage_95", "ece"}.issubset(metrics)
    assert {"crps", "sharpness", "interval_width_95"}.issubset(metrics)

    obs = sparse_observations(test["fields"], num_sensors=5, noise_std=0.01, seed=9)
    assert obs["values"].shape == (3, 5, problem.num_fields)

    for baseline in (
        PINNBaseline(problem.num_parameters, problem.num_fields),
        DeepONetBaseline(problem.num_parameters, problem.num_fields),
        FNOBaseline(problem.num_parameters, problem.num_fields),
    ):
        prediction = baseline.predict(test["coords"], test["params"])
        assert prediction.shape == test["fields"].shape

    required = BaselineRegistry().required_names()
    assert "FEM/high-fidelity solver" in required
    assert "DeepONet" in required
    assert "PCGNO/probabilistic operator" in required
