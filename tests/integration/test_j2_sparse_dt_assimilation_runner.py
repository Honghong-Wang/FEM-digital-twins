from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_j2_sparse_digital_twin_assimilation_runner_outputs_calibration(tmp_path) -> None:
    project_root = Path(__file__).resolve().parents[2]
    script = project_root / "12_reproducibility" / "scripts" / "run_j2_sparse_digital_twin_assimilation.py"
    out = tmp_path / "sparse_dt.json"
    subprocess.run(
        [
            sys.executable,
            str(script),
            "--data-root",
            str(tmp_path / "data"),
            "--train-load-paths",
            "monotonic",
            "--eval-load-paths",
            "cyclic",
            "--epochs",
            "1",
            "--train-samples",
            "1",
            "--eval-samples",
            "1",
            "--batch-size",
            "1",
            "--eval-batch-size",
            "1",
            "--hidden-dim",
            "12",
            "--message-passing-layers",
            "1",
            "--nx",
            "3",
            "--ny",
            "3",
            "--mesh-kind",
            "structured",
            "--load-steps",
            "3",
            "--max-newton-steps",
            "8",
            "--num-sensors",
            "2",
            "--num-observation-steps",
            "2",
            "--inversion-steps",
            "4",
            "--num-posterior-chains",
            "2",
            "--force-regenerate",
            "--out",
            str(out),
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
    metrics = payload["evaluations"]["cyclic"]
    assert payload["metadata"]["num_sensors"] == 2
    assert "material_parameter_relative_l2" in metrics
    assert "history_relative_l2" in metrics
    assert "field_ece" in metrics
    assert out.with_suffix(".csv").exists()
