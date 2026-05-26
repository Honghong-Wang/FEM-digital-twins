from __future__ import annotations

from dataclasses import dataclass
from typing import NamedTuple

import torch
from torch import nn


@dataclass(frozen=True)
class J2ReturnMappingConfig:
    """Scalar differentiable J2 radial-return projection for exported history channels.

    The layer operates on the five scalar channels used by the J2 path dataset:
    [equivalent plastic strain, plastic work, plastic multiplier increment, yield flag,
    von Mises stress].  It is intentionally a scalar projection of the local return mapping,
    not a replacement for the full tensorial integration point update.
    """

    young_modulus_index: int = 0
    poisson_ratio_index: int = 1
    yield_stress_index: int = 2
    hardening_modulus_index: int = 3
    min_shear_modulus: float = 1.0e-8
    min_denom: float = 1.0e-8
    yield_flag_sharpness: float = 20.0
    eps: float = 1.0e-12


class J2PlaneStrainReturnState(NamedTuple):
    """Differentiable local J2 state produced by a plane-strain radial return."""

    history: torch.Tensor
    plastic_strain: torch.Tensor
    stress_voigt: torch.Tensor
    algorithmic_tangent: torch.Tensor
    yield_function: torch.Tensor
    trial_von_mises: torch.Tensor


class TrueJ2PlaneStrainReturnState(NamedTuple):
    """QP-level J2 state with consistent tangent and implicit multiplier sensitivity."""

    history: torch.Tensor
    plastic_strain: torch.Tensor
    stress_voigt: torch.Tensor
    algorithmic_tangent: torch.Tensor
    yield_function: torch.Tensor
    trial_yield_function: torch.Tensor
    trial_von_mises: torch.Tensor
    plastic_multiplier: torch.Tensor
    consistency_residual: torch.Tensor


class _ImplicitPlasticMultiplier(torch.autograd.Function):
    """Linear-hardening J2 consistency solve with an explicit IFT backward.

    For the active set the plastic multiplier solves

    q_tr - 3G dgamma - sigma_y - H(alpha_old + dgamma) = 0.

    The backward pass applies the implicit-function derivative of this scalar equation.
    """

    @staticmethod
    def forward(
        ctx,
        trial_von_mises: torch.Tensor,
        eqp_old: torch.Tensor,
        yield_stress: torch.Tensor,
        hardening: torch.Tensor,
        shear_modulus: torch.Tensor,
        min_denom: float,
    ) -> torch.Tensor:
        denom = (3.0 * shear_modulus + hardening).clamp_min(float(min_denom))
        trial_yield = trial_von_mises - yield_stress - hardening * eqp_old
        active = trial_yield > 0.0
        plastic_multiplier = torch.where(
            active,
            trial_yield / denom,
            torch.zeros_like(trial_yield),
        )
        ctx.save_for_backward(active.to(dtype=trial_yield.dtype), denom, trial_yield, eqp_old, hardening)
        return plastic_multiplier

    @staticmethod
    def backward(ctx, grad_output: torch.Tensor) -> tuple[torch.Tensor | None, ...]:
        active, denom, trial_yield, eqp_old, hardening = ctx.saved_tensors
        active_grad = active * grad_output
        denom_sq = denom.square().clamp_min(torch.finfo(denom.dtype).eps)
        grad_trial_von_mises = active_grad / denom
        grad_eqp_old = -active_grad * hardening / denom
        grad_yield_stress = -active_grad / denom
        grad_hardening = active_grad * (-(eqp_old * denom + trial_yield) / denom_sq)
        grad_shear_modulus = active_grad * (-3.0 * trial_yield / denom_sq)
        return (
            grad_trial_von_mises,
            grad_eqp_old,
            grad_yield_stress,
            grad_hardening,
            grad_shear_modulus,
            None,
        )


