from __future__ import annotations

from dataclasses import dataclass

import torch
from torch import nn

from pcgno_dt.physics.j2_return import (
    DifferentiableJ2PlaneStrainReturnMapping,
    DifferentiableJ2ReturnMapping,
    J2ReturnMappingConfig,
    TrueDifferentiableJ2PlaneStrainReturnMapping,
)


@dataclass(frozen=True)
class HistoryGraphOperatorConfig:
    num_parameters: int
    num_fields: int = 2
    spatial_dim: int = 2
    history_dim: int = 5
    hidden_dim: int = 96
    num_message_passing_layers: int = 3
    k_neighbors: int = 8
    min_log_variance: float = -8.0
    max_log_variance: float = 4.0
    enforce_j2_irreversibility: bool = True
    thermo_hard_j2_return: bool = False
    predict_qp_history: bool = False
    num_quadrature_points: int = 1
    qp_feature_conditioning: bool = False
    qp_embedding_dim: int = 8
    qp_dual_history_head: bool = False
    qp_dual_sparse_initialization: bool = False
    qp_plastic_memory_corrector: bool = False
    qp_plastic_increment_scale: float = 1.0e-4
    qp_plastic_gate_floor: float = 1.0e-2
    qp_plastic_gate_power: float = 1.0
    j2_yield_flag_sharpness: float = 20.0
    true_differentiable_j2_return: bool = False
    path_feature_dim: int = 3


