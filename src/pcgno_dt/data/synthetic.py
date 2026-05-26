from __future__ import annotations

from dataclasses import dataclass

import torch

from pcgno_dt.physics.manufactured import CoupledPDEProblem
from pcgno_dt.physics.protocols import OperatorProblem
from pcgno_dt.physics.structural import NonlinearElasticBarProblem
from pcgno_dt.physics.thermo_mechanical import ThermoMechanicalBarProblem


@dataclass(frozen=True)
class ParameterRanges:
    lower: tuple[float, ...]
    upper: tuple[float, ...]

    def sample(
        self,
        n_samples: int,
        generator: torch.Generator | None = None,
        device: str = "cpu",
        dtype: torch.dtype = torch.float32,
    ) -> torch.Tensor:
        lower = torch.tensor(self.lower, device=device, dtype=dtype)
        upper = torch.tensor(self.upper, device=device, dtype=dtype)
        values = torch.rand(
            n_samples, lower.numel(), generator=generator, device=device, dtype=dtype
        )
        return lower + values * (upper - lower)


RANGES: dict[str, ParameterRanges] = {
    "train": ParameterRanges(
        lower=(0.55, 0.55, 0.50, 0.50, 0.40, 0.40, -0.10, -0.10, -0.10, -0.10),
        upper=(1.45, 1.45, 1.60, 1.60, 1.20, 1.20, 0.10, 0.10, 0.10, 0.10),
    ),
    "test": ParameterRanges(
        lower=(0.60, 0.60, 0.55, 0.55, 0.45, 0.45, -0.08, -0.08, -0.08, -0.08),
        upper=(1.40, 1.40, 1.55, 1.55, 1.15, 1.15, 0.08, 0.08, 0.08, 0.08),
    ),
    "ood_material": ParameterRanges(
        lower=(1.70, 1.70, 1.80, 1.80, 0.50, 0.50, -0.08, -0.08, -0.08, -0.08),
        upper=(2.30, 2.30, 2.50, 2.50, 1.10, 1.10, 0.08, 0.08, 0.08, 0.08),
    ),
    "ood_boundary": ParameterRanges(
        lower=(0.70, 0.70, 0.70, 0.70, 0.50, 0.50, -0.45, -0.45, -0.45, -0.45),
        upper=(1.30, 1.30, 1.40, 1.40, 1.10, 1.10, 0.45, 0.45, 0.45, 0.45),
    ),
    "ood_loading": ParameterRanges(
        lower=(0.70, 0.70, 0.70, 0.70, 1.45, 1.45, -0.08, -0.08, -0.08, -0.08),
        upper=(1.30, 1.30, 1.40, 1.40, 2.20, 2.20, 0.08, 0.08, 0.08, 0.08),
    ),
}


STRUCTURAL_RANGES: dict[str, ParameterRanges] = {
    "train": ParameterRanges(
        lower=(0.70, 0.10, 0.20, -0.10, -0.05, -0.05),
        upper=(1.60, 0.80, 0.90, 0.35, 0.05, 0.05),
    ),
    "test": ParameterRanges(
        lower=(0.75, 0.12, 0.25, -0.08, -0.04, -0.04),
        upper=(1.50, 0.70, 0.85, 0.30, 0.04, 0.04),
    ),
    "ood_material": ParameterRanges(
        lower=(1.85, 1.00, 0.25, -0.08, -0.04, -0.04),
        upper=(2.60, 1.60, 0.85, 0.30, 0.04, 0.04),
    ),
    "ood_boundary": ParameterRanges(
        lower=(0.85, 0.20, 0.25, -0.08, -0.35, -0.35),
        upper=(1.40, 0.70, 0.85, 0.30, 0.35, 0.35),
    ),
    "ood_loading": ParameterRanges(
        lower=(0.85, 0.20, 1.10, 0.45, -0.04, -0.04),
        upper=(1.40, 0.70, 1.80, 0.90, 0.04, 0.04),
    ),
}