class DifferentiableJ2ReturnMapping(nn.Module):
    """Project raw history logits through a differentiable scalar J2 return map.

    Inputs are previous scalar history, raw model output, and material parameters.  The raw
    von-Mises channel is interpreted as a nonnegative trial equivalent stress.  The return
    update enforces nonnegative plastic multiplier, equivalent plastic strain and plastic work,
    and projects plastic states back to the isotropic-hardening flow stress.
    """

    def __init__(self, config: J2ReturnMappingConfig | None = None) -> None:
        super().__init__()
        self.config = config or J2ReturnMappingConfig()

    def forward(
        self,
        previous_history: torch.Tensor,
        raw_update: torch.Tensor,
        params: torch.Tensor,
    ) -> torch.Tensor:
        if previous_history.shape[-1] < 5 or raw_update.shape[-1] < 5:
            raise ValueError("J2 return mapping requires at least five history channels")
        if params.ndim != 2 or params.shape[-1] <= max(
            self.config.young_modulus_index,
            self.config.poisson_ratio_index,
            self.config.yield_stress_index,
            self.config.hardening_modulus_index,
        ):
            raise ValueError("params must contain [E, nu, sigma_y, H] channels")

        dtype = previous_history.dtype
        device = previous_history.device
        params = params.to(device=device, dtype=dtype)
        young_modulus = params[:, None, self.config.young_modulus_index].clamp_min(self.config.eps)
        poisson_ratio = params[:, None, self.config.poisson_ratio_index].clamp(-0.49, 0.49)
        yield_stress = params[:, None, self.config.yield_stress_index].clamp_min(self.config.eps)
        hardening = params[:, None, self.config.hardening_modulus_index].clamp_min(0.0)
        shear_modulus = (
            young_modulus / (2.0 * (1.0 + poisson_ratio))
        ).clamp_min(self.config.min_shear_modulus)

        eqp_old = previous_history[..., 0].clamp_min(0.0)
        plastic_work_old = previous_history[..., 1].clamp_min(0.0)
        trial_von_mises = torch.nn.functional.softplus(raw_update[..., 4])
        flow_old = yield_stress + hardening * eqp_old
        yield_value = trial_von_mises - flow_old
        plastic_multiplier = torch.relu(yield_value) / (
            3.0 * shear_modulus + hardening
        ).clamp_min(self.config.min_denom)
        eqp_next = eqp_old + plastic_multiplier
        flow_next = yield_stress + hardening * eqp_next
        plastic_von_mises = flow_next
        elastic_von_mises = trial_von_mises.clamp_max(flow_old)
        yielded_weight = torch.sigmoid(
            self.config.yield_flag_sharpness
            * yield_value
            / flow_old.detach().clamp_min(self.config.eps)
        )
        von_mises_next = yielded_weight * plastic_von_mises + (1.0 - yielded_weight) * elastic_von_mises
        plastic_work_increment = (
            yield_stress * plastic_multiplier
            + 0.5 * hardening * (eqp_next.square() - eqp_old.square())
        ).clamp_min(0.0)
        plastic_work_next = plastic_work_old + plastic_work_increment

        next_history = previous_history.clone()
        next_history[..., 0] = eqp_next
        next_history[..., 1] = plastic_work_next
        next_history[..., 2] = plastic_multiplier
        next_history[..., 3] = yielded_weight.clamp(0.0, 1.0)
        next_history[..., 4] = von_mises_next.clamp_min(0.0)
        if previous_history.shape[-1] > 5:
            next_history[..., 5:] = previous_history[..., 5:] + raw_update[..., 5:]
        return next_history


