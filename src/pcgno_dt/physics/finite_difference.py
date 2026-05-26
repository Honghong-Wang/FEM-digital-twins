from __future__ import annotations

import torch


def gradient_1d(values: torch.Tensor, dx: float) -> torch.Tensor:
    """Second-order finite-difference gradient for fields shaped [batch, points, channels]."""

    if values.ndim != 3:
        raise ValueError("values must have shape [batch, points, channels]")
    if values.shape[1] < 3:
        raise ValueError("at least three grid points are required")

    grad = torch.empty_like(values)
    grad[:, 1:-1, :] = (values[:, 2:, :] - values[:, :-2, :]) / (2.0 * dx)
    grad[:, 0, :] = (-3.0 * values[:, 0, :] + 4.0 * values[:, 1, :] - values[:, 2, :]) / (
        2.0 * dx
    )
    grad[:, -1, :] = (3.0 * values[:, -1, :] - 4.0 * values[:, -2, :] + values[:, -3, :]) / (
        2.0 * dx
    )
    return grad


def laplacian_1d(values: torch.Tensor, dx: float) -> torch.Tensor:
    """Second-order finite-difference Laplacian for fields shaped [batch, points, channels]."""

    if values.ndim != 3:
        raise ValueError("values must have shape [batch, points, channels]")
    if values.shape[1] < 4:
        raise ValueError("at least four grid points are required")

    lap = torch.empty_like(values)
    lap[:, 1:-1, :] = (values[:, :-2, :] - 2.0 * values[:, 1:-1, :] + values[:, 2:, :]) / (
        dx * dx
    )
    lap[:, 0, :] = lap[:, 1, :]
    lap[:, -1, :] = lap[:, -2, :]
    return lap


def integrate_trapezoid(values: torch.Tensor, dx: float) -> torch.Tensor:
    """Integrate fields over a uniform 1D grid with the trapezoidal rule."""

    if values.ndim < 2:
        raise ValueError("values must have at least [batch, points] dimensions")
    weights = torch.ones(values.shape[1], device=values.device, dtype=values.dtype)
    weights[0] = 0.5
    weights[-1] = 0.5
    view_shape = (1, values.shape[1]) + (1,) * (values.ndim - 2)
    return (values * weights.view(view_shape)).sum(dim=1) * dx