THERMO_MECHANICAL_RANGES: dict[str, ParameterRanges] = {
    "train": ParameterRanges(
        lower=(0.80, 0.50, 0.05, 0.55, 0.25, 0.20, -0.05, -0.05, -0.05, -0.05),
        upper=(1.70, 1.40, 0.35, 1.60, 0.90, 0.85, 0.05, 0.05, 0.05, 0.05),
    ),
    "test": ParameterRanges(
        lower=(0.85, 0.55, 0.06, 0.60, 0.30, 0.25, -0.04, -0.04, -0.04, -0.04),
        upper=(1.60, 1.30, 0.30, 1.50, 0.85, 0.80, 0.04, 0.04, 0.04, 0.04),
    ),
    "ood_material": ParameterRanges(
        lower=(1.90, 1.60, 0.05, 1.80, 0.30, 0.25, -0.04, -0.04, -0.04, -0.04),
        upper=(2.60, 2.30, 0.45, 2.60, 0.85, 0.80, 0.04, 0.04, 0.04, 0.04),
    ),
    "ood_boundary": ParameterRanges(
        lower=(0.90, 0.65, 0.06, 0.70, 0.30, 0.25, -0.30, -0.30, -0.30, -0.30),
        upper=(1.50, 1.25, 0.30, 1.40, 0.85, 0.80, 0.30, 0.30, 0.30, 0.30),
    ),
    "ood_loading": ParameterRanges(
        lower=(0.90, 0.65, 0.06, 0.70, 1.10, 1.05, -0.04, -0.04, -0.04, -0.04),
        upper=(1.50, 1.25, 0.30, 1.40, 1.80, 1.70, 0.04, 0.04, 0.04, 0.04),
    ),
}


BENCHMARK_RANGES: dict[type[object], dict[str, ParameterRanges]] = {
    CoupledPDEProblem: RANGES,
    NonlinearElasticBarProblem: STRUCTURAL_RANGES,
    ThermoMechanicalBarProblem: THERMO_MECHANICAL_RANGES,
}


def generate_operator_dataset(
    problem: OperatorProblem,
    n_samples: int,
    split: str = "train",
    seed: int = 0,
    ranges: dict[str, ParameterRanges] | None = None,
) -> dict[str, torch.Tensor | str | tuple[str, ...]]:
    """Generate a manufactured dataset through the common operator protocol."""

    if ranges is None:
        ranges = BENCHMARK_RANGES.get(type(problem))
    if ranges is None:
        raise KeyError(
            f"no parameter ranges registered for {type(problem).__name__}; pass ranges explicitly"
        )
    if split not in ranges:
        raise KeyError(f"unknown split {split!r}; options are {sorted(ranges)}")

    generator = torch.Generator(device=problem.device).manual_seed(seed)  # type: ignore[attr-defined]
    params = ranges[split].sample(
        n_samples,
        generator=generator,
        device=problem.device,  # type: ignore[attr-defined]
        dtype=problem.dtype,  # type: ignore[attr-defined]
    )
    coords = problem.grid(n_samples)
    fields = problem.exact_solution(params)  # type: ignore[attr-defined]
    forcing = problem.forcing(params)  # type: ignore[attr-defined]
    return {
        "coords": coords,
        "params": params,
        "fields": fields,
        "forcing": forcing,
        "split": split,
        "family": type(problem).__name__,
        "parameter_names": problem.parameter_names,
    }


def generate_coupled_pde_dataset(
    problem: CoupledPDEProblem,
    n_samples: int,
    split: str = "train",
    seed: int = 0,
) -> dict[str, torch.Tensor | str | tuple[str, ...]]:
    """Generate a manufactured operator-learning dataset."""

    return generate_operator_dataset(problem, n_samples=n_samples, split=split, seed=seed, ranges=RANGES)


def sparse_observations(
    fields: torch.Tensor,
    num_sensors: int,
    noise_std: float = 0.0,
    seed: int = 0,
) -> dict[str, torch.Tensor]:
    """Extract sparse observations from field data."""

    if fields.ndim != 3:
        raise ValueError("fields must have shape [batch, points, channels]")
    if num_sensors < 1 or num_sensors > fields.shape[1]:
        raise ValueError("num_sensors must be within [1, num_points]")

    generator = torch.Generator(device=fields.device).manual_seed(seed)
    sensor_idx = torch.linspace(0, fields.shape[1] - 1, num_sensors, device=fields.device)
    sensor_idx = sensor_idx.round().long().unique()
    values = fields.index_select(dim=1, index=sensor_idx)
    if noise_std > 0.0:
        values = values + noise_std * torch.randn(
            values.shape, generator=generator, device=fields.device, dtype=fields.dtype
        )
    return {"sensor_idx": sensor_idx, "values": values}
