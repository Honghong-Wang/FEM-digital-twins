from __future__ import annotations

from dataclasses import dataclass
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import torch
from scipy import sparse
from scipy.sparse import linalg as sparse_linalg

from pcgno_dt.data.fem import save_fem_npz
from pcgno_dt.data.mesh_io import load_external_tri_mesh
from pcgno_dt.numerics.fem2d import PlaneStressMesh, make_rectangular_tri_mesh


J2_PARAMETER_NAMES = (
    "young_modulus",
    "poisson_ratio",
    "yield_stress",
    "hardening_modulus",
    "traction_x",
    "traction_y",
)
J2_FIELD_NAMES = ("u_x", "u_y")
J2_LOAD_PATHS = (
    "monotonic",
    "unload_reload",
    "cyclic",
    "nonproportional",
    "random_amplitude",
    "pre_stress",
)


@dataclass(frozen=True)
class J2SampleRanges:
    lower: tuple[float, float, float, float, float, float]
    upper: tuple[float, float, float, float, float, float]

    def sample(self, n_samples: int, rng: np.random.Generator) -> np.ndarray:
        lower = np.asarray(self.lower, dtype=np.float64)
        upper = np.asarray(self.upper, dtype=np.float64)
        return lower + rng.random((n_samples, 6)) * (upper - lower)


J2_RANGES: dict[str, J2SampleRanges] = {
    "train": J2SampleRanges((80.0, 0.26, 0.08, 0.8, 0.16, -0.04), (140.0, 0.34, 0.14, 3.0, 0.42, 0.04)),
    "test": J2SampleRanges((90.0, 0.27, 0.09, 1.0, 0.18, -0.03), (130.0, 0.33, 0.13, 2.6, 0.38, 0.03)),
    "ood_material": J2SampleRanges((150.0, 0.35, 0.05, 0.2, 0.18, -0.03), (220.0, 0.42, 0.09, 0.8, 0.38, 0.03)),
    "ood_loading": J2SampleRanges((90.0, 0.27, 0.09, 1.0, 0.55, -0.10), (130.0, 0.33, 0.13, 2.6, 0.85, 0.10)),
}


def make_j2_load_factor_path(load_steps: int, load_path: str = "monotonic") -> np.ndarray:
    """Return 2D load factors for x/y traction components along a path."""

    if load_steps < 1:
        raise ValueError("load_steps must be positive")
    load_path = load_path.lower()
    times = np.linspace(1.0 / load_steps, 1.0, load_steps, dtype=np.float64)
    if load_path == "monotonic":
        return np.stack([times, times], axis=-1)
    if load_path == "unload_reload":
        scalar = _piecewise_linear_path(
            times,
            anchors=np.asarray(
                [
                    [0.0, 0.0],
                    [0.45, 1.0],
                    [0.70, 0.25],
                    [1.0, 1.0],
                ],
                dtype=np.float64,
            ),
        )
        return np.stack([scalar, scalar], axis=-1)
    if load_path == "cyclic":
        scalar = _piecewise_linear_path(
            times,
            anchors=np.asarray(
                [
                    [0.0, 0.0],
                    [0.25, 1.0],
                    [0.50, -0.60],
                    [0.75, 1.0],
                    [1.0, 0.0],
                ],
                dtype=np.float64,
            ),
        )
        return np.stack([scalar, scalar], axis=-1)
    if load_path == "nonproportional":
        fx = _piecewise_linear_path(
            times,
            anchors=np.asarray(
                [
                    [0.0, 0.0],
                    [0.35, 1.0],
                    [0.70, 1.0],
                    [1.0, 0.35],
                ],
                dtype=np.float64,
            ),
        )
        fy = _piecewise_linear_path(
            times,
            anchors=np.asarray(
                [
                    [0.0, 0.0],
                    [0.35, 0.0],
                    [0.70, 1.0],
                    [1.0, 1.0],
                ],
                dtype=np.float64,
            ),
        )
        return np.stack([fx, fy], axis=-1)
    if load_path == "random_amplitude":
        fx = _piecewise_linear_path(
            times,
            anchors=np.asarray(
                [
                    [0.0, 0.0],
                    [0.16, 0.70],
                    [0.31, 0.36],
                    [0.47, 1.08],
                    [0.62, -0.24],
                    [0.78, 0.88],
                    [0.90, 0.18],
                    [1.0, 1.0],
                ],
                dtype=np.float64,
            ),
        )
        fy = _piecewise_linear_path(
            times,
            anchors=np.asarray(
                [
                    [0.0, 0.0],
                    [0.18, -0.18],
                    [0.36, 0.55],
                    [0.52, 0.12],
                    [0.68, 0.86],
                    [0.82, -0.12],
                    [1.0, 0.34],
                ],
                dtype=np.float64,
            ),
        )
        return np.stack([fx, fy], axis=-1)
    if load_path == "pre_stress":
        fx = _piecewise_linear_path(
            times,
            anchors=np.asarray(
                [
                    [0.0, -0.35],
                    [0.22, -0.35],
                    [0.42, 0.20],
                    [0.72, 0.75],
                    [1.0, 1.0],
                ],
                dtype=np.float64,
            ),
        )
        fy = _piecewise_linear_path(
            times,
            anchors=np.asarray(
                [
                    [0.0, 0.45],
                    [0.25, 0.45],
                    [0.55, 0.00],
                    [1.0, 0.25],
                ],
                dtype=np.float64,
            ),
        )
        return np.stack([fx, fy], axis=-1)
    raise ValueError(f"load_path must be one of {J2_LOAD_PATHS}")


