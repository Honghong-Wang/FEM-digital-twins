from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import torch

from pcgno_dt.data.fem import save_fem_npz
from pcgno_dt.data.mesh_io import load_external_tri_mesh


PLANE_STRESS_PARAMETER_NAMES = ("young_modulus", "poisson_ratio", "traction_x", "traction_y")
PLANE_STRESS_FIELD_NAMES = ("u_x", "u_y")


@dataclass(frozen=True)
class PlaneStressMesh:
    coords: np.ndarray
    connectivity: np.ndarray
    grid_shape: tuple[int, int]
    mesh_kind: str = "structured"
    boundary_edges: np.ndarray | None = None


@dataclass(frozen=True)
class PlaneStressSampleRanges:
    lower: tuple[float, float, float, float]
    upper: tuple[float, float, float, float]

    def sample(self, n_samples: int, rng: np.random.Generator) -> np.ndarray:
        lower = np.asarray(self.lower, dtype=np.float64)
        upper = np.asarray(self.upper, dtype=np.float64)
        return lower + rng.random((n_samples, 4)) * (upper - lower)


PLANE_STRESS_RANGES: dict[str, PlaneStressSampleRanges] = {
    "train": PlaneStressSampleRanges((1.0, 0.22, 0.10, -0.20), (2.2, 0.34, 1.00, 0.20)),
    "test": PlaneStressSampleRanges((1.1, 0.24, 0.15, -0.15), (2.0, 0.32, 0.90, 0.15)),
    "ood_material": PlaneStressSampleRanges((2.6, 0.36, 0.15, -0.15), (3.5, 0.42, 0.90, 0.15)),
    "ood_loading": PlaneStressSampleRanges((1.1, 0.24, 1.20, -0.60), (2.0, 0.32, 2.00, 0.60)),
}


def make_rectangular_tri_mesh(
    nx: int = 9,
    ny: int = 7,
    mesh_kind: str = "structured",
    perturbation: float = 0.0,
    rng: np.random.Generator | None = None,
) -> PlaneStressMesh:
    if nx < 2 or ny < 2:
        raise ValueError("nx and ny must be at least 2")
    supported_mesh_kinds = {
        "structured",
        "jittered",
        "hole",
        "multi_hole",
        "random_holes",
        "notch",
        "crack",
        "crack_tip",
        "stress_concentration",
        "curved",
        "curved_hole",
    }
    if mesh_kind not in supported_mesh_kinds:
        raise ValueError(f"mesh_kind must be one of {sorted(supported_mesh_kinds)}")
    rng = np.random.default_rng(0) if rng is None else rng
    xs = np.linspace(0.0, 1.0, nx)
    ys = np.linspace(0.0, 1.0, ny)
    coords = np.asarray([(x, y) for x in xs for y in ys], dtype=np.float64)
    cutout_mesh_kinds = {
        "hole",
        "multi_hole",
        "random_holes",
        "notch",
        "crack",
        "crack_tip",
        "stress_concentration",
        "curved_hole",
    }
    if (mesh_kind == "jittered" or mesh_kind in cutout_mesh_kinds) and perturbation > 0.0:
        coords = _jitter_interior_nodes(coords, nx, ny, perturbation, rng)
    if mesh_kind in {"curved", "curved_hole"}:
        coords = _curve_top_boundary(coords, amplitude=max(perturbation, 0.12))

    triangles: list[tuple[int, int, int]] = []
    for i in range(nx - 1):
        for j in range(ny - 1):
            n00 = i * ny + j
            n01 = i * ny + j + 1
            n10 = (i + 1) * ny + j
            n11 = (i + 1) * ny + j + 1
            if (mesh_kind == "jittered" or mesh_kind in cutout_mesh_kinds) and rng.random() < 0.5:
                triangles.extend(_positive_cell_triangles(coords, (n00, n10, n01), (n10, n11, n01)))
            else:
                triangles.extend(_positive_cell_triangles(coords, (n00, n10, n11), (n00, n11, n01)))
    connectivity = np.asarray(triangles, dtype=np.int64)
    if mesh_kind in cutout_mesh_kinds:
        coords, connectivity = _apply_domain_cutout(coords, connectivity, mesh_kind, rng=rng)
    boundary_edges = _boundary_edges(connectivity)
    return PlaneStressMesh(
        coords=coords,
        connectivity=connectivity,
        grid_shape=(nx, ny),
        mesh_kind=mesh_kind,
        boundary_edges=boundary_edges,
    )


