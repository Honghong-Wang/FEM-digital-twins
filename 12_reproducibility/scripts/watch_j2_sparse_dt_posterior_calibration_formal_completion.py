from __future__ import annotations

import argparse
import csv
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
STATUS_SCRIPT = PROJECT_ROOT / "12_reproducibility" / "scripts" / "check_j2_sparse_dt_posterior_calibration_main_status.py"
SUITE_SCRIPT = PROJECT_ROOT / "12_reproducibility" / "scripts" / "run_j2_sparse_dt_posterior_calibration_main_suite.py"
AUDIT_SCRIPT = PROJECT_ROOT / "12_reproducibility" / "scripts" / "audit_j2_sparse_dt_posterior_calibration_formal.py"
STATUS_CSV = PROJECT_ROOT / "10_results" / "reports" / "j2_sparse_dt_posterior_calibration_main_status.csv"
LOCK_FILE = PROJECT_ROOT / "10_results" / "logs" / "j2_sparse_dt_posterior_calibration_formal_watcher.lock"


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Watch the 9-condition sparse-DT posterior calibration campaign. "
            "When all conditions are complete, aggregate the formal tables and run the formal audit."
        )
    )
    parser.add_argument("--poll-seconds", type=int, default=300)
    parser.add_argument("--max-hours", type=float, default=72.0)
    parser.add_argument("--force", action="store_true", help="Ignore an existing watcher lock file.")
    args = parser.parse_args()

    LOCK_FILE.parent.mkdir(parents=True, exist_ok=True)
    if LOCK_FILE.exists() and not args.force:
        print(f"watcher lock exists: {LOCK_FILE}", flush=True)
        return
    LOCK_FILE.write_text(f"started={datetime.now().isoformat()}\n", encoding="utf-8")
    deadline = datetime.now() + timedelta(hours=args.max_hours)
    try:
        while datetime.now() < deadline:
            _run([sys.executable, str(STATUS_SCRIPT)])
            rows = _read_status_rows()
            complete = rows and all(row.get("Status") == "complete" for row in rows)
            completed = sum(1 for row in rows if row.get("Status") == "complete")
            print(
                f"[{datetime.now().isoformat(timespec='seconds')}] "
                f"posterior calibration formal status: {completed}/{len(rows)} complete",
                flush=True,
            )
            if complete:
                print("all conditions complete; aggregating formal tables", flush=True)
                _run(_aggregate_command())
                print("running formal audit", flush=True)
                _run([sys.executable, str(AUDIT_SCRIPT)])
                print("formal watcher completed successfully", flush=True)
                return
            time.sleep(max(30, args.poll_seconds))
        raise TimeoutError(f"formal watcher exceeded {args.max_hours} hours")
    finally:
        try:
            LOCK_FILE.unlink()
        except FileNotFoundError:
            pass


def _run(command: list[str]) -> None:
    print(" ".join(command), flush=True)
    subprocess.run(command, cwd=PROJECT_ROOT, check=True)


def _read_status_rows() -> list[dict[str, str]]:
    if not STATUS_CSV.exists():
        return []
    with STATUS_CSV.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def _aggregate_command() -> list[str]:
    return [
        sys.executable,
        str(SUITE_SCRIPT),
        "--aggregate-only",
        "--protocols",
        "strict_path_ood,reversal_curriculum,family_upper_bound",
        "--sparse-configs",
        "s2_t2:2:2:0.001,s4_t2:4:2:0.001,s6_t3:6:3:0.001",
        "--epochs",
        "50",
        "--seeds",
        "20260517,20260518,20260519,20260520,20260521",
        "--train-samples",
        "32",
        "--eval-samples",
        "8",
        "--num-posterior-chains",
        "8",
        "--inversion-steps",
        "120",
        "--device",
        "cuda",
        "--paper-csv-out",
        "11_paper/tables/j2_sparse_dt_posterior_calibration_main_table.csv",
        "--paper-md-out",
        "11_paper/tables/j2_sparse_dt_posterior_calibration_main_table.md",
        "--compact-csv-out",
        "11_paper/tables/j2_sparse_dt_posterior_calibration_compact_main.csv",
        "--compact-md-out",
        "11_paper/tables/j2_sparse_dt_posterior_calibration_compact_main.md",
        "--gain-csv-out",
        "11_paper/tables/j2_sparse_dt_posterior_calibration_gain_table.csv",
        "--gain-md-out",
        "11_paper/tables/j2_sparse_dt_posterior_calibration_gain_table.md",
        "--gain-aggregate-csv-out",
        "11_paper/tables/j2_sparse_dt_posterior_calibration_gain_aggregate.csv",
        "--gain-aggregate-md-out",
        "11_paper/tables/j2_sparse_dt_posterior_calibration_gain_aggregate.md",
    ]


if __name__ == "__main__":
    main()