def generate_j2_plasticity_fem_snapshots(
    n_samples: int,
    split: str = "train",
    seed: int = 0,
    sample_offset: int = 0,
    nx: int = 3,
    ny: int = 3,
    mesh_kind: str = "structured",
    perturbation: float = 0.0,
    mesh_file: str | Path | None = None,
    normalize_external_mesh: bool = True,
    thickness: float = 1.0,
    load_steps: int = 6,
    load_path: str = "monotonic",
    max_newton_steps: int = 14,
    element_order: str = "linear",
    quadrature_order: int | None = None,
    solver_backend: str = "auto",
    export_tangent_sequence: bool = True,
    export_final_tangent: bool = True,
    num_workers: int = 1,
    dtype: torch.dtype = torch.float32,
) -> dict[str, torch.Tensor | tuple[str, ...] | tuple[int, int] | np.ndarray | str]:
    """Generate path-dependent plane-strain J2 plasticity FEM snapshots."""

    if split not in J2_RANGES:
        raise KeyError(f"unknown split {split!r}; options are {sorted(J2_RANGES)}")
    rng = np.random.default_rng(seed)
    load_factors = make_j2_load_factor_path(load_steps, load_path)
    if mesh_file is None:
        mesh = make_rectangular_tri_mesh(
            nx=nx,
            ny=ny,
            mesh_kind=mesh_kind,
            perturbation=perturbation,
            rng=rng,
        )
        mesh_source = "procedural"
    else:
        mesh = _load_j2_mesh(mesh_file, normalize=normalize_external_mesh)
        mesh_source = str(mesh_file)
    element_order = _validate_element_order(element_order)
    if element_order == "quadratic":
        mesh = _to_quadratic_tri_mesh(mesh)
    quadrature_order = _default_quadrature_order(element_order, quadrature_order)
    if sample_offset < 0:
        raise ValueError("sample_offset must be non-negative")
    if sample_offset:
        J2_RANGES[split].sample(sample_offset, rng)
    params = J2_RANGES[split].sample(n_samples, rng)
    fields = []
    forcing = []
    tangent_stiffness = []
    newton_residual = []
    reference_energy = []
    material_history = []
    material_history_qp = []
    plastic_strain = []
    plastic_strain_qp = []
    fields_sequence = []
    forcing_sequence = []
    tangent_stiffness_sequence = []
    newton_residual_sequence = []
    reference_energy_sequence = []
    material_history_sequence = []
    material_history_qp_sequence = []
    plastic_strain_sequence = []
    plastic_strain_qp_sequence = []
    stress_sequence = []
    strain_sequence = []
    fixed_dofs = _fixed_left_edge_dofs(mesh)

    jobs = [
        (
            mesh,
            tuple(float(value) for value in row),
            thickness,
            load_steps,
            load_path,
            max_newton_steps,
            element_order,
            quadrature_order,
            solver_backend,
            export_tangent_sequence,
            export_final_tangent,
        )
        for row in params
    ]
    if num_workers > 1 and len(jobs) > 1:
        with ProcessPoolExecutor(max_workers=num_workers) as executor:
            samples = list(executor.map(_solve_j2_sample_job, jobs))
    else:
        samples = [_solve_j2_sample_job(job) for job in jobs]

    for sample in samples:
        fields.append(sample["displacement"])
        forcing.append(sample["force"])
        if sample.get("tangent_stiffness") is not None:
            tangent_stiffness.append(sample["tangent_stiffness"])
        newton_residual.append(sample["newton_residual"])
        reference_energy.append(sample["reference_energy"])
        material_history.append(sample["material_history"])
        material_history_qp.append(sample["material_history_qp"])
        plastic_strain.append(sample["plastic_strain"])
        plastic_strain_qp.append(sample["plastic_strain_qp"])
        fields_sequence.append(sample["displacement_sequence"])
        forcing_sequence.append(sample["force_sequence"])
        if sample.get("tangent_stiffness_sequence") is not None:
            tangent_stiffness_sequence.append(sample["tangent_stiffness_sequence"])
        newton_residual_sequence.append(sample["newton_residual_sequence"])
        reference_energy_sequence.append(sample["reference_energy_sequence"])
        material_history_sequence.append(sample["material_history_sequence"])
        material_history_qp_sequence.append(sample["material_history_qp_sequence"])
        plastic_strain_sequence.append(sample["plastic_strain_sequence"])
        plastic_strain_qp_sequence.append(sample["plastic_strain_qp_sequence"])
        stress_sequence.append(sample["stress_sequence"])
        strain_sequence.append(sample["strain_sequence"])

    coords = np.repeat(mesh.coords[None, :, :], n_samples, axis=0)
    tensors = {
        "coords": torch.as_tensor(coords, dtype=dtype),
        "params": torch.as_tensor(params, dtype=dtype),
        "fields": torch.as_tensor(np.stack(fields, axis=0), dtype=dtype),
        "forcing": torch.as_tensor(np.stack(forcing, axis=0), dtype=dtype),
        "fields_sequence": torch.as_tensor(np.stack(fields_sequence, axis=0), dtype=dtype),
        "forcing_sequence": torch.as_tensor(np.stack(forcing_sequence, axis=0), dtype=dtype),
        "sample_id": torch.arange(sample_offset, sample_offset + n_samples, dtype=torch.long),
    }
    return {
        **tensors,
        "split": split,
        "family": "J2PlasticityFEM2D",
        "parameter_names": J2_PARAMETER_NAMES,
        "field_names": J2_FIELD_NAMES,
        "connectivity": mesh.connectivity,
        "boundary_edges": mesh.boundary_edges,
        "grid_shape": mesh.grid_shape,
        "mesh_kind": mesh.mesh_kind,
        "mesh_source": mesh_source,
        "perturbation": float(perturbation),
        "fixed_dofs": fixed_dofs,
        **({"tangent_stiffness": np.stack(tangent_stiffness, axis=0)} if tangent_stiffness else {}),
        "newton_residual": np.stack(newton_residual, axis=0),
        "reference_energy": np.asarray(reference_energy, dtype=np.float64),
        "material_history": np.stack(material_history, axis=0),
        "material_history_qp": np.stack(material_history_qp, axis=0),
        "plastic_strain": np.stack(plastic_strain, axis=0),
        "plastic_strain_qp": np.stack(plastic_strain_qp, axis=0),
        **(
            {"tangent_stiffness_sequence": np.stack(tangent_stiffness_sequence, axis=0)}
            if tangent_stiffness_sequence
            else {}
        ),
        "newton_residual_sequence": np.stack(newton_residual_sequence, axis=0),
        "reference_energy_sequence": np.stack(reference_energy_sequence, axis=0),
        "material_history_sequence": np.stack(material_history_sequence, axis=0),
        "material_history_qp_sequence": np.stack(material_history_qp_sequence, axis=0),
        "plastic_strain_sequence": np.stack(plastic_strain_sequence, axis=0),
        "plastic_strain_qp_sequence": np.stack(plastic_strain_qp_sequence, axis=0),
        "stress_sequence": np.stack(stress_sequence, axis=0),
        "strain_sequence": np.stack(strain_sequence, axis=0),
        "load_factors": load_factors,
        "load_path": load_path,
        "element_order": element_order,
        "quadrature_order": int(quadrature_order),
    }