class HistoryGraphOperator(nn.Module):
    """Mesh-aware recurrent neural operator for path-dependent mechanics.

    The model advances element-wise material history and nodal displacement along a loading
    path. Node states communicate through a graph operator, while element states are updated by a
    recurrent cell conditioned on averaged nodal states and previous internal variables.
    """

    def __init__(self, config: HistoryGraphOperatorConfig) -> None:
        super().__init__()
        self.config = config
        self.node_input = nn.Sequential(
            nn.Linear(
                config.spatial_dim
                + config.num_parameters
                + 3 * config.num_fields
                + config.history_dim
                + config.path_feature_dim,
                config.hidden_dim,
            ),
            nn.SiLU(),
            nn.Linear(config.hidden_dim, config.hidden_dim),
            nn.SiLU(),
        )
        self.node_updates = nn.ModuleList(
            [
                nn.Sequential(
                    nn.Linear(2 * config.hidden_dim + config.spatial_dim, config.hidden_dim),
                    nn.SiLU(),
                    nn.Linear(config.hidden_dim, config.hidden_dim),
                )
                for _ in range(config.num_message_passing_layers)
            ]
        )
        self.node_gru = nn.GRUCell(config.hidden_dim, config.hidden_dim)
        self.element_input = nn.Sequential(
            nn.Linear(
                config.hidden_dim
                + config.num_parameters
                + config.history_dim
                + 2 * config.num_fields
                + config.path_feature_dim,
                config.hidden_dim,
            ),
            nn.SiLU(),
            nn.Linear(config.hidden_dim, config.hidden_dim),
            nn.SiLU(),
        )
        self.element_gru = nn.GRUCell(config.hidden_dim, config.hidden_dim)
        self.displacement_delta = nn.Linear(config.hidden_dim, config.num_fields)
        self.logvar_head = nn.Linear(config.hidden_dim, config.num_fields)
        self.history_head = nn.Linear(config.hidden_dim, config.history_dim)
        self.qp_history_head = (
            nn.Linear(config.hidden_dim, config.num_quadrature_points * config.history_dim)
            if config.predict_qp_history
            else None
        )
        self.qp_embedding = (
            nn.Embedding(config.num_quadrature_points, config.qp_embedding_dim)
            if config.predict_qp_history and config.qp_feature_conditioning
            else None
        )
        self.qp_conditioned_history_head = (
            nn.Sequential(
                nn.Linear(
                    config.hidden_dim
                    + config.num_parameters
                    + config.history_dim
                    + 3
                    + config.qp_embedding_dim,
                    config.hidden_dim,
                ),
                nn.SiLU(),
                nn.Linear(config.hidden_dim, config.history_dim),
            )
            if config.predict_qp_history and config.qp_feature_conditioning
            else None
        )
        qp_conditioned_dim = (
            config.hidden_dim
            + config.num_parameters
            + config.history_dim
            + 3
            + config.qp_embedding_dim
        )
        self.qp_plastic_scalar_head = (
            nn.Sequential(
                nn.Linear(qp_conditioned_dim, config.hidden_dim),
                nn.SiLU(),
                nn.Linear(config.hidden_dim, 4),
            )
            if (
                config.predict_qp_history
                and config.qp_feature_conditioning
                and config.qp_dual_history_head
                and config.history_dim >= 5
            )
            else None
        )
        self.qp_stress_consistency_head = (
            nn.Sequential(
                nn.Linear(qp_conditioned_dim, config.hidden_dim),
                nn.SiLU(),
                nn.Linear(config.hidden_dim, 1),
            )
            if (
                config.predict_qp_history
                and config.qp_feature_conditioning
                and config.qp_dual_history_head
                and config.history_dim >= 5
            )
            else None
        )
        self.qp_extra_history_head = (
            nn.Sequential(
                nn.Linear(qp_conditioned_dim, config.hidden_dim),
                nn.SiLU(),
                nn.Linear(config.hidden_dim, config.history_dim - 5),
            )
            if (
                config.predict_qp_history
                and config.qp_feature_conditioning
                and config.qp_dual_history_head
                and config.history_dim > 5
            )
            else None
        )
        self.j2_scalar_return = (
            DifferentiableJ2ReturnMapping(
                J2ReturnMappingConfig(yield_flag_sharpness=config.j2_yield_flag_sharpness)
            )
            if config.thermo_hard_j2_return
            else None
        )
        j2_tensor_cls = (
            TrueDifferentiableJ2PlaneStrainReturnMapping
            if config.true_differentiable_j2_return
            else DifferentiableJ2PlaneStrainReturnMapping
        )
        self.j2_tensor_return = (
            j2_tensor_cls(J2ReturnMappingConfig(yield_flag_sharpness=config.j2_yield_flag_sharpness))
            if config.thermo_hard_j2_return
            else None
        )
        self._initialize_qp_dual_heads()

    def forward(
        self,
        coords: torch.Tensor,
        params: torch.Tensor,
        forcing_sequence: torch.Tensor,
        initial_history: torch.Tensor | None = None,
        connectivity: torch.Tensor | None = None,
        initial_plastic_strain: torch.Tensor | None = None,
        initial_qp_history: torch.Tensor | None = None,
        teacher_history: torch.Tensor | None = None,
        teacher_qp_history: torch.Tensor | None = None,
        teacher_plastic_strain: torch.Tensor | None = None,
        teacher_forcing_ratio: float = 0.0,
    ) -> dict[str, torch.Tensor]:
        if coords.ndim != 3 or coords.shape[-1] != self.config.spatial_dim:
            raise ValueError(f"coords must have shape [batch, nodes, {self.config.spatial_dim}]")
        if params.ndim != 2 or params.shape[-1] != self.config.num_parameters:
            raise ValueError(f"params must have shape [batch, {self.config.num_parameters}]")
        if forcing_sequence.ndim != 4 or forcing_sequence.shape[-1] != self.config.num_fields:
            raise ValueError("forcing_sequence must have shape [batch, steps, nodes, fields]")
        if coords.shape[0] != params.shape[0] or coords.shape[0] != forcing_sequence.shape[0]:
            raise ValueError("coords, params, and forcing_sequence must share batch dimension")
        if coords.shape[1] != forcing_sequence.shape[2]:
            raise ValueError("coords and forcing_sequence must share node count")

        batch_size, n_steps, n_nodes, _ = forcing_sequence.shape
        connectivity_local = _prepare_connectivity(connectivity, coords.device)
        n_elements = _num_elements(connectivity_local, n_nodes)
        history = _initial_history(
            initial_history,
            batch_size=batch_size,
            n_elements=n_elements,
            history_dim=self.config.history_dim,
            device=coords.device,
            dtype=coords.dtype,
        )
        qp_history = _initial_qp_history(
            initial_qp_history,
            batch_size=batch_size,
            n_elements=n_elements,
            n_qp=self.config.num_quadrature_points,
            history_dim=self.config.history_dim,
            device=coords.device,
            dtype=coords.dtype,
        )
        if self.config.predict_qp_history:
            history = qp_history.mean(dim=2)
        node_state = coords.new_zeros(batch_size, n_nodes, self.config.hidden_dim)
        element_state = coords.new_zeros(batch_size, n_elements, self.config.hidden_dim)
        displacement = coords.new_zeros(batch_size, n_nodes, self.config.num_fields)
        plastic_strain = _initial_plastic_strain(
            initial_plastic_strain,
            batch_size=batch_size,
            n_elements=n_elements,
            device=coords.device,
            dtype=coords.dtype,
        )
        plastic_strain_qp = _initial_qp_plastic_strain(
            initial_plastic_strain,
            batch_size=batch_size,
            n_elements=n_elements,
            n_qp=self.config.num_quadrature_points,
            device=coords.device,
            dtype=coords.dtype,
        )
        adjacency = _knn_adjacency(coords, self.config.k_neighbors)
        previous_forcing = coords.new_zeros(batch_size, n_nodes, self.config.num_fields)
        previous_forcing_increment = coords.new_zeros(batch_size, n_nodes, self.config.num_fields)

        displacement_steps = []
        logvar_steps = []
        history_steps = []
        qp_history_steps = []
        plastic_strain_steps = []
        plastic_strain_qp_steps = []
        predicted_history_steps = []
        predicted_qp_history_steps = []
        predicted_plastic_strain_steps = []
        predicted_plastic_strain_qp_steps = []
        stress_steps = []
        tangent_steps = []
        yield_function_steps = []
        strain_steps = []
        qp_stress_steps = []
        qp_tangent_steps = []
        qp_yield_function_steps = []
        qp_strain_steps = []
        qp_trial_yield_function_steps = []
        qp_trial_von_mises_steps = []
        qp_plastic_multiplier_steps = []
        qp_consistency_residual_steps = []
        for step in range(n_steps):
            forcing = forcing_sequence[:, step]
            forcing_increment = forcing - previous_forcing
            path_features = _path_step_features(
                forcing_increment,
                previous_forcing_increment,
                step,
                n_steps,
            )
            path_features_nodes = path_features.unsqueeze(1).expand(-1, n_nodes, -1)
            history_for_nodes = _element_history_to_nodes(history, connectivity_local, n_nodes)
            node_features = self.node_input(
                torch.cat(
                    [
                        coords,
                        params.unsqueeze(1).expand(-1, n_nodes, -1),
                        forcing,
                        forcing_increment,
                        displacement,
                        history_for_nodes,
                        path_features_nodes,
                    ],
                    dim=-1,
                )
            )
            for update in self.node_updates:
                messages = torch.bmm(adjacency, node_features)
                node_features = node_features + update(torch.cat([node_features, messages, coords], dim=-1))
            node_state = self.node_gru(
                node_features.reshape(batch_size * n_nodes, -1),
                node_state.reshape(batch_size * n_nodes, -1),
            ).view(batch_size, n_nodes, -1)
            displacement = displacement + self.displacement_delta(node_state)
            logvar = self.logvar_head(node_state).clamp(
                self.config.min_log_variance,
                self.config.max_log_variance,
            )

            element_node_state = _nodes_to_elements(node_state, connectivity_local)
            element_force = _nodes_to_elements(forcing, connectivity_local)
            element_force_increment = _nodes_to_elements(forcing_increment, connectivity_local)
            path_features_elements = path_features.unsqueeze(1).expand(-1, n_elements, -1)
            element_features = self.element_input(
                torch.cat(
                    [
                        element_node_state,
                        params.unsqueeze(1).expand(-1, n_elements, -1),
                        history,
                        element_force,
                        element_force_increment,
                        path_features_elements,
                    ],
                    dim=-1,
                )
            )
            element_state = self.element_gru(
                element_features.reshape(batch_size * n_elements, -1),
                element_state.reshape(batch_size * n_elements, -1),
            ).view(batch_size, n_elements, -1)
            if self.config.predict_qp_history:
                if self.qp_history_head is None:
                    raise RuntimeError("qp_history_head is required when predict_qp_history=True")
                strain_qp_voigt = (
                    _element_quadrature_strain_voigt(
                        coords,
                        displacement,
                        connectivity_local,
                        self.config.num_quadrature_points,
                    )
                    if connectivity_local is not None
                    else None
                )
                raw_qp_update = self._raw_qp_update(
                    element_state,
                    qp_history,
                    params,
                    strain_qp_voigt,
                )
                if (
                    self.config.true_differentiable_j2_return
                    and self.j2_tensor_return is not None
                    and connectivity_local is not None
                ):
                    if strain_qp_voigt is None:
                        raise RuntimeError("true differentiable QP J2 return requires quadrature strain")
                    state = self.j2_tensor_return(strain_qp_voigt, plastic_strain_qp, qp_history, params)
                    qp_history = state.history
                    plastic_strain_qp = state.plastic_strain
                    plastic_strain = plastic_strain_qp.mean(dim=2)
                    history = qp_history.mean(dim=2)
                    qp_stress_steps.append(state.stress_voigt)
                    qp_tangent_steps.append(state.algorithmic_tangent)
                    qp_yield_function_steps.append(state.yield_function)
                    qp_strain_steps.append(strain_qp_voigt)
                    if hasattr(state, "trial_yield_function"):
                        qp_trial_yield_function_steps.append(state.trial_yield_function)
                    if hasattr(state, "trial_von_mises"):
                        qp_trial_von_mises_steps.append(state.trial_von_mises)
                    if hasattr(state, "plastic_multiplier"):
                        qp_plastic_multiplier_steps.append(state.plastic_multiplier)
                    if hasattr(state, "consistency_residual"):
                        qp_consistency_residual_steps.append(state.consistency_residual)
                else:
                    qp_history = self._advance_qp_history(qp_history, raw_qp_update, params)
                    history = qp_history.mean(dim=2)
            else:
                proposed_history = self.history_head(element_state)
                strain_voigt = (
                    _element_strain_voigt(coords, displacement, connectivity_local)
                    if self.j2_tensor_return is not None and connectivity_local is not None
                    else None
                )
                advanced = self._advance_history(
                    history,
                    proposed_history,
                    params,
                    strain_voigt=strain_voigt,
                    plastic_strain=plastic_strain,
                )
                if isinstance(advanced, tuple):
                    history, plastic_strain, stress_voigt, tangent, yield_function = advanced
                    stress_steps.append(stress_voigt)
                    tangent_steps.append(tangent)
                    yield_function_steps.append(yield_function)
                    if strain_voigt is not None:
                        strain_steps.append(strain_voigt)
                else:
                    history = advanced
            predicted_history_steps.append(history)
            predicted_plastic_strain_steps.append(plastic_strain)
            if self.config.predict_qp_history:
                predicted_qp_history_steps.append(qp_history)
                predicted_plastic_strain_qp_steps.append(plastic_strain_qp)
            if teacher_history is not None and teacher_forcing_ratio > 0.0:
                ratio = float(max(0.0, min(teacher_forcing_ratio, 1.0)))
                if self.config.predict_qp_history and teacher_qp_history is not None:
                    target_qp_history = teacher_qp_history[:, step, :, :, : self.config.history_dim].to(
                        device=qp_history.device,
                        dtype=qp_history.dtype,
                    )
                    qp_history = (1.0 - ratio) * qp_history + ratio * target_qp_history
                    history = qp_history.mean(dim=2)
                else:
                    target_history = teacher_history[:, step, :, : self.config.history_dim].to(
                        device=history.device,
                        dtype=history.dtype,
                    )
                    history = (1.0 - ratio) * history + ratio * target_history
                    if self.config.predict_qp_history:
                        qp_history = history.unsqueeze(2).expand_as(qp_history).contiguous()
                if teacher_plastic_strain is not None and not self.config.predict_qp_history:
                    target_plastic_strain = _history_voigt_to_tensor(
                        teacher_plastic_strain[:, step],
                        device=plastic_strain.device,
                        dtype=plastic_strain.dtype,
                    )
                    plastic_strain = (1.0 - ratio) * plastic_strain + ratio * target_plastic_strain
                if teacher_plastic_strain is not None and self.config.predict_qp_history:
                    target_plastic_strain = _history_voigt_to_tensor(
                        teacher_plastic_strain[:, step],
                        device=plastic_strain_qp.device,
                        dtype=plastic_strain_qp.dtype,
                    )
                    if target_plastic_strain.ndim == 4:
                        target_plastic_strain = target_plastic_strain.unsqueeze(2).expand_as(plastic_strain_qp)
                    plastic_strain_qp = (1.0 - ratio) * plastic_strain_qp + ratio * target_plastic_strain
                    plastic_strain = plastic_strain_qp.mean(dim=2)

            displacement_steps.append(displacement)
            logvar_steps.append(logvar)
            history_steps.append(history)
            if self.config.predict_qp_history:
                qp_history_steps.append(qp_history)
                plastic_strain_qp_steps.append(plastic_strain_qp)
            plastic_strain_steps.append(plastic_strain)
            previous_forcing_increment = forcing_increment
            previous_forcing = forcing

        outputs = {
            "mean_sequence": torch.stack(displacement_steps, dim=1),
            "logvar_sequence": torch.stack(logvar_steps, dim=1),
            "history_sequence": torch.stack(history_steps, dim=1),
            "plastic_strain_sequence": torch.stack(plastic_strain_steps, dim=1),
            "mean": displacement_steps[-1],
            "logvar": logvar_steps[-1],
            "history": history_steps[-1],
            "plastic_strain": plastic_strain_steps[-1],
        }
        if qp_history_steps:
            outputs["history_qp_sequence"] = torch.stack(qp_history_steps, dim=1)
            outputs["history_qp"] = qp_history_steps[-1]
        if plastic_strain_qp_steps:
            outputs["plastic_strain_qp_sequence"] = torch.stack(plastic_strain_qp_steps, dim=1)
            outputs["plastic_strain_qp"] = plastic_strain_qp_steps[-1]
        if predicted_history_steps:
            outputs["history_prediction_sequence"] = torch.stack(predicted_history_steps, dim=1)
            outputs["history_prediction"] = predicted_history_steps[-1]
        if predicted_plastic_strain_steps:
            outputs["plastic_strain_prediction_sequence"] = torch.stack(predicted_plastic_strain_steps, dim=1)
            outputs["plastic_strain_prediction"] = predicted_plastic_strain_steps[-1]
        if predicted_qp_history_steps:
            outputs["history_qp_prediction_sequence"] = torch.stack(predicted_qp_history_steps, dim=1)
            outputs["history_qp_prediction"] = predicted_qp_history_steps[-1]
        if predicted_plastic_strain_qp_steps:
            outputs["plastic_strain_qp_prediction_sequence"] = torch.stack(predicted_plastic_strain_qp_steps, dim=1)
            outputs["plastic_strain_qp_prediction"] = predicted_plastic_strain_qp_steps[-1]
        if stress_steps:
            outputs["j2_stress_sequence"] = torch.stack(stress_steps, dim=1)
        if tangent_steps:
            outputs["j2_algorithmic_tangent_sequence"] = torch.stack(tangent_steps, dim=1)
        if yield_function_steps:
            outputs["j2_yield_function_sequence"] = torch.stack(yield_function_steps, dim=1)
        if strain_steps:
            outputs["j2_strain_sequence"] = torch.stack(strain_steps, dim=1)
        if qp_stress_steps:
            outputs["j2_qp_stress_sequence"] = torch.stack(qp_stress_steps, dim=1)
        if qp_tangent_steps:
            outputs["j2_qp_algorithmic_tangent_sequence"] = torch.stack(qp_tangent_steps, dim=1)
        if qp_yield_function_steps:
            outputs["j2_qp_yield_function_sequence"] = torch.stack(qp_yield_function_steps, dim=1)
        if qp_strain_steps:
            outputs["j2_qp_strain_sequence"] = torch.stack(qp_strain_steps, dim=1)
        if qp_trial_yield_function_steps:
            outputs["j2_qp_trial_yield_function_sequence"] = torch.stack(qp_trial_yield_function_steps, dim=1)
        if qp_trial_von_mises_steps:
            outputs["j2_qp_trial_von_mises_sequence"] = torch.stack(qp_trial_von_mises_steps, dim=1)
        if qp_plastic_multiplier_steps:
            outputs["j2_qp_plastic_multiplier_sequence"] = torch.stack(qp_plastic_multiplier_steps, dim=1)
        if qp_consistency_residual_steps:
            outputs["j2_qp_consistency_residual_sequence"] = torch.stack(qp_consistency_residual_steps, dim=1)
        return outputs

    def _advance_history(
        self,
        previous: torch.Tensor,
        raw_update: torch.Tensor,
        params: torch.Tensor,
        strain_voigt: torch.Tensor | None = None,
        plastic_strain: torch.Tensor | None = None,
    ) -> torch.Tensor | tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
        if (
            self.j2_tensor_return is not None
            and self.config.history_dim >= 5
            and strain_voigt is not None
            and plastic_strain is not None
        ):
            state = self.j2_tensor_return(strain_voigt, plastic_strain, previous, params)
            return (
                state.history,
                state.plastic_strain,
                state.stress_voigt,
                state.algorithmic_tangent,
                state.yield_function,
            )
        if self.j2_scalar_return is not None and self.config.history_dim >= 5:
            return self.j2_scalar_return(previous, raw_update, params)
        if not self.config.enforce_j2_irreversibility or self.config.history_dim < 5:
            return previous + raw_update
        next_history = previous.clone()
        next_history[..., 0] = previous[..., 0] + torch.nn.functional.softplus(raw_update[..., 0])
        next_history[..., 1] = previous[..., 1] + torch.nn.functional.softplus(raw_update[..., 1])
        next_history[..., 2] = torch.nn.functional.softplus(raw_update[..., 2])
        next_history[..., 3] = torch.sigmoid(raw_update[..., 3])
        next_history[..., 4] = torch.nn.functional.softplus(raw_update[..., 4])
        if self.config.history_dim > 5:
            next_history[..., 5:] = previous[..., 5:] + raw_update[..., 5:]
        return next_history

    def _advance_qp_history(
        self,
        previous: torch.Tensor,
        raw_update: torch.Tensor,
        params: torch.Tensor,
    ) -> torch.Tensor:
        if previous.shape != raw_update.shape:
            raise ValueError("qp history and raw update must share shape")
        if self.config.qp_plastic_memory_corrector and self.config.history_dim >= 5:
            return self._advance_qp_history_memory_corrector(previous, raw_update, params)
        if self.j2_scalar_return is not None and self.config.history_dim >= 5:
            batch_size, n_elements, n_qp, history_dim = previous.shape
            projected = self.j2_scalar_return(
                previous.reshape(batch_size, n_elements * n_qp, history_dim),
                raw_update.reshape(batch_size, n_elements * n_qp, history_dim),
                params,
            )
            return projected.view(batch_size, n_elements, n_qp, history_dim)
        if not self.config.enforce_j2_irreversibility or self.config.history_dim < 5:
            return previous + raw_update
        next_history = previous.clone()
        next_history[..., 0] = previous[..., 0] + torch.nn.functional.softplus(raw_update[..., 0])
        next_history[..., 1] = previous[..., 1] + torch.nn.functional.softplus(raw_update[..., 1])
        next_history[..., 2] = torch.nn.functional.softplus(raw_update[..., 2])
        next_history[..., 3] = torch.sigmoid(raw_update[..., 3])
        next_history[..., 4] = torch.nn.functional.softplus(raw_update[..., 4])
        if self.config.history_dim > 5:
            next_history[..., 5:] = previous[..., 5:] + raw_update[..., 5:]
        return next_history

    def _advance_qp_history_memory_corrector(
        self,
        previous: torch.Tensor,
        raw_update: torch.Tensor,
        params: torch.Tensor,
    ) -> torch.Tensor:
        """Monotone QP plastic-memory update that exposes scalar plastic increments.

        The scalar J2 projection uses the predicted trial von-Mises channel to infer the
        plastic multiplier.  That is mechanically admissible, but it gives the network no
        direct route from the QP plastic-history losses to the eqp/work increment logits.
        This corrector keeps the hard monotonicity and plastic-work lower bound, while
        allowing the learned QP update to directly predict nonzero active-zone plastic
        increments.
        """

        if params.ndim != 2 or params.shape[-1] < 4:
            raise ValueError("params must contain [E, nu, sigma_y, H] channels")
        dtype = previous.dtype
        device = previous.device
        params = params.to(device=device, dtype=dtype)
        expand_shape = (params.shape[0],) + (1,) * (previous.ndim - 2)
        yield_stress = params[:, 2].view(expand_shape).clamp_min(1.0e-12)
        hardening = params[:, 3].view(expand_shape).clamp_min(0.0)
        scale = max(float(self.config.qp_plastic_increment_scale), 1.0e-12)
        gate_floor = max(float(self.config.qp_plastic_gate_floor), 0.0)
        gate_power = max(float(self.config.qp_plastic_gate_power), 1.0)

        eqp_old = previous[..., 0].clamp_min(0.0)
        work_old = previous[..., 1].clamp_min(0.0)
        raw_eqp_increment = torch.nn.functional.softplus(raw_update[..., 0]) * scale
        learned_yield_weight = torch.sigmoid(raw_update[..., 3])
        plastic_gate = learned_yield_weight.pow(gate_power)
        plastic_multiplier = raw_eqp_increment * (gate_floor + plastic_gate)
        eqp_next = eqp_old + plastic_multiplier

        flow_old = yield_stress + hardening * eqp_old
        plastic_work_increment = (
            yield_stress * plastic_multiplier
            + 0.5 * hardening * (eqp_next.square() - eqp_old.square())
        ).clamp_min(0.0)
        work_next = work_old + plastic_work_increment

        flow_next = yield_stress + hardening * eqp_next
        trial_von_mises = torch.nn.functional.softplus(raw_update[..., 4])
        elastic_von_mises = torch.minimum(trial_von_mises, flow_old)
        von_mises_next = learned_yield_weight * flow_next + (1.0 - learned_yield_weight) * elastic_von_mises

        next_history = previous.clone()
        next_history[..., 0] = eqp_next
        next_history[..., 1] = work_next
        next_history[..., 2] = plastic_multiplier
        next_history[..., 3] = learned_yield_weight.clamp(0.0, 1.0)
        next_history[..., 4] = von_mises_next.clamp_min(0.0)
        if self.config.history_dim > 5:
            next_history[..., 5:] = previous[..., 5:] + raw_update[..., 5:]
        return next_history

    def _raw_qp_update(
        self,
        element_state: torch.Tensor,
        qp_history: torch.Tensor,
        params: torch.Tensor,
        strain_qp_voigt: torch.Tensor | None,
    ) -> torch.Tensor:
        batch_size, n_elements, n_qp, _ = qp_history.shape
        if not self.config.qp_feature_conditioning:
            if self.qp_history_head is None:
                raise RuntimeError("qp_history_head is required when predict_qp_history=True")
            return self.qp_history_head(element_state).view(
                batch_size,
                n_elements,
                self.config.num_quadrature_points,
                self.config.history_dim,
            )
        if self.qp_conditioned_history_head is None or self.qp_embedding is None:
            raise RuntimeError("QP-conditioned history head is not initialized")
        if strain_qp_voigt is None:
            strain_qp_voigt = qp_history.new_zeros(batch_size, n_elements, n_qp, 3)
        qp_ids = torch.arange(n_qp, device=qp_history.device)
        qp_features = self.qp_embedding(qp_ids).to(dtype=qp_history.dtype)
        qp_features = qp_features.view(1, 1, n_qp, -1).expand(batch_size, n_elements, -1, -1)
        features = torch.cat(
            [
                element_state.unsqueeze(2).expand(-1, -1, n_qp, -1),
                params.unsqueeze(1).unsqueeze(2).expand(-1, n_elements, n_qp, -1),
                qp_history,
                strain_qp_voigt.to(device=qp_history.device, dtype=qp_history.dtype),
                qp_features,
            ],
            dim=-1,
        )
        if self.config.qp_dual_history_head:
            return self._raw_qp_dual_head_update(features, qp_history)
        return self.qp_conditioned_history_head(features)

    def _raw_qp_dual_head_update(
        self,
        features: torch.Tensor,
        qp_history: torch.Tensor,
    ) -> torch.Tensor:
        if self.qp_plastic_scalar_head is None or self.qp_stress_consistency_head is None:
            raise RuntimeError("dual QP history heads are not initialized")
        plastic_raw = self.qp_plastic_scalar_head(features)
        stress_raw = self.qp_stress_consistency_head(features)
        raw = qp_history.new_zeros(*qp_history.shape[:-1], self.config.history_dim)
        raw[..., 0] = plastic_raw[..., 0]
        raw[..., 1] = plastic_raw[..., 1]
        raw[..., 2] = plastic_raw[..., 2]
        raw[..., 3] = plastic_raw[..., 3]
        raw[..., 4] = stress_raw[..., 0]
        if self.config.history_dim > 5:
            if self.qp_extra_history_head is None:
                raise RuntimeError("extra QP history head is required for history_dim > 5")
            raw[..., 5:] = self.qp_extra_history_head(features)
        return raw

    def _initialize_qp_dual_heads(self) -> None:
        if self.qp_plastic_scalar_head is None or not self.config.qp_dual_sparse_initialization:
            return
        final = self.qp_plastic_scalar_head[-1]
        if not isinstance(final, nn.Linear):
            return
        with torch.no_grad():
            final.bias.zero_()
            final.bias[0] = -2.0
            final.bias[1] = -2.0
            final.bias[2] = -2.0
            final.bias[3] = -4.0


