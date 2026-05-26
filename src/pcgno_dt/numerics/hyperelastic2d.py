from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import torch

from pcgno_dt.data.fem import save_fem_npz
from pcgno_dt.numerics.fem2d import PlaneStressMesh, make_rectangular_tri_mesh


NEO_HOOKEAN_PARAMETER_NAMES = ("shear_modulus", "bulk_modulus", "traction_x", "traction_y")
NEO_HOOKEAN_FIELD_NAMES = ("u_x", "u_y")


@dataclass(frozen=True)
class NeoHookeanSampleRanges:
    lower: tuple[float, float, float, float]
    upper: tuple[float, float, float, float]

    def sample(self, n_samples: int, rng: np.random.Generator) -> np.ndarray:
        lower = np.asarray(self.lower, dtype=np.float64)
        upper = np.asarray(self.upper, dtype=np.float64)
        return lower + rng.random((n_samples, 4)) * (upper - lower)


NEO_HOOKEAN_RANGES: dict[str, NeoHookeanSampleRanges] = {
    "train": NeoHookeanSampleRanges((0.8, 4.0, 0.015, -0.020), (1.4, 8.0, 0.080, 0.020)),
    "test": NeoHookeanSampleRanges((0.9, 4.5, 0.020, -0.015), (1.3, 7.5, 0.070, 0.015)),
    "ood_material": NeoHookeanSampleRanges((1.8, 9.0, 0.020, -0.015), (2.6, 14.0, 0.070, 0.015)),
    "ood_loading": NeoHookeanSampleRanges((0.9, 4.5, 0.100, -0.060), (1.3, 7.5, 0.180, 0.060)),
}


def generate_neo_hookean_fem_snapshots(
    n_samples: int,
    split: str = "train",
    seed: int = 0,
    nx: int = 4,
    ny: int = 3,
    mesh_kind: str = "structured",
    perturbation: float = 0.0,
    thickness: float = 1.0,
    max_newton_steps: int = 20,
    dtype: torch.dtype = torch.float32,
) -> dict[str, torch.Tensor | tuple[str, ...] | tuple[int, int] | np.ndarray | str]:
    """Generate finite-deformation Neo-Hookean FEM snapshots with stateful tangent data."""

    if split not in NEO_HOOKEAN_RANGES:
        raise KeyError(f"unknown split {split!r}; options are {sorted(NEO_HOOKEAN_RANGES)}")
    rng = np.random.default_rng(seed)
    mesh = make_rectangular_tri_mesh(
        nx=nx,
        ny=ny,
        mesh_kind=mesh_kind,
        perturbation=perturbation,
        rng=rng,
    )
    params = NEO_HOOKEAN_RANGES[split].sample(n_samples, rng)
    fields = []
    forcing = []
    tangent_stiffness = []
    newton_residual = []
    reference_energy = []
    material_history = []
    fixed_dofs = _fixed_left_edge_dofs(mesh)

    for shear_modulus, bulk_modulus, traction_x, traction_y in params:
        sample = solve_neo_hookean_snapshot(
            mesh=mesh,
            shear_modulus=float(shear_modulus),
            bulk_modulus=float(bulk_modulus),
            traction=(float(traction_x), float(traction_y)),
            thickness=thickness,
            max_newton_steps=max_newton_steps,
        )
        fields.append(sample["displacement"])
        forcing.append(sample["force"])
        tangent_stiffness.append(sample["tangent_stiffness"])
        newton_residual.append(sample["newton_residual"])
        reference_energy.append(sample["reference_energy"])
        material_history.append(sample["material_history"])

    coords = np.repeat(mesh.coords[None, :, :], n_samples, axis=0)
    tensors = {
        "coords": torch.as_tensor(coords, dtype=dtype),
        "params": torch.as_tensor(params, dtype=dtype),
        "fields": torch.as_tensor(np.stack(fields, axis=0), dtype=dtype),
        "forcing": torch.as_tensor(np.stack(forcing, axis=0), dtype=dtype),
        "sample_id": torch.arange(n_samples, dtype=torch.long),
    }
    return {
        **tensors,
        "split": split,
        "family": "NeoHookeanFEM2D",
        "parameter_names": NEO_HOOKEAN_PARAMETER_NAMES,
        "field_names": NEO_HOOKEAN_FIELD_NAMES,
        "connectivity": mesh.connectivity,
        "boundary_edges": mesh.boundary_edges,
        "grid_shape": mesh.grid_shape,
        "mesh_kind": mesh.mesh_kind,
        "mesh_source": "procedural",
        "perturbation": float(perturbation),
        "fixed_dofs": fixed_dofs,
        "tangent_stiffness": np.stack(tangent_stiffness, axis=0),
        "newton_residual": np.stack(newton_residual, axis=0),
        "reference_energy": np.asarray(reference_energy, dtype=np.float64),
        "material_history": np.stack(material_history, axis=0),
    }


