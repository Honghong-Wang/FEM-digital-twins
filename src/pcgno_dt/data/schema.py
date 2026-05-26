from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SampleSchema:
    """Names expected in a single simulation sample."""

    sample_id: str = "sample_id"
    geometry: str = "geometry"
    parameters: str = "parameters"
    boundary_conditions: str = "boundary_conditions"
    solution_fields: str = "solution_fields"
    observations: str = "observations"
    metadata: str = "metadata"
