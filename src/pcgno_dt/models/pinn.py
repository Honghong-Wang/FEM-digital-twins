from __future__ import annotations

import torch
from torch import nn

from pcgno_dt.models.pcgno import MLP


class PointwisePINN(nn.Module):
    """Pointwise PINN-style baseline parameterized by coordinates and PDE parameters."""

    def __init__(
        self,
        num_parameters: int,
        num_fields: int = 2,
        spatial_dim: int = 1,
        hidden_dim: int = 96,
    ) -> None:
        super().__init__()
        self.net = MLP(spatial_dim + num_parameters, hidden_dim, num_fields, depth=4)

    def forward(self, coords: torch.Tensor, params: torch.Tensor) -> dict[str, torch.Tensor]:
        expanded_params = params.unsqueeze(1).expand(-1, coords.shape[1], -1)
        features = torch.cat([coords, expanded_params], dim=-1)
        return {"mean": self.net(features)}