def save_neo_hookean_fem_dataset(
    path: str | Path,
    n_samples: int,
    split: str = "train",
    seed: int = 0,
    nx: int = 4,
    ny: int = 3,
    mesh_kind: str = "structured",
    perturbation: float = 0.0,
    max_newton_steps: int = 20,
) -> None:
    data = generate_neo_hookean_fem_snapshots(
        n_samples=n_samples,
        split=split,
        seed=seed,
        nx=nx,
        ny=ny,
        mesh_kind=mesh_kind,
        perturbation=perturbation,
        max_newton_steps=max_newton_steps,
    )
    tensors = {key: value for key, value in data.items() if isinstance(value, torch.Tensor)}
    save_fem_npz(
        path,
        tensors,
        parameter_names=NEO_HOOKEAN_PARAMETER_NAMES,
        field_names=NEO_HOOKEAN_FIELD_NAMES,
        connectivity=data["connectivity"],
        boundary_edges=data["boundary_edges"],
        grid_shape=np.asarray(data["grid_shape"], dtype=np.int64),
        mesh_kind=np.asarray([data["mesh_kind"]]),
        mesh_source=np.asarray([data["mesh_source"]]),
        perturbation=np.asarray([data["perturbation"]], dtype=np.float64),
        fixed_dofs=data["fixed_dofs"],
        tangent_stiffness=data["tangent_stiffness"],
        newton_residual=data["newton_residual"],
        reference_energy=data["reference_energy"],
        material_history=data["material_history"],
        split=np.asarray([split]),
        family=np.asarray(["NeoHookeanFEM2D"]),
    )


def solve_neo_hookean_snapshot(
    mesh: PlaneStressMesh,
    shear_modulus: float,
    bulk_modulus: float,
    traction: tuple[float, float],
    thickness: float = 1.0,
    max_newton_steps: int = 20,
    tolerance: float = 1.0e-9,
) -> dict[str, np.ndarray | float]:
    """Solve one total-Lagrangian Neo-Hookean equilibrium problem."""

    coords = torch.as_tensor(mesh.coords, dtype=torch.float64)
    connectivity = torch.as_tensor(mesh.connectivity, dtype=torch.long)
    force = torch.as_tensor(_right_edge_traction_force(mesh, traction, thickness), dtype=torch.float64).reshape(-1)
    fixed_dofs_np = _fixed_left_edge_dofs(mesh)
    fixed_dofs = torch.as_tensor(fixed_dofs_np, dtype=torch.long)
    all_dofs = torch.arange(coords.shape[0] * 2, dtype=torch.long)
    free_mask = torch.ones(all_dofs.numel(), dtype=torch.bool)
    free_mask[fixed_dofs] = False
    free_dofs = all_dofs[free_mask]

    u = torch.zeros(all_dofs.numel(), dtype=torch.float64)
    for _ in range(max_newton_steps):
        gradient, hessian, energy = _residual_tangent_energy(
            u,
            coords,
            connectivity,
            force,
            shear_modulus=shear_modulus,
            bulk_modulus=bulk_modulus,
            thickness=thickness,
        )
        residual_free = gradient.index_select(0, free_dofs)
        if float(residual_free.norm()) <= tolerance:
            break
        tangent_free = hessian.index_select(0, free_dofs).index_select(1, free_dofs)
        regularization = 1.0e-9 * torch.eye(tangent_free.shape[0], dtype=tangent_free.dtype)
        step = torch.linalg.solve(tangent_free + regularization, -residual_free)
        u = _line_search_update(
            u,
            free_dofs,
            step,
            energy,
            coords,
            connectivity,
            force,
            shear_modulus,
            bulk_modulus,
            thickness,
        )

    gradient, hessian, energy = _residual_tangent_energy(
        u,
        coords,
        connectivity,
        force,
        shear_modulus=shear_modulus,
        bulk_modulus=bulk_modulus,
        thickness=thickness,
    )
    history = _element_history(
        u,
        coords,
        connectivity,
        shear_modulus=shear_modulus,
        bulk_modulus=bulk_modulus,
    )
    return {
        "displacement": u.detach().numpy().reshape(coords.shape[0], 2),
        "force": force.detach().numpy().reshape(coords.shape[0], 2),
        "tangent_stiffness": hessian.detach().numpy(),
        "newton_residual": gradient.detach().numpy().reshape(coords.shape[0], 2),
        "reference_energy": float(energy.detach()),
        "material_history": history.detach().numpy(),
    }


