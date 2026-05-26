from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class PhysicsSystemSpec:
    """Minimal description of a parameterized multiphysics system."""

    name: str
    state_fields: tuple[str, ...]
    parameter_names: tuple[str, ...]
    spatial_dimension: int
    time_dependent: bool
    coupling_terms: tuple[str, ...] = field(default_factory=tuple)
    metadata: dict[str, Any] = field(default_factory=dict)