def generate_plane_stress_fem_snapshots(
    n_samples: int,
    split: str = "train",
    seed: int = 0,
    nx: int = 9,
    ny: int = 7,
    mesh_kind: str = "structured",
    perturbation: float = 0.0,
    mesh_file: str | Path | None = None,
    normalize_external_mesh: bool = True,
    thickness: float = 1.0,
    dtype: torch.dtype = torch.float32,
) -> dict[str, torch.Tensor | tuple[str, ...] | tuple[int, int] | np.ndarray | str]:
    """Generate 2D plane-stress FEM snapshots with CST triangular elements."""

    if split not in PLANE_STRESS_RANGES:
        raise KeyError(f"unknown split {split!r}; options are {sorted(PLANE_STRESS_RANGES)}")
    rng = np.random.default_rng(seed)
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
        mesh = _load_plane_stress_mesh(mesh_file, normalize=normalize_external_mesh)
        mesh_source = str(mesh_file)
    params = PLANE_STRESS_RANGES[split].sample(n_samples, rng)
    fields = []
    forcing = []
    for young_modulus, poisson_ratio, traction_x, traction_y in params:
        displacement, force = solve_plane_stress_snapshot(
            mesh,
            young_modulus=float(young_modulus),
            poisson_ratio=float(poisson_ratio),
            traction=(float(traction_x), float(traction_y)),
            thickness=thickness,
        )
        fields.append(displacement)
        forcing.append(force)

    coords = np.repeat(mesh.coords[None, :, :], n_samples, axis=0)
    tensors = {
        "coords": torch.as_tensor(coords, dtype=dtype),
        "params": torch.as_tensor(params, dtype=dtype),
        "fields": torch.as_tensor(np.stack(fields, axis=0), dtype=dtype),
        "forcing": torch.as_tensor(np.stack(forcing, axis=0), dtype=dtype),
    }
    return {
        **tensors,
        "split": split,
        "family": "PlaneStressFEM2D",
        "parameter_names": PLANE_STRESS_PARAMETER_NAMES,
        "field_names": PLANE_STRESS_FIELD_NAMES,
        "connectivity": mesh.connectivity,
        "boundary_edges": mesh.boundary_edges,
        "grid_shape": mesh.grid_shape,
        "mesh_kind": mesh.mesh_kind,
        "mesh_source": mesh_source,
        "perturbation": float(perturbation),
    }


def save_plane_stress_fem_dataset(
    path: str | Path,
    n_samples: int,
    split: str = "train",
    seed: int = 0,
    nx: int = 9,
    ny: int = 7,
    mesh_kind: str = "structured",
    perturbation: float = 0.0,
    mesh_file: str | Path | None = None,
    normalize_external_mesh: bool = True,
) -> None:
    data = generate_plane_stress_fem_snapshots(
        n_samples=n_samples,
        split=split,
        seed=seed,
        nx=nx,
        ny=ny,
        mesh_kind=mesh_kind,
        perturbation=perturbation,
        mesh_file=mesh_file,
        normalize_external_mesh=normalize_external_mesh,
    )
    tensors = {key: value for key, value in data.items() if isinstance(value, torch.Tensor)}
    save_fem_npz(
        path,
        tensors,
        parameter_names=PLANE_STRESS_PARAMETER_NAMES,
        field_names=PLANE_STRESS_FIELD_NAMES,
        connectivity=data["connectivity"],
        boundary_edges=data["boundary_edges"],
        grid_shape=np.asarray(data["grid_shape"], dtype=np.int64),
        mesh_kind=np.asarray([data["mesh_kind"]]),
        mesh_source=np.asarray([data["mesh_source"]]),
        perturbation=np.asarray([data["perturbation"]], dtype=np.float64),
        split=np.asarray([split]),
        family=np.asarray(["PlaneStressFEM2D"]),
    )


