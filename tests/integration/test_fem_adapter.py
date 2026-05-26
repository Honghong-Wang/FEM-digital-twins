from __future__ import annotations

import numpy as np
import torch

from pcgno_dt.data.datasets import OperatorTensorDataset, PathOperatorTensorDataset
from pcgno_dt.data.fem import (
    has_assembled_linear_fem_data,
    has_stateful_nonlinear_fem_data,
    load_fem_path_snapshots,
    load_fem_snapshots,
    make_assembled_linear_fem_callbacks,
    make_fem_problem_adapter,
    make_stateful_nonlinear_fem_callbacks,
    save_fem_npz,
)
from pcgno_dt.evaluation.path_history import evaluate_j2_path_history_consistency
from pcgno_dt.data.synthetic import generate_operator_dataset
from pcgno_dt.numerics.hyperelastic2d import generate_neo_hookean_fem_snapshots
from pcgno_dt.numerics.j2plasticity2d import J2_LOAD_PATHS, generate_j2_plasticity_fem_snapshots
from pcgno_dt.physics.structural import NonlinearElasticBarProblem
from pcgno_dt.training.losses import physics_constrained_loss


def test_fem_npz_adapter_uses_common_tensor_protocol(tmp_path) -> None:
    problem = NonlinearElasticBarProblem(num_points=32)
    data = generate_operator_dataset(problem, n_samples=5, split="train", seed=19)
    tensors = {key: value for key, value in data.items() if isinstance(value, torch.Tensor)}
    path = tmp_path / "structural_fem_snapshots.npz"
    save_fem_npz(
        path,
        tensors,
        parameter_names=problem.parameter_names,
        field_names=("displacement",),
        connectivity=torch.arange(32).numpy(),
    )

    loaded = load_fem_snapshots(path)
    fem_tensors = loaded["tensors"]
    fem_problem = make_fem_problem_adapter(fem_tensors, loaded["metadata"])
    dataset = OperatorTensorDataset(fem_tensors)

    assert len(dataset) == 5
    assert "sample_id" in dataset[0]
    assert fem_problem.num_points == 32
    assert fem_problem.num_parameters == problem.num_parameters
    assert fem_problem.num_fields == problem.num_fields
    assert fem_problem.parameter_names == problem.parameter_names
    assert fem_problem.field_names == ("displacement",)

    batch = {key: value[:2] for key, value in fem_tensors.items()}
    outputs = {"mean": batch["fields"], "logvar": torch.zeros_like(batch["fields"])}
    losses = physics_constrained_loss(outputs, batch, fem_problem)
    assert torch.isfinite(losses["total"])


def test_assembled_linear_fem_callbacks_use_exported_stiffness(tmp_path) -> None:
    coords = torch.tensor([[0.0], [1.0]])
    params = torch.ones(1, 1)
    fields = torch.tensor([[[0.0], [1.0]]])
    stiffness = torch.tensor([[1.0, -1.0], [-1.0, 1.0]])
    forcing = (stiffness @ fields[0, :, 0]).reshape(1, 2, 1)
    tensors = {
        "coords": coords,
        "params": params,
        "fields": fields,
        "forcing": forcing,
    }
    path = tmp_path / "assembled_linear_snapshots.npz"
    save_fem_npz(
        path,
        tensors,
        parameter_names=("load_scale",),
        field_names=("displacement",),
        stiffness=stiffness.numpy(),
        fixed_dofs=torch.tensor([0], dtype=torch.int64).numpy(),
    )

    loaded = load_fem_snapshots(path)
    assert has_assembled_linear_fem_data(loaded["extra"])
    callbacks = make_assembled_linear_fem_callbacks(loaded["tensors"], loaded["extra"])
    fem_problem = make_fem_problem_adapter(
        loaded["tensors"],
        loaded["metadata"],
        residual_callback=callbacks[0],
        boundary_callback=callbacks[1],
        energy_callback=callbacks[2],
    )

    residual = fem_problem.residual(params, fields, forcing)
    boundary = fem_problem.boundary_residual(params, fields)
    energy = fem_problem.energy(params, fields, forcing)
    assert torch.allclose(residual, torch.zeros_like(residual), atol=1.0e-7)
    assert torch.allclose(boundary, torch.zeros_like(boundary), atol=1.0e-7)
    assert torch.isfinite(energy).all()

    batch = {key: value for key, value in loaded["tensors"].items()}
    outputs = {"mean": batch["fields"], "logvar": torch.zeros_like(batch["fields"])}
    losses = physics_constrained_loss(outputs, batch, fem_problem)
    assert losses["pde_residual"] < 1.0e-12
    assert losses["boundary"] < 1.0e-12
    assert losses["energy"] < 1.0e-12


