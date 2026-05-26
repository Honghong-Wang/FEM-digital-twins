from __future__ import annotations

import torch
from torch import nn
import torch.nn.functional as F


class SpectralConv1d(nn.Module):
    def __init__(self, in_channels: int, out_channels: int, modes: int) -> None:
        super().__init__()
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.modes = modes
        scale = 1.0 / max(1, in_channels * out_channels)
        self.weights = nn.Parameter(
            scale * torch.randn(in_channels, out_channels, modes, dtype=torch.cfloat)
        )

    def forward(self, values: torch.Tensor) -> torch.Tensor:
        batch_size, _, num_points = values.shape
        values_ft = torch.fft.rfft(values)
        out_ft = torch.zeros(
            batch_size,
            self.out_channels,
            values_ft.shape[-1],
            device=values.device,
            dtype=torch.cfloat,
        )
        modes = min(self.modes, values_ft.shape[-1])
        out_ft[:, :, :modes] = torch.einsum(
            "bim,iom->bom", values_ft[:, :, :modes], self.weights[:, :, :modes]
        )
        return torch.fft.irfft(out_ft, n=num_points)


class FourierNeuralOperator1D(nn.Module):
    """Compact FNO baseline for 1D operator-learning benchmarks."""

    def __init__(
        self,
        num_parameters: int,
        num_fields: int = 2,
        width: int = 48,
        modes: int = 12,
        depth: int = 3,
    ) -> None:
        super().__init__()
        self.lift = nn.Linear(1 + num_parameters, width)
        self.spectral_layers = nn.ModuleList([SpectralConv1d(width, width, modes) for _ in range(depth)])
        self.local_layers = nn.ModuleList([nn.Conv1d(width, width, kernel_size=1) for _ in range(depth)])
        self.project = nn.Sequential(nn.Linear(width, width), nn.GELU(), nn.Linear(width, num_fields))

    def forward(self, coords: torch.Tensor, params: torch.Tensor) -> dict[str, torch.Tensor]:
        expanded_params = params.unsqueeze(1).expand(-1, coords.shape[1], -1)
        values = self.lift(torch.cat([coords, expanded_params], dim=-1)).transpose(1, 2)
        for spectral, local in zip(self.spectral_layers, self.local_layers):
            values = F.gelu(spectral(values) + local(values))
        return {"mean": self.project(values.transpose(1, 2))}


class SpectralConv2d(nn.Module):
    def __init__(self, in_channels: int, out_channels: int, modes_x: int, modes_y: int) -> None:
        super().__init__()
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.modes_x = modes_x
        self.modes_y = modes_y
        scale = 1.0 / max(1, in_channels * out_channels)
        self.weights = nn.Parameter(
            scale * torch.randn(in_channels, out_channels, modes_x, modes_y, dtype=torch.cfloat)
        )

    def forward(self, values: torch.Tensor) -> torch.Tensor:
        batch_size, _, nx, ny = values.shape
        values_ft = torch.fft.rfft2(values, dim=(-2, -1))
        out_ft = torch.zeros(
            batch_size,
            self.out_channels,
            values_ft.shape[-2],
            values_ft.shape[-1],
            device=values.device,
            dtype=torch.cfloat,
        )
        modes_x = min(self.modes_x, values_ft.shape[-2])
        modes_y = min(self.modes_y, values_ft.shape[-1])
        out_ft[:, :, :modes_x, :modes_y] = torch.einsum(
            "bixy,ioxy->boxy",
            values_ft[:, :, :modes_x, :modes_y],
            self.weights[:, :, :modes_x, :modes_y],
        )
        return torch.fft.irfft2(out_ft, s=(nx, ny), dim=(-2, -1))


class FourierNeuralOperator2D(nn.Module):
    """Compact 2D FNO baseline for structured FEM snapshot grids."""

    def __init__(
        self,
        num_parameters: int,
        grid_shape: tuple[int, int],
        num_fields: int = 2,
        width: int = 32,
        modes_x: int = 8,
        modes_y: int = 8,
        depth: int = 3,
    ) -> None:
        super().__init__()
        self.grid_shape = grid_shape
        self.lift = nn.Linear(2 + num_parameters, width)
        self.spectral_layers = nn.ModuleList(
            [SpectralConv2d(width, width, modes_x, modes_y) for _ in range(depth)]
        )
        self.local_layers = nn.ModuleList([nn.Conv2d(width, width, kernel_size=1) for _ in range(depth)])
        self.project = nn.Sequential(nn.Linear(width, width), nn.GELU(), nn.Linear(width, num_fields))

    def forward(self, coords: torch.Tensor, params: torch.Tensor) -> dict[str, torch.Tensor]:
        nx, ny = self.grid_shape
        if coords.shape[1] != nx * ny or coords.shape[-1] != 2:
            raise ValueError("2D FNO expects flattened structured coords [batch, nx*ny, 2]")
        expanded_params = params.unsqueeze(1).expand(-1, coords.shape[1], -1)
        values = self.lift(torch.cat([coords, expanded_params], dim=-1))
        values = values.view(coords.shape[0], nx, ny, -1).permute(0, 3, 1, 2)
        for spectral, local in zip(self.spectral_layers, self.local_layers):
            values = F.gelu(spectral(values) + local(values))
        values = values.permute(0, 2, 3, 1).reshape(coords.shape[0], nx * ny, -1)
        return {"mean": self.project(values)}
