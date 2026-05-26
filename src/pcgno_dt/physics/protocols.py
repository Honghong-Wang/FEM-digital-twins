from __future__ import annotations

from typing import Protocol

import torch


class OperatorProblem(Protocol):
    """Common interface for manufactured and FEM-backed operator-learning problems."""

    num_points: int
    num_parameters: int
    num_fields: int
    parameter_names: tuple[str, ...]

    def grid(self, batch_size: int | None = None) -> torch.Tensor:
        """Return coordinates shaped [batch, points, spatial_dim] or [1, points, spatial_dim]."""

    def residual(
        self,
        params: torch.Tensor,
        fields: torch.Tensor,
        forcing: torch.Tensor | None = None,
        use_finite_difference: bool = True,
    ) -> torch.Tensor:
        """Return PDE residual shaped like fields."""

    def boundary_residual(self, params: torch.Tensor, fields: torch.Tensor) -> torch.Tensor:
        """Return boundary residual shaped [batch, boundary_nodes, fields]."""

    def energy(
        self, params: torch.Tensor, fields: torch.Tensor, forcing: torch.Tensor | None = None
    ) -> torch.Tensor:
        """Return diagnostic energy shaped [batch]."""

    def thermodynamic_penalty(self, params: torch.Tensor) -> torch.Tensor:
        """Return scalar penalty for inadmissible parameters."""