def solve_plane_stress_snapshot(
    mesh: PlaneStressMesh,
    young_modulus: float,
    poisson_ratio: float,
    traction: tuple[float, float],
    thickness: float = 1.0,
) -> tuple[np.ndarray, np.ndarray]:
    n_nodes = mesh.coords.shape[0]
    n_dofs = 2 * n_nodes
    stiffness = np.zeros((n_dofs, n_dofs), dtype=np.float64)
    force = np.zeros(n_dofs, dtype=np.float64)
    d_matrix = _plane_stress_matrix(young_modulus, poisson_ratio)

    for tri in mesh.connectivity:
        element_coords = mesh.coords[tri]
        ke = _triangle_stiffness(element_coords, d_matrix, thickness=thickness)
        dofs = np.asarray([2 * tri[0], 2 * tri[0] + 1, 2 * tri[1], 2 * tri[1] + 1, 2 * tri[2], 2 * tri[2] + 1])
        stiffness[np.ix_(dofs, dofs)] += ke

    tx, ty = traction
    for n0, n1 in _right_edge_segments(mesh):
        edge_length = float(np.linalg.norm(mesh.coords[n1] - mesh.coords[n0]))
        for node in (n0, n1):
            force[2 * node] += tx * edge_length * thickness / 2.0
            force[2 * node + 1] += ty * edge_length * thickness / 2.0

    fixed_dofs = []
    for node in _left_edge_nodes_numpy(mesh):
        fixed_dofs.extend([2 * node, 2 * node + 1])
    all_dofs = np.arange(n_dofs)
    free_dofs = np.setdiff1d(all_dofs, np.asarray(fixed_dofs, dtype=np.int64))

    displacement = np.zeros(n_dofs, dtype=np.float64)
    k_ff = stiffness[np.ix_(free_dofs, free_dofs)]
    f_f = force[free_dofs]
    displacement[free_dofs] = np.linalg.solve(k_ff, f_f)
    return displacement.reshape(n_nodes, 2), force.reshape(n_nodes, 2)


def _load_plane_stress_mesh(path: str | Path, normalize: bool = True) -> PlaneStressMesh:
    external = load_external_tri_mesh(path, normalize=normalize)
    return PlaneStressMesh(
        coords=external.coords,
        connectivity=external.connectivity,
        grid_shape=(external.coords.shape[0], 0),
        mesh_kind=f"external_{external.source_format}",
        boundary_edges=external.boundary_edges,
    )