def _prepare_connectivity(connectivity: torch.Tensor | None, device: torch.device) -> torch.Tensor | None:
    if connectivity is None:
        return None
    return torch.as_tensor(connectivity, dtype=torch.long, device=device)


def _num_elements(connectivity: torch.Tensor | None, n_nodes: int) -> int:
    if connectivity is None:
        return n_nodes
    return int(connectivity.shape[0])


def _path_step_features(
    forcing_increment: torch.Tensor,
    previous_forcing_increment: torch.Tensor,
    step: int,
    n_steps: int,
) -> torch.Tensor:
    if forcing_increment.ndim != 3:
        raise ValueError("forcing_increment must have shape [batch, nodes, fields]")
    global_increment = forcing_increment.mean(dim=1)
    previous_global_increment = previous_forcing_increment.mean(dim=1)
    increment_norm = global_increment.square().sum(dim=-1).sqrt()
    previous_norm = previous_global_increment.square().sum(dim=-1).sqrt()
    dot = (global_increment * previous_global_increment).sum(dim=-1)
    reversal = ((dot < 0.0) & (increment_norm * previous_norm > 1.0e-12)).to(dtype=forcing_increment.dtype)
    step_fraction = forcing_increment.new_full(
        (forcing_increment.shape[0],),
        float(step) / float(max(n_steps - 1, 1)),
    )
    relative_increment = increment_norm / (
        previous_norm + increment_norm + forcing_increment.new_tensor(1.0e-12)
    )
    return torch.stack([step_fraction, relative_increment, reversal], dim=-1)


