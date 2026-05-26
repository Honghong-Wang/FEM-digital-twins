from __future__ import annotations

from dataclasses import dataclass

import torch
from torch import nn

from pcgno_dt.physics.j2_return import DifferentiableJ2ReturnMapping, J2ReturnMappingConfig


@dataclass(frozen=True)
class ControlledPathOperatorConfig:
    num_parameters: int
    num_fields: int = 2
    spatial_dim: int = 2
    history_dim: int = 5
    hidden_dim: int = 96
    thermo_hard_j2_return: bool = False
    enforce_j2_irreversibility: bool = True
    min_log_variance: float = -8.0
    max_log_variance: float = 4.0


@dataclass(frozen=True)
class NeuralCDEPathOperatorConfig:
    num_parameters: int
    num_fields: int = 2
    spatial_dim: int = 2
    history_dim: int = 5
    hidden_dim: int = 96
    thermo_hard_j2_return: bool = False
    enforce_j2_irreversibility: bool = True
    min_log_variance: float = -8.0
    max_log_variance: float = 4.0


@dataclass(frozen=True)
class WindowedHistoryOperatorConfig:
    num_parameters: int
    num_fields: int = 2
    spatial_dim: int = 2
    history_dim: int = 5
    hidden_dim: int = 96
    window_size: int = 3
    num_attention_heads: int = 1
    enforce_j2_irreversibility: bool = True
    min_log_variance: float = -8.0
    max_log_variance: float = 4.0


@dataclass(frozen=True)
class FaithfulHANOOperatorConfig:
    num_parameters: int
    num_fields: int = 2
    spatial_dim: int = 2
    history_dim: int = 5
    strain_dim: int = 3
    stress_dim: int = 3
    hidden_dim: int = 96
    window_size: int = 4
    num_attention_heads: int = 2
    num_spectral_modes: int = 4
    enforce_j2_irreversibility: bool = True
    min_log_variance: float = -8.0
    max_log_variance: float = 4.0