def make_plane_stress_fem_callbacks(
    coords: torch.Tensor | np.ndarray,
    connectivity: torch.Tensor | np.ndarray,
    grid_shape: tuple[int, int] | np.ndarray | None = None,
    thickness: float = 1.0,
):
    """Create differentiable assembled FEM residual, boundary, and energy callbacks.

    The callbacks match `FEMProblemAdapter`:

    - residual: `K(mu) u - f`, zeroed on fixed DOFs where reaction forces live
    - boundary: displacement on fixed left-edge nodes
    - energy: total potential `0.5 u^T K(mu) u - f^T u`
    """

    coords_t = torch.as_tensor(coords)
    if coords_t.ndim == 3:
        coords_t = coords_t[0]
    conn_t = torch.as_tensor(connectivity, dtype=torch.long)
    fixed_nodes = _fixed_left_edge_nodes(coords_t, grid_shape)

    def residual_callback(
        params: torch.Tensor, fields: torch.Tensor, forcing: torch.Tensor | None
    ) -> torch.Tensor:
        if forcing is None:
            forcing = torch.zeros_like(fields)
        coords_local = coords_t.to(device=fields.device, dtype=fields.dtype)
        conn_local = conn_t.to(device=fields.device)
        fixed_dofs = _node_dofs(fixed_nodes.to(device=fields.device), device=fields.device)
        residuals = []
        for sample in range(fields.shape[0]):
            stiffness = assemble_plane_stress_stiffness_torch(
                coords_local,
                conn_local,
                young_modulus=params[sample, 0],
                poisson_ratio=params[sample, 1],
                thickness=thickness,
            )
            residual_flat = stiffness @ fields[sample].reshape(-1) - forcing[sample].reshape(-1)
            residual_flat = residual_flat.clone()
            residual_flat[fixed_dofs] = 0.0
            residuals.append(residual_flat.view_as(fields[sample]))
        return torch.stack(residuals, dim=0)

    def boundary_callback(params: torch.Tensor, fields: torch.Tensor) -> torch.Tensor:
        del params
        return fields.index_select(dim=1, index=fixed_nodes.to(device=fields.device))

    def energy_callback(
        params: torch.Tensor, fields: torch.Tensor, forcing: torch.Tensor | None
    ) -> torch.Tensor:
        if forcing is None:
            forcing = torch.zeros_like(fields)
        coords_local = coords_t.to(device=fields.device, dtype=fields.dtype)
        conn_local = conn_t.to(device=fields.device)
        energies = []
        for sample in range(fields.shape[0]):
            stiffness = assemble_plane_stress_stiffness_torch(
                coords_local,
                conn_local,
                young_modulus=params[sample, 0],
                poisson_ratio=params[sample, 1],
                thickness=thickness,
            )
            displacement = fields[sample].reshape(-1)
            force = forcing[sample].reshape(-1)
            energies.append(0.5 * displacement @ (stiffness @ displacement) - force @ displacement)
        return torch.stack(energies, dim=0)

    return residual_callback, boundary_callback, energy_callback


def assemble_plane_stress_stiffness_torch(
    coords: torch.Tensor,
    connectivity: torch.Tensor,
    young_modulus: torch.Tensor,
    poisson_ratio: torch.Tensor,
    thickness: float = 1.0,
) -> torch.Tensor:
    """Assemble a CST plane-stress stiffness matrix in torch."""

    n_nodes = coords.shape[0]
    stiffness = coords.new_zeros(2 * n_nodes, 2 * n_nodes)
    d_matrix = _plane_stress_matrix_torch(young_modulus, poisson_ratio)
    for tri in connectivity:
        element_coords = coords.index_select(dim=0, index=tri)
        ke = _triangle_stiffness_torch(element_coords, d_matrix, thickness=thickness)
        dofs = torch.stack(
            [
                2 * tri[0],
                2 * tri[0] + 1,
                2 * tri[1],
                2 * tri[1] + 1,
                2 * tri[2],
                2 * tri[2] + 1,
            ]
        )
        stiffness.index_put_((dofs[:, None], dofs[None, :]), ke, accumulate=True)
    return stiffness


def _plane_stress_matrix(young_modulus: float, poisson_ratio: float) -> np.ndarray:
    factor = young_modulus / (1.0 - poisson_ratio**2)
    return factor * np.asarray(
        [
            [1.0, poisson_ratio, 0.0],
            [poisson_ratio, 1.0, 0.0],
            [0.0, 0.0, (1.0 - poisson_ratio) / 2.0],
        ],
        dtype=np.float64,
    )


def _triangle_stiffness(coords: np.ndarray, d_matrix: np.ndarray, thickness: float) -> np.ndarray:
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
    return thickness * area * (b_matrix.T @ d_matrix @ b_matrix)


def _plane_stress_matrix_torch(young_modulus: torch.Tensor, poisson_ratio: torch.Tensor) -> torch.Tensor:
    factor = young_modulus / (1.0 - poisson_ratio.square())
    zero = young_modulus.new_tensor(0.0)
    one = young_modulus.new_tensor(1.0)
    half = young_modulus.new_tensor(0.5)
    return factor * torch.stack(
        [
            torch.stack([one, poisson_ratio, zero]),
            torch.stack([poisson_ratio, one, zero]),
            torch.stack([zero, zero, (one - poisson_ratio) * half]),
        ],
        dim=0,
    )