def _initial_history(
    initial_history: torch.Tensor | None,
    batch_size: int,
    n_elements: int,
    history_dim: int,
    device: torch.device,
    dtype: torch.dtype,
) -> torch.Tensor:
    if initial_history is None:
        return torch.zeros(batch_size, n_elements, history_dim, device=device, dtype=dtype)
    history = initial_history.to(device=device, dtype=dtype)
    if history.shape != (batch_size, n_elements, history_dim):
        raise ValueError(
            f"initial_history must have shape [{batch_size}, {n_elements}, {history_dim}], got {tuple(history.shape)}"
        )
    return history


def _initial_qp_history(
    initial_qp_history: torch.Tensor | None,
    batch_size: int,
    n_elements: int,
    n_qp: int,
    history_dim: int,
    device: torch.device,
    dtype: torch.dtype,
) -> torch.Tensor:
    if initial_qp_history is None:
        return torch.zeros(batch_size, n_elements, n_qp, history_dim, device=device, dtype=dtype)
    history = initial_qp_history.to(device=device, dtype=dtype)
    if history.shape != (batch_size, n_elements, n_qp, history_dim):
        raise ValueError(
            "initial_qp_history must have shape "
            f"[{batch_size}, {n_elements}, {n_qp}, {history_dim}], got {tuple(history.shape)}"
        )
    return history