def save_j2_plasticity_fem_dataset(
    path: str | Path,
    n_samples: int,
    split: str = "train",
    seed: int = 0,
    sample_offset: int = 0,
    nx: int = 3,
    ny: int = 3,
    mesh_kind: str = "structured",
    perturbation: float = 0.0,
    mesh_file: str | Path | None = None,
    normalize_external_mesh: bool = True,
    load_steps: int = 6,
    load_path: str = "monotonic",
    max_newton_steps: int = 14,
    element_order: str = "linear",
    quadrature_order: int | None = None,
    solver_backend: str = "auto",
    export_tangent_sequence: bool = True,
    export_final_tangent: bool = True,
    num_workers: int = 1,
) -> None:
    data = generate_j2_plasticity_fem_snapshots(
        n_samples=n_samples,
        split=split,
        seed=seed,
        sample_offset=sample_offset,
        nx=nx,
        ny=ny,
        mesh_kind=mesh_kind,
        perturbation=perturbation,
        mesh_file=mesh_file,
        normalize_external_mesh=normalize_external_mesh,
        load_steps=load_steps,
        load_path=load_path,
        max_newton_steps=max_newton_steps,
        element_order=element_order,
        quadrature_order=quadrature_order,
        solver_backend=solver_backend,
        export_tangent_sequence=export_tangent_sequence,
        export_final_tangent=export_final_tangent,
        num_workers=num_workers,
    )
    tensors = {key: value for key, value in data.items() if isinstance(value, torch.Tensor)}
    save_fem_npz(
        path,
        tensors,
        parameter_names=J2_PARAMETER_NAMES,
        field_names=J2_FIELD_NAMES,
        connectivity=data["connectivity"],
        boundary_edges=data["boundary_edges"],
        grid_shape=np.asarray(data["grid_shape"], dtype=np.int64),
        mesh_kind=np.asarray([data["mesh_kind"]]),
        mesh_source=np.asarray([data["mesh_source"]]),
        perturbation=np.asarray([data["perturbation"]], dtype=np.float64),
        fixed_dofs=data["fixed_dofs"],
        **({"tangent_stiffness": data["tangent_stiffness"]} if "tangent_stiffness" in data else {}),
        newton_residual=data["newton_residual"],
        reference_energy=data["reference_energy"],
        material_history=data["material_history"],
        material_history_qp=data["material_history_qp"],
        plastic_strain=data["plastic_strain"],
        plastic_strain_qp=data["plastic_strain_qp"],
        **(
            {"tangent_stiffness_sequence": data["tangent_stiffness_sequence"]}
            if "tangent_stiffness_sequence" in data
            else {}
        ),
        newton_residual_sequence=data["newton_residual_sequence"],
        reference_energy_sequence=data["reference_energy_sequence"],
        material_history_sequence=data["material_history_sequence"],
        material_history_qp_sequence=data["material_history_qp_sequence"],
        plastic_strain_sequence=data["plastic_strain_sequence"],
        plastic_strain_qp_sequence=data["plastic_strain_qp_sequence"],
        stress_sequence=data["stress_sequence"],
        strain_sequence=data["strain_sequence"],
        load_factors=data["load_factors"],
        load_path=np.asarray([data["load_path"]]),
        element_order=np.asarray([data["element_order"]]),
        quadrature_order=np.asarray([data["quadrature_order"]], dtype=np.int64),
        split=np.asarray([split]),
        family=np.asarray(["J2PlasticityFEM2D"]),
    )


def _load_j2_mesh(path: str | Path, normalize: bool = True) -> PlaneStressMesh:
    external = load_external_tri_mesh(path, normalize=normalize)
    return PlaneStressMesh(
        coords=external.coords,
        connectivity=external.connectivity,
        grid_shape=(external.coords.shape[0], 0),
        mesh_kind=f"external_{external.source_format}",
        boundary_edges=external.boundary_edges,
    )


def _solve_j2_sample_job(
    job: tuple[
        PlaneStressMesh,
        tuple[float, float, float, float, float, float],
        float,
        int,
        str,
        int,
        str,
        int,
        str,
        bool,
        bool,
    ],
) -> dict[str, np.ndarray | float]:
    (
        mesh,
        params,
        thickness,
        load_steps,
        load_path,
        max_newton_steps,
        element_order,
        quadrature_order,
        solver_backend,
        export_tangent_sequence,
        export_final_tangent,
    ) = job
    young_modulus, poisson_ratio, yield_stress, hardening_modulus, traction_x, traction_y = params
    return solve_j2_plasticity_snapshot(
        mesh=mesh,
        young_modulus=young_modulus,
        poisson_ratio=poisson_ratio,
        yield_stress=yield_stress,
        hardening_modulus=hardening_modulus,
        traction=(traction_x, traction_y),
        thickness=thickness,
        load_steps=load_steps,
        load_path=load_path,
        max_newton_steps=max_newton_steps,
        element_order=element_order,
        quadrature_order=quadrature_order,
        solver_backend=solver_backend,
        export_tangent_sequence=export_tangent_sequence,
        export_final_tangent=export_final_tangent,
    )