def _triangle_stiffness_torch(
    coords: torch.Tensor, d_matrix: torch.Tensor, thickness: float
) -> torch.Tensor:
    x1, y1 = coords[0, 0], coords[0, 1]
    x2, y2 = coords[1, 0], coords[1, 1]
    x3, y3 = coords[2, 0], coords[2, 1]
    area = 0.5 * ((x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1))
    b = torch.stack([y2 - y3, y3 - y1, y1 - y2])
    c = torch.stack([x3 - x2, x1 - x3, x2 - x1])
    zero = coords.new_tensor(0.0)
    b_matrix = torch.stack(
        [
            torch.stack([b[0], zero, b[1], zero, b[2], zero]),
            torch.stack([zero, c[0], zero, c[1], zero, c[2]]),
            torch.stack([c[0], b[0], c[1], b[1], c[2], b[2]]),
        ],
        dim=0,
    ) / (2.0 * area)
    return thickness * area * (b_matrix.T @ d_matrix @ b_matrix)


def _fixed_left_edge_nodes(
    coords: torch.Tensor, grid_shape: tuple[int, int] | np.ndarray | None = None
) -> torch.Tensor:
    del grid_shape
    min_x = coords[:, 0].min()
    tolerance = coords.new_tensor(1.0e-6)
    return torch.nonzero((coords[:, 0] - min_x).abs() <= tolerance, as_tuple=False).flatten().long()


def _node_dofs(nodes: torch.Tensor, device: torch.device) -> torch.Tensor:
    nodes = nodes.to(device=device, dtype=torch.long)
    return torch.stack([2 * nodes, 2 * nodes + 1], dim=-1).flatten()


def _jitter_interior_nodes(
    coords: np.ndarray,
    nx: int,
    ny: int,
    perturbation: float,
    rng: np.random.Generator,
) -> np.ndarray:
    jittered = coords.copy()
    dx = 1.0 / float(nx - 1)
    dy = 1.0 / float(ny - 1)
    scale = perturbation * min(dx, dy)
    for i in range(1, nx - 1):
        for j in range(1, ny - 1):
            node = i * ny + j
            jittered[node] += rng.uniform(-scale, scale, size=2)
    return jittered


def _curve_top_boundary(coords: np.ndarray, amplitude: float) -> np.ndarray:
    curved = coords.copy()
    x = curved[:, 0]
    y = curved[:, 1]
    top = 1.0 + amplitude * np.sin(np.pi * x)
    curved[:, 1] = y * top
    return curved