def test_assembled_linear_fem_callbacks_reject_sample_dependent_stiffness(tmp_path) -> None:
    tensors = {
        "coords": torch.tensor([[0.0], [1.0]]),
        "params": torch.ones(2, 1),
        "fields": torch.zeros(2, 2, 1),
        "forcing": torch.zeros(2, 2, 1),
    }
    extra = {
        "stiffness": torch.eye(2).repeat(2, 1, 1).numpy(),
    }

    try:
        make_assembled_linear_fem_callbacks(tensors, extra)
    except ValueError as exc:
        assert "sample-dependent stiffness" in str(exc)
    else:
        raise AssertionError("sample-dependent stiffness should require a stateful callback")


def test_stateful_nonlinear_fem_callbacks_align_shuffled_sample_ids(tmp_path) -> None:
    coords = torch.tensor([[0.0], [1.0]])
    params = torch.ones(2, 1)
    fields = torch.tensor([[[0.0], [1.0]], [[0.0], [2.0]]])
    forcing = torch.zeros_like(fields)
    tangent = torch.stack(
        [
            torch.tensor([[2.0, -2.0], [-2.0, 2.0]]),
            torch.tensor([[3.0, -3.0], [-3.0, 3.0]]),
        ]
    )
    sample_id = torch.tensor([10, 20], dtype=torch.int64)
    material_history = torch.tensor([[0.1], [-0.2]])
    path = tmp_path / "stateful_nonlinear_snapshots.npz"
    save_fem_npz(
        path,
        {
            "coords": coords,
            "params": params,
            "fields": fields,
            "forcing": forcing,
            "sample_id": sample_id,
        },
        parameter_names=("load_scale",),
        field_names=("displacement",),
        tangent_stiffness=tangent.numpy(),
        fixed_dofs=torch.tensor([0], dtype=torch.int64).numpy(),
        material_history=material_history.numpy(),
    )

    loaded = load_fem_snapshots(path)
    assert has_stateful_nonlinear_fem_data(loaded["tensors"], loaded["extra"])
    callbacks = make_stateful_nonlinear_fem_callbacks(loaded["tensors"], loaded["extra"])
    fem_problem = make_fem_problem_adapter(
        loaded["tensors"],
        loaded["metadata"],
        residual_callback=callbacks[0],
        boundary_callback=callbacks[1],
        energy_callback=callbacks[2],
        thermodynamic_callback=callbacks[3],
    )

    shuffled = {
        "sample_id": torch.tensor([20, 10], dtype=torch.int64),
        "params": params[[1, 0]],
        "fields": fields[[1, 0]],
        "forcing": forcing[[1, 0]],
    }
    fem_problem.set_batch_context(shuffled)
    residual = fem_problem.residual(shuffled["params"], shuffled["fields"], shuffled["forcing"])
    boundary = fem_problem.boundary_residual(shuffled["params"], shuffled["fields"])
    thermo = fem_problem.thermodynamic_penalty(shuffled["params"])
    assert torch.allclose(residual, torch.zeros_like(residual), atol=1.0e-7)
    assert torch.allclose(boundary, torch.zeros_like(boundary), atol=1.0e-7)
    assert torch.allclose(thermo, torch.tensor(0.02), atol=1.0e-7)

    perturbed_fields = shuffled["fields"].clone()
    perturbed_fields[0, 1, 0] = 3.0
    residual = fem_problem.residual(shuffled["params"], perturbed_fields, shuffled["forcing"])
    energy = fem_problem.energy(shuffled["params"], perturbed_fields, shuffled["forcing"])
    assert torch.allclose(residual[0], torch.tensor([[0.0], [3.0]]), atol=1.0e-7)
    assert torch.allclose(residual[1], torch.zeros_like(residual[1]), atol=1.0e-7)
    assert torch.allclose(energy, torch.tensor([1.5, 0.0]), atol=1.0e-7)
    fem_problem.clear_batch_context()