def solve_j2_plasticity_snapshot(
    mesh: PlaneStressMesh,
    young_modulus: float,
    poisson_ratio: float,
    yield_stress: float,
    hardening_modulus: float,
    traction: tuple[float, float],
    thickness: float = 1.0,
    load_steps: int = 6,
    load_path: str = "monotonic",
    max_newton_steps: int = 14,
    tolerance: float = 1.0e-8,
    element_order: str = "linear",
    quadrature_order: int | None = None,
    solver_backend: str = "auto",
    export_tangent_sequence: bool = True,
    export_final_tangent: bool = True,
) -> dict[str, np.ndarray | float]:
    """Solve one monotonic-load J2 plasticity sample and export final Newton state."""

    element_order = _validate_element_order(element_order)
    quadrature_order = _default_quadrature_order(element_order, quadrature_order)
    n_dofs = 2 * mesh.coords.shape[0]
    use_sparse = _use_sparse_solver(solver_backend, n_dofs)
    fixed_dofs = _fixed_left_edge_dofs(mesh)
    free_dofs = np.setdiff1d(np.arange(n_dofs), fixed_dofs)
    load_factors = make_j2_load_factor_path(load_steps, load_path)
    x_force = _right_edge_traction_force(mesh, (traction[0], 0.0), thickness).reshape(-1)
    y_force = _right_edge_traction_force(mesh, (0.0, traction[1]), thickness).reshape(-1)
    final_force = x_force * load_factors[-1, 0] + y_force * load_factors[-1, 1]
    history = _initial_history(mesh.connectivity.shape[0], n_qp=_quadrature_rule(element_order, quadrature_order)[0].shape[0])
    displacement = np.zeros(n_dofs, dtype=np.float64)
    last_residual = np.zeros(n_dofs, dtype=np.float64)
    last_tangent = np.eye(n_dofs, dtype=np.float64)
    displacement_sequence = []
    force_sequence = []
    tangent_sequence = []
    residual_sequence = []
    energy_sequence = []
    material_history_sequence = []
    material_history_qp_sequence = []
    plastic_strain_sequence = []
    plastic_strain_qp_sequence = []
    stress_sequence = []
    strain_sequence = []

    for step_index, factors in enumerate(load_factors, start=1):
        del step_index
        step_force = x_force * factors[0] + y_force * factors[1]
        step_history = history
        for _ in range(max_newton_steps):
            residual, tangent, _ = _assemble_residual_tangent_and_history(
                displacement,
                mesh,
                step_force,
                young_modulus,
                poisson_ratio,
                yield_stress,
                hardening_modulus,
                step_history,
                thickness,
                element_order=element_order,
                quadrature_order=quadrature_order,
                tangent_format="sparse" if use_sparse else "dense",
            )
            residual_free = residual[free_dofs]
            if np.linalg.norm(residual_free) <= tolerance:
                break
            if sparse.issparse(tangent):
                tangent_free = tangent[free_dofs, :][:, free_dofs].tocsr()
                tangent_free = tangent_free + 1.0e-8 * sparse.eye(tangent_free.shape[0], dtype=np.float64, format="csr")
                increment = sparse_linalg.spsolve(tangent_free, -residual_free)
            else:
                tangent_free = tangent[np.ix_(free_dofs, free_dofs)]
                regularization = 1.0e-8 * np.eye(tangent_free.shape[0], dtype=np.float64)
                increment = np.linalg.solve(tangent_free + regularization, -residual_free)
            displacement = _damped_update(
                displacement,
                free_dofs,
                increment,
                residual_free,
                mesh,
                step_force,
                young_modulus,
                poisson_ratio,
                yield_stress,
                hardening_modulus,
                step_history,
                thickness,
                element_order=element_order,
                quadrature_order=quadrature_order,
            )
        residual, displacement = _polish_dense_newton_if_needed(
            displacement,
            free_dofs,
            mesh,
            step_force,
            young_modulus,
            poisson_ratio,
            yield_stress,
            hardening_modulus,
            step_history,
            thickness,
            tolerance,
            use_sparse,
            element_order,
            quadrature_order,
        )
        last_residual, last_tangent, updated_history = _assemble_residual_tangent_and_history(
            displacement,
            mesh,
            step_force,
            young_modulus,
            poisson_ratio,
            yield_stress,
            hardening_modulus,
            step_history,
            thickness,
            element_order=element_order,
            quadrature_order=quadrature_order,
            tangent_format="sparse" if use_sparse else "dense",
        )
        history = updated_history
        step_energy = _incremental_reference_energy(
            displacement,
            mesh,
            step_force,
            young_modulus,
            poisson_ratio,
            hardening_modulus,
            history,
            thickness,
            element_order=element_order,
            quadrature_order=quadrature_order,
        )
        strain, stress = _element_strain_stress(
            displacement,
            mesh,
            young_modulus,
            poisson_ratio,
            history,
            element_order=element_order,
            quadrature_order=quadrature_order,
        )
        displacement_sequence.append(displacement.reshape(mesh.coords.shape[0], 2).copy())
        force_sequence.append(step_force.reshape(mesh.coords.shape[0], 2).copy())
        if export_tangent_sequence:
            tangent_sequence.append(_as_dense_matrix(last_tangent))
        residual_sequence.append(last_residual.reshape(mesh.coords.shape[0], 2).copy())
        energy_sequence.append(step_energy)
        material_history_sequence.append(_export_material_history(history))
        material_history_qp_sequence.append(_export_material_history_qp(history))
        plastic_strain_sequence.append(_export_plastic_strain(history))
        plastic_strain_qp_sequence.append(_export_plastic_strain_qp(history))
        stress_sequence.append(stress)
        strain_sequence.append(strain)

    reference_energy = _incremental_reference_energy(
        displacement,
        mesh,
        final_force,
        young_modulus,
        poisson_ratio,
        hardening_modulus,
        history,
        thickness,
        element_order=element_order,
        quadrature_order=quadrature_order,
    )
    return {
        "displacement": displacement.reshape(mesh.coords.shape[0], 2),
        "force": final_force.reshape(mesh.coords.shape[0], 2),
        "tangent_stiffness": _as_dense_matrix(last_tangent) if export_final_tangent else None,
        "newton_residual": last_residual.reshape(mesh.coords.shape[0], 2),
        "reference_energy": reference_energy,
        "material_history": _export_material_history(history),
        "material_history_qp": _export_material_history_qp(history),
        "plastic_strain": _export_plastic_strain(history),
        "plastic_strain_qp": _export_plastic_strain_qp(history),
        "displacement_sequence": np.stack(displacement_sequence, axis=0),
        "force_sequence": np.stack(force_sequence, axis=0),
        "tangent_stiffness_sequence": np.stack(tangent_sequence, axis=0) if tangent_sequence else None,
        "newton_residual_sequence": np.stack(residual_sequence, axis=0),
        "reference_energy_sequence": np.asarray(energy_sequence, dtype=np.float64),
        "material_history_sequence": np.stack(material_history_sequence, axis=0),
        "material_history_qp_sequence": np.stack(material_history_qp_sequence, axis=0),
        "plastic_strain_sequence": np.stack(plastic_strain_sequence, axis=0),
        "plastic_strain_qp_sequence": np.stack(plastic_strain_qp_sequence, axis=0),
        "stress_sequence": np.stack(stress_sequence, axis=0),
        "strain_sequence": np.stack(strain_sequence, axis=0),
    }


def _assemble_residual_and_history(
    displacement: np.ndarray,
    mesh: PlaneStressMesh,
    force: np.ndarray,
    young_modulus: float,
    poisson_ratio: float,
    yield_stress: float,
    hardening_modulus: float,
    history: dict[str, np.ndarray],
    thickness: float,
    element_order: str = "linear",
    quadrature_order: int | None = None,
) -> tuple[np.ndarray, dict[str, np.ndarray]]:
    residual, _, updated = _assemble_residual_tangent_and_history(
        displacement,
        mesh,
        force,
        young_modulus,
        poisson_ratio,
        yield_stress,
        hardening_modulus,
        history,
        thickness,
        element_order=element_order,
        quadrature_order=quadrature_order,
    )
    return residual, updated