def _initial_plastic_strain(
    initial_plastic_strain: torch.Tensor | None,
    batch_size: int,
    n_elements: int,
    device: torch.device,
    dtype: torch.dtype,
) -> torch.Tensor:
    if initial_plastic_strain is None:
        return torch.zeros(batch_size, n_elements, 3, 3, device=device, dtype=dtype)
    value = _history_voigt_to_tensor(initial_plastic_strain, device=device, dtype=dtype)
    if value.shape == (batch_size, n_elements, 3, 3):
        return value
    if value.ndim == 5 and value.shape[:2] == (batch_size, n_elements):
        return value.mean(dim=2)
    raise ValueError("initial plastic strain is incompatible with the element layout")


def _initial_qp_plastic_strain(
    initial_plastic_strain: torch.Tensor | None,
    batch_size: int,
    n_elements: int,
    n_qp: int,
    device: torch.device,
    dtype: torch.dtype,
) -> torch.Tensor:
    if initial_plastic_strain is None:
        return torch.zeros(batch_size, n_elements, n_qp, 3, 3, device=device, dtype=dtype)
    value = _history_voigt_to_tensor(initial_plastic_strain, device=device, dtype=dtype)
    if value.shape == (batch_size, n_elements, n_qp, 3, 3):
        return value
    if value.shape == (batch_size, n_elements, 3, 3):
        return value.unsqueeze(2).expand(-1, -1, n_qp, -1, -1).contiguous()
    raise ValueError("initial qp plastic strain is incompatible with the quadrature layout")