class TrueDifferentiableJ2PlaneStrainReturnMapping(nn.Module):
    """True QP-level differentiable plane-strain J2 return mapping layer.

    This layer is intended for Level-6 style experiments where the neural operator should
    call a constitutive update rather than only clip scalar history channels. It supports
    element-level inputs ``[batch, elements, 3]`` and multi-integration-point inputs
    ``[batch, elements, q_points, 3]``. The plastic multiplier is treated as the implicit
    solution of the local consistency equation, and the exported tangent is the derivative
    of the returned stress with respect to the plane-strain engineering strain vector.
    """

    def __init__(self, config: J2ReturnMappingConfig | None = None) -> None:
        super().__init__()
        self.config = config or J2ReturnMappingConfig()

    def forward(
        self,
        strain_voigt: torch.Tensor,
        previous_plastic_strain: torch.Tensor,
        previous_history: torch.Tensor,
        params: torch.Tensor,
    ) -> TrueJ2PlaneStrainReturnState:
        squeeze_qp = False
        if strain_voigt.ndim == 3:
            strain_voigt = strain_voigt.unsqueeze(2)
            previous_history = previous_history.unsqueeze(2)
            if previous_plastic_strain.ndim == 4:
                previous_plastic_strain = previous_plastic_strain.unsqueeze(2)
            squeeze_qp = True
        if strain_voigt.ndim != 4 or strain_voigt.shape[-1] != 3:
            raise ValueError("strain_voigt must have shape [batch, elements, 3] or [batch, elements, q_points, 3]")
        if previous_history.shape[:3] != strain_voigt.shape[:3] or previous_history.shape[-1] < 5:
            raise ValueError("previous_history must match strain leading dimensions and contain at least five channels")
        if previous_plastic_strain.shape != (*strain_voigt.shape[:3], 3, 3):
            raise ValueError(
                "previous_plastic_strain must have shape "
                "[batch, elements, q_points, 3, 3] or [batch, elements, 3, 3]"
            )
        if params.ndim != 2 or params.shape[-1] <= max(
            self.config.young_modulus_index,
            self.config.poisson_ratio_index,
            self.config.yield_stress_index,
            self.config.hardening_modulus_index,
        ):
            raise ValueError("params must contain [E, nu, sigma_y, H] channels")

        dtype = strain_voigt.dtype
        device = strain_voigt.device
        params = params.to(device=device, dtype=dtype)
        leading_shape = strain_voigt.shape[:-1]
        young_modulus, poisson_ratio, yield_stress, hardening, shear_modulus, bulk_modulus = _material_parameters(
            params,
            leading_shape,
            self.config,
            dtype=dtype,
            device=device,
        )

        strain_tensor = _strain_voigt_to_tensor(strain_voigt)
        plastic_old = previous_plastic_strain.to(device=device, dtype=dtype)
        history_old = previous_history.to(device=device, dtype=dtype)
        eqp_old = history_old[..., 0].clamp_min(0.0)
        plastic_work_old = history_old[..., 1].clamp_min(0.0)

        elastic_trial = strain_tensor - plastic_old
        trace_trial = _trace(elastic_trial)
        stress_trial = (
            bulk_modulus[..., None, None] * trace_trial[..., None, None] * _identity(device, dtype)
            + 2.0 * shear_modulus[..., None, None] * _deviator(elastic_trial)
        )
        stress_dev_trial = _deviator(stress_trial)
        norm_dev = stress_dev_trial.square().sum(dim=(-2, -1)).clamp_min(self.config.eps).sqrt()
        trial_von_mises = (1.5**0.5) * norm_dev
        flow_old = yield_stress + hardening * eqp_old
        trial_yield_function = trial_von_mises - flow_old
        plastic_multiplier = _ImplicitPlasticMultiplier.apply(
            trial_von_mises,
            eqp_old,
            yield_stress,
            hardening,
            shear_modulus,
            self.config.min_denom,
        )

        flow_direction = 1.5 * stress_dev_trial / trial_von_mises[..., None, None].clamp_min(self.config.eps)
        plastic_strain = plastic_old + plastic_multiplier[..., None, None] * flow_direction
        radial_factor = (
            1.0
            - 3.0 * shear_modulus * plastic_multiplier / trial_von_mises.clamp_min(self.config.eps)
        ).clamp_min(0.0)
        stress_dev = stress_dev_trial * radial_factor[..., None, None]
        stress = stress_dev + (_trace(stress_trial) / 3.0)[..., None, None] * _identity(device, dtype)
        eqp_next = eqp_old + plastic_multiplier
        von_mises = (1.5 * stress_dev.square().sum(dim=(-2, -1))).clamp_min(0.0).sqrt()
        flow_next = yield_stress + hardening * eqp_next
        yield_function = von_mises - flow_next
        plastic_work_increment = (
            yield_stress * plastic_multiplier
            + 0.5 * hardening * (eqp_next.square() - eqp_old.square())
        ).clamp_min(0.0)
        plastic_work = plastic_work_old + plastic_work_increment
        yield_flag = (plastic_multiplier > 0.0).to(dtype=dtype)

        next_history = history_old.clone()
        next_history[..., 0] = eqp_next
        next_history[..., 1] = plastic_work
        next_history[..., 2] = plastic_multiplier
        next_history[..., 3] = yield_flag
        next_history[..., 4] = von_mises
        consistency_residual = trial_von_mises - 3.0 * shear_modulus * plastic_multiplier - flow_next

        state = TrueJ2PlaneStrainReturnState(
            history=next_history,
            plastic_strain=plastic_strain,
            stress_voigt=_stress_tensor_to_voigt(stress),
            algorithmic_tangent=_consistent_plane_strain_tangent(
                strain_voigt,
                stress_dev_trial,
                shear_modulus,
                bulk_modulus,
                hardening,
                plastic_multiplier,
                trial_von_mises,
                self.config.eps,
            ),
            yield_function=yield_function,
            trial_yield_function=trial_yield_function,
            trial_von_mises=trial_von_mises,
            plastic_multiplier=plastic_multiplier,
            consistency_residual=consistency_residual,
        )
        if not squeeze_qp:
            return state
        return TrueJ2PlaneStrainReturnState(
            history=state.history.squeeze(2),
            plastic_strain=state.plastic_strain.squeeze(2),
            stress_voigt=state.stress_voigt.squeeze(2),
            algorithmic_tangent=state.algorithmic_tangent.squeeze(2),
            yield_function=state.yield_function.squeeze(2),
            trial_yield_function=state.trial_yield_function.squeeze(2),
            trial_von_mises=state.trial_von_mises.squeeze(2),
            plastic_multiplier=state.plastic_multiplier.squeeze(2),
            consistency_residual=state.consistency_residual.squeeze(2),
        )


