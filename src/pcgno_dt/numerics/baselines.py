from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import torch

from pcgno_dt.models.pcgno import DeterministicDeepONet
from pcgno_dt.models.fno import FourierNeuralOperator1D, FourierNeuralOperator2D
from pcgno_dt.models.pinn import PointwisePINN
from pcgno_dt.physics.manufactured import CoupledPDEProblem


class OperatorBaseline(Protocol):
    name: str

    def predict(self, coords: torch.Tensor, params: torch.Tensor) -> torch.Tensor:
        """Return field predictions shaped [batch, points, channels]."""


@dataclass
class HighFidelityManufacturedBaseline:
    """High-fidelity placeholder backed by the manufactured exact solution."""

    problem: CoupledPDEProblem
    name: str = "manufactured_fem_reference"

    def predict(self, coords: torch.Tensor, params: torch.Tensor) -> torch.Tensor:
        del coords
        return self.problem.exact_solution(params)


@dataclass
class PODROMBaseline:
    """Small POD + least-squares regression baseline for systematic comparisons."""

    rank: int = 8
    ridge: float = 1.0e-6
    name: str = "pod_rom"

    def fit(self, params: torch.Tensor, fields: torch.Tensor) -> "PODROMBaseline":
        flat = fields.flatten(start_dim=1)
        self.mean_ = flat.mean(dim=0, keepdim=True)
        centered = flat - self.mean_
        _, _, vh = torch.linalg.svd(centered, full_matrices=False)
        self.basis_ = vh[: self.rank].T
        coeffs = centered @ self.basis_
        design = torch.cat([torch.ones(params.shape[0], 1, device=params.device), params], dim=1)
        gram = design.T @ design + self.ridge * torch.eye(
            design.shape[1], device=params.device, dtype=params.dtype
        )
        self.weights_ = torch.linalg.solve(gram, design.T @ coeffs)
        self.field_shape_ = fields.shape[1:]
        return self

    def predict(self, coords: torch.Tensor, params: torch.Tensor) -> torch.Tensor:
        del coords
        design = torch.cat([torch.ones(params.shape[0], 1, device=params.device), params], dim=1)
        coeffs = design @ self.weights_
        flat = self.mean_ + coeffs @ self.basis_.T
        return flat.view(params.shape[0], *self.field_shape_)


class DeepONetBaseline(torch.nn.Module):
    name = "deeponet"

    def __init__(self, num_parameters: int, num_fields: int = 2, spatial_dim: int = 1) -> None:
        super().__init__()
        self.model = DeterministicDeepONet(
            num_parameters=num_parameters,
            num_fields=num_fields,
            spatial_dim=spatial_dim,
        )

    def forward(self, coords: torch.Tensor, params: torch.Tensor) -> dict[str, torch.Tensor]:
        return self.model(coords, params)

    def predict(self, coords: torch.Tensor, params: torch.Tensor) -> torch.Tensor:
        return self.forward(coords, params)["mean"]


class PINNBaseline(torch.nn.Module):
    name = "pinn"

    def __init__(self, num_parameters: int, num_fields: int = 2, spatial_dim: int = 1) -> None:
        super().__init__()
        self.model = PointwisePINN(
            num_parameters=num_parameters,
            num_fields=num_fields,
            spatial_dim=spatial_dim,
        )

    def forward(self, coords: torch.Tensor, params: torch.Tensor) -> dict[str, torch.Tensor]:
        return self.model(coords, params)

    def predict(self, coords: torch.Tensor, params: torch.Tensor) -> torch.Tensor:
        return self.forward(coords, params)["mean"]


class FNOBaseline(torch.nn.Module):
    name = "fno"

    def __init__(
        self,
        num_parameters: int,
        num_fields: int = 2,
        spatial_dim: int = 1,
        grid_shape: tuple[int, int] | None = None,
    ) -> None:
        super().__init__()
        if spatial_dim == 1:
            self.model = FourierNeuralOperator1D(num_parameters=num_parameters, num_fields=num_fields)
        elif spatial_dim == 2 and grid_shape is not None:
            self.model = FourierNeuralOperator2D(
                num_parameters=num_parameters,
                num_fields=num_fields,
                grid_shape=grid_shape,
            )
        else:
            raise ValueError("FNOBaseline needs spatial_dim=1 or spatial_dim=2 with grid_shape")

    def forward(self, coords: torch.Tensor, params: torch.Tensor) -> dict[str, torch.Tensor]:
        return self.model(coords, params)

    def predict(self, coords: torch.Tensor, params: torch.Tensor) -> torch.Tensor:
        return self.forward(coords, params)["mean"]


