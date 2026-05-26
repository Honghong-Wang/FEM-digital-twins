from __future__ import annotations

from dataclasses import dataclass

import torch

from pcgno_dt.physics.finite_difference import gradient_1d, integrate_trapezoid


STRUCTURAL_PARAMETER_NAMES = (
    "young_modulus",
    "nonlinear_stiffness",
    "amp_1",
    "amp_2",
    "u_left",
    "u_right",
)


@dataclass(frozen=True)
class NonlinearElasticBarProblem:
    """Manufactured nonlinear structural mechanics benchmark family.

    Strong form:

    ```text
    -d/dx sigma(u_x; mu) = f
    sigma = E u_x + gamma u_x^3
    ```

    This is a small but useful nonlinear solid/structure benchmark: it has a variational energy,
    nonlinear constitutive response, boundary conditions, exact manufactured fields, and the same
    `coords/params/fields/forcing/residual` protocol used by FEM-backed data.
    """

    num_points: int = 64
    device: str = "cpu"
    dtype: torch.dtype = torch.float32

    @property
    def parameter_names(self) -> tuple[str, ...]:
        return STRUCTURAL_PARAMETER_NAMES

    @property
    def num_parameters(self) -> int:
        return len(STRUCTURAL_PARAMETER_NAMES)

    @property
    def num_fields(self) -> int:
        return 1

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
        amp_1 = params[:, 2:3].unsqueeze(1)
        amp_2 = params[:, 3:4].unsqueeze(1)
        u_left = params[:, 4:5].unsqueeze(1)
        u_right = params[:, 5:6].unsqueeze(1)
        linear = u_left * (1.0 - x) + u_right * x
        u = linear + amp_1 * torch.sin(pi * x) + amp_2 * torch.sin(2.0 * pi * x)
        return u

    def exact_gradient(self, params: torch.Tensor) -> torch.Tensor:
        params = self._check_params(params)
        x = self.grid(params.shape[0])
        pi = torch.pi
        amp_1 = params[:, 2:3].unsqueeze(1)
        amp_2 = params[:, 3:4].unsqueeze(1)
        slope = (params[:, 5:6] - params[:, 4:5]).unsqueeze(1)
        return slope + amp_1 * pi * torch.cos(pi * x) + amp_2 * 2.0 * pi * torch.cos(
            2.0 * pi * x
        )

    def exact_laplacian(self, params: torch.Tensor) -> torch.Tensor:
        params = self._check_params(params)
        x = self.grid(params.shape[0])
        pi = torch.pi
        amp_1 = params[:, 2:3].unsqueeze(1)
        amp_2 = params[:, 3:4].unsqueeze(1)
        return -amp_1 * pi**2 * torch.sin(pi * x) - amp_2 * (2.0 * pi) ** 2 * torch.sin(
            2.0 * pi * x
        )

    def forcing(self, params: torch.Tensor) -> torch.Tensor:
        grad = self.exact_gradient(params)
        lap = self.exact_laplacian(params)
        return self._forcing_from_derivatives(params, grad, lap)

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
            grad = gradient_1d(fields, self.dx)
            stress = self._stress(params, grad)
            predicted_forcing = -gradient_1d(stress, self.dx)
        else:
            predicted_forcing = self.forcing(params)
        return predicted_forcing - forcing

    def boundary_residual(self, params: torch.Tensor, fields: torch.Tensor) -> torch.Tensor:
        params = self._check_params(params)
        expected = torch.stack([params[:, 4], params[:, 5]], dim=1).unsqueeze(-1)
        actual = torch.stack([fields[:, 0, 0], fields[:, -1, 0]], dim=1).unsqueeze(-1)
        return actual - expected

    def energy(
        self, params: torch.Tensor, fields: torch.Tensor, forcing: torch.Tensor | None = None
    ) -> torch.Tensor:
        params = self._check_params(params)
        if forcing is None:
            forcing = self.forcing(params)
        grad = gradient_1d(fields, self.dx)
        e_mod = params[:, 0:1].unsqueeze(1)
        gamma = params[:, 1:2].unsqueeze(1)
        density = 0.5 * e_mod * grad.square() + 0.25 * gamma * grad.pow(4) - forcing * fields
        return integrate_trapezoid(density, self.dx).squeeze(-1)

    def thermodynamic_penalty(self, params: torch.Tensor) -> torch.Tensor:
        params = self._check_params(params)
        admissible = params[:, :2]
        return torch.relu(1.0e-6 - admissible).square().mean()

    def _stress(self, params: torch.Tensor, grad: torch.Tensor) -> torch.Tensor:
        e_mod = params[:, 0:1].unsqueeze(1)
        gamma = params[:, 1:2].unsqueeze(1)
        return e_mod * grad + gamma * grad.pow(3)

    def _forcing_from_derivatives(
        self, params: torch.Tensor, grad: torch.Tensor, laplacian: torch.Tensor
    ) -> torch.Tensor:
        e_mod = params[:, 0:1].unsqueeze(1)
        gamma = params[:, 1:2].unsqueeze(1)
        stress_x = e_mod * laplacian + 3.0 * gamma * grad.square() * laplacian
        return -stress_x

    def _check_params(self, params: torch.Tensor) -> torch.Tensor:
        if params.ndim != 2 or params.shape[-1] != self.num_parameters:
            raise ValueError(f"params must have shape [batch, {self.num_parameters}]")
        return params.to(device=self.device, dtype=self.dtype)
