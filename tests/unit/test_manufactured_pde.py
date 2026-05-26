from __future__ import annotations

import torch

from pcgno_dt.data.synthetic import generate_coupled_pde_dataset
from pcgno_dt.physics.manufactured import CoupledPDEProblem


def test_manufactured_solution_satisfies_analytic_residual_and_boundary_conditions() -> None:
    problem = CoupledPDEProblem(num_points=64)
    data = generate_coupled_pde_dataset(problem, n_samples=3, split="train", seed=7)

    residual = problem.residual(
        data["params"],
        data["fields"],
        forcing=data["forcing"],
        use_finite_difference=False,
    )
    boundary = problem.boundary_residual(data["params"], data["fields"])

    assert torch.max(torch.abs(residual)).item() < 1.0e-5
    assert torch.max(torch.abs(boundary)).item() < 1.0e-6


def test_dataset_contains_ood_splits() -> None:
    problem = CoupledPDEProblem(num_points=16)
    for split in ("train", "test", "ood_material", "ood_boundary", "ood_loading"):
        data = generate_coupled_pde_dataset(problem, n_samples=2, split=split, seed=1)
        assert data["coords"].shape == (2, 16, 1)
        assert data["params"].shape == (2, problem.num_parameters)
        assert data["fields"].shape == (2, 16, problem.num_fields)
        assert data["forcing"].shape == (2, 16, problem.num_fields)
