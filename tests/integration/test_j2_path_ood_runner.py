from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import numpy as np

from pcgno_dt.data.fem import load_fem_path_snapshots, load_fem_snapshots
from pcgno_dt.numerics.j2plasticity2d import save_j2_plasticity_fem_dataset


def test_j2_path_ood_comparison_runner_quantifies_cyclic_degradation(tmp_path) -> None:
    project_root = Path(__file__).resolve().parents[2]
    script = project_root / "12_reproducibility" / "scripts" / "run_j2_path_ood_comparison.py"
    out = tmp_path / "j2_path_ood_results.json"
    data_root = tmp_path / "j2_path_ood_data"

    subprocess.run(
        [
            sys.executable,
            str(script),
            "--data-root",
            str(data_root),
            "--train-samples",
            "1",
            "--eval-samples",
            "1",
            "--epochs",
            "1",
            "--batch-size",
            "1",
            "--eval-batch-size",
            "1",
            "--hidden-dim",
            "12",
            "--message-passing-layers",
            "1",
            "--model-kind",
            "thermo_hard_hgo",
            "--load-steps",
            "4",
            "--max-newton-steps",
            "8",
            "--eval-load-paths",
            "monotonic,cyclic",
            "--out",
            str(out),
            "--force-regenerate",
            "--device",
            "cpu",
        ],
        cwd=project_root,
        check=True,
        capture_output=True,
        text=True,
        timeout=180,
    )

    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["metadata"]["model_kind"] == "thermo_hard_hgo"
    assert payload["metadata"]["training_load_paths"] == ["monotonic"]
    assert payload["metadata"]["strict_path_ood"] is True
    assert set(payload["evaluations"]) == {"monotonic", "cyclic"}
    assert "history_increment_relative_l2" in payload["evaluations"]["cyclic"]
    assert "cyclic" in payload["path_ood_degradation_vs_monotonic"]
    assert "history_relative_l2_ratio" in payload["path_ood_degradation_vs_monotonic"]["cyclic"]
    assert out.with_suffix(".csv").exists()


def test_j2_complex_and_external_mesh_path_datasets(tmp_path) -> None:
    complex_path = tmp_path / "j2_hole_cyclic.npz"
    save_j2_plasticity_fem_dataset(
        complex_path,
        n_samples=1,
        split="test",
        seed=41,
        nx=6,
        ny=5,
        mesh_kind="hole",
        perturbation=0.08,
        load_steps=3,
        load_path="cyclic",
        max_newton_steps=8,
    )
    loaded = load_fem_path_snapshots(complex_path)
    assert loaded["extra"]["mesh_kind"][0] == "hole"
    assert loaded["tensors"]["fields_sequence"].shape[1] == 3
    assert np.asarray(loaded["extra"]["connectivity"]).shape[1] == 3

    mesh_path = tmp_path / "external_rect_mesh.npz"
    np.savez(
        mesh_path,
        coords=np.asarray([[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0]], dtype=np.float64),
        connectivity=np.asarray([[0, 1, 2], [0, 2, 3]], dtype=np.int64),
    )
    external_path = tmp_path / "j2_external_monotonic.npz"
    save_j2_plasticity_fem_dataset(
        external_path,
        n_samples=1,
        split="test",
        seed=43,
        mesh_file=mesh_path,
        load_steps=2,
        load_path="monotonic",
        max_newton_steps=8,
    )
    external = load_fem_snapshots(external_path)
    assert external["extra"]["mesh_kind"][0] == "external_npz"
    assert external["extra"]["mesh_source"][0].endswith("external_rect_mesh.npz")
    assert external["tensors"]["coords"].shape[1] == 4


def test_j2_level4_complex_mesh_kinds_generate(tmp_path) -> None:
    for mesh_kind in (
        "multi_hole",
        "crack",
        "curved_hole",
        "random_holes",
        "crack_tip",
        "stress_concentration",
    ):
        out = tmp_path / f"j2_{mesh_kind}.npz"
        save_j2_plasticity_fem_dataset(
            out,
            n_samples=1,
            split="test",
            seed=51,
            nx=8,
            ny=6,
            mesh_kind=mesh_kind,
            perturbation=0.10,
            load_steps=2,
            load_path="unload_reload",
            max_newton_steps=8,
        )
        loaded = load_fem_path_snapshots(out)
        assert loaded["extra"]["mesh_kind"][0] == mesh_kind
        assert loaded["tensors"]["fields_sequence"].shape[1] == 2
        assert np.asarray(loaded["extra"]["connectivity"]).shape[0] > 0