class DifferentiableJ2PlaneStrainReturnMapping(nn.Module):
    """Tensorial small-strain plane-strain J2 radial-return layer.

    This layer is the stricter hard-thermodynamic path used by the recurrent operator.  It
    consumes the element strain implied by the predicted displacement field, the previous
    plastic strain tensor, the previous scalar history channels, and material parameters.  It
    then performs a differentiable radial return and exports the same five scalar history
    channels used by the dataset:

    ``[eq_plastic_strain, plastic_work, plastic_multiplier_increment, yield_flag, von_mises]``.

    The returned state also exposes stress, the trial yield value, and an approximate
    consistent algorithmic tangent for auditing and future FEM residual coupling.
    """

    def __init__(self, config: J2ReturnMappingConfig | None = None) -> None:
        super().__init__()
        self.config = config or J2ReturnMappingConfig()

    def forward(
        self,
        strain_voigt: torch.Tensor,
        previous_plastic_strain: torch.Tensor,
        previous_history: torch.Tensor,
        params: torch.Tensor,
    ) -> J2PlaneStrainReturnState:
        if strain_voigt.ndim != 3 or strain_voigt.shape[-1] != 3:
            raise ValueError("strain_voigt must have shape [batch, elements, 3]")
        if previous_plastic_strain.shape != (*strain_voigt.shape[:2], 3, 3):
            raise ValueError("previous_plastic_strain must have shape [batch, elements, 3, 3]")
        if previous_history.shape[:2] != strain_voigt.shape[:2] or previous_history.shape[-1] < 5:
            raise ValueError("previous_history must have shape [batch, elements, at least 5]")
        if params.ndim != 2 or params.shape[-1] <= max(
            self.config.young_modulus_index,
            self.config.poisson_ratio_index,
            self.config.yield_stress_index,
            self.config.hardening_modulus_index,
        ):
            raise ValueError("params must contain [E, nu, sigma_y, H] channels")

        dtype = strain_voigt.dtype
        device = strain_voigt.device
        params = params.to(device=device, dtype=dtype)
        young_modulus = params[:, None, self.config.young_modulus_index].clamp_min(self.config.eps)
        poisson_ratio = params[:, None, self.config.poisson_ratio_index].clamp(-0.49, 0.49)
        yield_stress = params[:, None, self.config.yield_stress_index].clamp_min(self.config.eps)
        hardening = params[:, None, self.config.hardening_modulus_index].clamp_min(0.0)
        shear_modulus = (
            young_modulus / (2.0 * (1.0 + poisson_ratio))
        ).clamp_min(self.config.min_shear_modulus)
        bulk_modulus = young_modulus / (3.0 * (1.0 - 2.0 * poisson_ratio)).clamp_min(self.config.eps)

        strain_tensor = _strain_voigt_to_tensor(strain_voigt)
        plastic_old = previous_plastic_strain.to(device=device, dtype=dtype)
        eqp_old = previous_history[..., 0].clamp_min(0.0)
        plastic_work_old = previous_history[..., 1].clamp_min(0.0)

        elastic_trial = strain_tensor - plastic_old
        trace_trial = _trace(elastic_trial)
        stress_trial = (
            bulk_modulus[..., None, None] * trace_trial[..., None, None] * _identity(device, dtype)
            + 2.0 * shear_modulus[..., None, None] * _deviator(elastic_trial)
        )
        stress_dev_trial = _deviator(stress_trial)
        norm_dev = stress_dev_trial.square().sum(dim=(-2, -1)).clamp_min(self.config.eps).sqrt()
        trial_von_mises = (1.5**0.5) * norm_dev
        flow_old = yield_stress + hardening * eqp_old
        yield_function = trial_von_mises - flow_old

        plastic_multiplier = torch.relu(yield_function) / (
            3.0 * shear_modulus + hardening
        ).clamp_min(self.config.min_denom)
        flow_direction = 1.5 * stress_dev_trial / trial_von_mises[..., None, None].clamp_min(self.config.eps)
        plastic_strain = plastic_old + plastic_multiplier[..., None, None] * flow_direction
        radial_factor = (
            1.0
            - 3.0 * shear_modulus * plastic_multiplier / trial_von_mises.clamp_min(self.config.eps)
        ).clamp_min(0.0)
        stress_dev = stress_dev_trial * radial_factor[..., None, None]
        stress = stress_dev + (_trace(stress_trial) / 3.0)[..., None, None] * _identity(device, dtype)
        eqp_next = eqp_old + plastic_multiplier
        von_mises = (1.5 * stress_dev.square().sum(dim=(-2, -1))).clamp_min(0.0).sqrt()
        plastic_work_increment = (
            yield_stress * plastic_multiplier
            + 0.5 * hardening * (eqp_next.square() - eqp_old.square())
        ).clamp_min(0.0)
        plastic_work = plastic_work_old + plastic_work_increment
        yield_flag = torch.sigmoid(
            self.config.yield_flag_sharpness
            * yield_function
            / flow_old.detach().clamp_min(self.config.eps)
        ).clamp(0.0, 1.0)

        next_history = previous_history.clone()
        next_history[..., 0] = eqp_next
        next_history[..., 1] = plastic_work
        next_history[..., 2] = plastic_multiplier
        next_history[..., 3] = yield_flag
        next_history[..., 4] = von_mises

        return J2PlaneStrainReturnState(
            history=next_history,
            plastic_strain=plastic_strain,
            stress_voigt=_stress_tensor_to_voigt(stress),
            algorithmic_tangent=_algorithmic_tangent(
                strain_voigt,
                stress_dev_trial,
                shear_modulus,
                bulk_modulus,
                hardening,
                plastic_multiplier,
                self.config.eps,
            ),
            yield_function=yield_function,
            trial_von_mises=trial_von_mises,
        )


