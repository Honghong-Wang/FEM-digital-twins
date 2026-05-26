from __future__ import annotations

import argparse
import sys
from pathlib import Path

import torch
from torch.utils.data import DataLoader

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pcgno_dt.data.datasets import OperatorTensorDataset
from pcgno_dt.data.multifamily import build_multifamily_tensors
from pcgno_dt.data.synthetic import generate_operator_dataset, sparse_observations
from pcgno_dt.evaluation.comparison import evaluate_prediction
from pcgno_dt.models.pcgno import PCGNOConfig, PhysicsConstrainedGenerativeNeuralOperator
from pcgno_dt.numerics.baselines import BaselineRegistry, HighFidelityManufacturedBaseline, PODROMBaseline
from pcgno_dt.physics.manufactured import CoupledPDEProblem
from pcgno_dt.physics.structural import NonlinearElasticBarProblem
from pcgno_dt.physics.thermo_mechanical import ThermoMechanicalBarProblem
from pcgno_dt.training.losses import (
    PhysicsLossWeights,
    multifamily_physics_constrained_loss,
    physics_constrained_loss,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a minimal PCGNO operator-learning demo.")
    parser.add_argument("--epochs", type=int, default=5)
    parser.add_argument("--num-points", type=int, default=64)
    parser.add_argument("--train-samples", type=int, default=48)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument(
        "--family",
        choices=("coupled", "structural", "thermo", "multifamily"),
        default="coupled",
    )
    args = parser.parse_args()

    torch.manual_seed(20260516)
    if args.family == "multifamily":
        _run_multifamily_demo(args)
        return

    problem = _make_problem(args.family, args.num_points)
    train = generate_operator_dataset(problem, args.train_samples, split="train", seed=1)
    test = generate_operator_dataset(problem, 16, split="test", seed=2)
    ood = generate_operator_dataset(problem, 16, split="ood_loading", seed=3)

    train_tensors = {key: value for key, value in train.items() if isinstance(value, torch.Tensor)}
    loader = DataLoader(OperatorTensorDataset(train_tensors), batch_size=args.batch_size, shuffle=True)

    model = PhysicsConstrainedGenerativeNeuralOperator(
        PCGNOConfig(
            num_parameters=problem.num_parameters,
            num_fields=problem.num_fields,
            hidden_dim=64,
            latent_dim=8,
        )
    )
    optimizer = torch.optim.Adam(model.parameters(), lr=1.0e-3)
    weights = PhysicsLossWeights(data=1.0, pde_residual=1.0e-3, boundary=0.1, energy=1.0e-4)

    for epoch in range(args.epochs):
        running = 0.0
        for batch in loader:
            optimizer.zero_grad()
            outputs = model(batch["coords"], batch["params"], n_samples=0)
            losses = physics_constrained_loss(outputs, batch, problem, weights)
            losses["total"].backward()
            optimizer.step()
            running += float(losses["total"].detach())
        print(f"epoch={epoch + 1:03d} loss={running / max(len(loader), 1):.6f}")

    for split_name, data in (("test", test), ("ood_loading", ood)):
        outputs = model(data["coords"], data["params"], n_samples=16)
        metrics = evaluate_prediction(outputs["mean"], data["fields"], outputs["samples"])
        printable = {key: float(value.detach()) for key, value in metrics.items()}
        print(f"{split_name}: {printable}")

    fem = HighFidelityManufacturedBaseline(problem)
    rom = PODROMBaseline(rank=8).fit(train["params"], train["fields"])
    fem_error = evaluate_prediction(fem.predict(test["coords"], test["params"]), test["fields"])
    rom_error = evaluate_prediction(rom.predict(test["coords"], test["params"]), test["fields"])
    print("baseline_registry:", BaselineRegistry().required_names())
    print("fem_reference:", {key: float(value.detach()) for key, value in fem_error.items()})
    print("pod_rom:", {key: float(value.detach()) for key, value in rom_error.items()})

    observations = sparse_observations(test["fields"], num_sensors=6, noise_std=0.01, seed=4)
    print("sparse_observation_shape:", tuple(observations["values"].shape))
    print("project_root:", PROJECT_ROOT)


def _run_multifamily_demo(args: argparse.Namespace) -> None:
    problems = (
        NonlinearElasticBarProblem(num_points=args.num_points),
        ThermoMechanicalBarProblem(num_points=args.num_points),
    )
    train_tensors, spec = build_multifamily_tensors(
        [generate_operator_dataset(problem, args.train_samples, split="train", seed=i + 1) for i, problem in enumerate(problems)]
    )
    test_tensors, _ = build_multifamily_tensors(
        [generate_operator_dataset(problem, 16, split="test", seed=i + 11) for i, problem in enumerate(problems)],
        spec=spec,
    )
    ood_tensors, _ = build_multifamily_tensors(
        [
            generate_operator_dataset(problem, 16, split="ood_loading", seed=i + 21)
            for i, problem in enumerate(problems)
        ],
        spec=spec,
    )

    loader = DataLoader(OperatorTensorDataset(train_tensors), batch_size=args.batch_size, shuffle=True)
    model = PhysicsConstrainedGenerativeNeuralOperator(
        PCGNOConfig(
            num_parameters=spec.max_parameters,
            num_fields=spec.max_fields,
            hidden_dim=64,
            latent_dim=8,
        )
    )
    optimizer = torch.optim.Adam(model.parameters(), lr=1.0e-3)
    weights = PhysicsLossWeights(data=1.0, pde_residual=1.0e-3, boundary=0.1, energy=1.0e-4)
    problem_map = {index: problem for index, problem in enumerate(problems)}

    for epoch in range(args.epochs):
        running = 0.0
        for batch in loader:
            optimizer.zero_grad()
            outputs = model(batch["coords"], batch["params"], n_samples=0)
            losses = multifamily_physics_constrained_loss(outputs, batch, problem_map, weights)
            losses["total"].backward()
            optimizer.step()
            running += float(losses["total"].detach())
        print(f"epoch={epoch + 1:03d} multifamily_loss={running / max(len(loader), 1):.6f}")

    for split_name, tensors in (("test", test_tensors), ("ood_loading", ood_tensors)):
        outputs = model(tensors["coords"], tensors["params"], n_samples=16)
        metrics = evaluate_prediction(
            outputs["mean"],
            tensors["fields"],
            outputs["samples"],
            field_mask=tensors["field_mask"],
        )
        printable = {key: float(value.detach()) for key, value in metrics.items()}
        print(f"{split_name}: {printable}")

    observations = sparse_observations(test_tensors["fields"], num_sensors=6, noise_std=0.01, seed=4)
    print("family_names:", spec.family_names)
    print("baseline_registry:", BaselineRegistry().required_names())
    print("sparse_observation_shape:", tuple(observations["values"].shape))
    print("project_root:", PROJECT_ROOT)


def _make_problem(family: str, num_points: int):
    if family == "coupled":
        return CoupledPDEProblem(num_points=num_points)
    if family == "structural":
        return NonlinearElasticBarProblem(num_points=num_points)
    if family == "thermo":
        return ThermoMechanicalBarProblem(num_points=num_points)
    raise ValueError(f"unknown benchmark family: {family}")


if __name__ == "__main__":
    main()