class ControlledPathOperator(nn.Module):
    """Load-increment GRU path baseline retained for ablation continuity."""

    def __init__(self, config: ControlledPathOperatorConfig) -> None:
        super().__init__()
        self.config = config
        control_dim = config.num_parameters + 2 * config.num_fields + 1
        self.control_encoder = nn.Sequential(
            nn.Linear(control_dim, config.hidden_dim),
            nn.SiLU(),
            nn.Linear(config.hidden_dim, config.hidden_dim),
            nn.SiLU(),
        )
        self.control_gru = nn.GRUCell(config.hidden_dim, config.hidden_dim)
        self.node_decoder = _node_decoder(config.spatial_dim, config.num_parameters, config.num_fields, config.hidden_dim)
        self.displacement_delta = nn.Linear(config.hidden_dim, config.num_fields)
        self.logvar_head = nn.Linear(config.hidden_dim, config.num_fields)
        self.history_decoder = _history_decoder(
            config.spatial_dim,
            config.num_parameters,
            config.num_fields,
            config.history_dim,
            config.hidden_dim,
        )
        self.j2_return = (
            DifferentiableJ2ReturnMapping(J2ReturnMappingConfig())
            if config.thermo_hard_j2_return
            else None
        )

    def forward(
        self,
        coords: torch.Tensor,
        params: torch.Tensor,
        forcing_sequence: torch.Tensor,
        initial_history: torch.Tensor | None = None,
        connectivity: torch.Tensor | None = None,
        teacher_history: torch.Tensor | None = None,
        teacher_forcing_ratio: float = 0.0,
    ) -> dict[str, torch.Tensor]:
        del teacher_history, teacher_forcing_ratio
        batch_size, n_steps, n_nodes, _ = _validate_path_inputs(coords, forcing_sequence)
        connectivity_local = _prepare_connectivity(connectivity, coords.device)
        n_elements = _num_elements(connectivity_local, n_nodes)
        history = _initial_history(
            initial_history,
            batch_size,
            n_elements,
            self.config.history_dim,
            coords.device,
            coords.dtype,
        )
        latent = coords.new_zeros(batch_size, self.config.hidden_dim)
        displacement = coords.new_zeros(batch_size, n_nodes, self.config.num_fields)
        previous_global_load = coords.new_zeros(batch_size, self.config.num_fields)
        displacement_steps = []
        logvar_steps = []
        history_steps = []
        for step in range(n_steps):
            forcing = forcing_sequence[:, step]
            global_load = forcing.mean(dim=1)
            load_increment = global_load - previous_global_load
            previous_global_load = global_load
            step_fraction = coords.new_full((batch_size, 1), float(step + 1) / max(n_steps, 1))
            control = self.control_encoder(torch.cat([params, global_load, load_increment, step_fraction], dim=-1))
            latent = self.control_gru(control, latent)
            displacement, logvar, history = self._decode_step(
                coords,
                params,
                forcing,
                connectivity_local,
                latent,
                displacement,
                history,
            )
            displacement_steps.append(displacement)
            logvar_steps.append(logvar)
            history_steps.append(history)
        return _pack_outputs(displacement_steps, logvar_steps, history_steps)

    def _decode_step(
        self,
        coords: torch.Tensor,
        params: torch.Tensor,
        forcing: torch.Tensor,
        connectivity: torch.Tensor | None,
        latent: torch.Tensor,
        displacement: torch.Tensor,
        history: torch.Tensor,
    ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        n_nodes = coords.shape[1]
        n_elements = _num_elements(connectivity, n_nodes)
        latent_nodes = latent.unsqueeze(1).expand(-1, n_nodes, -1)
        node_features = self.node_decoder(
            torch.cat([coords, params.unsqueeze(1).expand(-1, n_nodes, -1), forcing, latent_nodes], dim=-1)
        )
        displacement = displacement + self.displacement_delta(node_features)
        logvar = self.logvar_head(node_features).clamp(self.config.min_log_variance, self.config.max_log_variance)
        raw_history = self.history_decoder(
            torch.cat(
                [
                    _nodes_to_elements(coords, connectivity),
                    params.unsqueeze(1).expand(-1, n_elements, -1),
                    _nodes_to_elements(forcing, connectivity),
                    history,
                    latent.unsqueeze(1).expand(-1, n_elements, -1),
                ],
                dim=-1,
            )
        )
        history = self._advance_history(history, raw_history, params)
        return displacement, logvar, history

    def _advance_history(self, previous: torch.Tensor, raw_update: torch.Tensor, params: torch.Tensor) -> torch.Tensor:
        if self.j2_return is not None and self.config.history_dim >= 5:
            return self.j2_return(previous, raw_update, params)
        if not self.config.enforce_j2_irreversibility or self.config.history_dim < 5:
            return previous + raw_update
        return _j2_channel_update(previous, raw_update)


class NeuralCDEPathOperator(nn.Module):
    """Euler-solved neural controlled differential equation baseline.

    The hidden state follows ``dz = f_theta(z, p) dX`` where ``X`` is formed from global
    load components and time. This is closer to INCDE than a GRU because the state update is
    explicitly driven by path increments.
    """

    def __init__(self, config: NeuralCDEPathOperatorConfig) -> None:
        super().__init__()
        self.config = config
        self.control_dim = config.num_fields + 1
        self.initial = nn.Sequential(
            nn.Linear(config.num_parameters, config.hidden_dim),
            nn.SiLU(),
            nn.Linear(config.hidden_dim, config.hidden_dim),
        )
        self.vector_field = nn.Sequential(
            nn.Linear(config.hidden_dim + config.num_parameters, config.hidden_dim),
            nn.SiLU(),
            nn.Linear(config.hidden_dim, config.hidden_dim * self.control_dim),
        )
        self.node_decoder = _node_decoder(config.spatial_dim, config.num_parameters, config.num_fields, config.hidden_dim)
        self.displacement_delta = nn.Linear(config.hidden_dim, config.num_fields)
        self.logvar_head = nn.Linear(config.hidden_dim, config.num_fields)
        self.history_decoder = _history_decoder(
            config.spatial_dim,
            config.num_parameters,
            config.num_fields,
            config.history_dim,
            config.hidden_dim,
        )
        self.j2_return = (
            DifferentiableJ2ReturnMapping(J2ReturnMappingConfig())
            if config.thermo_hard_j2_return
            else None
        )

    def forward(
        self,
        coords: torch.Tensor,
        params: torch.Tensor,
        forcing_sequence: torch.Tensor,
        initial_history: torch.Tensor | None = None,
        connectivity: torch.Tensor | None = None,
        teacher_history: torch.Tensor | None = None,
        teacher_forcing_ratio: float = 0.0,
    ) -> dict[str, torch.Tensor]:
        del teacher_history, teacher_forcing_ratio
        batch_size, n_steps, n_nodes, _ = _validate_path_inputs(coords, forcing_sequence)
        connectivity_local = _prepare_connectivity(connectivity, coords.device)
        n_elements = _num_elements(connectivity_local, n_nodes)
        history = _initial_history(
            initial_history,
            batch_size,
            n_elements,
            self.config.history_dim,
            coords.device,
            coords.dtype,
        )
        latent = self.initial(params)
        displacement = coords.new_zeros(batch_size, n_nodes, self.config.num_fields)
        previous_control = coords.new_zeros(batch_size, self.control_dim)
        displacement_steps = []
        logvar_steps = []
        history_steps = []
        for step in range(n_steps):
            forcing = forcing_sequence[:, step]
            global_load = forcing.mean(dim=1)
            time = coords.new_full((batch_size, 1), float(step + 1) / max(n_steps, 1))
            control = torch.cat([global_load, time], dim=-1)
            d_control = control - previous_control
            previous_control = control
            vector_field = self.vector_field(torch.cat([latent, params], dim=-1)).view(
                batch_size,
                self.config.hidden_dim,
                self.control_dim,
            )
            latent = latent + torch.bmm(vector_field, d_control.unsqueeze(-1)).squeeze(-1)
            displacement, logvar, history = self._decode_step(
                coords,
                params,
                forcing,
                connectivity_local,
                latent,
                displacement,
                history,
            )
            displacement_steps.append(displacement)
            logvar_steps.append(logvar)
            history_steps.append(history)
        return _pack_outputs(displacement_steps, logvar_steps, history_steps)

    def _decode_step(
        self,
        coords: torch.Tensor,
        params: torch.Tensor,
        forcing: torch.Tensor,
        connectivity: torch.Tensor | None,
        latent: torch.Tensor,
        displacement: torch.Tensor,
        history: torch.Tensor,
    ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        n_nodes = coords.shape[1]
        n_elements = _num_elements(connectivity, n_nodes)
        latent_nodes = latent.unsqueeze(1).expand(-1, n_nodes, -1)
        node_features = self.node_decoder(
            torch.cat([coords, params.unsqueeze(1).expand(-1, n_nodes, -1), forcing, latent_nodes], dim=-1)
        )
        displacement = displacement + self.displacement_delta(node_features)
        logvar = self.logvar_head(node_features).clamp(self.config.min_log_variance, self.config.max_log_variance)
        raw_history = self.history_decoder(
            torch.cat(
                [
                    _nodes_to_elements(coords, connectivity),
                    params.unsqueeze(1).expand(-1, n_elements, -1),
                    _nodes_to_elements(forcing, connectivity),
                    history,
                    latent.unsqueeze(1).expand(-1, n_elements, -1),
                ],
                dim=-1,
            )
        )
        history = self._advance_history(history, raw_history, params)
        return displacement, logvar, history

    def _advance_history(self, previous: torch.Tensor, raw_update: torch.Tensor, params: torch.Tensor) -> torch.Tensor:
        if self.j2_return is not None and self.config.history_dim >= 5:
            return self.j2_return(previous, raw_update, params)
        if not self.config.enforce_j2_irreversibility or self.config.history_dim < 5:
            return previous + raw_update
        return _j2_channel_update(previous, raw_update)


class WindowedHistoryOperator(nn.Module):
    """HANO-style explicit recent-history neural operator baseline.

    A finite window of recent history/load/displacement tokens is attended directly. The model
    does not keep a hidden recurrent state, but it is intentionally labeled HANO-style because it
    does not use the strain-stress window and Fourier backbone of HANO.
    """

    def __init__(self, config: WindowedHistoryOperatorConfig) -> None:
        super().__init__()
        if config.window_size < 1:
            raise ValueError("window_size must be positive")
        self.config = config
        token_dim = config.history_dim + 2 * config.num_fields + 1
        self.token_encoder = nn.Sequential(
            nn.Linear(token_dim, config.hidden_dim),
            nn.SiLU(),
            nn.Linear(config.hidden_dim, config.hidden_dim),
        )
        self.attention = nn.MultiheadAttention(
            config.hidden_dim,
            num_heads=config.num_attention_heads,
            batch_first=True,
        )
        self.context_norm = nn.LayerNorm(config.hidden_dim)
        self.node_decoder = nn.Sequential(
            nn.Linear(
                config.spatial_dim + config.num_parameters + config.num_fields + config.history_dim + config.hidden_dim,
                config.hidden_dim,
            ),
            nn.SiLU(),
            nn.Linear(config.hidden_dim, config.hidden_dim),
            nn.SiLU(),
        )
        self.displacement_delta = nn.Linear(config.hidden_dim, config.num_fields)
        self.logvar_head = nn.Linear(config.hidden_dim, config.num_fields)
        self.history_decoder = _history_decoder(
            config.spatial_dim,
            config.num_parameters,
            config.num_fields,
            config.history_dim,
            config.hidden_dim,
        )

    def forward(
        self,
        coords: torch.Tensor,
        params: torch.Tensor,
        forcing_sequence: torch.Tensor,
        initial_history: torch.Tensor | None = None,
        connectivity: torch.Tensor | None = None,
        teacher_history: torch.Tensor | None = None,
        teacher_forcing_ratio: float = 0.0,
    ) -> dict[str, torch.Tensor]:
        batch_size, n_steps, n_nodes, _ = _validate_path_inputs(coords, forcing_sequence)
        connectivity_local = _prepare_connectivity(connectivity, coords.device)
        n_elements = _num_elements(connectivity_local, n_nodes)
        history = _initial_history(
            initial_history,
            batch_size,
            n_elements,
            self.config.history_dim,
            coords.device,
            coords.dtype,
        )
        displacement = coords.new_zeros(batch_size, n_nodes, self.config.num_fields)
        element_forcing = coords.new_zeros(batch_size, n_elements, self.config.num_fields)
        element_displacement = coords.new_zeros(batch_size, n_elements, self.config.num_fields)
        time_token = coords.new_zeros(batch_size, n_elements, 1)
        window = torch.cat([history, element_forcing, element_displacement, time_token], dim=-1).unsqueeze(2)
        window = window.expand(-1, -1, self.config.window_size, -1).contiguous()

        displacement_steps = []
        logvar_steps = []
        history_steps = []
        for step in range(n_steps):
            forcing = forcing_sequence[:, step]
            context = self._window_context(window)
            history_for_nodes = _element_values_to_nodes(history, connectivity_local, n_nodes)
            context_for_nodes = _element_values_to_nodes(context, connectivity_local, n_nodes)
            node_features = self.node_decoder(
                torch.cat(
                    [
                        coords,
                        params.unsqueeze(1).expand(-1, n_nodes, -1),
                        forcing,
                        history_for_nodes,
                        context_for_nodes,
                    ],
                    dim=-1,
                )
            )
            displacement = displacement + self.displacement_delta(node_features)
            logvar = self.logvar_head(node_features).clamp(
                self.config.min_log_variance,
                self.config.max_log_variance,
            )
            element_coords = _nodes_to_elements(coords, connectivity_local)
            element_forcing = _nodes_to_elements(forcing, connectivity_local)
            element_displacement = _nodes_to_elements(displacement, connectivity_local)
            raw_history = self.history_decoder(
                torch.cat(
                    [
                        element_coords,
                        params.unsqueeze(1).expand(-1, n_elements, -1),
                        element_forcing,
                        history,
                        context,
                    ],
                    dim=-1,
                )
            )
            history = (
                _j2_channel_update(history, raw_history)
                if self.config.enforce_j2_irreversibility and self.config.history_dim >= 5
                else history + raw_history
            )
            if teacher_history is not None and teacher_forcing_ratio > 0.0:
                ratio = float(max(0.0, min(teacher_forcing_ratio, 1.0)))
                target_history = teacher_history[:, step, :, : self.config.history_dim].to(
                    device=history.device,
                    dtype=history.dtype,
                )
                history = (1.0 - ratio) * history + ratio * target_history
            time_token = coords.new_full((batch_size, n_elements, 1), float(step + 1) / max(n_steps, 1))
            token = torch.cat([history, element_forcing, element_displacement, time_token], dim=-1)
            window = torch.cat([window[:, :, 1:], token.unsqueeze(2)], dim=2)
            displacement_steps.append(displacement)
            logvar_steps.append(logvar)
            history_steps.append(history)
        return _pack_outputs(displacement_steps, logvar_steps, history_steps)

    def _window_context(self, window: torch.Tensor) -> torch.Tensor:
        batch_size, n_elements, window_size, _ = window.shape
        tokens = self.token_encoder(window).reshape(batch_size * n_elements, window_size, self.config.hidden_dim)
        attended, _ = self.attention(tokens, tokens, tokens, need_weights=False)
        context = self.context_norm(attended[:, -1])
        return context.view(batch_size, n_elements, self.config.hidden_dim)


class FaithfulHANOOperator(nn.Module):
    """HANO reproduction baseline adapted to the FEM path-operator protocol.

    The baseline follows the most important HANO design choices for path-dependent materials:
    it is autoregressive, uses a finite window of recent observable strain-stress-history
    segments, avoids a hidden recurrent state, and applies a temporal Fourier mixer followed by
    self-attention to extract multiscale path features. The FEM adaptation decodes both nodal
    displacement and element material history so it can be compared in the same path-OOD tables.
    """

    def __init__(self, config: FaithfulHANOOperatorConfig) -> None:
        super().__init__()
        if config.window_size < 1:
            raise ValueError("window_size must be positive")
        if config.num_spectral_modes < 1:
            raise ValueError("num_spectral_modes must be positive")
        self.config = config
        token_dim = (
            config.strain_dim
            + config.stress_dim
            + config.history_dim
            + 2 * config.num_fields
            + 1
        )
        self.token_encoder = nn.Sequential(
            nn.Linear(token_dim, config.hidden_dim),
            nn.SiLU(),
            nn.Linear(config.hidden_dim, config.hidden_dim),
        )
        self.spectral_weight_real = nn.Parameter(torch.ones(config.num_spectral_modes, config.hidden_dim))
        self.spectral_weight_imag = nn.Parameter(torch.zeros(config.num_spectral_modes, config.hidden_dim))
        self.attention = nn.MultiheadAttention(
            config.hidden_dim,
            num_heads=config.num_attention_heads,
            batch_first=True,
        )
        self.context_norm = nn.LayerNorm(config.hidden_dim)
        self.node_decoder = nn.Sequential(
            nn.Linear(config.spatial_dim + config.num_parameters + config.num_fields + config.hidden_dim, config.hidden_dim),
            nn.SiLU(),
            nn.Linear(config.hidden_dim, config.hidden_dim),
            nn.SiLU(),
        )
        self.displacement_delta = nn.Linear(config.hidden_dim, config.num_fields)
        self.logvar_head = nn.Linear(config.hidden_dim, config.num_fields)
        self.history_decoder = _history_decoder(
            config.spatial_dim,
            config.num_parameters,
            config.num_fields,
            config.history_dim,
            config.hidden_dim,
        )
        self.stress_head = nn.Linear(config.hidden_dim, config.stress_dim)

    def forward(
        self,
        coords: torch.Tensor,
        params: torch.Tensor,
        forcing_sequence: torch.Tensor,
        initial_history: torch.Tensor | None = None,
        connectivity: torch.Tensor | None = None,
        teacher_history: torch.Tensor | None = None,
        teacher_strain: torch.Tensor | None = None,
        teacher_stress: torch.Tensor | None = None,
        teacher_forcing_ratio: float = 0.0,
    ) -> dict[str, torch.Tensor]:
        batch_size, n_steps, n_nodes, _ = _validate_path_inputs(coords, forcing_sequence)
        connectivity_local = _prepare_connectivity(connectivity, coords.device)
        n_elements = _num_elements(connectivity_local, n_nodes)
        history = _initial_history(
            initial_history,
            batch_size,
            n_elements,
            self.config.history_dim,
            coords.device,
            coords.dtype,
        )
        displacement = coords.new_zeros(batch_size, n_nodes, self.config.num_fields)
        strain = coords.new_zeros(batch_size, n_elements, self.config.strain_dim)
        stress = coords.new_zeros(batch_size, n_elements, self.config.stress_dim)
        element_forcing = coords.new_zeros(batch_size, n_elements, self.config.num_fields)
        element_displacement = coords.new_zeros(batch_size, n_elements, self.config.num_fields)
        time_token = coords.new_zeros(batch_size, n_elements, 1)
        token = torch.cat([strain, stress, history, element_forcing, element_displacement, time_token], dim=-1)
        window = token.unsqueeze(2).expand(-1, -1, self.config.window_size, -1).contiguous()

        displacement_steps = []
        logvar_steps = []
        history_steps = []
        stress_steps = []
        strain_steps = []
        for step in range(n_steps):
            forcing = forcing_sequence[:, step]
            context = self._window_context(window)
            context_for_nodes = _element_values_to_nodes(context, connectivity_local, n_nodes)
            node_features = self.node_decoder(
                torch.cat(
                    [
                        coords,
                        params.unsqueeze(1).expand(-1, n_nodes, -1),
                        forcing,
                        context_for_nodes,
                    ],
                    dim=-1,
                )
            )
            displacement = displacement + self.displacement_delta(node_features)
            logvar = self.logvar_head(node_features).clamp(
                self.config.min_log_variance,
                self.config.max_log_variance,
            )
            element_coords = _nodes_to_elements(coords, connectivity_local)
            element_forcing = _nodes_to_elements(forcing, connectivity_local)
            element_displacement = _nodes_to_elements(displacement, connectivity_local)
            raw_history = self.history_decoder(
                torch.cat(
                    [
                        element_coords,
                        params.unsqueeze(1).expand(-1, n_elements, -1),
                        element_forcing,
                        history,
                        context,
                    ],
                    dim=-1,
                )
            )
            history = (
                _j2_channel_update(history, raw_history)
                if self.config.enforce_j2_irreversibility and self.config.history_dim >= 5
                else history + raw_history
            )
            stress = self.stress_head(context)
            strain = _element_strain_proxy(coords, displacement, connectivity_local, self.config.strain_dim)
            if teacher_forcing_ratio > 0.0:
                ratio = float(max(0.0, min(teacher_forcing_ratio, 1.0)))
                if teacher_history is not None:
                    target_history = teacher_history[:, step, :, : self.config.history_dim].to(
                        device=history.device,
                        dtype=history.dtype,
                    )
                    history = (1.0 - ratio) * history + ratio * target_history
                if teacher_strain is not None:
                    target_strain = teacher_strain[:, step, :, : self.config.strain_dim].to(
                        device=strain.device,
                        dtype=strain.dtype,
                    )
                    strain = (1.0 - ratio) * strain + ratio * target_strain
                if teacher_stress is not None:
                    target_stress = teacher_stress[:, step, :, : self.config.stress_dim].to(
                        device=stress.device,
                        dtype=stress.dtype,
                    )
                    stress = (1.0 - ratio) * stress + ratio * target_stress
            time_token = coords.new_full((batch_size, n_elements, 1), float(step + 1) / max(n_steps, 1))
            token = torch.cat([strain, stress, history, element_forcing, element_displacement, time_token], dim=-1)
            window = torch.cat([window[:, :, 1:], token.unsqueeze(2)], dim=2)
            displacement_steps.append(displacement)
            logvar_steps.append(logvar)
            history_steps.append(history)
            stress_steps.append(stress)
            strain_steps.append(strain)
        outputs = _pack_outputs(displacement_steps, logvar_steps, history_steps)
        outputs["hano_stress_sequence"] = torch.stack(stress_steps, dim=1)
        outputs["hano_strain_sequence"] = torch.stack(strain_steps, dim=1)
        return outputs

    def _window_context(self, window: torch.Tensor) -> torch.Tensor:
        batch_size, n_elements, window_size, _ = window.shape
        tokens = self.token_encoder(window).reshape(batch_size * n_elements, window_size, self.config.hidden_dim)
        spectral = torch.fft.rfft(tokens, dim=1)
        n_modes = min(self.config.num_spectral_modes, spectral.shape[1])
        weights = torch.complex(
            self.spectral_weight_real[:n_modes],
            self.spectral_weight_imag[:n_modes],
        ).unsqueeze(0)
        weighted_modes = spectral[:, :n_modes, :] * weights
        if n_modes < spectral.shape[1]:
            spectral = torch.cat([weighted_modes, spectral[:, n_modes:, :]], dim=1)
        else:
            spectral = weighted_modes
        mixed = torch.fft.irfft(spectral, n=window_size, dim=1)
        attended, _ = self.attention(mixed, mixed, mixed, need_weights=False)
        context = self.context_norm(attended[:, -1] + tokens[:, -1])
        return context.view(batch_size, n_elements, self.config.hidden_dim)


def _node_decoder(spatial_dim: int, num_parameters: int, num_fields: int, hidden_dim: int) -> nn.Sequential:
    return nn.Sequential(
        nn.Linear(spatial_dim + num_parameters + num_fields + hidden_dim, hidden_dim),
        nn.SiLU(),
        nn.Linear(hidden_dim, hidden_dim),
        nn.SiLU(),
    )


def _history_decoder(
    spatial_dim: int,
    num_parameters: int,
    num_fields: int,
    history_dim: int,
    hidden_dim: int,
) -> nn.Sequential:
    return nn.Sequential(
        nn.Linear(spatial_dim + num_parameters + num_fields + history_dim + hidden_dim, hidden_dim),
        nn.SiLU(),
        nn.Linear(hidden_dim, hidden_dim),
        nn.SiLU(),
        nn.Linear(hidden_dim, history_dim),
    )


def _validate_path_inputs(coords: torch.Tensor, forcing_sequence: torch.Tensor) -> tuple[int, int, int, int]:
    if coords.ndim != 3:
        raise ValueError("coords must have shape [batch, nodes, spatial_dim]")
    if forcing_sequence.ndim != 4:
        raise ValueError("forcing_sequence must have shape [batch, steps, nodes, fields]")
    if coords.shape[0] != forcing_sequence.shape[0] or coords.shape[1] != forcing_sequence.shape[2]:
        raise ValueError("coords and forcing_sequence must share batch and node dimensions")
    return forcing_sequence.shape


def _pack_outputs(
    displacement_steps: list[torch.Tensor],
    logvar_steps: list[torch.Tensor],
    history_steps: list[torch.Tensor],
) -> dict[str, torch.Tensor]:
    return {
        "mean_sequence": torch.stack(displacement_steps, dim=1),
        "logvar_sequence": torch.stack(logvar_steps, dim=1),
        "history_sequence": torch.stack(history_steps, dim=1),
        "mean": displacement_steps[-1],
        "logvar": logvar_steps[-1],
        "history": history_steps[-1],
    }


def _prepare_connectivity(connectivity: torch.Tensor | None, device: torch.device) -> torch.Tensor | None:
    if connectivity is None:
        return None
    return torch.as_tensor(connectivity, dtype=torch.long, device=device)


def _num_elements(connectivity: torch.Tensor | None, n_nodes: int) -> int:
    if connectivity is None:
        return n_nodes
    return int(connectivity.shape[0])


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
    return initial_history.to(device=device, dtype=dtype)


def _nodes_to_elements(values: torch.Tensor, connectivity: torch.Tensor | None) -> torch.Tensor:
    if connectivity is None:
        return values
    element_values = values.index_select(dim=1, index=connectivity.reshape(-1))
    return element_values.view(
        values.shape[0],
        connectivity.shape[0],
        connectivity.shape[1],
        values.shape[-1],
    ).mean(dim=2)


def _element_values_to_nodes(
    values: torch.Tensor,
    connectivity: torch.Tensor | None,
    n_nodes: int,
) -> torch.Tensor:
    if connectivity is None:
        if values.shape[1] == n_nodes:
            return values
        return values.mean(dim=1, keepdim=True).expand(-1, n_nodes, -1)
    batch_size, _, dim = values.shape
    nodal = values.new_zeros(batch_size, n_nodes, dim)
    counts = values.new_zeros(n_nodes, 1)
    for local in range(connectivity.shape[1]):
        nodes = connectivity[:, local]
        nodal.index_add_(1, nodes, values)
        counts.index_add_(0, nodes, torch.ones_like(counts).index_select(0, nodes))
    return nodal / counts.transpose(0, 1).unsqueeze(-1).clamp_min(1.0)


def _element_strain_proxy(
    coords: torch.Tensor,
    displacement: torch.Tensor,
    connectivity: torch.Tensor | None,
    strain_dim: int,
) -> torch.Tensor:
    if connectivity is None or connectivity.shape[1] not in {3, 6}:
        strain = _nodes_to_elements(displacement, connectivity)
        if strain.shape[-1] < strain_dim:
            strain = torch.nn.functional.pad(strain, (0, strain_dim - strain.shape[-1]))
        return strain[..., :strain_dim]
    if connectivity.shape[1] == 6:
        corner_connectivity = connectivity[:, :3]
    else:
        corner_connectivity = connectivity
    tri_coords = coords.index_select(dim=1, index=corner_connectivity.reshape(-1))
    tri_coords = tri_coords.view(coords.shape[0], corner_connectivity.shape[0], 3, coords.shape[-1])
    tri_disp = displacement.index_select(dim=1, index=corner_connectivity.reshape(-1))
    tri_disp = tri_disp.view(displacement.shape[0], corner_connectivity.shape[0], 3, displacement.shape[-1])
    x1, y1 = tri_coords[..., 0, 0], tri_coords[..., 0, 1]
    x2, y2 = tri_coords[..., 1, 0], tri_coords[..., 1, 1]
    x3, y3 = tri_coords[..., 2, 0], tri_coords[..., 2, 1]
    twice_area = ((x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1)).abs().clamp_min(1.0e-12)
    b = torch.stack([y2 - y3, y3 - y1, y1 - y2], dim=-1)
    c = torch.stack([x3 - x2, x1 - x3, x2 - x1], dim=-1)
    ux = tri_disp[..., 0]
    uy = tri_disp[..., 1]
    eps_xx = (b * ux).sum(dim=-1) / twice_area
    eps_yy = (c * uy).sum(dim=-1) / twice_area
    gamma_xy = ((c * ux) + (b * uy)).sum(dim=-1) / twice_area
    strain = torch.stack([eps_xx, eps_yy, gamma_xy], dim=-1)
    if strain_dim > 3:
        strain = torch.nn.functional.pad(strain, (0, strain_dim - 3))
    return strain[..., :strain_dim]


def _j2_channel_update(previous: torch.Tensor, raw_update: torch.Tensor) -> torch.Tensor:
    next_history = previous.clone()
    next_history[..., 0] = previous[..., 0] + torch.nn.functional.softplus(raw_update[..., 0])
    next_history[..., 1] = previous[..., 1] + torch.nn.functional.softplus(raw_update[..., 1])
    next_history[..., 2] = torch.nn.functional.softplus(raw_update[..., 2])
    next_history[..., 3] = torch.sigmoid(raw_update[..., 3])
    next_history[..., 4] = torch.nn.functional.softplus(raw_update[..., 4])
    if previous.shape[-1] > 5:
        next_history[..., 5:] = previous[..., 5:] + raw_update[..., 5:]
    return next_history
