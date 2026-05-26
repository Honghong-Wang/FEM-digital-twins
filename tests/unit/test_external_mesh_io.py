from __future__ import annotations

import torch

from pcgno_dt.data.mesh_io import load_external_tri_mesh
from pcgno_dt.data.fem import load_fem_snapshots
from pcgno_dt.numerics.fem2d import save_plane_stress_fem_dataset


def test_load_gmsh_v2_ascii_mesh(tmp_path) -> None:
    path = tmp_path / "square.msh"
    path.write_text(
        "\n".join(
            [
                "$MeshFormat",
                "2.2 0 8",
                "$EndMeshFormat",
                "$Nodes",
                "4",
                "1 0 0 0",
                "2 1 0 0",
                "3 1 1 0",
                "4 0 1 0",
                "$EndNodes",
                "$Elements",
                "2",
                "1 2 0 1 2 3",
                "2 2 0 1 3 4",
                "$EndElements",
            ]
        ),
        encoding="utf-8",
    )

    mesh = load_external_tri_mesh(path)

    assert mesh.coords.shape == (4, 2)
    assert mesh.connectivity.shape == (2, 3)
    assert mesh.boundary_edges.shape == (4, 2)


def test_load_abaqus_quad_mesh_and_generate_snapshots(tmp_path) -> None:
    mesh_path = tmp_path / "square.inp"
    mesh_path.write_text(
        "\n".join(
            [
                "*Node",
                "1, 0, 0, 0",
                "2, 1, 0, 0",
                "3, 1, 1, 0",
                "4, 0, 1, 0",
                "*Element, type=CPS4",
                "1, 1, 2, 3, 4",
            ]
        ),
        encoding="utf-8",
    )
    out = tmp_path / "external_train.npz"

    save_plane_stress_fem_dataset(
        out,
        n_samples=2,
        split="train",
        seed=41,
        mesh_file=mesh_path,
    )
    loaded = load_fem_snapshots(out)

    assert loaded["tensors"]["coords"].shape == (2, 4, 2)
    assert loaded["extra"]["connectivity"].shape == (2, 3)
    assert torch.isfinite(loaded["tensors"]["fields"]).all()


def test_load_fenics_legacy_xml_mesh(tmp_path) -> None:
    path = tmp_path / "mesh.xml"
    path.write_text(
        """<?xml version="1.0"?>
<dolfin xmlns:dolfin="http://fenicsproject.org">
  <mesh celltype="triangle" dim="2">
    <vertices size="4">
      <vertex index="0" x="0" y="0" />
      <vertex index="1" x="1" y="0" />
      <vertex index="2" x="1" y="1" />
      <vertex index="3" x="0" y="1" />
    </vertices>
    <cells size="2">
      <triangle index="0" v0="0" v1="1" v2="2" />
      <triangle index="1" v0="0" v1="2" v2="3" />
    </cells>
  </mesh>
</dolfin>
""",
        encoding="utf-8",
    )

    mesh = load_external_tri_mesh(path)

    assert mesh.source_format == "fenics_xml"
    assert mesh.coords.shape == (4, 2)
    assert mesh.connectivity.shape == (2, 3)
