from __future__ import annotations

import subprocess
import sys
from datetime import datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
LOG_DIR = PROJECT_ROOT / "10_results" / "logs"
LOG = LOG_DIR / "level6_cmame_auto_loop.out.log"
ERR = LOG_DIR / "level6_cmame_auto_loop.err.log"
EVAL = PROJECT_ROOT / "12_reproducibility" / "scripts" / "evaluate_level6_readiness.py"
SOLVER = PROJECT_ROOT / "12_reproducibility" / "scripts" / "run_solver_in_loop_formal_main_suite.py"


def main() -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    _log("LEVEL6_CMAME_AUTO_PY_START")
    _run([sys.executable, str(EVAL)], "STEP 1 EVALUATE_INITIAL")
    _run(_solver_command(), "STEP 2 RUN_SOLVER_IN_LOOP_FORMAL_3CASE")
    _run([sys.executable, str(EVAL)], "STEP 3 EVALUATE_AFTER_SOLVER")
    _log("LEVEL6_CMAME_AUTO_PY_EXIT 0")


def _solver_command() -> list[str]:
    return [
        sys.executable,
        str(SOLVER),
        "--matrix-root",
        "05_data_pipeline/processed/level4_formal_complex_j2_t6_8step_qp_9case",
        "--case-names",
        "multi_hole_14x11,notch_14x11,curved_hole_14x11",
        "--models",
        "hgo_qp_true_j2",
        "--train-load-paths",
        "monotonic",
        "--eval-load-paths",
        "monotonic,unload_reload,cyclic,nonproportional",
        "--seeds",
        "20260517,20260518,20260519,20260520,20260521",
        "--epochs",
        "50",
        "--batch-size",
        "1",
        "--eval-batch-size",
        "1",
        "--device",
        "cuda",
        "--step-policy",
        "all",
        "--main-csv-out",
        "11_paper/tables/solver_in_loop_formal_main_table.csv",
        "--main-md-out",
        "11_paper/tables/solver_in_loop_formal_main_table.md",
        "--case-csv-out",
        "11_paper/tables/solver_in_loop_formal_main_case_rows.csv",
        "--case-md-out",
        "11_paper/tables/solver_in_loop_formal_main_case_rows.md",
        "--case-aggregate-csv-out",
        "11_paper/tables/solver_in_loop_formal_main_case_aggregate.csv",
        "--case-aggregate-md-out",
        "11_paper/tables/solver_in_loop_formal_main_case_aggregate.md",
        "--reduction-csv-out",
        "11_paper/tables/solver_in_loop_formal_main_reduction.csv",
        "--reduction-md-out",
        "11_paper/tables/solver_in_loop_formal_main_reduction.md",
        "--reduction-aggregate-csv-out",
        "11_paper/tables/solver_in_loop_formal_main_reduction_aggregate.csv",
        "--reduction-aggregate-md-out",
        "11_paper/tables/solver_in_loop_formal_main_reduction_aggregate.md",
    ]


def _run(command: list[str], label: str) -> None:
    _log(label)
    _log("COMMAND " + " ".join(command))
    with LOG.open("a", encoding="utf-8") as out, ERR.open("a", encoding="utf-8") as err:
        result = subprocess.run(command, cwd=PROJECT_ROOT, stdout=out, stderr=err)
    _log(f"{label}_EXIT {result.returncode}")
    if result.returncode != 0:
        raise SystemExit(result.returncode)


def _log(message: str) -> None:
    stamp = datetime.now().isoformat(timespec="seconds")
    with LOG.open("a", encoding="utf-8") as f:
        f.write(f"{stamp} {message}\n")
    print(f"{stamp} {message}", flush=True)


if __name__ == "__main__":
    main()
