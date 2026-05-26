from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

import torch


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RUNNER = PROJECT_ROOT / "12_reproducibility" / "scripts" / "run_j2_path_dependent_baseline_table.py"
DATA_ROOT = PROJECT_ROOT / "05_data_pipeline" / "processed" / "level4_formal_complex_j2_t6_8step_qp_9case"
REPORT_DIR = PROJECT_ROOT / "10_results" / "reports"

DEFAULT_CASES = (
    "curved_hole_14x11",
    "curved_hole_16x12",
    "curved_hole_18x14",
    "curved_hole_20x15",
    "multi_hole_14x11",
    "multi_hole_16x12",
    "multi_hole_18x14",
    "multi_hole_20x15",
    "notch_14x11",
    "notch_16x12",
    "notch_18x14",
    "notch_20x15",
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Run the complete 12-case faithful HANO baseline on the Level-4 T6/QP matrix. "
            "Each case uses monotonic training, cyclic testing, 50 epochs, and five seeds."
        )
    )
    parser.add_argument("--cases", default=",".join(DEFAULT_CASES), help="Comma-separated geometry-mesh case names.")
    parser.add_argument("--epochs", type=int, default=50)
    parser.add_argument("--seeds", default="20260517,20260518,20260519,20260520,20260521")
    parser.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    parser.add_argument("--force", action="store_true", help="Re-run cases even when the JSON output exists.")
    args = parser.parse_args()

    cases = tuple(item.strip() for item in args.cases.split(",") if item.strip())
    if not cases:
        raise ValueError("at least one case is required")

    for case in cases:
        data_root = DATA_ROOT / case
        if not data_root.exists():
            raise FileNotFoundError(data_root)
        stem = f"level4_t6_faithful_hano_12case_{case}"
        out_json = REPORT_DIR / f"{stem}.json"
        if out_json.exists() and not args.force:
            print(f"[skip] {case}: {out_json} exists")
            continue
        command = [
            sys.executable,
            str(RUNNER),
            "--data-root",
            str(data_root.relative_to(PROJECT_ROOT)),
            "--models",
            "hano_faithful",
            "--train-load-paths",
            "monotonic",
            "--eval-load-paths",
            "cyclic",
            "--seeds",
            args.seeds,
            "--epochs",
            str(args.epochs),
            "--batch-size",
            "4",
            "--eval-batch-size",
            "8",
            "--hidden-dim",
            "96",
            "--message-passing-layers",
            "3",
            "--teacher-forcing-ratio",
            "0.5",
            "--fem-audit-metrics",
            "--device",
            args.device,
            "--out",
            str((REPORT_DIR / f"{stem}.json").relative_to(PROJECT_ROOT)),
            "--csv-out",
            str((REPORT_DIR / f"{stem}.csv").relative_to(PROJECT_ROOT)),
            "--md-out",
            str((REPORT_DIR / f"{stem}.md").relative_to(PROJECT_ROOT)),
            "--robust-csv-out",
            str((REPORT_DIR / f"{stem}_robust.csv").relative_to(PROJECT_ROOT)),
            "--robust-md-out",
            str((REPORT_DIR / f"{stem}_robust.md").relative_to(PROJECT_ROOT)),
            "--per-seed-csv-out",
            str((REPORT_DIR / f"{stem}_per_seed.csv").relative_to(PROJECT_ROOT)),
            "--per-seed-md-out",
            str((REPORT_DIR / f"{stem}_per_seed.md").relative_to(PROJECT_ROOT)),
            "--outlier-csv-out",
            str((REPORT_DIR / f"{stem}_outliers.csv").relative_to(PROJECT_ROOT)),
            "--outlier-md-out",
            str((REPORT_DIR / f"{stem}_outliers.md").relative_to(PROJECT_ROOT)),
            "--pathwise-csv-out",
            str((REPORT_DIR / f"{stem}_by_path.csv").relative_to(PROJECT_ROOT)),
            "--pathwise-md-out",
            str((REPORT_DIR / f"{stem}_by_path.md").relative_to(PROJECT_ROOT)),
        ]
        print(f"[run] {case}: faithful HANO, epochs={args.epochs}, seeds={args.seeds}, device={args.device}")
        subprocess.run(command, cwd=PROJECT_ROOT, check=True)


if __name__ == "__main__":
    main()
