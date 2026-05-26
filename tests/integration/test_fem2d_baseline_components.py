from __future__ import annotations

import torch

from pcgno_dt.data.fem import load_fem_snapshots, make_fem_problem_adapter
from pcgno_dt.evaluation.physics import evaluate_physics_consistency
from pcgno_dt.models.pcgno import PCGNOConfig, PhysicsConstrainedGenerativeNeuralOperator
from pcgno_dt.numerics.baselines import (
    DeepONetBaseline,
    FNOBaseline,
    MeshGraphOperatorBaseline,
    MeshToMeshGraphOperatorBaseline,
    PINNBaseline,
)
from pcgno_dt.numerics.fem2d import (
    generate_plane_stress_fem_snapshots,
    make_plane_stress_fem_callbacks,
    save_plane_stress_fem_dataset,
)
from pcgno_dt.training.losses import PhysicsLossWeights, physics_constrained_loss


def test_plane_stress_fem_snapshots_and_2d_baselines(tmp_path) -> None:
    data = generate_plane_stress_fem_snapshots(
        n_samples=3,
        split="train",
        seed=23,
        nx=5,
        ny=4,
    )
    coords = data["coords"]
    params = data["params"]
    fields = data["fields"]

    assert coords.shape == (3, 20, 2)
    assert params.shape == (3, 4)
    assert fields.shape == (3, 20, 2)
    assert torch.isfinite(fields).all()

    for model in (
        PINNBaseline(4, 2, spatial_dim=2),
        DeepONetBaseline(4, 2, spatial_dim=2),
        FNOBaseline(4, 2, spatial_dim=2, grid_shape=(5, 4)),
        MeshGraphOperatorBaseline(4, 2, spatial_dim=2, hidden_dim=24, num_layers=2),
        MeshToMeshGraphOperatorBaseline(4, 2, spatial_dim=2, hidden_dim=24, num_layers=2),
        PhysicsConstrainedGenerativeNeuralOperator(
            PCGNOConfig(num_parameters=4, num_fields=2, spatial_dim=2, hidden_dim=24, latent_dim=4)
        ),
    ):
        outputs = model(coords, params)
        assert outputs["mean"].shape == fields.shape

    path = tmp_path / "fem2d_train.npz"
    save_plane_stress_fem_dataset(path, n_samples=3, split="train", seed=24, nx=5, ny=4)
    loaded = load_fem_snapshots(path)
    assert loaded["tensors"]["coords"].shape == (3, 20, 2)
    assert tuple(loaded["extra"]["grid_shape"].tolist()) == (5, 4)


def test_jittered_plane_stress_fem_snapshots_are_physics_consistent(tmp_path) -> None:
    path = tmp_path / "fem2d_jittered_train.npz"
    save_plane_stress_fem_dataset(
        path,
        n_samples=3,
        split="train",
        seed=31,
        nx=5,
        ny=4,
        mesh_kind="jittered",
        perturbation=0.15,
    )
    loaded = load_fem_snapshots(path)
    tensors = loaded["tensors"]
    callbacks = make_plane_stress_fem_callbacks(
        coords=tensors["coords"],
        connectivity=loaded["extra"]["connectivity"],
        grid_shape=loaded["extra"]["grid_shape"],
    )
    problem = make_fem_problem_adapter(
        tensors,
        loaded["metadata"],
        residual_callback=callbacks[0],
        boundary_callback=callbacks[1],
        energy_callback=callbacks[2],
    )

    residual = problem.residual(tensors["params"], tensors["fields"], tensors["forcing"])
    boundary = problem.boundary_residual(tensors["params"], tensors["fields"])

    assert loaded["extra"]["mesh_kind"][0] == "jittered"
    assert residual.abs().max().item() < 1.0e-4
    assert boundary.abs().max().item() < 1.0e-7