def _assemble_residual_tangent_and_history(
    displacement: np.ndarray,
    mesh: PlaneStressMesh,
    force: np.ndarray,
    young_modulus: float,
    poisson_ratio: float,
    yield_stress: float,
    hardening_modulus: float,
    history: dict[str, np.ndarray],
    thickness: float,
    element_order: str = "linear",
    quadrature_order: int | None = None,
    tangent_format: str = "dense",
) -> tuple[np.ndarray, np.ndarray | sparse.csr_matrix, dict[str, np.ndarray]]:
    element_order = _validate_element_order(element_order)
    quadrature_order = _default_quadrature_order(element_order, quadrature_order)
    q_points, q_weights = _quadrature_rule(element_order, quadrature_order)
    residual = -force.copy()
    use_sparse = tangent_format == "sparse"
    tangent = None if use_sparse else np.zeros((displacement.shape[0], displacement.shape[0]), dtype=np.float64)
    rows: list[np.ndarray] = []
    cols: list[np.ndarray] = []
    values: list[np.ndarray] = []
    updated = _empty_history_like(history)
    for element_index, tri in enumerate(mesh.connectivity):
        element_coords = mesh.coords[tri]
        dofs = _element_dofs(tri)
        for qp_index, (point, weight) in enumerate(zip(q_points, q_weights)):
            b_matrix, jacobian_weight = _element_b_matrix_and_weight(element_coords, point, float(weight))
            strain = b_matrix @ displacement[dofs]
            update = _j2_return_mapping(
                strain,
                history["plastic_strain_tensor"][element_index, qp_index],
                float(history["eq_plastic_strain"][element_index, qp_index]),
                young_modulus,
                poisson_ratio,
                yield_stress,
                hardening_modulus,
            )
            weighted_volume = thickness * jacobian_weight
            residual[dofs] += weighted_volume * (b_matrix.T @ update["stress_voigt"])
            local_tangent = weighted_volume * (b_matrix.T @ update["algorithmic_tangent_voigt"] @ b_matrix)
            if use_sparse:
                rows.append(np.repeat(dofs, dofs.shape[0]))
                cols.append(np.tile(dofs, dofs.shape[0]))
                values.append(local_tangent.reshape(-1))
            else:
                tangent[np.ix_(dofs, dofs)] += local_tangent
            updated["plastic_strain_tensor"][element_index, qp_index] = update["plastic_strain_tensor"]
            updated["plastic_strain_voigt"][element_index, qp_index] = _tensor_to_history_voigt(
                update["plastic_strain_tensor"]
            )
            updated["eq_plastic_strain"][element_index, qp_index] = update["eq_plastic_strain"]
            updated["last_delta_gamma"][element_index, qp_index] = update["delta_gamma"]
            updated["yielded"][element_index, qp_index] = update["yielded"]
            updated["von_mises"][element_index, qp_index] = update["von_mises"]
            updated["plastic_work"][element_index, qp_index] = (
                history["plastic_work"][element_index, qp_index] + update["plastic_work"]
            )
    if use_sparse:
        if values:
            tangent_sparse = sparse.coo_matrix(
                (np.concatenate(values), (np.concatenate(rows), np.concatenate(cols))),
                shape=(displacement.shape[0], displacement.shape[0]),
            ).tocsr()
        else:
            tangent_sparse = sparse.csr_matrix((displacement.shape[0], displacement.shape[0]), dtype=np.float64)
        return residual, 0.5 * (tangent_sparse + tangent_sparse.T), updated
    if tangent is None:
        raise RuntimeError("dense tangent assembly failed")
    return residual, 0.5 * (tangent + tangent.T), updated


def _finite_difference_tangent(
    displacement: np.ndarray,
    mesh: PlaneStressMesh,
    force: np.ndarray,
    young_modulus: float,
    poisson_ratio: float,
    yield_stress: float,
    hardening_modulus: float,
    history: dict[str, np.ndarray],
    thickness: float,
    element_order: str = "linear",
    quadrature_order: int | None = None,
) -> np.ndarray:
    n_dofs = displacement.shape[0]
    tangent = np.zeros((n_dofs, n_dofs), dtype=np.float64)
    for dof in range(n_dofs):
        step = 1.0e-6 * max(1.0, abs(float(displacement[dof])))
        plus = displacement.copy()
        minus = displacement.copy()
        plus[dof] += step
        minus[dof] -= step
        residual_plus, _ = _assemble_residual_and_history(
            plus,
            mesh,
            force,
            young_modulus,
            poisson_ratio,
            yield_stress,
            hardening_modulus,
            history,
            thickness,
            element_order=element_order,
            quadrature_order=quadrature_order,
        )
        residual_minus, _ = _assemble_residual_and_history(
            minus,
            mesh,
            force,
            young_modulus,
            poisson_ratio,
            yield_stress,
            hardening_modulus,
            history,
            thickness,
            element_order=element_order,
            quadrature_order=quadrature_order,
        )
        tangent[:, dof] = (residual_plus - residual_minus) / (2.0 * step)
    return 0.5 * (tangent + tangent.T)


def _polish_dense_newton_if_needed(
    displacement: np.ndarray,
    free_dofs: np.ndarray,
    mesh: PlaneStressMesh,
    force: np.ndarray,
    young_modulus: float,
    poisson_ratio: float,
    yield_stress: float,
    hardening_modulus: float,
    history: dict[str, np.ndarray],
    thickness: float,
    tolerance: float,
    use_sparse: bool,
    element_order: str,
    quadrature_order: int,
) -> tuple[np.ndarray, np.ndarray]:
    residual, _ = _assemble_residual_and_history(
        displacement,
        mesh,
        force,
        young_modulus,
        poisson_ratio,
        yield_stress,
        hardening_modulus,
        history,
        thickness,
        element_order=element_order,
        quadrature_order=quadrature_order,
    )
    if use_sparse or element_order != "linear" or np.linalg.norm(residual[free_dofs]) <= tolerance:
        return residual, displacement
    for _ in range(4):
        tangent = _finite_difference_tangent(
            displacement,
            mesh,
            force,
            young_modulus,
            poisson_ratio,
            yield_stress,
            hardening_modulus,
            history,
            thickness,
            element_order=element_order,
            quadrature_order=quadrature_order,
        )
        tangent_free = tangent[np.ix_(free_dofs, free_dofs)]
        regularization = 1.0e-10 * np.eye(tangent_free.shape[0], dtype=np.float64)
        increment = np.linalg.solve(tangent_free + regularization, -residual[free_dofs])
        displacement = _damped_update(
            displacement,
            free_dofs,
            increment,
            residual[free_dofs],
            mesh,
            force,
            young_modulus,
            poisson_ratio,
            yield_stress,
            hardening_modulus,
            history,
            thickness,
            element_order=element_order,
            quadrature_order=quadrature_order,
        )
        residual, _ = _assemble_residual_and_history(
            displacement,
            mesh,
            force,
            young_modulus,
            poisson_ratio,
            yield_stress,
            hardening_modulus,
            history,
            thickness,
            element_order=element_order,
            quadrature_order=quadrature_order,
        )
        if np.linalg.norm(residual[free_dofs]) <= tolerance:
            break
    return residual, displacement


def _damped_update(
    displacement: np.ndarray,
    free_dofs: np.ndarray,
    increment: np.ndarray,
    residual_free: np.ndarray,
    mesh: PlaneStressMesh,
    force: np.ndarray,
    young_modulus: float,
    poisson_ratio: float,
    yield_stress: float,
    hardening_modulus: float,
    history: dict[str, np.ndarray],
    thickness: float,
    element_order: str = "linear",
    quadrature_order: int | None = None,
) -> np.ndarray:
    reference_norm = np.linalg.norm(residual_free)
    alpha = 1.0
    for _ in range(10):
        candidate = displacement.copy()
        candidate[free_dofs] += alpha * increment
        residual, _ = _assemble_residual_and_history(
            candidate,
            mesh,
            force,
            young_modulus,
            poisson_ratio,
            yield_stress,
            hardening_modulus,
            history,
            thickness,
            element_order=element_order,
            quadrature_order=quadrature_order,
        )
        if np.linalg.norm(residual[free_dofs]) <= reference_norm:
            return candidate
        alpha *= 0.5
    candidate = displacement.copy()
    candidate[free_dofs] += alpha * increment
    return candidate