def test_stateful_nonlinear_fem_callbacks_require_sample_id_for_partial_batch(tmp_path) -> None:
    tensors = {
        "coords": torch.tensor([[0.0], [1.0]]),
        "params": torch.ones(2, 1),
        "fields": torch.zeros(2, 2, 1),
        "forcing": torch.zeros(2, 2, 1),
        "sample_id": torch.tensor([0, 1], dtype=torch.int64),
    }
    extra = {
        "tangent_stiffness": torch.eye(2).repeat(2, 1, 1).numpy(),
    }
    callbacks = make_stateful_nonlinear_fem_callbacks(tensors, extra)
    fem_problem = make_fem_problem_adapter(
        tensors,
        residual_callback=callbacks[0],
        boundary_callback=callbacks[1],
        energy_callback=callbacks[2],
        thermodynamic_callback=callbacks[3],
    )

    try:
        fem_problem.residual(tensors["params"][:1], tensors["fields"][:1], tensors["forcing"][:1])
    except ValueError as exc:
        assert "sample_id" in str(exc)
    else:
        raise AssertionError("partial stateful FEM batches must include sample_id context")


def test_neo_hookean_solver_exports_stateful_fem_callbacks(tmp_path) -> None:
    data = generate_neo_hookean_fem_snapshots(
        n_samples=2,
        split="train",
        seed=7,
        nx=3,
        ny=3,
        max_newton_steps=15,
    )
    tensors = {key: value for key, value in data.items() if isinstance(value, torch.Tensor)}
    path = tmp_path / "neo_hookean_stateful_snapshots.npz"
    save_fem_npz(
        path,
        tensors,
        parameter_names=data["parameter_names"],
        field_names=data["field_names"],
        tangent_stiffness=data["tangent_stiffness"],
        newton_residual=data["newton_residual"],
        reference_energy=data["reference_energy"],
        material_history=data["material_history"],
        fixed_dofs=data["fixed_dofs"],
    )

    loaded = load_fem_snapshots(path)
    assert has_stateful_nonlinear_fem_data(loaded["tensors"], loaded["extra"])
    callbacks = make_stateful_nonlinear_fem_callbacks(loaded["tensors"], loaded["extra"])
    fem_problem = make_fem_problem_adapter(
        loaded["tensors"],
        loaded["metadata"],
        residual_callback=callbacks[0],
        boundary_callback=callbacks[1],
        energy_callback=callbacks[2],
        thermodynamic_callback=callbacks[3],
    )

    batch = loaded["tensors"]
    outputs = {"mean": batch["fields"], "logvar": torch.zeros_like(batch["fields"])}
    losses = physics_constrained_loss(outputs, batch, fem_problem)
    assert losses["pde_residual"] < 1.0e-6
    assert losses["boundary"] < 1.0e-12
    assert losses["energy"] < 1.0e-12
    assert losses["thermodynamic"] < 1.0e-12
    assert loaded["extra"]["tangent_stiffness"].shape[0] == 2
    assert loaded["extra"]["material_history"].shape[0] == 2


