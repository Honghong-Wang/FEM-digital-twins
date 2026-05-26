from __future__ import annotations

import torch

from pcgno_dt.training.loss_balancing import (
    GradNormLossBalancer,
    ResidualAdaptiveLossBalancer,
    SoftAdaptLossBalancer,
    StaticLossBalancer,
    UncertaintyLossBalancer,
)


def test_static_loss_balancer_uses_existing_total() -> None:
    losses = {"total": torch.tensor(3.0), "data": torch.tensor(1.0)}
    balanced = StaticLossBalancer()(losses)
    assert balanced["total"].item() == 3.0


def test_uncertainty_loss_balancer_learns_effective_weights() -> None:
    balancer = UncertaintyLossBalancer(terms=("data", "pde_residual"))
    losses = {"data": torch.tensor(1.0), "pde_residual": torch.tensor(2.0)}
    output = balancer(losses)
    output["total"].backward()
    weights = balancer.effective_weights()
    assert set(weights) == {"data", "pde_residual"}
    assert all(value > 0.0 for value in weights.values())
    assert balancer.log_variances["data"].grad is not None


def test_softadapt_loss_balancer_returns_positive_weights() -> None:
    balancer = SoftAdaptLossBalancer(terms=("data", "pde_residual"))
    first = balancer({"data": torch.tensor(1.0), "pde_residual": torch.tensor(2.0)})
    second = balancer({"data": torch.tensor(0.8), "pde_residual": torch.tensor(2.2)})

    assert first["total"].item() > 0.0
    assert second["total"].item() > 0.0
    assert all(value > 0.0 for value in second["effective_weights"].values())


def test_gradnorm_loss_balancer_updates_task_weights() -> None:
    parameter = torch.nn.Parameter(torch.tensor(1.0))
    balancer = GradNormLossBalancer(terms=("data", "pde_residual"))
    losses = {
        "data": (parameter - 1.5).square() + 1.0,
        "pde_residual": (2.0 * parameter + 0.1).square() + 1.0,
    }
    output = balancer(losses, shared_parameters=[parameter])
    output["total"].backward()

    assert parameter.grad is not None
    assert balancer.log_weights["data"].grad is not None
    assert all(value > 0.0 for value in output["effective_weights"].values())


def test_residual_adaptive_balancer_emphasizes_large_residuals() -> None:
    balancer = ResidualAdaptiveLossBalancer(terms=("data", "pde_residual"), target_ratio=0.1)
    output = balancer({"data": torch.tensor(1.0), "pde_residual": torch.tensor(10.0)})
    weights = output["effective_weights"]

    assert output["total"].item() > 0.0
    assert weights["pde_residual"] > weights["data"]