def neo_hookean_total_potential(
    displacement_flat: torch.Tensor,
    coords: torch.Tensor,
    connectivity: torch.Tensor,
    force_flat: torch.Tensor,
    shear_modulus: float,
    bulk_modulus: float,
    thickness: float = 1.0,
) -> torch.Tensor:
    strain_energy = displacement_flat.new_tensor(0.0)
    displacement = displacement_flat.reshape(coords.shape[0], 2)
    deformed = coords + displacement
    for tri in connectivity:
        x_ref = coords.index_select(0, tri)
        x_def = deformed.index_select(0, tri)
        dm = torch.stack([x_ref[1] - x_ref[0], x_ref[2] - x_ref[0]], dim=1)
        ds = torch.stack([x_def[1] - x_def[0], x_def[2] - x_def[0]], dim=1)
        area = 0.5 * torch.det(dm)
        deformation_gradient = ds @ torch.linalg.inv(dm)
        strain_energy = strain_energy + thickness * area * _compressible_neo_hookean_density(
            deformation_gradient,
            shear_modulus=shear_modulus,
            bulk_modulus=bulk_modulus,
        )
    external_work = force_flat @ displacement_flat
    return strain_energy - external_work


def _compressible_neo_hookean_density(
    deformation_gradient: torch.Tensor,
    shear_modulus: float,
    bulk_modulus: float,
) -> torch.Tensor:
    j_det = torch.det(deformation_gradient)
    log_j = torch.log(j_det)
    i1 = torch.trace(deformation_gradient.T @ deformation_gradient)
    mu = deformation_gradient.new_tensor(shear_modulus)
    kappa = deformation_gradient.new_tensor(bulk_modulus)
    return 0.5 * mu * (i1 - 2.0 - 2.0 * log_j) + 0.5 * kappa * log_j.square()


