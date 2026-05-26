from __future__ import annotations

from typing import Protocol

import torch


class ProbabilisticOperator(Protocol):
    """Protocol for neural operators that return field samples or distributions."""

    def forward(self, inputs: dict[str, torch.Tensor]) -> dict[str, torch.Tensor]:
        """Run operator inference."""
