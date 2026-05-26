from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import xml.etree.ElementTree as ET

import numpy as np


@dataclass(frozen=True)
class ExternalTriMesh:
    """Dependency-light triangular mesh container for imported FEM/CAD meshes."""

    coords: np.ndarray
    connectivity: np.ndarray
    boundary_edges: np.ndarray
    source_format: str
    source_path: str


def load_external_tri_mesh(path: str | Path, normalize: bool = True) -> ExternalTriMesh:
    """Load a 2D triangular mesh exported from common external tools.

    Supported formats:

    - Gmsh ASCII `.msh` v2.x and simple v4.x triangle/quad meshes
    - Abaqus `.inp` with triangular or quadrilateral 2D elements
    - FEniCS/DOLFIN legacy `.xml` meshes
    - `.npz` with `coords` and `connectivity`

    Quadrilateral elements are split into two triangles. Higher-order elements keep their corner
    nodes only. Coordinates are optionally normalized to a unit bounding box for stable ML scales.
    """

    path = Path(path)
    suffix = path.suffix.lower()
    if suffix == ".npz":
        coords, connectivity, boundary_edges = _load_npz_mesh(path)
        source_format = "npz"
    elif suffix == ".msh":
        coords, connectivity = _load_gmsh_ascii(path)
        boundary_edges = _boundary_edges(connectivity)
        source_format = "gmsh"
    elif suffix == ".inp":
        coords, connectivity = _load_abaqus_inp(path)
        boundary_edges = _boundary_edges(connectivity)
        source_format = "abaqus"
    elif suffix == ".xml":
        coords, connectivity = _load_fenics_legacy_xml(path)
        boundary_edges = _boundary_edges(connectivity)
        source_format = "fenics_xml"
    elif suffix == ".xdmf":
        coords, connectivity = _load_xdmf_inline(path)
        boundary_edges = _boundary_edges(connectivity)
        source_format = "xdmf_inline"
    else:
        raise ValueError(f"unsupported mesh format: {suffix}")

    coords, connectivity = _compact_mesh(coords[:, :2], connectivity)
    connectivity = _orient_triangles_positive(coords, connectivity)
    boundary_edges = _boundary_edges(connectivity)
    if normalize:
        coords = _normalize_coords(coords)
    return ExternalTriMesh(
        coords=coords.astype(np.float64, copy=False),
        connectivity=connectivity.astype(np.int64, copy=False),
        boundary_edges=boundary_edges.astype(np.int64, copy=False),
        source_format=source_format,
        source_path=str(path),
    )


def save_external_tri_mesh_npz(
    path: str | Path,
    coords: np.ndarray,
    connectivity: np.ndarray,
    boundary_edges: np.ndarray | None = None,
) -> None:
    coords, connectivity = _compact_mesh(np.asarray(coords, dtype=np.float64), np.asarray(connectivity, dtype=np.int64))
    connectivity = _orient_triangles_positive(coords[:, :2], connectivity)
    if boundary_edges is None:
        boundary_edges = _boundary_edges(connectivity)
    np.savez(
        Path(path),
        coords=coords[:, :2],
        connectivity=connectivity,
        boundary_edges=np.asarray(boundary_edges, dtype=np.int64),
    )


def _load_npz_mesh(path: Path) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    with np.load(path, allow_pickle=False) as data:
        if "coords" not in data or "connectivity" not in data:
            raise KeyError("mesh .npz must contain coords and connectivity arrays")
        coords = np.asarray(data["coords"], dtype=np.float64)
        connectivity = _triangulate_cells(np.asarray(data["connectivity"], dtype=np.int64))
        boundary_edges = (
            np.asarray(data["boundary_edges"], dtype=np.int64)
            if "boundary_edges" in data
            else _boundary_edges(connectivity)
        )
    if coords.ndim == 3:
        coords = coords[0]
    return coords[:, :2], connectivity, boundary_edges


def _load_gmsh_ascii(path: Path) -> tuple[np.ndarray, np.ndarray]:
    lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    if "$Nodes" not in lines or "$Elements" not in lines:
        raise ValueError("only ASCII Gmsh files with $Nodes and $Elements are supported")
    node_start = lines.index("$Nodes") + 1
    node_end = lines.index("$EndNodes")
    element_start = lines.index("$Elements") + 1
    element_end = lines.index("$EndElements")
    nodes = _parse_gmsh_nodes(lines[node_start:node_end])
    elements = _parse_gmsh_elements(lines[element_start:element_end])
    return _remap_nodes(nodes, elements)