def _residual_tangent_energy(
    displacement_flat: torch.Tensor,
    coords: torch.Tensor,
    connectivity: torch.Tensor,
    force_flat: torch.Tensor,
    shear_modulus: float,
    bulk_modulus: float,
    thickness: float,
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    u = displacement_flat.detach().clone().requires_grad_(True)

    def potential(candidate: torch.Tensor) -> torch.Tensor:
        return neo_hookean_total_potential(
            candidate,
            coords,
            connectivity,
            force_flat,
            shear_modulus=shear_modulus,
            bulk_modulus=bulk_modulus,
            thickness=thickness,
        )

    energy = potential(u)
    gradient = torch.autograd.grad(energy, u, create_graph=True)[0]
    hessian = torch.autograd.functional.hessian(potential, u)
    return gradient.detach(), hessian.detach(), energy.detach()


def _line_search_update(
    displacement_flat: torch.Tensor,
    free_dofs: torch.Tensor,
    step: torch.Tensor,
    current_energy: torch.Tensor,
    coords: torch.Tensor,
    connectivity: torch.Tensor,
    force_flat: torch.Tensor,
    shear_modulus: float,
    bulk_modulus: float,
    thickness: float,
) -> torch.Tensor:
    alpha = 1.0
    for _ in range(12):
        candidate = displacement_flat.clone()
        candidate[free_dofs] = candidate[free_dofs] + alpha * step
        if _all_element_jacobians_positive(candidate, coords, connectivity):
            candidate_energy = neo_hookean_total_potential(
                candidate,
                coords,
                connectivity,
                force_flat,
                shear_modulus=shear_modulus,
                bulk_modulus=bulk_modulus,
                thickness=thickness,
            )
            if torch.isfinite(candidate_energy) and candidate_energy <= current_energy + 1.0e-12:
                return candidate.detach()
        alpha *= 0.5
    candidate = displacement_flat.clone()
    candidate[free_dofs] = candidate[free_dofs] + alpha * step
    return candidate.detach()


def _all_element_jacobians_positive(
    displacement_flat: torch.Tensor,
    coords: torch.Tensor,
    connectivity: torch.Tensor,
) -> bool:
    displacement = displacement_flat.reshape(coords.shape[0], 2)
    deformed = coords + displacement
    for tri in connectivity:
        x_ref = coords.index_select(0, tri)
        x_def = deformed.index_select(0, tri)
        dm = torch.stack([x_ref[1] - x_ref[0], x_ref[2] - x_ref[0]], dim=1)
        ds = torch.stack([x_def[1] - x_def[0], x_def[2] - x_def[0]], dim=1)
        if float(torch.det(ds @ torch.linalg.inv(dm))) <= 0.0:
            return False
    return True


def _element_history(
    displacement_flat: torch.Tensor,
    coords: torch.Tensor,
    connectivity: torch.Tensor,
    shear_modulus: float,
    bulk_modulus: float,
) -> torch.Tensor:
    displacement = displacement_flat.reshape(coords.shape[0], 2)
    deformed = coords + displacement
    values = []
    for tri in connectivity:
        x_ref = coords.index_select(0, tri)
        x_def = deformed.index_select(0, tri)
        dm = torch.stack([x_ref[1] - x_ref[0], x_ref[2] - x_ref[0]], dim=1)
        ds = torch.stack([x_def[1] - x_def[0], x_def[2] - x_def[0]], dim=1)
        deformation_gradient = ds @ torch.linalg.inv(dm)
        j_det = torch.det(deformation_gradient)
        i1 = torch.trace(deformation_gradient.T @ deformation_gradient)
        psi = _compressible_neo_hookean_density(
            deformation_gradient,
            shear_modulus=shear_modulus,
            bulk_modulus=bulk_modulus,
        )
        values.append(torch.stack([j_det, i1, psi]))
    return torch.stack(values, dim=0)


def _right_edge_traction_force(
    mesh: PlaneStressMesh,
    traction: tuple[float, float],
    thickness: float,
) -> np.ndarray:
    force = np.zeros((mesh.coords.shape[0], 2), dtype=np.float64)
    tx, ty = traction
    max_x = mesh.coords[:, 0].max()
    edges = mesh.boundary_edges
    if edges is None:
        raise ValueError("Neo-Hookean benchmark requires boundary edges")
    for n0, n1 in edges:
        if abs(mesh.coords[n0, 0] - max_x) > 1.0e-6 or abs(mesh.coords[n1, 0] - max_x) > 1.0e-6:
            continue
        edge_length = float(np.linalg.norm(mesh.coords[n1] - mesh.coords[n0]))
        force[n0, 0] += tx * edge_length * thickness / 2.0
        force[n0, 1] += ty * edge_length * thickness / 2.0
        force[n1, 0] += tx * edge_length * thickness / 2.0
        force[n1, 1] += ty * edge_length * thickness / 2.0
    return force


def _fixed_left_edge_dofs(mesh: PlaneStressMesh) -> np.ndarray:
    min_x = mesh.coords[:, 0].min()
    nodes = np.nonzero(np.abs(mesh.coords[:, 0] - min_x) <= 1.0e-6)[0].astype(np.int64)
    return np.stack([2 * nodes, 2 * nodes + 1], axis=-1).reshape(-1)
