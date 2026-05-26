from __future__ import annotations

import torch

from pcgno_dt.training.path_losses import PathLossWeights, history_graph_operator_loss


def test_current_increment_active_qp_mask_focuses_on_new_plastic_update() -> None:
    outputs, batch = _qp_loss_fixture()
    outputs["history_qp_sequence"][:, 1, ..., 0] = 1.0
    accumulated = history_graph_operator_loss(
        outputs,
        batch,
        _weights(qp_active_mask_mode="accumulated"),
    )
    current_increment = history_graph_operator_loss(
        outputs,
        batch,
        _weights(qp_active_mask_mode="current_increment"),
    )

    assert accumulated["qp_history_increment_active"] > current_increment["qp_history_increment_active"]


def test_reversal_qp_loss_uses_current_increment_activity() -> None:
    outputs, batch = _qp_loss_fixture()
    losses = history_graph_operator_loss(
        outputs,
        batch,
        _weights(qp_active_mask_mode="current_increment", qp_reversal_plastic_increment_active=1.0),
    )

    assert losses["qp_reversal_plastic_increment_active"] > 0.0
    assert torch.isfinite(losses["total"])


def _qp_loss_fixture() -> tuple[dict[str, torch.Tensor], dict[str, torch.Tensor]]:
    batch_size, steps, nodes, elements, qps, fields, history_dim = 1, 4, 1, 1, 1, 2, 5
    target_qp = torch.zeros(batch_size, steps, elements, qps, history_dim)
    target_qp[:, 0, ..., 0] = 0.10
    target_qp[:, 1, ..., 0] = 0.10
    target_qp[:, 2, ..., 0] = 0.20
    target_qp[:, 2, ..., 1] = 0.20
    target_qp[:, 2, ..., 2] = 0.10
    target_qp[:, 2, ..., 3] = 1.00
    target_qp[:, 3, ..., 0] = 0.20
    target_qp[:, 3, ..., 1] = 0.20

    forcing = torch.tensor([[[[0.0, 0.0]], [[1.0, 0.0]], [[0.0, 0.0]], [[1.0, 0.0]]]])
    outputs = {
        "mean_sequence": torch.zeros(batch_size, steps, nodes, fields),
        "history_sequence": torch.zeros(batch_size, steps, elements, history_dim),
        "history_qp_sequence": torch.zeros_like(target_qp),
        "logvar_sequence": torch.zeros(batch_size, steps, nodes, fields),
    }
    batch = {
        "fields_sequence": torch.zeros(batch_size, steps, nodes, fields),
        "material_history_sequence": target_qp.mean(dim=3),
        "material_history_qp_sequence": target_qp,
        "forcing_sequence": forcing,
        "params": torch.tensor([[100.0, 0.30, 0.10, 1.0, 0.0, 0.0]]),
    }
    return outputs, batch


def _weights(**overrides: object) -> PathLossWeights:
    kwargs = {
        "displacement": 0.0,
        "history": 0.0,
        "qp_history_increment_active": 1.0,
        "calibration": 0.0,
        "eqp_monotonicity": 0.0,
        "plastic_work_monotonicity": 0.0,
        "plastic_multiplier_nonnegative": 0.0,
        "yield_bounds": 0.0,
    }
    kwargs.update(overrides)
    return PathLossWeights(**kwargs)
