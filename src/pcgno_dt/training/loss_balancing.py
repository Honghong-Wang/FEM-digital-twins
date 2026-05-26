from __future__ import annotations

from collections.abc import Mapping, Sequence

import torch
import torch.nn.functional as F
from torch import nn


DEFAULT_BALANCED_TERMS = ("data", "pde_residual", "boundary", "energy", "calibration")
PHYSICS_TERMS = ("pde_residual", "boundary", "energy")


class StaticLossBalancer(nn.Module):
    """Combine existing weighted `total` from the loss dictionary."""

    def forward(
        self,
        losses: Mapping[str, torch.Tensor],
        **_: object,
    ) -> dict[str, torch.Tensor | dict[str, float]]:
        if "total" not in losses:
            raise KeyError("loss dictionary must contain 'total'")
        return {"total": losses["total"], "effective_weights": {}}


class UncertaintyLossBalancer(nn.Module):
    """Learn task weights with homoscedastic uncertainty weighting.

    For each positive loss term L_i, optimize:

    ```text
    exp(-s_i) L_i + s_i
    ```

    The effective task weight is `exp(-s_i)`.
    """

    def __init__(
        self,
        terms: tuple[str, ...] = DEFAULT_BALANCED_TERMS,
        initial_log_variance: float = 0.0,
    ) -> None:
        super().__init__()
        self.terms = terms
        self.log_variances = nn.ParameterDict(
            {
                term: nn.Parameter(torch.tensor(float(initial_log_variance)))
                for term in terms
            }
        )

    def forward(
        self,
        losses: Mapping[str, torch.Tensor],
        term_scales: Mapping[str, float] | None = None,
        **_: object,
    ) -> dict[str, torch.Tensor | dict[str, float]]:
        total = None
        for term in self.terms:
            if term not in losses:
                continue
            log_var = self.log_variances[term].to(device=losses[term].device, dtype=losses[term].dtype)
            scale = _term_scale(term_scales, term, losses[term])
            contribution = torch.exp(-log_var) * scale * losses[term] + log_var
            total = contribution if total is None else total + contribution
        if total is None:
            raise KeyError("none of the requested loss terms were present")
        return {"total": total, "effective_weights": self.effective_weights(term_scales=term_scales)}

    def effective_weights(self, term_scales: Mapping[str, float] | None = None) -> dict[str, float]:
        return {
            term: float(torch.exp(-param.detach()).cpu()) * float(term_scales.get(term, 1.0) if term_scales else 1.0)
            for term, param in self.log_variances.items()
        }


class SoftAdaptLossBalancer(nn.Module):
    """Adapt task weights from recent loss changes.

    This implementation follows the practical SoftAdapt idea: terms that are decreasing too
    slowly receive larger weights. It is intentionally stateful and lightweight, which makes it
    useful for sweep-scale triage before running more expensive GradNorm experiments.
    """

    def __init__(
        self,
        terms: tuple[str, ...] = DEFAULT_BALANCED_TERMS,
        temperature: float = 0.5,
        ema: float = 0.8,
        score_clip: float = 2.0,
    ) -> None:
        super().__init__()
        self.terms = terms
        self.temperature = temperature
        self.ema = ema
        self.score_clip = score_clip
        self._previous_losses: dict[str, torch.Tensor] = {}
        self._effective_weights: dict[str, float] = {term: 1.0 for term in terms}

    def forward(
        self,
        losses: Mapping[str, torch.Tensor],
        term_scales: Mapping[str, float] | None = None,
        **_: object,
    ) -> dict[str, torch.Tensor | dict[str, float]]:
        active_terms = [term for term in self.terms if term in losses]
        if not active_terms:
            raise KeyError("none of the requested loss terms were present")
        current = torch.stack([losses[term].detach() for term in active_terms])
        if all(term in self._previous_losses for term in active_terms):
            previous = torch.stack([self._previous_losses[term].to(current) for term in active_terms])
            scores = (current - previous) / previous.abs().clamp_min(1.0e-12)
            scores = scores.clamp(min=-self.score_clip, max=self.score_clip)
            weights = len(active_terms) * torch.softmax(scores / self.temperature, dim=0)
        else:
            weights = torch.ones_like(current)

        total = losses[active_terms[0]].new_tensor(0.0)
        effective_weights: dict[str, float] = {}
        for term, weight in zip(active_terms, weights, strict=True):
            scale = _term_scale(term_scales, term, losses[term])
            total = total + scale * weight.to(losses[term]) * losses[term]
            effective_weights[term] = float((scale * weight.detach()).cpu())

        self._effective_weights = effective_weights
        with torch.no_grad():
            for term in active_terms:
                detached = losses[term].detach()
                if term in self._previous_losses:
                    old = self._previous_losses[term].to(detached)
                    self._previous_losses[term] = self.ema * old + (1.0 - self.ema) * detached
                else:
                    self._previous_losses[term] = detached
        return {"total": total, "effective_weights": effective_weights}

    def effective_weights(self) -> dict[str, float]:
        return self._effective_weights