class MeshSampledFNOBaseline(torch.nn.Module):
    """Structured FNO baseline sampled back to an arbitrary FEM mesh.

    This keeps the spectral operator inductive bias of a conventional 2D FNO while making the
    baseline usable on T6/QP complex-geometry meshes whose active node set is not a dense tensor
    grid.  The operator is evaluated on a rectangular latent grid spanning the sample coordinates,
    then transferred to FEM nodes with differentiable RBF interpolation.  It is still a static
    sequence baseline: no path memory or hidden state is exposed to the model.
    """

    name = "mesh_sampled_fno"

    def __init__(
        self,
        num_parameters: int,
        num_fields: int = 2,
        spatial_dim: int = 2,
        grid_shape: tuple[int, int] = (16, 16),
        transfer_temperature: float | None = None,
    ) -> None:
        super().__init__()
        if spatial_dim != 2:
            raise ValueError("MeshSampledFNOBaseline currently supports spatial_dim=2")
        if grid_shape[0] < 2 or grid_shape[1] < 2:
            raise ValueError("grid_shape must have at least two points per axis")
        self.grid_shape = (int(grid_shape[0]), int(grid_shape[1]))
        self.transfer_temperature = transfer_temperature
        self.model = FourierNeuralOperator2D(
            num_parameters=num_parameters,
            num_fields=num_fields,
            grid_shape=self.grid_shape,
        )

    def forward(self, coords: torch.Tensor, params: torch.Tensor) -> dict[str, torch.Tensor]:
        if coords.ndim != 3 or coords.shape[-1] != 2:
            raise ValueError("coords must have shape [batch, points, 2]")
        regular_coords = self._regular_grid(coords)
        grid_values = self.model(regular_coords, params)["mean"]
        transfer = self._rbf_transfer_weights(coords, regular_coords)
        return {"mean": torch.bmm(transfer, grid_values)}

    def predict(self, coords: torch.Tensor, params: torch.Tensor) -> torch.Tensor:
        return self.forward(coords, params)["mean"]

    def _regular_grid(self, coords: torch.Tensor) -> torch.Tensor:
        batch_size = coords.shape[0]
        nx, ny = self.grid_shape
        coord_min = coords.amin(dim=1)
        coord_max = coords.amax(dim=1)
        span = (coord_max - coord_min).clamp_min(1.0e-6)
        x = torch.linspace(0.0, 1.0, nx, device=coords.device, dtype=coords.dtype)
        y = torch.linspace(0.0, 1.0, ny, device=coords.device, dtype=coords.dtype)
        xx, yy = torch.meshgrid(x, y, indexing="ij")
        unit_grid = torch.stack([xx.reshape(-1), yy.reshape(-1)], dim=-1)
        return coord_min[:, None, :] + unit_grid[None, :, :] * span[:, None, :]

    def _rbf_transfer_weights(self, coords: torch.Tensor, regular_coords: torch.Tensor) -> torch.Tensor:
        distances = torch.cdist(coords, regular_coords)
        if self.transfer_temperature is None:
            nx, ny = self.grid_shape
            span = (regular_coords.amax(dim=1) - regular_coords.amin(dim=1)).norm(dim=-1)
            temperature = (span / max(nx, ny)).clamp_min(1.0e-6)
        else:
            temperature = coords.new_full((coords.shape[0],), float(self.transfer_temperature))
        logits = -distances.square() / temperature[:, None, None].square().clamp_min(1.0e-12)
        return torch.softmax(logits, dim=-1)


class MeshGraphOperatorBaseline(torch.nn.Module):
    name = "meshgno"

    def __init__(
        self,
        num_parameters: int,
        num_fields: int = 2,
        spatial_dim: int = 2,
        hidden_dim: int = 64,
        num_layers: int = 3,
        k_neighbors: int = 8,
    ) -> None:
        super().__init__()
        self.k_neighbors = k_neighbors
        self.input = torch.nn.Sequential(
            torch.nn.Linear(spatial_dim + num_parameters, hidden_dim),
            torch.nn.SiLU(),
            torch.nn.Linear(hidden_dim, hidden_dim),
            torch.nn.SiLU(),
        )
        self.updates = torch.nn.ModuleList(
            [
                torch.nn.Sequential(
                    torch.nn.Linear(2 * hidden_dim + spatial_dim, hidden_dim),
                    torch.nn.SiLU(),
                    torch.nn.Linear(hidden_dim, hidden_dim),
                )
                for _ in range(num_layers)
            ]
        )
        self.output = torch.nn.Linear(hidden_dim, num_fields)

    def forward(self, coords: torch.Tensor, params: torch.Tensor) -> dict[str, torch.Tensor]:
        if coords.ndim != 3:
            raise ValueError("coords must have shape [batch, points, spatial_dim]")
        context = params.unsqueeze(1).expand(-1, coords.shape[1], -1)
        h = self.input(torch.cat([coords, context], dim=-1))
        adjacency = _knn_adjacency(coords, self.k_neighbors)
        for update in self.updates:
            messages = torch.bmm(adjacency, h)
            h = h + update(torch.cat([h, messages, coords], dim=-1))
        return {"mean": self.output(h)}

    def predict(self, coords: torch.Tensor, params: torch.Tensor) -> torch.Tensor:
        return self.forward(coords, params)["mean"]