def j2_yield_residual(
    history: torch.Tensor,
    params: torch.Tensor,
    config: J2ReturnMappingConfig | None = None,
) -> torch.Tensor:
    """Return f = sigma_vm - (sigma_y + H eqp) for scalar history diagnostics."""

    cfg = config or J2ReturnMappingConfig()
    params = params.to(device=history.device, dtype=history.dtype)
    expand_shape = (params.shape[0],) + (1,) * (history.ndim - 2)
    yield_stress = params[:, cfg.yield_stress_index].view(expand_shape).clamp_min(cfg.eps)
    hardening = params[:, cfg.hardening_modulus_index].view(expand_shape).clamp_min(0.0)
    return history[..., 4] - (yield_stress + hardening * history[..., 0].clamp_min(0.0))


def _strain_voigt_to_tensor(strain: torch.Tensor) -> torch.Tensor:
    tensor = strain.new_zeros(*strain.shape[:-1], 3, 3)
    tensor[..., 0, 0] = strain[..., 0]
    tensor[..., 1, 1] = strain[..., 1]
    tensor[..., 0, 1] = 0.5 * strain[..., 2]
    tensor[..., 1, 0] = 0.5 * strain[..., 2]
    return tensor


def _stress_tensor_to_voigt(stress: torch.Tensor) -> torch.Tensor:
    return torch.stack([stress[..., 0, 0], stress[..., 1, 1], stress[..., 0, 1]], dim=-1)