def _j2_return_mapping(
    strain_voigt: np.ndarray,
    plastic_strain_old: np.ndarray,
    eq_plastic_strain_old: float,
    young_modulus: float,
    poisson_ratio: float,
    yield_stress: float,
    hardening_modulus: float,
) -> dict[str, np.ndarray | float]:
    shear_modulus = young_modulus / (2.0 * (1.0 + poisson_ratio))
    bulk_modulus = young_modulus / (3.0 * (1.0 - 2.0 * poisson_ratio))
    elastic_tangent = _plane_strain_tangent_matrix(shear_modulus, bulk_modulus)
    strain_tensor = _strain_voigt_to_tensor(strain_voigt)
    elastic_trial = strain_tensor - plastic_strain_old
    stress_trial = bulk_modulus * np.trace(elastic_trial) * np.eye(3) + 2.0 * shear_modulus * _deviator(
        elastic_trial
    )
    stress_mean = np.trace(stress_trial) / 3.0
    stress_dev_trial = _deviator(stress_trial)
    norm_dev = float(np.sqrt(np.sum(stress_dev_trial * stress_dev_trial)))
    von_mises_trial = np.sqrt(1.5) * norm_dev
    yield_value = von_mises_trial - (yield_stress + hardening_modulus * eq_plastic_strain_old)
    if yield_value <= 1.0e-12 or norm_dev <= 1.0e-14:
        stress = stress_trial
        return {
            "stress_voigt": _stress_tensor_to_voigt(stress),
            "algorithmic_tangent_voigt": elastic_tangent,
            "plastic_strain_tensor": plastic_strain_old.copy(),
            "eq_plastic_strain": float(eq_plastic_strain_old),
            "delta_gamma": 0.0,
            "yielded": 0.0,
            "von_mises": float(von_mises_trial),
            "plastic_work": 0.0,
        }

    delta_gamma = yield_value / (3.0 * shear_modulus + hardening_modulus)
    flow_direction = 1.5 * stress_dev_trial / von_mises_trial
    plastic_strain = plastic_strain_old + delta_gamma * flow_direction
    stress_dev = stress_dev_trial * max(0.0, 1.0 - 3.0 * shear_modulus * delta_gamma / von_mises_trial)
    stress = stress_dev + stress_mean * np.eye(3)
    eq_plastic_strain = eq_plastic_strain_old + delta_gamma
    von_mises = float(np.sqrt(1.5 * np.sum(stress_dev * stress_dev)))
    plastic_work = max(0.0, yield_stress * delta_gamma + 0.5 * hardening_modulus * (eq_plastic_strain**2 - eq_plastic_strain_old**2))
    return {
        "stress_voigt": _stress_tensor_to_voigt(stress),
        "algorithmic_tangent_voigt": _j2_algorithmic_tangent_voigt(
            elastic_tangent,
            flow_direction,
            hardening_modulus,
        ),
        "plastic_strain_tensor": plastic_strain,
        "eq_plastic_strain": float(eq_plastic_strain),
        "delta_gamma": float(delta_gamma),
        "yielded": 1.0,
        "von_mises": von_mises,
        "plastic_work": float(plastic_work),
    }


def _plane_strain_tangent_matrix(shear_modulus: float, bulk_modulus: float) -> np.ndarray:
    c11 = bulk_modulus + 4.0 * shear_modulus / 3.0
    c12 = bulk_modulus - 2.0 * shear_modulus / 3.0
    return np.asarray(
        [
            [c11, c12, 0.0],
            [c12, c11, 0.0],
            [0.0, 0.0, shear_modulus],
        ],
        dtype=np.float64,
    )


def _j2_algorithmic_tangent_voigt(
    elastic_tangent: np.ndarray,
    flow_direction_tensor: np.ndarray,
    hardening_modulus: float,
) -> np.ndarray:
    # The strain vector uses engineering shear gamma_xy; therefore the flow direction
    # conjugate to [eps_xx, eps_yy, gamma_xy] uses the tensorial xy component.
    normal = np.asarray(
        [
            flow_direction_tensor[0, 0],
            flow_direction_tensor[1, 1],
            flow_direction_tensor[0, 1],
        ],
        dtype=np.float64,
    )
    c_normal = elastic_tangent @ normal
    denom = float(normal @ c_normal + hardening_modulus)
    if denom <= 1.0e-14:
        return elastic_tangent.copy()
    tangent = elastic_tangent - np.outer(c_normal, c_normal) / denom
    return 0.5 * (tangent + tangent.T)


def _incremental_reference_energy(
    displacement: np.ndarray,
    mesh: PlaneStressMesh,
    force: np.ndarray,
    young_modulus: float,
    poisson_ratio: float,
    hardening_modulus: float,
    history: dict[str, np.ndarray],
    thickness: float,
    element_order: str = "linear",
    quadrature_order: int | None = None,
) -> float:
    shear_modulus = young_modulus / (2.0 * (1.0 + poisson_ratio))
    bulk_modulus = young_modulus / (3.0 * (1.0 - 2.0 * poisson_ratio))
    internal_energy = 0.0
    element_order = _validate_element_order(element_order)
    quadrature_order = _default_quadrature_order(element_order, quadrature_order)
    q_points, q_weights = _quadrature_rule(element_order, quadrature_order)
    for element_index, tri in enumerate(mesh.connectivity):
        dofs = _element_dofs(tri)
        element_coords = mesh.coords[tri]
        for qp_index, (point, weight) in enumerate(zip(q_points, q_weights)):
            b_matrix, jacobian_weight = _element_b_matrix_and_weight(element_coords, point, float(weight))
            strain = _strain_voigt_to_tensor(b_matrix @ displacement[dofs])
            plastic_strain = history["plastic_strain_tensor"][element_index, qp_index]
            elastic_strain = strain - plastic_strain
            stress = bulk_modulus * np.trace(elastic_strain) * np.eye(3) + 2.0 * shear_modulus * _deviator(elastic_strain)
            elastic_energy = 0.5 * float(np.sum(stress * elastic_strain))
            hardening_energy = 0.5 * hardening_modulus * float(history["eq_plastic_strain"][element_index, qp_index] ** 2)
            internal_energy += thickness * jacobian_weight * (elastic_energy + hardening_energy)
    return float(internal_energy - force @ displacement)