def _history_voigt_to_tensor(
    plastic_strain: torch.Tensor,
    device: torch.device,
    dtype: torch.dtype,
) -> torch.Tensor:
    value = plastic_strain.to(device=device, dtype=dtype)
    if value.ndim >= 4 and value.shape[-2:] == (3, 3):
        return value
    if value.ndim not in {3, 4} or value.shape[-1] not in {3, 6}:
        raise ValueError(
            "plastic strain must have shape [batch, elements, 3/6], "
            "[batch, elements, q_points, 3/6], or tensor form"
        )
    tensor = value.new_zeros(*value.shape[:-1], 3, 3)
    tensor[..., 0, 0] = value[..., 0]
    tensor[..., 1, 1] = value[..., 1]
    if value.shape[-1] == 3:
        tensor[..., 0, 1] = value[..., 2]
        tensor[..., 1, 0] = value[..., 2]
    else:
        tensor[..., 2, 2] = value[..., 2]
        tensor[..., 0, 1] = value[..., 3]
        tensor[..., 1, 0] = value[..., 3]
        tensor[..., 1, 2] = value[..., 4]
        tensor[..., 2, 1] = value[..., 4]
        tensor[..., 0, 2] = value[..., 5]
        tensor[..., 2, 0] = value[..., 5]
    return tensor