def _trace(tensor: torch.Tensor) -> torch.Tensor:
    return tensor.diagonal(dim1=-2, dim2=-1).sum(dim=-1)


def _deviator(tensor: torch.Tensor) -> torch.Tensor:
    return tensor - _trace(tensor)[..., None, None] * _identity(tensor.device, tensor.dtype) / 3.0


def _identity(device: torch.device, dtype: torch.dtype) -> torch.Tensor:
    return torch.eye(3, device=device, dtype=dtype)


def _material_parameters(
    params: torch.Tensor,
    leading_shape: torch.Size,
    config: J2ReturnMappingConfig,
    dtype: torch.dtype,
    device: torch.device,
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
    expand_shape = (params.shape[0],) + (1,) * (len(leading_shape) - 1)
    target_shape = tuple(leading_shape)
    young_modulus = params[:, config.young_modulus_index].view(expand_shape).expand(target_shape).clamp_min(config.eps)
    poisson_ratio = params[:, config.poisson_ratio_index].view(expand_shape).expand(target_shape).clamp(-0.49, 0.49)
    yield_stress = params[:, config.yield_stress_index].view(expand_shape).expand(target_shape).clamp_min(config.eps)
    hardening = params[:, config.hardening_modulus_index].view(expand_shape).expand(target_shape).clamp_min(0.0)
    shear_modulus = (
        young_modulus / (2.0 * (1.0 + poisson_ratio))
    ).clamp_min(config.min_shear_modulus)
    bulk_modulus = young_modulus / (3.0 * (1.0 - 2.0 * poisson_ratio)).clamp_min(config.eps)
    return (
        young_modulus.to(device=device, dtype=dtype),
        poisson_ratio.to(device=device, dtype=dtype),
        yield_stress.to(device=device, dtype=dtype),
        hardening.to(device=device, dtype=dtype),
        shear_modulus.to(device=device, dtype=dtype),
        bulk_modulus.to(device=device, dtype=dtype),
    )


def _elastic_tangent(
    strain_voigt: torch.Tensor,
    shear_modulus: torch.Tensor,
    bulk_modulus: torch.Tensor,
) -> torch.Tensor:
    tangent = strain_voigt.new_zeros(*strain_voigt.shape[:-1], 3, 3)
    c11 = bulk_modulus + 4.0 * shear_modulus / 3.0
    c12 = bulk_modulus - 2.0 * shear_modulus / 3.0
    tangent[..., 0, 0] = c11
    tangent[..., 0, 1] = c12
    tangent[..., 1, 0] = c12
    tangent[..., 1, 1] = c11
    tangent[..., 2, 2] = shear_modulus
    return tangent


def _consistent_plane_strain_tangent(
    strain_voigt: torch.Tensor,
    stress_dev_trial: torch.Tensor,
    shear_modulus: torch.Tensor,
    bulk_modulus: torch.Tensor,
    hardening: torch.Tensor,
    plastic_multiplier: torch.Tensor,
    trial_von_mises: torch.Tensor,
    eps: float,
) -> torch.Tensor:
    elastic = _elastic_tangent(strain_voigt, shear_modulus, bulk_modulus)
    identity = _identity(strain_voigt.device, strain_voigt.dtype)
    q_trial = trial_von_mises.clamp_min(eps)
    denom = (3.0 * shear_modulus + hardening).clamp_min(eps)
    beta = (1.0 - 3.0 * shear_modulus * plastic_multiplier / q_trial).clamp_min(0.0)
    normal = 1.5 * stress_dev_trial / q_trial[..., None, None]
    basis = strain_voigt.new_tensor(
        [
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0],
        ]
    )
    columns = []
    for column in range(3):
        d_strain = basis[column].view(*((1,) * (strain_voigt.ndim - 1)), 3).expand_as(strain_voigt)
        d_strain_tensor = _strain_voigt_to_tensor(d_strain)
        trace_d = _trace(d_strain_tensor)
        d_stress_dev_trial = 2.0 * shear_modulus[..., None, None] * _deviator(d_strain_tensor)
        d_q = (normal * d_stress_dev_trial).sum(dim=(-2, -1))
        d_gamma = d_q / denom
        d_beta = -3.0 * shear_modulus * (
            d_gamma / q_trial
            - plastic_multiplier * d_q / q_trial.square()
        )
        d_stress = (
            bulk_modulus[..., None, None] * trace_d[..., None, None] * identity
            + beta[..., None, None] * d_stress_dev_trial
            + d_beta[..., None, None] * stress_dev_trial
        )
        columns.append(_stress_tensor_to_voigt(d_stress))
    plastic = torch.stack(columns, dim=-1)
    yielded = (plastic_multiplier > 0.0).to(dtype=strain_voigt.dtype)[..., None, None]
    return yielded * plastic + (1.0 - yielded) * elastic


def _algorithmic_tangent(
    strain_voigt: torch.Tensor,
    stress_dev_trial: torch.Tensor,
    shear_modulus: torch.Tensor,
    bulk_modulus: torch.Tensor,
    hardening: torch.Tensor,
    plastic_multiplier: torch.Tensor,
    eps: float,
) -> torch.Tensor:
    elastic = _elastic_tangent(strain_voigt, shear_modulus, bulk_modulus)
    von_mises_trial = (1.5 * stress_dev_trial.square().sum(dim=(-2, -1))).clamp_min(eps).sqrt()
    normal = _stress_tensor_to_voigt(1.5 * stress_dev_trial / von_mises_trial[..., None, None].clamp_min(eps))
    c_normal = torch.einsum("beij,bej->bei", elastic, normal)
    denom = (
        torch.einsum("bei,bei->be", normal, c_normal)
        + hardening
    ).clamp_min(eps)
    plastic = elastic - torch.einsum("bei,bej->beij", c_normal, c_normal) / denom[..., None, None]
    yielded = (plastic_multiplier > 0.0).to(dtype=strain_voigt.dtype)[..., None, None]
    return yielded * plastic + (1.0 - yielded) * elastic
