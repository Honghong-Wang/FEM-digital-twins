from __future__ import annotations

from dataclasses import dataclass

import torch

from pcgno_dt.physics.finite_difference import gradient_1d, integrate_trapezoid, laplacian_1d


THERMO_MECH_PARAMETER_NAMES = (
    "young_modulus",
    "thermal_conductivity",
    "coupling",
    "thermal_reaction",
    "amp_u",
    "amp_theta",
    "u_left",
    "u_right",
    "theta_left",
    "theta_right",
)


@dataclass(frozen=True)
class ThermoMechanicalBarProblem:
    """Manufactured thermo-mechanical benchmark family.

    Strong form:

    ```text
    -d/dx(E u_x - c theta) = f_u
    -k theta_xx + r theta + c u_x = f_theta
    ```

    The fields are `[u, theta]`. The parameters include material stiffness, conductivity,
    coupling strength, thermal reaction, manufactured amplitudes, and boundary values.
    """

    num_points: int = 64
    device: str = "cpu"
    dtype: torch.dtype = torch.float32

    @property
    def parameter_names(self) -> tuple[str, ...]:
        return THERMO_MECH_PARAMETER_NAMES

    @property
    def num_parameters(self) -> int:
        return len(THERMO_MECH_PARAMETER_NAMES)

    @property
    def num_fields(self) -> int:
        return 2

    @property
    def dx(self) -> float:
        return 1.0 / float(self.num_points - 1)

    def grid(self, batch_size: int | None = None) -> torch.Tensor:
        x = torch.linspace(0.0, 1.0, self.num_points, device=self.device, dtype=self.dtype)
        x = x.view(1, self.num_points, 1)
        if batch_size is None:
            return x
        return x.repeat(batch_size, 1, 1)

    def exact_solution(self, params: torch.Tensor) -> torch.Tensor:
        params = self._check_params(params)
        x = self.grid(params.shape[0])
        pi = torch.pi
        amp_u = params[:, 4:5].unsqueeze(1)
        amp_t = params[:, 5:6].unsqueeze(1)
        u_left = params[:, 6:7].unsqueeze(1)
        u_right = params[:, 7:8].unsqueeze(1)
        t_left = params[:, 8:9].unsqueeze(1)
        t_right = params[:, 9:10].unsqueeze(1)

        u = u_left * (1.0 - x) + u_right * x
        u = u + amp_u * torch.sin(pi * x) + 0.20 * amp_u * torch.sin(2.0 * pi * x)
        theta = t_left * (1.0 - x) + t_right * x
        theta = theta + amp_t * torch.sin(pi * x) + 0.10 * amp_u * amp_t * torch.sin(
            3.0 * pi * x
        )
        return torch.cat([u, theta], dim=-1)

    def exact_derivatives(self, params: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        params = self._check_params(params)
        x = self.grid(params.shape[0])
        pi = torch.pi
        amp_u = params[:, 4:5].unsqueeze(1)
        amp_t = params[:, 5:6].unsqueeze(1)
        u_slope = (params[:, 7:8] - params[:, 6:7]).unsqueeze(1)
        t_slope = (params[:, 9:10] - params[:, 8:9]).unsqueeze(1)

        u_x = u_slope + amp_u * pi * torch.cos(pi * x)
        u_x = u_x + 0.20 * amp_u * 2.0 * pi * torch.cos(2.0 * pi * x)
        theta_x = t_slope + amp_t * pi * torch.cos(pi * x)
        theta_x = theta_x + 0.10 * amp_u * amp_t * 3.0 * pi * torch.cos(3.0 * pi * x)

        u_xx = -amp_u * pi**2 * torch.sin(pi * x)
        u_xx = u_xx - 0.20 * amp_u * (2.0 * pi) ** 2 * torch.sin(2.0 * pi * x)
        theta_xx = -amp_t * pi**2 * torch.sin(pi * x)
        theta_xx = theta_xx - 0.10 * amp_u * amp_t * (3.0 * pi) ** 2 * torch.sin(
            3.0 * pi * x
        )
        first = torch.cat([u_x, theta_x], dim=-1)
        second = torch.cat([u_xx, theta_xx], dim=-1)
        return first, second

    def forcing(self, params: torch.Tensor) -> torch.Tensor:
        fields = self.exact_solution(params)
        first, second = self.exact_derivatives(params)
        return self._forcing_from_derivatives(params, fields, first, second)

    def residual(
        self,
        params: torch.Tensor,
        fields: torch.Tensor,
        forcing: torch.Tensor | None = None,
        use_finite_difference: bool = True,
    ) -> torch.Tensor:
        params = self._check_params(params)
        if forcing is None:
            forcing = self.forcing(params)
        if use_finite_difference:
            first = gradient_1d(fields, self.dx)
            second = laplacian_1d(fields, self.dx)
        else:
            first, second = self.exact_derivatives(params)
        predicted_forcing = self._forcing_from_derivatives(params, fields, first, second)
        return predicted_forcing - forcing

    def boundary_residual(self, params: torch.Tensor, fields: torch.Tensor) -> torch.Tensor:
        params = self._check_params(params)
        expected = torch.stack(
            [
                torch.stack([params[:, 6], params[:, 8]], dim=-1),
                torch.stack([params[:, 7], params[:, 9]], dim=-1),
            ],
            dim=1,
        )
        actual = torch.stack([fields[:, 0, :], fields[:, -1, :]], dim=1)
        return actual - expected

    def energy(
        self, params: torch.Tensor, fields: torch.Tensor, forcing: torch.Tensor | None = None
    ) -> torch.Tensor:
        params = self._check_params(params)
        if forcing is None:
            forcing = self.forcing(params)
        grad = gradient_1d(fields, self.dx)
        u = fields[..., 0:1]
        theta = fields[..., 1:2]
        u_x = grad[..., 0:1]
        theta_x = grad[..., 1:2]
        f_u = forcing[..., 0:1]
        f_t = forcing[..., 1:2]

        e_mod = params[:, 0:1].unsqueeze(1)
        kappa = params[:, 1:2].unsqueeze(1)
        coupling = params[:, 2:3].unsqueeze(1)
        reaction = params[:, 3:4].unsqueeze(1)

        density = 0.5 * e_mod * u_x.square()
        density = density + 0.5 * kappa * theta_x.square()
        density = density + 0.5 * reaction * theta.square()
        density = density - coupling * theta * u_x
        density = density - f_u * u - f_t * theta
        return integrate_trapezoid(density, self.dx).squeeze(-1)

    def thermodynamic_penalty(self, params: torch.Tensor) -> torch.Tensor:
        params = self._check_params(params)
        e_mod = params[:, 0]
        kappa = params[:, 1]
        coupling = params[:, 2]
        reaction = params[:, 3]
        positivity = torch.stack([e_mod, kappa, reaction], dim=-1)
        positive_penalty = torch.relu(1.0e-6 - positivity).square().mean()
        stability_margin = e_mod * reaction - coupling.square()
        stability_penalty = torch.relu(1.0e-6 - stability_margin).square().mean()
        return positive_penalty + stability_penalty

    def _forcing_from_derivatives(
        self,
        params: torch.Tensor,
        fields: torch.Tensor,
        first: torch.Tensor,
        second: torch.Tensor,
    ) -> torch.Tensor:
        e_mod = params[:, 0:1].unsqueeze(1)
        kappa = params[:, 1:2].unsqueeze(1)
        coupling = params[:, 2:3].unsqueeze(1)
        reaction = params[:, 3:4].unsqueeze(1)
        theta = fields[..., 1:2]
        u_x = first[..., 0:1]
        theta_x = first[..., 1:2]
        u_xx = second[..., 0:1]
        theta_xx = second[..., 1:2]

        f_u = -(e_mod * u_xx - coupling * theta_x)
        f_theta = -kappa * theta_xx + reaction * theta + coupling * u_x
        return torch.cat([f_u, f_theta], dim=-1)

    def _check_params(self, params: torch.Tensor) -> torch.Tensor:
        if params.ndim != 2 or params.shape[-1] != self.num_parameters:
            raise ValueError(f"params must have shape [batch, {self.num_parameters}]")
        return params.to(device=self.device, dtype=self.dtype)