def _knn_adjacency(coords: torch.Tensor, k_neighbors: int) -> torch.Tensor:
    batch, n_points, _ = coords.shape
    if n_points < 2:
        return coords.new_ones(batch, n_points, n_points)
    k = min(k_neighbors + 1, n_points)
    distances = torch.cdist(coords, coords)
    neighbor_idx = distances.topk(k=k, largest=False, dim=-1).indices[..., 1:]
    adjacency = coords.new_zeros(batch, n_points, n_points)
    adjacency.scatter_(dim=2, index=neighbor_idx, value=1.0)
    return adjacency / adjacency.sum(dim=-1, keepdim=True).clamp_min(1.0)


def _element_history_to_nodes(
    history: torch.Tensor,
    connectivity: torch.Tensor | None,
    n_nodes: int,
) -> torch.Tensor:
    if connectivity is None:
        if history.shape[1] == n_nodes:
            return history
        return history.mean(dim=1, keepdim=True).expand(-1, n_nodes, -1)
    batch_size, _, history_dim = history.shape
    nodal = history.new_zeros(batch_size, n_nodes, history_dim)
    counts = history.new_zeros(n_nodes, 1)
    for local in range(connectivity.shape[1]):
        nodes = connectivity[:, local]
        nodal.index_add_(1, nodes, history)
        counts.index_add_(0, nodes, torch.ones_like(counts).index_select(0, nodes))
    return nodal / counts.transpose(0, 1).unsqueeze(-1).clamp_min(1.0)


def _nodes_to_elements(values: torch.Tensor, connectivity: torch.Tensor | None) -> torch.Tensor:
    if connectivity is None:
        return values
    element_values = values.index_select(dim=1, index=connectivity.reshape(-1))
    element_values = element_values.view(values.shape[0], connectivity.shape[0], connectivity.shape[1], values.shape[-1])
    return element_values.mean(dim=2)