class GradNormLossBalancer(nn.Module):
    """Balance losses by equalizing gradient norms across task terms."""

    def __init__(
        self,
        terms: tuple[str, ...] = DEFAULT_BALANCED_TERMS,
        alpha: float = 1.5,
        penalty_weight: float = 0.1,
    ) -> None:
        super().__init__()
        self.terms = terms
        self.alpha = alpha
        self.penalty_weight = penalty_weight
        self.log_weights = nn.ParameterDict(
            {term: nn.Parameter(torch.zeros(())) for term in terms}
        )
        self._initial_losses: dict[str, torch.Tensor] = {}

    def forward(
        self,
        losses: Mapping[str, torch.Tensor],
        shared_parameters: Sequence[torch.nn.Parameter] | None = None,
        term_scales: Mapping[str, float] | None = None,
    ) -> dict[str, torch.Tensor | dict[str, float]]:
        active_terms = [term for term in self.terms if term in losses]
        if not active_terms:
            raise KeyError("none of the requested loss terms were present")

        weights = self._normalized_weights(active_terms)
        total = losses[active_terms[0]].new_tensor(0.0)
        weighted_losses: list[torch.Tensor] = []
        effective_weights: dict[str, float] = {}
        for term, weight in zip(active_terms, weights, strict=True):
            scale = _term_scale(term_scales, term, losses[term])
            weighted_loss = scale * weight.to(losses[term]) * losses[term]
            weighted_losses.append(weighted_loss)
            total = total + weighted_loss
            effective_weights[term] = float((scale * weight.detach()).cpu())
            self._initial_losses.setdefault(term, losses[term].detach().clamp_min(1.0e-12))

        parameters = [param for param in (shared_parameters or []) if param.requires_grad]
        if parameters:
            grad_norms = torch.stack(
                [
                    _gradient_norm(weighted_loss, parameters)
                    for weighted_loss in weighted_losses
                ]
            )
            loss_ratios = torch.stack(
                [
                    losses[term].detach().clamp_min(1.0e-12)
                    / self._initial_losses[term].to(losses[term]).clamp_min(1.0e-12)
                    for term in active_terms
                ]
            )
            inverse_rates = loss_ratios / loss_ratios.mean().clamp_min(1.0e-12)
            target = grad_norms.detach().mean() * inverse_rates.pow(self.alpha)
            total = total + self.penalty_weight * F.l1_loss(grad_norms, target.detach(), reduction="sum")

        return {"total": total, "effective_weights": effective_weights}

    def effective_weights(self) -> dict[str, float]:
        return {
            term: float(weight)
            for term, weight in zip(self.terms, self._normalized_weights(list(self.terms)).detach().cpu(), strict=True)
        }

    def _normalized_weights(self, active_terms: list[str]) -> torch.Tensor:
        raw = torch.stack([self.log_weights[term] for term in active_terms])
        return len(active_terms) * torch.softmax(raw, dim=0)


