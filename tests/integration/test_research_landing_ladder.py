from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_research_landing_ladder_dry_run_records_two_claim_tracks(tmp_path) -> None:
    project_root = Path(__file__).resolve().parents[2]
    script = project_root / "12_reproducibility" / "scripts" / "run_research_landing_ladder.py"
    out = tmp_path / "landing_ladder.json"

    subprocess.run(
        [
            sys.executable,
            str(script),
            "--preset",
            "smoke",
            "--track",
            "all",
            "--dry-run",
            "--out",
            str(out),
        ],
        cwd=project_root,
        check=True,
        capture_output=True,
        text=True,
        timeout=60,
    )

    payload = json.loads(out.read_text(encoding="utf-8"))
    assert [stage["name"] for stage in payload["stages"]] == [
        "operator_fem_evidence",
        "stateful_path_operator",
    ]
    assert all(result["status"] == "planned" for result in payload["results"])
    commands = [" ".join(stage["command"]) for stage in payload["stages"]]
    assert any("run_fem2d_baseline_runner.py" in command for command in commands)
    assert any("run_j2_path_ood_comparison.py" in command for command in commands)
    assert payload["research_ladder"][0]["level"] == 1
    assert payload["research_ladder"][1]["level"] == 2