def _parse_gmsh_nodes(lines: list[str]) -> dict[int, tuple[float, float]]:
    header = [int(float(part)) for part in lines[0].split()]
    nodes: dict[int, tuple[float, float]] = {}
    if len(header) == 1:
        for line in lines[1 : 1 + header[0]]:
            parts = line.split()
            nodes[int(parts[0])] = (float(parts[1]), float(parts[2]))
        return nodes

    # Gmsh v4 block format: numEntityBlocks numNodes ...
    index = 1
    for _ in range(header[0]):
        entity_header = lines[index].split()
        index += 1
        num_nodes = int(entity_header[3])
        tags = [int(lines[index + offset].split()[0]) for offset in range(num_nodes)]
        index += num_nodes
        for tag in tags:
            xyz = lines[index].split()
            index += 1
            nodes[tag] = (float(xyz[0]), float(xyz[1]))
    return nodes


def _parse_gmsh_elements(lines: list[str]) -> list[list[int]]:
    header = [int(float(part)) for part in lines[0].split()]
    cells: list[list[int]] = []
    if len(header) == 1:
        for line in lines[1 : 1 + header[0]]:
            parts = [int(float(part)) for part in line.split()]
            element_type = parts[1]
            num_tags = parts[2]
            node_tags = parts[3 + num_tags :]
            _append_gmsh_cell(cells, element_type, node_tags)
        return cells

    index = 1
    for _ in range(header[0]):
        entity_dim, _, element_type, num_elements = [int(float(part)) for part in lines[index].split()]
        index += 1
        for _ in range(num_elements):
            parts = [int(float(part)) for part in lines[index].split()]
            index += 1
            if entity_dim == 2:
                _append_gmsh_cell(cells, element_type, parts[1:])
    return cells


def _append_gmsh_cell(cells: list[list[int]], element_type: int, node_tags: list[int]) -> None:
    if element_type in {2, 9, 21, 23, 25, 26}:  # triangle variants
        cells.append(node_tags[:3])
    elif element_type in {3, 10, 16, 36, 37}:  # quad variants
        cells.extend([node_tags[:3], [node_tags[0], node_tags[2], node_tags[3]]])


def _load_abaqus_inp(path: Path) -> tuple[np.ndarray, np.ndarray]:
    node_map: dict[int, tuple[float, float]] = {}
    cells: list[list[int]] = []
    mode: str | None = None
    element_type = ""
    for raw_line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("**"):
            continue
        if line.startswith("*"):
            lower = line.lower()
            if lower.startswith("*node"):
                mode = "node"
            elif lower.startswith("*element"):
                mode = "element"
                element_type = lower
            else:
                mode = None
            continue
        if mode == "node":
            parts = [part.strip() for part in line.split(",") if part.strip()]
            node_map[int(parts[0])] = (float(parts[1]), float(parts[2]))
        elif mode == "element":
            parts = [int(float(part.strip())) for part in line.split(",") if part.strip()]
            node_tags = parts[1:]
            if any(token in element_type for token in ("cps3", "cpe3", "s3", "m3d3")):
                cells.append(node_tags[:3])
            elif any(token in element_type for token in ("cps4", "cpe4", "s4", "m3d4")):
                cells.extend([node_tags[:3], [node_tags[0], node_tags[2], node_tags[3]]])
    return _remap_nodes(node_map, cells)


def _load_fenics_legacy_xml(path: Path) -> tuple[np.ndarray, np.ndarray]:
    root = ET.parse(path).getroot()
    vertices = root.findall(".//vertex")
    triangles = root.findall(".//triangle")
    if not vertices or not triangles:
        raise ValueError("FEniCS XML mesh must contain vertex and triangle tags")
    node_map = {
        int(vertex.attrib["index"]): (float(vertex.attrib["x"]), float(vertex.attrib["y"]))
        for vertex in vertices
    }
    cells = [
        [int(triangle.attrib["v0"]), int(triangle.attrib["v1"]), int(triangle.attrib["v2"])]
        for triangle in triangles
    ]
    return _remap_nodes(node_map, cells)


