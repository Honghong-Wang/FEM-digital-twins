from __future__ import annotations

from dataclasses import dataclass

import torch


@dataclass(frozen=True)
class InversionConfig:
    steps: int = 200
    learning_rate: float = 1.0e-2
    prior_weight: float = 1.0e-4


def invert_parameters_from_sparse_observations(
    model: torch.nn.Module,
    coords: torch.Tensor,
    sensor_idx: torch.Tensor,
    observed_values: torch.Tensor,
    initial_params: torch.Tensor,
    lower_bounds: torch.Tensor,
    upper_bounds: torch.Tensor,
    config: InversionConfig = InversionConfig(),
) -> dict[str, torch.Tensor]:
    """Gradient-based sparse-observation inverse identification through a differentiable operator."""

    raw = torch.nn.Parameter(torch.zeros_like(initial_params))
    center = 0.5 * (lower_bounds + upper_bounds)
    scale = (upper_bounds - lower_bounds).clamp_min(1.0e-8)
    with torch.no_grad():
        normalized = ((initial_params - lower_bounds) / scale).clamp(1.0e-4, 1.0 - 1.0e-4)
        raw.copy_(torch.logit(normalized))

    optimizer = torch.optim.Adam([raw], lr=config.learning_rate)
    history: list[torch.Tensor] = []
    for _ in range(config.steps):
        optimizer.zero_grad()
        params = lower_bounds + torch.sigmoid(raw) * scale
        prediction = model(coords, params)["mean"].index_select(dim=1, index=sensor_idx)
        data_loss = (prediction - observed_values).square().mean()
        prior_loss = ((params - center) / scale).square().mean()
        loss = data_loss + config.prior_weight * prior_loss
        loss.backward()
        optimizer.step()
        history.append(loss.detach())

    params = lower_bounds + torch.sigmoid(raw.detach()) * scale
    return {"params": params, "loss_history": torch.stack(history)}