def _element_strain_stress(
    displacement: np.ndarray,
    mesh: PlaneStressMesh,
    young_modulus: float,
    poisson_ratio: float,
    history: dict[str, np.ndarray],
    element_order: str = "linear",
    quadrature_order: int | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    shear_modulus = young_modulus / (2.0 * (1.0 + poisson_ratio))
    bulk_modulus = young_modulus / (3.0 * (1.0 - 2.0 * poisson_ratio))
    strains = []
    stresses = []
    element_order = _validate_element_order(element_order)
    quadrature_order = _default_quadrature_order(element_order, quadrature_order)
    q_points, q_weights = _quadrature_rule(element_order, quadrature_order)
    for element_index, tri in enumerate(mesh.connectivity):
        dofs = _element_dofs(tri)
        element_coords = mesh.coords[tri]
        element_strains = []
        element_stresses = []
        for qp_index, (point, weight) in enumerate(zip(q_points, q_weights)):
            del weight
            b_matrix, _ = _element_b_matrix_and_weight(element_coords, point, 1.0)
            strain_voigt = b_matrix @ displacement[dofs]
            strain_tensor = _strain_voigt_to_tensor(strain_voigt)
            plastic_strain = history["plastic_strain_tensor"][element_index, qp_index]
            elastic_strain = strain_tensor - plastic_strain
            stress = bulk_modulus * np.trace(elastic_strain) * np.eye(3) + 2.0 * shear_modulus * _deviator(elastic_strain)
            element_strains.append(strain_voigt)
            element_stresses.append(_stress_tensor_to_voigt(stress))
        strains.append(np.mean(np.stack(element_strains, axis=0), axis=0))
        stresses.append(np.mean(np.stack(element_stresses, axis=0), axis=0))
    return np.stack(strains, axis=0), np.stack(stresses, axis=0)


def _initial_history(n_elements: int, n_qp: int = 1) -> dict[str, np.ndarray]:
    return {
        "plastic_strain_tensor": np.zeros((n_elements, n_qp, 3, 3), dtype=np.float64),
        "plastic_strain_voigt": np.zeros((n_elements, n_qp, 6), dtype=np.float64),
        "eq_plastic_strain": np.zeros((n_elements, n_qp), dtype=np.float64),
        "last_delta_gamma": np.zeros((n_elements, n_qp), dtype=np.float64),
        "yielded": np.zeros((n_elements, n_qp), dtype=np.float64),
        "von_mises": np.zeros((n_elements, n_qp), dtype=np.float64),
        "plastic_work": np.zeros((n_elements, n_qp), dtype=np.float64),
    }


def _empty_history_like(history: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    return {key: np.zeros_like(value) for key, value in history.items()}


def _export_material_history(history: dict[str, np.ndarray]) -> np.ndarray:
    eqp = history["eq_plastic_strain"].mean(axis=1)
    plastic_work = history["plastic_work"].mean(axis=1)
    last_delta_gamma = history["last_delta_gamma"].mean(axis=1)
    yielded = history["yielded"].max(axis=1)
    von_mises = history["von_mises"].mean(axis=1)
    return np.stack(
        [
            eqp,
            plastic_work,
            last_delta_gamma,
            yielded,
            von_mises,
        ],
        axis=-1,
    )


def _export_material_history_qp(history: dict[str, np.ndarray]) -> np.ndarray:
    return np.stack(
        [
            history["eq_plastic_strain"],
            history["plastic_work"],
            history["last_delta_gamma"],
            history["yielded"],
            history["von_mises"],
        ],
        axis=-1,
    )


def _export_plastic_strain(history: dict[str, np.ndarray]) -> np.ndarray:
    return history["plastic_strain_voigt"].mean(axis=1)


def _export_plastic_strain_qp(history: dict[str, np.ndarray]) -> np.ndarray:
    return history["plastic_strain_voigt"].copy()


def _piecewise_linear_path(times: np.ndarray, anchors: np.ndarray) -> np.ndarray:
    return np.interp(times, anchors[:, 0], anchors[:, 1])


def _validate_element_order(element_order: str) -> str:
    order = element_order.lower().strip()
    aliases = {"t3": "linear", "linear": "linear", "p1": "linear", "t6": "quadratic", "quadratic": "quadratic", "p2": "quadratic"}
    if order not in aliases:
        raise ValueError("element_order must be linear/T3/P1 or quadratic/T6/P2")
    return aliases[order]


def _default_quadrature_order(element_order: str, quadrature_order: int | None) -> int:
    if quadrature_order is not None:
        if quadrature_order not in {1, 2}:
            raise ValueError("quadrature_order must be 1 or 2 for triangular J2 elements")
        return int(quadrature_order)
    return 1 if element_order == "linear" else 2


def _quadrature_rule(element_order: str, quadrature_order: int) -> tuple[np.ndarray, np.ndarray]:
    del element_order
    if quadrature_order == 1:
        return (
            np.asarray([[1.0 / 3.0, 1.0 / 3.0]], dtype=np.float64),
            np.asarray([0.5], dtype=np.float64),
        )
    return (
        np.asarray(
            [
                [1.0 / 6.0, 1.0 / 6.0],
                [2.0 / 3.0, 1.0 / 6.0],
                [1.0 / 6.0, 2.0 / 3.0],
            ],
            dtype=np.float64,
        ),
        np.asarray([1.0 / 6.0, 1.0 / 6.0, 1.0 / 6.0], dtype=np.float64),
    )


def _use_sparse_solver(solver_backend: str, n_dofs: int) -> bool:
    backend = solver_backend.lower().strip()
    if backend == "auto":
        return n_dofs >= 600
    if backend == "sparse":
        return True
    if backend == "dense":
        return False
    raise ValueError("solver_backend must be auto, sparse, or dense")


def _as_dense_matrix(matrix: np.ndarray | sparse.spmatrix) -> np.ndarray:
    if sparse.issparse(matrix):
        return matrix.toarray()
    return np.asarray(matrix, dtype=np.float64)


def _to_quadratic_tri_mesh(mesh: PlaneStressMesh) -> PlaneStressMesh:
    if mesh.connectivity.shape[1] == 6:
        return mesh
    if mesh.connectivity.shape[1] != 3:
        raise ValueError("quadratic conversion expects three-node triangular connectivity")
    coords = [point.copy() for point in mesh.coords]
    midpoint_index: dict[tuple[int, int], int] = {}

    def midpoint(a: int, b: int) -> int:
        edge = tuple(sorted((int(a), int(b))))
        if edge not in midpoint_index:
            midpoint_index[edge] = len(coords)
            coords.append(0.5 * (mesh.coords[edge[0]] + mesh.coords[edge[1]]))
        return midpoint_index[edge]

    quadratic = []
    for tri in mesh.connectivity:
        a, b, c = (int(tri[0]), int(tri[1]), int(tri[2]))
        quadratic.append((a, b, c, midpoint(a, b), midpoint(b, c), midpoint(c, a)))
    boundary_edges = mesh.boundary_edges
    if boundary_edges is None:
        boundary_edges = _linear_boundary_edges(mesh.connectivity)
    quadratic_edges = []
    for edge in boundary_edges:
        a, b = int(edge[0]), int(edge[-1])
        quadratic_edges.append((a, midpoint(a, b), b))
    return PlaneStressMesh(
        coords=np.asarray(coords, dtype=np.float64),
        connectivity=np.asarray(quadratic, dtype=np.int64),
        grid_shape=mesh.grid_shape,
        mesh_kind=f"{mesh.mesh_kind}_t6",
        boundary_edges=np.asarray(quadratic_edges, dtype=np.int64),
    )


def _triangle_b_matrix(coords: np.ndarray) -> tuple[np.ndarray, float]:
    x1, y1 = coords[0]
    x2, y2 = coords[1]
    x3, y3 = coords[2]
    area = 0.5 * np.linalg.det(np.asarray([[1.0, x1, y1], [1.0, x2, y2], [1.0, x3, y3]]))
    if area <= 0.0:
        raise ValueError("triangle area must be positive")
    b = np.asarray([y2 - y3, y3 - y1, y1 - y2], dtype=np.float64)
    c = np.asarray([x3 - x2, x1 - x3, x2 - x1], dtype=np.float64)
    b_matrix = np.asarray(
        [
            [b[0], 0.0, b[1], 0.0, b[2], 0.0],
            [0.0, c[0], 0.0, c[1], 0.0, c[2]],
            [c[0], b[0], c[1], b[1], c[2], b[2]],
        ],
        dtype=np.float64,
    ) / (2.0 * area)
    return b_matrix, float(area)


def _element_b_matrix_and_weight(coords: np.ndarray, point: np.ndarray, weight: float) -> tuple[np.ndarray, float]:
    if coords.shape[0] == 3:
        b_matrix, area = _triangle_b_matrix(coords)
        return b_matrix, 2.0 * area * weight
    if coords.shape[0] == 6:
        return _quadratic_triangle_b_matrix_and_weight(coords, point, weight)
    raise ValueError("J2 elements must be three-node T3 or six-node T6 triangles")


def _quadratic_triangle_b_matrix_and_weight(
    coords: np.ndarray,
    point: np.ndarray,
    weight: float,
) -> tuple[np.ndarray, float]:
    d_shape_ref = _quadratic_shape_gradients(point)
    jacobian = d_shape_ref.T @ coords
    det_j = float(np.linalg.det(jacobian))
    if det_j <= 0.0:
        raise ValueError("quadratic triangle Jacobian must be positive")
    d_shape_xy = d_shape_ref @ np.linalg.inv(jacobian)
    b_matrix = np.zeros((3, 12), dtype=np.float64)
    for node in range(6):
        dnx, dny = d_shape_xy[node]
        b_matrix[0, 2 * node] = dnx
        b_matrix[1, 2 * node + 1] = dny
        b_matrix[2, 2 * node] = dny
        b_matrix[2, 2 * node + 1] = dnx
    return b_matrix, det_j * weight


def _quadratic_shape_gradients(point: np.ndarray) -> np.ndarray:
    r, s = float(point[0]), float(point[1])
    l1 = 1.0 - r - s
    l2 = r
    l3 = s
    return np.asarray(
        [
            [-(4.0 * l1 - 1.0), -(4.0 * l1 - 1.0)],
            [4.0 * l2 - 1.0, 0.0],
            [0.0, 4.0 * l3 - 1.0],
            [4.0 * (l1 - l2), -4.0 * l2],
            [4.0 * l3, 4.0 * l2],
            [-4.0 * l3, 4.0 * (l1 - l3)],
        ],
        dtype=np.float64,
    )


def _element_dofs(tri: np.ndarray) -> np.ndarray:
    return np.stack([2 * tri, 2 * tri + 1], axis=-1).reshape(-1).astype(np.int64)


def _strain_voigt_to_tensor(strain: np.ndarray) -> np.ndarray:
    return np.asarray(
        [
            [strain[0], 0.5 * strain[2], 0.0],
            [0.5 * strain[2], strain[1], 0.0],
            [0.0, 0.0, 0.0],
        ],
        dtype=np.float64,
    )


def _stress_tensor_to_voigt(stress: np.ndarray) -> np.ndarray:
    return np.asarray([stress[0, 0], stress[1, 1], stress[0, 1]], dtype=np.float64)


def _tensor_to_history_voigt(tensor: np.ndarray) -> np.ndarray:
    return np.asarray([tensor[0, 0], tensor[1, 1], tensor[2, 2], tensor[0, 1], tensor[1, 2], tensor[0, 2]])


def _deviator(tensor: np.ndarray) -> np.ndarray:
    return tensor - np.trace(tensor) * np.eye(3) / 3.0


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
        raise ValueError("J2 benchmark requires boundary edges")
    for edge in edges:
        edge = np.asarray(edge, dtype=np.int64).reshape(-1)
        n0 = int(edge[0])
        n1 = int(edge[-1])
        if abs(mesh.coords[n0, 0] - max_x) > 1.0e-6 or abs(mesh.coords[n1, 0] - max_x) > 1.0e-6:
            continue
        edge_length = float(np.linalg.norm(mesh.coords[n1] - mesh.coords[n0]))
        if edge.shape[0] == 3:
            weights = (1.0 / 6.0, 2.0 / 3.0, 1.0 / 6.0)
            edge_nodes = (int(edge[0]), int(edge[1]), int(edge[2]))
        else:
            weights = (0.5, 0.5)
            edge_nodes = (n0, n1)
        for node, weight in zip(edge_nodes, weights):
            force[node, 0] += tx * edge_length * thickness * weight
            force[node, 1] += ty * edge_length * thickness * weight
    return force


def _fixed_left_edge_dofs(mesh: PlaneStressMesh) -> np.ndarray:
    min_x = mesh.coords[:, 0].min()
    nodes = np.nonzero(np.abs(mesh.coords[:, 0] - min_x) <= 1.0e-6)[0].astype(np.int64)
    return np.stack([2 * nodes, 2 * nodes + 1], axis=-1).reshape(-1)


def _linear_boundary_edges(connectivity: np.ndarray) -> np.ndarray:
    counts: dict[tuple[int, int], int] = {}
    for tri in connectivity:
        for a, b in ((tri[0], tri[1]), (tri[1], tri[2]), (tri[2], tri[0])):
            edge = tuple(sorted((int(a), int(b))))
            counts[edge] = counts.get(edge, 0) + 1
    return np.asarray([edge for edge, count in counts.items() if count == 1], dtype=np.int64)