def _load_xdmf_inline(path: Path) -> tuple[np.ndarray, np.ndarray]:
    root = ET.parse(path).getroot()
    topology = root.find(".//Topology")
    geometry = root.find(".//Geometry")
    if topology is None or geometry is None:
        raise ValueError("XDMF mesh must contain Topology and Geometry")
    topo_item = topology.find(".//DataItem")
    geom_item = geometry.find(".//DataItem")
    if topo_item is None or geom_item is None or topo_item.text is None or geom_item.text is None:
        raise ValueError("only inline XML XDMF DataItem meshes are supported")
    if "h5" in topo_item.text.lower() or "hdf" in topo_item.text.lower():
        raise ValueError("HDF-backed XDMF is not parsed here; export legacy XML or .npz instead")
    topo_dims = [int(part) for part in topo_item.attrib.get("Dimensions", "").split()]
    geom_dims = [int(part) for part in geom_item.attrib.get("Dimensions", "").split()]
    connectivity = np.asarray([int(float(part)) for part in topo_item.text.split()], dtype=np.int64).reshape(topo_dims)
    coords = np.asarray([float(part) for part in geom_item.text.split()], dtype=np.float64).reshape(geom_dims)
    return coords[:, :2], _triangulate_cells(connectivity)


def _remap_nodes(node_map: dict[int, tuple[float, float]], cells: list[list[int]]) -> tuple[np.ndarray, np.ndarray]:
    if not node_map or not cells:
        raise ValueError("mesh contains no supported 2D cells")
    used = sorted({tag for cell in cells for tag in cell})
    remap = {tag: index for index, tag in enumerate(used)}
    coords = np.asarray([node_map[tag] for tag in used], dtype=np.float64)
    connectivity = np.asarray([[remap[tag] for tag in cell] for cell in cells], dtype=np.int64)
    return coords, _triangulate_cells(connectivity)


def _triangulate_cells(connectivity: np.ndarray) -> np.ndarray:
    if connectivity.ndim != 2:
        raise ValueError("connectivity must be a 2D array")
    if connectivity.shape[1] == 3:
        return connectivity[:, :3]
    if connectivity.shape[1] == 4:
        return np.concatenate(
            [connectivity[:, [0, 1, 2]], connectivity[:, [0, 2, 3]]],
            axis=0,
        )
    if connectivity.shape[1] > 4:
        return connectivity[:, :3]
    raise ValueError("connectivity must contain triangle or quadrilateral cells")


def _compact_mesh(coords: np.ndarray, connectivity: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    used = np.unique(connectivity.reshape(-1))
    remap = -np.ones(coords.shape[0], dtype=np.int64)
    remap[used] = np.arange(used.shape[0], dtype=np.int64)
    return coords[used], remap[connectivity]


def _orient_triangles_positive(coords: np.ndarray, connectivity: np.ndarray) -> np.ndarray:
    oriented = connectivity.copy()
    p0 = coords[oriented[:, 0]]
    p1 = coords[oriented[:, 1]]
    p2 = coords[oriented[:, 2]]
    signed = (p1[:, 0] - p0[:, 0]) * (p2[:, 1] - p0[:, 1]) - (p2[:, 0] - p0[:, 0]) * (p1[:, 1] - p0[:, 1])
    flip = signed < 0.0
    tmp = oriented[flip, 1].copy()
    oriented[flip, 1] = oriented[flip, 2]
    oriented[flip, 2] = tmp
    if np.any(np.isclose(signed, 0.0)):
        raise ValueError("mesh contains zero-area triangles")
    return oriented


def _normalize_coords(coords: np.ndarray) -> np.ndarray:
    lower = coords.min(axis=0)
    upper = coords.max(axis=0)
    span = np.maximum(upper - lower, 1.0e-12)
    return (coords - lower) / span


def _boundary_edges(connectivity: np.ndarray) -> np.ndarray:
    counts: dict[tuple[int, int], int] = {}
    for tri in connectivity:
        for a, b in ((tri[0], tri[1]), (tri[1], tri[2]), (tri[2], tri[0])):
            edge = tuple(sorted((int(a), int(b))))
            counts[edge] = counts.get(edge, 0) + 1
    return np.asarray([edge for edge, count in counts.items() if count == 1], dtype=np.int64)