def test_j2_plasticity_solver_exports_path_dependent_history(tmp_path) -> None:
    data = generate_j2_plasticity_fem_snapshots(
        n_samples=1,
        split="train",
        seed=3,
        nx=3,
        ny=3,
        load_steps=4,
        max_newton_steps=12,
    )
    tensors = {key: value for key, value in data.items() if isinstance(value, torch.Tensor)}
    path = tmp_path / "j2_plasticity_stateful_snapshots.npz"
    save_fem_npz(
        path,
        tensors,
        parameter_names=data["parameter_names"],
        field_names=data["field_names"],
        tangent_stiffness=data["tangent_stiffness"],
        newton_residual=data["newton_residual"],
        reference_energy=data["reference_energy"],
        material_history=data["material_history"],
        plastic_strain=data["plastic_strain"],
        tangent_stiffness_sequence=data["tangent_stiffness_sequence"],
        newton_residual_sequence=data["newton_residual_sequence"],
        reference_energy_sequence=data["reference_energy_sequence"],
        material_history_sequence=data["material_history_sequence"],
        plastic_strain_sequence=data["plastic_strain_sequence"],
        stress_sequence=data["stress_sequence"],
        strain_sequence=data["strain_sequence"],
        load_factors=data["load_factors"],
        fixed_dofs=data["fixed_dofs"],
    )

    loaded = load_fem_snapshots(path)
    assert has_stateful_nonlinear_fem_data(loaded["tensors"], loaded["extra"])
    assert loaded["extra"]["material_history"][0, :, 0].max() > 0.0
    assert loaded["extra"]["plastic_strain"].shape[-1] == 6
    callbacks = make_stateful_nonlinear_fem_callbacks(loaded["tensors"], loaded["extra"])
    fem_problem = make_fem_problem_adapter(
        loaded["tensors"],
        loaded["metadata"],
        residual_callback=callbacks[0],
        boundary_callback=callbacks[1],
        energy_callback=callbacks[2],
        thermodynamic_callback=callbacks[3],
    )

    batch = loaded["tensors"]
    outputs = {"mean": batch["fields"], "logvar": torch.zeros_like(batch["fields"])}
    losses = physics_constrained_loss(outputs, batch, fem_problem)
    assert losses["pde_residual"] < 1.0e-8
    assert losses["boundary"] < 1.0e-12
    assert losses["energy"] < 1.0e-12
    assert losses["thermodynamic"] < 1.0e-12

    path_loaded = load_fem_path_snapshots(path)
    path_dataset = PathOperatorTensorDataset(path_loaded["tensors"])
    item = path_dataset[0]
    assert item["fields_sequence"].shape[0] == 4
    assert item["material_history_sequence"].shape[-1] == 5
    path_metrics = evaluate_j2_path_history_consistency(path_loaded["tensors"])
    assert path_metrics["eq_plastic_strain_monotonic_violation"] < 1.0e-12
    assert path_metrics["plastic_work_monotonic_violation"] < 1.0e-12
    assert path_metrics["negative_plastic_multiplier_violation"] < 1.0e-12
    assert path_metrics["max_eq_plastic_strain"] > 0.0


def test_j2_plasticity_solver_exports_memory_challenging_load_paths() -> None:
    assert set(J2_LOAD_PATHS) == {
        "monotonic",
        "unload_reload",
        "cyclic",
        "nonproportional",
        "random_amplitude",
        "pre_stress",
    }
    for load_path in ("unload_reload", "cyclic", "nonproportional", "random_amplitude", "pre_stress"):
        data = generate_j2_plasticity_fem_snapshots(
            n_samples=1,
            split="train",
            seed=5,
            nx=3,
            ny=3,
            load_steps=6,
            load_path=load_path,
            max_newton_steps=12,
        )
        load_factors = data["load_factors"]
        history = torch.as_tensor(data["material_history_sequence"], dtype=torch.float32)
        metrics = evaluate_j2_path_history_consistency({"material_history_sequence": history})
        assert metrics["eq_plastic_strain_monotonic_violation"] < 1.0e-12
        assert metrics["plastic_work_monotonic_violation"] < 1.0e-12
        assert metrics["negative_plastic_multiplier_violation"] < 1.0e-12
        if load_path == "unload_reload":
            assert (np.diff(load_factors[:, 0]) < 0.0).any()
            assert load_factors[-1, 0] > load_factors[-2, 0]
        elif load_path == "cyclic":
            assert load_factors[:, 0].min() < 0.0
            assert (np.diff(load_factors[:, 0]) < 0.0).any()
            assert (np.diff(load_factors[:, 0]) > 0.0).any()
        elif load_path == "nonproportional":
            assert not np.allclose(load_factors[:, 0], load_factors[:, 1])
            assert load_factors[0, 0] > load_factors[0, 1]
        elif load_path == "random_amplitude":
            assert not np.allclose(load_factors[:, 0], load_factors[:, 1])
            assert (np.diff(load_factors[:, 0]) < 0.0).any()
            assert (np.diff(load_factors[:, 1]) < 0.0).any()
        elif load_path == "pre_stress":
            assert load_factors[0, 0] < 0.0
            assert load_factors[0, 1] > 0.0
            assert load_factors[-1, 0] > 0.0
