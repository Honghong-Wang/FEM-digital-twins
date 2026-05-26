from __future__ import annotations

from dataclasses import dataclass

import torch
from torch import nn


@dataclass(frozen=True)
class PCGNOConfig:
    num_parameters: int
    num_fields: int = 2
    spatial_dim: int = 1
    hidden_dim: int = 96
    latent_dim: int = 16
    num_fourier_modes: int = 8
    min_log_variance: float = -8.0
    max_log_variance: float = 4.0


class FourierFeatures(nn.Module):
    def __init__(self, num_modes: int, spatial_dim: int = 1) -> None:
        super().__init__()
        self.num_modes = num_modes
        self.spatial_dim = spatial_dim

    @property
    def output_dim(self) -> int:
        return self.spatial_dim * (1 + 2 * self.num_modes)

    def forward(self, coords: torch.Tensor) -> torch.Tensor:
        modes = torch.arange(1, self.num_modes + 1, device=coords.device, dtype=coords.dtype)
        angles = torch.pi * coords.unsqueeze(-1) * modes.view(1, 1, 1, -1)
        sin = torch.sin(angles).flatten(start_dim=-2)
        cos = torch.cos(angles).flatten(start_dim=-2)
        return torch.cat([coords, sin, cos], dim=-1)


class MLP(nn.Module):
    def __init__(self, input_dim: int, hidden_dim: int, output_dim: int, depth: int = 3) -> None:
        super().__init__()
        layers: list[nn.Module] = []
        current = input_dim
        for _ in range(depth - 1):
            layers.extend([nn.Linear(current, hidden_dim), nn.GELU()])
            current = hidden_dim
        layers.append(nn.Linear(current, output_dim))
        self.net = nn.Sequential(*layers)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


class PhysicsConstrainedGenerativeNeuralOperator(nn.Module):
    """Small conditional probabilistic neural operator.

    This is a local implementation inspired by neural-operator, probabilistic-operator, and
    diffusion-operator patterns, but it does not vendor external project code.
    """

    def __init__(self, config: PCGNOConfig) -> None:
        super().__init__()
        self.config = config
        self.features = FourierFeatures(config.num_fourier_modes, spatial_dim=config.spatial_dim)
        self.context = MLP(config.num_parameters, config.hidden_dim, config.hidden_dim)
        point_dim = self.features.output_dim + config.hidden_dim
        self.mean_head = MLP(point_dim, config.hidden_dim, config.num_fields)
        self.logvar_head = MLP(point_dim, config.hidden_dim, config.num_fields)
        self.latent_basis = MLP(point_dim, config.hidden_dim, config.num_fields * config.latent_dim)

    def forward(
        self,
        coords: torch.Tensor,
        params: torch.Tensor,
        n_samples: int = 0,
        latent: torch.Tensor | None = None,
    ) -> dict[str, torch.Tensor]:
        if coords.ndim != 3 or coords.shape[-1] != self.config.spatial_dim:
            raise ValueError(
                f"coords must have shape [batch, points, {self.config.spatial_dim}]"
            )
        if params.ndim != 2 or params.shape[-1] != self.config.num_parameters:
            raise ValueError(f"params must have shape [batch, {self.config.num_parameters}]")
        if coords.shape[0] != params.shape[0]:
            raise ValueError("coords and params must share the batch dimension")

        point_features = self._point_features(coords, params)
        mean = self.mean_head(point_features)
        logvar = self.logvar_head(point_features).clamp(
            self.config.min_log_variance, self.config.max_log_variance
        )
        basis = self.latent_basis(point_features).view(
            coords.shape[0], coords.shape[1], self.config.num_fields, self.config.latent_dim
        )
        output = {"mean": mean, "logvar": logvar, "basis": basis}
        if n_samples > 0:
            output["samples"] = self.sample_from_outputs(output, n_samples=n_samples, latent=latent)
        return output

    def sample_from_outputs(
        self,
        outputs: dict[str, torch.Tensor],
        n_samples: int,
        latent: torch.Tensor | None = None,
    ) -> torch.Tensor:
        mean = outputs["mean"]
        logvar = outputs["logvar"]
        basis = outputs["basis"]
        batch_size = mean.shape[0]
        if latent is None:
            latent = torch.randn(
                batch_size,
                n_samples,
                self.config.latent_dim,
                device=mean.device,
                dtype=mean.dtype,
            )
        low_rank = torch.einsum("bncl,bsl->bsnc", basis, latent)
        point_noise = torch.randn(
            batch_size,
            n_samples,
            mean.shape[1],
            mean.shape[2],
            device=mean.device,
            dtype=mean.dtype,
        )
        return mean.unsqueeze(1) + low_rank + torch.exp(0.5 * logvar).unsqueeze(1) * point_noise

    def credible_interval(
        self, coords: torch.Tensor, params: torch.Tensor, level: float = 0.95, n_samples: int = 64
    ) -> dict[str, torch.Tensor]:
        outputs = self.forward(coords, params, n_samples=n_samples)
        samples = outputs["samples"]
        alpha = (1.0 - level) / 2.0
        return {
            "mean": outputs["mean"],
            "lower": torch.quantile(samples, alpha, dim=1),
            "upper": torch.quantile(samples, 1.0 - alpha, dim=1),
            "samples": samples,
        }

    def _point_features(self, coords: torch.Tensor, params: torch.Tensor) -> torch.Tensor:
        coord_features = self.features(coords)
        context = self.context(params).unsqueeze(1).expand(-1, coords.shape[1], -1)
        return torch.cat([coord_features, context], dim=-1)


class DeterministicDeepONet(nn.Module):
    """Compact DeepONet-style deterministic baseline."""

    def __init__(
        self,
        num_parameters: int,
        num_fields: int = 2,
        spatial_dim: int = 1,
        hidden_dim: int = 96,
        basis_dim: int = 32,
        num_fourier_modes: int = 8,
    ) -> None:
        super().__init__()
        self.num_fields = num_fields
        self.basis_dim = basis_dim
        self.features = FourierFeatures(num_fourier_modes, spatial_dim=spatial_dim)
        self.branch = MLP(num_parameters, hidden_dim, num_fields * basis_dim)
        self.trunk = MLP(self.features.output_dim, hidden_dim, num_fields * basis_dim)
        self.bias = nn.Parameter(torch.zeros(num_fields))

    def forward(self, coords: torch.Tensor, params: torch.Tensor) -> dict[str, torch.Tensor]:
        branch = self.branch(params).view(params.shape[0], self.num_fields, self.basis_dim)
        trunk = self.trunk(self.features(coords)).view(
            coords.shape[0], coords.shape[1], self.num_fields, self.basis_dim
        )
        mean = torch.einsum("bck,bnck->bnc", branch, trunk) / (self.basis_dim**0.5)
        mean = mean + self.bias.view(1, 1, -1)
        return {"mean": mean}
