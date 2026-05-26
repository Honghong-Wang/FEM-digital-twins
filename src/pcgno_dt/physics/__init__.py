"""Physics systems, governing equations, and residual definitions."""

from pcgno_dt.physics.j2_return import (
    DifferentiableJ2PlaneStrainReturnMapping,
    DifferentiableJ2ReturnMapping,
    J2PlaneStrainReturnState,
    J2ReturnMappingConfig,
    TrueDifferentiableJ2PlaneStrainReturnMapping,
    TrueJ2PlaneStrainReturnState,
)

__all__ = [
    "DifferentiableJ2PlaneStrainReturnMapping",
    "DifferentiableJ2ReturnMapping",
    "J2PlaneStrainReturnState",
    "J2ReturnMappingConfig",
    "TrueDifferentiableJ2PlaneStrainReturnMapping",
    "TrueJ2PlaneStrainReturnState",
]