class ResidualAdaptiveLossBalancer(nn.Module):
    """Increase physics weights when residual terms lag behind the data term.

    The rule is deliberately simple and auditable for ablation studies. It tracks an EMA of each
    loss term, compares physics terms to the data loss, and increases a physics term when its
    residual/data ratio exceeds a target ratio.
    """

    def __init__(
        self,
        terms: tuple[str, ...] = DEFAULT_BALANCED_TERMS,
        physics_terms: tuple[str, ...] = PHYSICS_TERMS,
        target_ratio: float = 0.1,
        gain: float = 0.5,
        ema: float = 0.9,
        min_weight: float = 1.0e-3,
        max_weight: float = 1.0e3,
    ) -> None:
        super().__init__()
        self.terms = terms
        self.physics_terms = physics_terms
        self.target_ratio = target_ratio
        self.gain = gain
        self.ema = ema
        self.min_weight = min_weight
        self.max_weight = max_weight
        self._ema_losses: dict[str, torch.Tensor] = {}
        self._effective_weights: dict[str, float] = {term: 1.0 for term in terms}

    def forward(
        self,
        losses: Mapping[str, torch.Tensor],
        term_scales: Mapping[str, float] | None = None,
        **_: object,
    ) -> dict[str, torch.Tensor | dict[str, float]]:
        active_terms = [term for term in self.terms if term in losses]
        if not active_terms:
            raise KeyError("none of the requested loss terms were present")
        self._update_ema(losses, active_terms)
        data_reference = self._ema_losses.get("data", losses[active_terms[0]].detach()).abs().clamp_min(1.0e-12)

        total = losses[active_terms[0]].new_tensor(0.0)
        effective_weights: dict[str, float] = {}
        for term in active_terms:
            scale = _term_scale(term_scales, term, losses[term])
            adaptive = self._adaptive_weight(term, data_reference, losses[term])
            total = total + scale * adaptive.to(losses[term]) * losses[term]
            effective_weights[term] = float((scale * adaptive.detach()).cpu())
        self._effective_weights = effective_weights
        return {"total": total, "effective_weights": effective_weights}

    def effective_weights(self) -> dict[str, float]:
        return self._effective_weights

    def _update_ema(self, losses: Mapping[str, torch.Tensor], active_terms: Sequence[str]) -> None:
        with torch.no_grad():
            for term in active_terms:
                value = losses[term].detach().abs().clamp_min(1.0e-12)
                if term in self._ema_losses:
                    old = self._ema_losses[term].to(value)
                    self._ema_losses[term] = self.ema * old + (1.0 - self.ema) * value
                else:
                    self._ema_losses[term] = value

    def _adaptive_weight(self, term: str, data_reference: torch.Tensor, reference: torch.Tensor) -> torch.Tensor:
        if term not in self.physics_terms:
            return reference.new_tensor(1.0)
        ratio = self._ema_losses[term].to(reference) / data_reference.to(reference)
        weight = (ratio / self.target_ratio).clamp_min(1.0e-12).pow(self.gain)
        return weight.clamp(min=self.min_weight, max=self.max_weight)


def make_loss_balancer(name: str) -> nn.Module:
    if name == "static":
        return StaticLossBalancer()
    if name == "uncertainty":
        return UncertaintyLossBalancer()
    if name == "softadapt":
        return SoftAdaptLossBalancer()
    if name == "gradnorm":
        return GradNormLossBalancer()
    if name == "residual_adaptive":
        return ResidualAdaptiveLossBalancer()
    raise ValueError(f"unknown loss balancer: {name}")


def _term_scale(
    term_scales: Mapping[str, float] | None,
    term: str,
    reference: torch.Tensor,
) -> torch.Tensor:
    scale = 1.0 if term_scales is None else float(term_scales.get(term, 1.0))
    return reference.new_tensor(scale)


def _gradient_norm(loss: torch.Tensor, parameters: Sequence[torch.nn.Parameter]) -> torch.Tensor:
    gradients = torch.autograd.grad(
        loss,
        parameters,
        retain_graph=True,
        create_graph=True,
        allow_unused=True,
    )
    norms = [
        gradient.norm(2)
        for gradient in gradients
        if gradient is not None
    ]
    if not norms:
        return loss.new_tensor(0.0)
    return torch.stack(norms).norm(2)