def test_complex_geometry_plane_stress_fem_snapshots_are_physics_consistent(tmp_path) -> None:
    for mesh_kind in ("hole", "notch", "curved"):
        path = tmp_path / f"fem2d_{mesh_kind}_train.npz"
        save_plane_stress_fem_dataset(
            path,
            n_samples=2,
            split="train",
            seed=37,
            nx=8,
            ny=6,
            mesh_kind=mesh_kind,
            perturbation=0.12,
        )
        loaded = load_fem_snapshots(path)
        tensors = loaded["tensors"]
        callbacks = make_plane_stress_fem_callbacks(
            coords=tensors["coords"],
            connectivity=loaded["extra"]["connectivity"],
            grid_shape=loaded["extra"]["grid_shape"],
        )
        problem = make_fem_problem_adapter(
            tensors,
            loaded["metadata"],
            residual_callback=callbacks[0],
            boundary_callback=callbacks[1],
            energy_callback=callbacks[2],
        )

        residual = problem.residual(tensors["params"], tensors["fields"], tensors["forcing"])
        boundary = problem.boundary_residual(tensors["params"], tensors["fields"])

        assert loaded["extra"]["mesh_kind"][0] == mesh_kind
        assert tensors["coords"].shape[1] <= 48
        assert residual.abs().max().item() < 1.0e-4
        assert boundary.abs().max().item() < 1.0e-7


def test_mesh_graph_operator_handles_different_node_counts() -> None:
    model = MeshGraphOperatorBaseline(4, 2, spatial_dim=2, hidden_dim=16, num_layers=1, k_neighbors=4)
    params = torch.rand(2, 4)
    coarse = torch.rand(2, 20, 2)
    fine = torch.rand(2, 30, 2)

    assert model(coarse, params)["mean"].shape == (2, 20, 2)
    assert model(fine, params)["mean"].shape == (2, 30, 2)


def test_mesh_to_mesh_graph_operator_transfers_between_node_counts() -> None:
    model = MeshToMeshGraphOperatorBaseline(4, 2, spatial_dim=2, hidden_dim=16, num_layers=1, k_neighbors=4)
    params = torch.rand(2, 4)
    coarse = torch.rand(2, 20, 2)
    fine = torch.rand(2, 30, 2)
    model.set_source_coords(coarse)

    assert model(coarse, params)["mean"].shape == (2, 20, 2)
    assert model(fine, params)["mean"].shape == (2, 30, 2)


def test_plane_stress_fem_callbacks_make_exact_snapshots_physics_consistent(tmp_path) -> None:
    path = tmp_path / "fem2d_train.npz"
    save_plane_stress_fem_dataset(path, n_samples=4, split="train", seed=29, nx=5, ny=4)
    loaded = load_fem_snapshots(path)
    tensors = loaded["tensors"]
    callbacks = make_plane_stress_fem_callbacks(
        coords=tensors["coords"],
        connectivity=loaded["extra"]["connectivity"],
        grid_shape=loaded["extra"]["grid_shape"],
    )
    problem = make_fem_problem_adapter(
        tensors,
        loaded["metadata"],
        residual_callback=callbacks[0],
        boundary_callback=callbacks[1],
        energy_callback=callbacks[2],
    )

    residual = problem.residual(tensors["params"], tensors["fields"], tensors["forcing"])
    boundary = problem.boundary_residual(tensors["params"], tensors["fields"])
    energy = problem.energy(tensors["params"], tensors["fields"], tensors["forcing"])

    assert residual.abs().max().item() < 1.0e-4
    assert boundary.abs().max().item() < 1.0e-7
    assert torch.isfinite(energy).all()

    outputs = {"mean": tensors["fields"], "logvar": torch.zeros_like(tensors["fields"])}
    losses = physics_constrained_loss(
        outputs,
        tensors,
        problem,
        PhysicsLossWeights(data=1.0, pde_residual=1.0, boundary=1.0, energy=1.0),
    )
    normalized_losses = physics_constrained_loss(
        outputs,
        tensors,
        problem,
        PhysicsLossWeights(
            data=1.0,
            pde_residual=1.0,
            boundary=1.0,
            energy=1.0,
            normalize_physics=True,
        ),
    )
    metrics = evaluate_physics_consistency(tensors["fields"], tensors, problem)
    assert losses["pde_residual"].item() < 1.0e-8
    assert losses["boundary"].item() < 1.0e-12
    assert losses["energy"].item() < 1.0e-12
    assert normalized_losses["pde_residual"].item() < 1.0e-8
    assert metrics["pde_residual_relative"].item() < 1.0e-4
    assert metrics["boundary_relative"].item() < 1.0e-7
    assert metrics["energy_error_relative"].item() < 1.0e-7
