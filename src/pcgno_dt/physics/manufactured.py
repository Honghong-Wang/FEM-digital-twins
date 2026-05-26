from __future__ import annotations

from dataclasses import dataclass

import torch

from pcgno_dt.physics.finite_difference import gradient_1d, integrate_trapezoid, laplacian_1d


PARAMETER_NAMES = (
    "k_u",
    "k_v",
    "alpha",
    "beta",
    "amp_u",
    "amp_v",
    "u_left",
    "u_right",
    "v_left",
    "v_right",
)


@dataclass(frozen=True)
class CoupledPDEProblem:
    """Manufactured nonlinear coupled PDE family for operator-learning experiments.

    The benchmark mimics a two-field nonlinear multiphysics problem while keeping an exact
    manufactured solution available. It is intended as the first reusable problem class before
    replacing the data source with FEM or other high-fidelity solvers.
    """

    num_points: int = 64
    device: str = "cpu"
    dtype: torch.dtype = torch.float32

    @property
    def parameter_names(self) -> tuple[str, ...]:
        return PARAMETER_NAMES

    @property
    def num_parameters(self) -> int:
        return len(PARAMETER_NAMES)

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
        amp_v = params[:, 5:6].unsqueeze(1)
        u_left = params[:, 6:7].unsqueeze(1)
        u_right = params[:, 7:8].unsqueeze(1)
        v_left = params[:, 8:9].unsqueeze(1)
        v_right = params[:, 9:10].unsqueeze(1)

        u_linear = u_left * (1.0 - x) + u_right * x
        v_linear = v_left * (1.0 - x) + v_right * x
        u = u_linear + amp_u * torch.sin(pi * x) + 0.25 * amp_u.square() * torch.sin(2.0 * pi * x)
        v = v_linear + amp_v * torch.sin(pi * x) + 0.15 * amp_u * amp_v * torch.sin(
            3.0 * pi * x
        )
        return torch.cat([u, v], dim=-1)

    def exact_laplacian(self, params: torch.Tensor) -> torch.Tensor:
        params = self._check_params(params)
        x = self.grid(params.shape[0])
        pi = torch.pi

        amp_u = params[:, 4:5].unsqueeze(1)
        amp_v = params[:, 5:6].unsqueeze(1)
        u_xx = -(pi**2) * amp_u * torch.sin(pi * x)
        u_xx = u_xx - 0.25 * amp_u.square() * (2.0 * pi) ** 2 * torch.sin(2.0 * pi * x)
        v_xx = -(pi**2) * amp_v * torch.sin(pi * x)
        v_xx = v_xx - 0.15 * amp_u * amp_v * (3.0 * pi) ** 2 * torch.sin(3.0 * pi * x)
        return torch.cat([u_xx, v_xx], dim=-1)

    def forcing(self, params: torch.Tensor) -> torch.Tensor:
        fields = self.exact_solution(params)
        lap = self.exact_laplacian(params)
        return self._forcing_from_fields(params, fields, lap)

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
            lap = laplacian_1d(fields, self.dx)
        else:
            lap = self.exact_laplacian(params)
        predicted_forcing = self._forcing_from_fields(params, fields, lap)
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

    def energy(self, params: torch.Tensor, fields: torch.Tensor, forcing: torch.Tensor | None = None) -> torch.Tensor:
        """Positive diagnostic free energy plus external work term."""

        params = self._check_params(params)
        if forcing is None:
            forcing = self.forcing(params)
        grad = gradient_1d(fields, self.dx)
        u = fields[..., 0:1]
        v = fields[..., 1:2]
        f_u = forcing[..., 0:1]
        f_v = forcing[..., 1:2]

        k_u = params[:, 0:1].unsqueeze(1)
        k_v = params[:, 1:2].unsqueeze(1)
        alpha = params[:, 2:3].unsqueeze(1)
        beta = params[:, 3:4].unsqueeze(1)

        density = 0.5 * k_u * grad[..., 0:1].square()
        density = density + 0.5 * k_v * grad[..., 1:2].square()
        density = density + 0.25 * alpha * u.pow(4)
        density = density + 0.5 * beta * (v - u.square()).square()
        density = density - f_u * u - f_v * v
        return integrate_trapezoid(density, self.dx).squeeze(-1)

    def thermodynamic_penalty(self, params: torch.Tensor) -> torch.Tensor:
        """Penalize non-admissible material/coupling parameters."""

        params = self._check_params(params)
        positive = params[:, :4]
        return torch.relu(1.0e-6 - positive).square().mean()

    def _forcing_from_fields(
        self, params: torch.Tensor, fields: torch.Tensor, laplacian: torch.Tensor
    ) -> torch.Tensor:
        k_u = params[:, 0:1].unsqueeze(1)
        k_v = params[:, 1:2].unsqueeze(1)
        alpha = params[:, 2:3].unsqueeze(1)
        beta = params[:, 3:4].unsqueeze(1)
        u = fields[..., 0:1]
        v = fields[..., 1:2]
        u_xx = laplacian[..., 0:1]
        v_xx = laplacian[..., 1:2]

        f_u = -k_u * u_xx + alpha * (u.pow(3) - v)
        f_v = -k_v * v_xx + beta * (v - u.square())
        return torch.cat([f_u, f_v], dim=-1)

    def _check_params(self, params: torch.Tensor) -> torch.Tensor:
        if params.ndim != 2 or params.shape[-1] != self.num_parameters:
            raise ValueError(f"params must have shape [batch, {self.num_parameters}]")
        return params.to(device=self.device, dtype=self.dtype)