def _apply_domain_cutout(
    coords: np.ndarray,
    connectivity: np.ndarray,
    mesh_kind: str,
    rng: np.random.Generator | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    centroids = coords[connectivity].mean(axis=1)
    rng = np.random.default_rng(0) if rng is None else rng
    if mesh_kind in {"hole", "curved_hole"}:
        center = np.asarray([0.52, 0.50], dtype=np.float64)
        radius = 0.18
        keep = np.linalg.norm(centroids - center, axis=1) >= radius
    elif mesh_kind == "multi_hole":
        centers = np.asarray([[0.38, 0.35], [0.62, 0.64]], dtype=np.float64)
        radii = np.asarray([0.13, 0.12], dtype=np.float64)
        keep = np.ones(connectivity.shape[0], dtype=bool)
        for center, radius in zip(centers, radii):
            keep &= np.linalg.norm(centroids - center, axis=1) >= radius
    elif mesh_kind == "random_holes":
        n_holes = 3
        centers = rng.uniform([0.25, 0.25], [0.75, 0.75], size=(n_holes, 2))
        radii = rng.uniform(0.07, 0.12, size=n_holes)
        keep = np.ones(connectivity.shape[0], dtype=bool)
        for center, radius in zip(centers, radii):
            keep &= np.linalg.norm(centroids - center, axis=1) >= radius
    elif mesh_kind == "notch":
        keep = ~(
            (centroids[:, 0] > 0.72)
            & (centroids[:, 1] > 0.38)
            & (centroids[:, 1] < 0.62)
        )
    elif mesh_kind == "crack":
        keep = ~(
            (centroids[:, 0] > 0.48)
            & (centroids[:, 0] < 0.78)
            & (np.abs(centroids[:, 1] - 0.50) < 0.035)
        )
    elif mesh_kind == "crack_tip":
        slit = (
            (centroids[:, 0] > 0.28)
            & (centroids[:, 0] < 0.66)
            & (np.abs(centroids[:, 1] - 0.50) < 0.030)
        )
        rounded_tip = np.linalg.norm(centroids - np.asarray([0.66, 0.50]), axis=1) < 0.060
        keep = ~(slit | rounded_tip)
    elif mesh_kind == "stress_concentration":
        ellipse = ((centroids[:, 0] - 0.55) / 0.10) ** 2 + ((centroids[:, 1] - 0.50) / 0.22) ** 2
        side_notch = (
            (centroids[:, 0] > 0.80)
            & (centroids[:, 1] > 0.44)
            & (centroids[:, 1] < 0.56)
        )
        keep = (ellipse >= 1.0) & ~side_notch
    else:
        keep = np.ones(connectivity.shape[0], dtype=bool)
    return _compact_mesh(coords, connectivity[keep])


def _compact_mesh(coords: np.ndarray, connectivity: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    used = np.unique(connectivity.reshape(-1))
    remap = -np.ones(coords.shape[0], dtype=np.int64)
    remap[used] = np.arange(used.shape[0], dtype=np.int64)
    return coords[used], remap[connectivity]


def _positive_cell_triangles(
    coords: np.ndarray,
    tri_a: tuple[int, int, int],
    tri_b: tuple[int, int, int],
) -> list[tuple[int, int, int]]:
    return [_positive_triangle(coords, tri_a), _positive_triangle(coords, tri_b)]


def _positive_triangle(coords: np.ndarray, tri: tuple[int, int, int]) -> tuple[int, int, int]:
    a, b, c = tri
    area2 = np.linalg.det(
        np.asarray(
            [
                [coords[b, 0] - coords[a, 0], coords[b, 1] - coords[a, 1]],
                [coords[c, 0] - coords[a, 0], coords[c, 1] - coords[a, 1]],
            ]
        )
    )
    return tri if area2 > 0.0 else (a, c, b)


def _right_edge_segments(mesh: PlaneStressMesh) -> list[tuple[int, int]]:
    edges = mesh.boundary_edges if mesh.boundary_edges is not None else _boundary_edges(mesh.connectivity)
    max_x = mesh.coords[:, 0].max()
    tolerance = 1.0e-6
    segments = [
        (int(n0), int(n1))
        for n0, n1 in edges
        if abs(mesh.coords[n0, 0] - max_x) <= tolerance and abs(mesh.coords[n1, 0] - max_x) <= tolerance
    ]
    return sorted(segments, key=lambda edge: min(mesh.coords[edge[0], 1], mesh.coords[edge[1], 1]))


def _left_edge_nodes_numpy(mesh: PlaneStressMesh) -> np.ndarray:
    min_x = mesh.coords[:, 0].min()
    return np.nonzero(np.abs(mesh.coords[:, 0] - min_x) <= 1.0e-6)[0].astype(np.int64)


def _boundary_edges(connectivity: np.ndarray) -> np.ndarray:
    counts: dict[tuple[int, int], int] = {}
    for tri in connectivity:
        for a, b in ((tri[0], tri[1]), (tri[1], tri[2]), (tri[2], tri[0])):
            edge = tuple(sorted((int(a), int(b))))
            counts[edge] = counts.get(edge, 0) + 1
    edges = [edge for edge, count in counts.items() if count == 1]
    return np.asarray(edges, dtype=np.int64)