def _element_strain_voigt(
    coords: torch.Tensor,
    displacement: torch.Tensor,
    connectivity: torch.Tensor,
) -> torch.Tensor:
    if connectivity.shape[1] == 6:
        return _quadratic_element_centroid_strain_voigt(coords, displacement, connectivity)
    if connectivity.shape[1] != 3:
        raise ValueError("tensorial J2 return mapping currently requires T3 or T6 triangular elements")
    tri_coords = coords.index_select(dim=1, index=connectivity.reshape(-1))
    tri_coords = tri_coords.view(coords.shape[0], connectivity.shape[0], 3, coords.shape[-1])
    tri_disp = displacement.index_select(dim=1, index=connectivity.reshape(-1))
    tri_disp = tri_disp.view(displacement.shape[0], connectivity.shape[0], 3, displacement.shape[-1])

    x1, y1 = tri_coords[..., 0, 0], tri_coords[..., 0, 1]
    x2, y2 = tri_coords[..., 1, 0], tri_coords[..., 1, 1]
    x3, y3 = tri_coords[..., 2, 0], tri_coords[..., 2, 1]
    twice_area = ((x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1)).clamp_min(1.0e-12)
    b = torch.stack([y2 - y3, y3 - y1, y1 - y2], dim=-1)
    c = torch.stack([x3 - x2, x1 - x3, x2 - x1], dim=-1)
    ux = tri_disp[..., 0]
    uy = tri_disp[..., 1]
    eps_xx = (b * ux).sum(dim=-1) / twice_area
    eps_yy = (c * uy).sum(dim=-1) / twice_area
    gamma_xy = ((c * ux) + (b * uy)).sum(dim=-1) / twice_area
    return torch.stack([eps_xx, eps_yy, gamma_xy], dim=-1)


def _element_quadrature_strain_voigt(
    coords: torch.Tensor,
    displacement: torch.Tensor,
    connectivity: torch.Tensor,
    n_qp: int,
) -> torch.Tensor:
    if connectivity.shape[1] == 3:
        strain = _element_strain_voigt(coords, displacement, connectivity)
        return strain.unsqueeze(2).expand(-1, -1, n_qp, -1).contiguous()
    if connectivity.shape[1] != 6:
        raise ValueError("true qp J2 return mapping currently requires T3 or T6 triangular elements")
    if n_qp == 1:
        return _quadratic_element_centroid_strain_voigt(coords, displacement, connectivity).unsqueeze(2)
    if n_qp != 3:
        raise ValueError("T6 qp J2 return mapping supports one centroid point or three triangle quadrature points")
    q_points = coords.new_tensor(
        [
            [1.0 / 6.0, 1.0 / 6.0],
            [2.0 / 3.0, 1.0 / 6.0],
            [1.0 / 6.0, 2.0 / 3.0],
        ]
    )
    return torch.stack(
        [
            _quadratic_element_point_strain_voigt(coords, displacement, connectivity, point)
            for point in q_points
        ],
        dim=2,
    )


def _quadratic_element_centroid_strain_voigt(
    coords: torch.Tensor,
    displacement: torch.Tensor,
    connectivity: torch.Tensor,
) -> torch.Tensor:
    return _quadratic_element_point_strain_voigt(
        coords,
        displacement,
        connectivity,
        coords.new_tensor([1.0 / 3.0, 1.0 / 3.0]),
    )


def _quadratic_element_point_strain_voigt(
    coords: torch.Tensor,
    displacement: torch.Tensor,
    connectivity: torch.Tensor,
    point: torch.Tensor,
) -> torch.Tensor:
    element_coords = coords.index_select(dim=1, index=connectivity.reshape(-1))
    element_coords = element_coords.view(coords.shape[0], connectivity.shape[0], 6, coords.shape[-1])
    element_disp = displacement.index_select(dim=1, index=connectivity.reshape(-1))
    element_disp = element_disp.view(displacement.shape[0], connectivity.shape[0], 6, displacement.shape[-1])
    r, s = point[0], point[1]
    l1 = 1.0 - r - s
    l2 = r
    l3 = s
    zero = torch.zeros((), device=coords.device, dtype=coords.dtype)
    d_shape_ref = torch.stack(
        [
            torch.stack([-(4.0 * l1 - 1.0), -(4.0 * l1 - 1.0)]),
            torch.stack([4.0 * l2 - 1.0, zero]),
            torch.stack([zero, 4.0 * l3 - 1.0]),
            torch.stack([4.0 * (l1 - l2), -4.0 * l2]),
            torch.stack([4.0 * l3, 4.0 * l2]),
            torch.stack([-4.0 * l3, 4.0 * (l1 - l3)]),
        ]
    )
    jacobian = torch.einsum("na,bend->bead", d_shape_ref, element_coords)
    inv_jacobian = torch.linalg.inv(jacobian)
    grad = torch.einsum("na,bead->bend", d_shape_ref, inv_jacobian)
    ux = element_disp[..., 0]
    uy = element_disp[..., 1]
    dnx = grad[..., 0]
    dny = grad[..., 1]
    eps_xx = (dnx * ux).sum(dim=-1)
    eps_yy = (dny * uy).sum(dim=-1)
    gamma_xy = (dny * ux + dnx * uy).sum(dim=-1)
    return torch.stack([eps_xx, eps_yy, gamma_xy], dim=-1)