class MeshToMeshGraphOperatorBaseline(torch.nn.Module):
    name = "mesh2meshgno"

    def __init__(
        self,
        num_parameters: int,
        num_fields: int = 2,
        spatial_dim: int = 2,
        hidden_dim: int = 64,
        num_layers: int = 3,
        k_neighbors: int = 8,
        transfer_temperature: float = 0.08,
    ) -> None:
        super().__init__()
        self.k_neighbors = k_neighbors
        self.transfer_temperature = transfer_temperature
        self.source_coords: torch.Tensor | None = None
        self.source_input = torch.nn.Sequential(
            torch.nn.Linear(spatial_dim + num_parameters, hidden_dim),
            torch.nn.SiLU(),
            torch.nn.Linear(hidden_dim, hidden_dim),
            torch.nn.SiLU(),
        )
        self.source_updates = torch.nn.ModuleList(
            [
                torch.nn.Sequential(
                    torch.nn.Linear(2 * hidden_dim + spatial_dim, hidden_dim),
                    torch.nn.SiLU(),
                    torch.nn.Linear(hidden_dim, hidden_dim),
                )
                for _ in range(num_layers)
            ]
        )
        self.target_decoder = torch.nn.Sequential(
            torch.nn.Linear(hidden_dim + spatial_dim + num_parameters, hidden_dim),
            torch.nn.SiLU(),
            torch.nn.Linear(hidden_dim, hidden_dim),
            torch.nn.SiLU(),
            torch.nn.Linear(hidden_dim, num_fields),
        )

    def set_source_coords(self, coords: torch.Tensor) -> None:
        if coords.ndim == 3:
            coords = coords[0]
        self.source_coords = coords.detach().clone()

    def forward(self, coords: torch.Tensor, params: torch.Tensor) -> dict[str, torch.Tensor]:
        if coords.ndim != 3:
            raise ValueError("coords must have shape [batch, points, spatial_dim]")
        if self.source_coords is None:
            self.set_source_coords(coords)
        source_coords = self.source_coords.to(device=coords.device, dtype=coords.dtype)
        source_coords_b = source_coords.unsqueeze(0).expand(params.shape[0], -1, -1)
        context_source = params.unsqueeze(1).expand(-1, source_coords.shape[0], -1)
        h = self.source_input(torch.cat([source_coords_b, context_source], dim=-1))
        adjacency = _knn_adjacency(source_coords_b, self.k_neighbors)
        for update in self.source_updates:
            messages = torch.bmm(adjacency, h)
            h = h + update(torch.cat([h, messages, source_coords_b], dim=-1))
        transfer = _rbf_transfer_weights(
            target_coords=coords,
            source_coords=source_coords_b,
            temperature=self.transfer_temperature,
        )
        target_latent = torch.bmm(transfer, h)
        context_target = params.unsqueeze(1).expand(-1, coords.shape[1], -1)
        return {"mean": self.target_decoder(torch.cat([target_latent, coords, context_target], dim=-1))}

    def predict(self, coords: torch.Tensor, params: torch.Tensor) -> torch.Tensor:
        return self.forward(coords, params)["mean"]


def _knn_adjacency(coords: torch.Tensor, k_neighbors: int) -> torch.Tensor:
    batch, n_points, _ = coords.shape
    if n_points < 2:
        return coords.new_ones(batch, n_points, n_points)
    k = min(k_neighbors + 1, n_points)
    distances = torch.cdist(coords, coords)
    neighbor_idx = distances.topk(k=k, largest=False, dim=-1).indices[..., 1:]
    adjacency = coords.new_zeros(batch, n_points, n_points)
    adjacency.scatter_(dim=2, index=neighbor_idx, value=1.0)
    return adjacency / adjacency.sum(dim=-1, keepdim=True).clamp_min(1.0)


def _rbf_transfer_weights(
    target_coords: torch.Tensor,
    source_coords: torch.Tensor,
    temperature: float,
) -> torch.Tensor:
    distances = torch.cdist(target_coords, source_coords)
    logits = -distances.square() / max(temperature**2, 1.0e-12)
    return torch.softmax(logits, dim=-1)


@dataclass(frozen=True)
class BaselineRegistry:
    """Checklist for the comparison suite expected by the manuscript."""

    include_fem: bool = True
    include_rom: bool = True
    include_pinn: bool = True
    include_deeponet: bool = True
    include_fno: bool = True
    include_mesh_graph_operator: bool = True
    include_mesh_to_mesh_graph_operator: bool = True
    include_probabilistic_operator: bool = True

    def required_names(self) -> tuple[str, ...]:
        names = []
        if self.include_fem:
            names.append("FEM/high-fidelity solver")
        if self.include_rom:
            names.append("ROM/POD/reduced basis")
        if self.include_pinn:
            names.append("PINN")
        if self.include_deeponet:
            names.append("DeepONet")
        if self.include_fno:
            names.append("FNO/neural operator")
        if self.include_mesh_graph_operator:
            names.append("MeshGraph operator")
        if self.include_mesh_to_mesh_graph_operator:
            names.append("Mesh-to-mesh graph operator")
        if self.include_probabilistic_operator:
            names.append("PCGNO/probabilistic operator")
        return tuple(names)
