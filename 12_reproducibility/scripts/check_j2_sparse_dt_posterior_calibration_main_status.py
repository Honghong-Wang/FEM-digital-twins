from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parents[1]
sys.path.insert(0, str(SCRIPT_DIR))

from run_j2_sparse_dt_posterior_calibration_main_suite import (  # noqa: E402
    DEFAULT_SPARSE_CONFIGS,
    PROTOCOLS,
    _parse_sparse_configs,
    _split_csv,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Check completion status for the formal sparse-DT posterior calibration main campaign."
    )
    parser.add_argument("--protocols", default="strict_path_ood,reversal_curriculum,family_upper_bound")
    parser.add_argument("--sparse-configs", default=DEFAULT_SPARSE_CONFIGS)
    parser.add_argument("--expected-seeds", default="20260517,20260518,20260519,20260520,20260521")
    parser.add_argument(
        "--report-root",
        type=Path,
        default=PROJECT_ROOT / "10_results" / "reports" / "j2_sparse_dt_posterior_calibration_main",
    )
    parser.add_argument(
        "--csv-out",
        type=Path,
        default=PROJECT_ROOT / "10_results" / "reports" / "j2_sparse_dt_posterior_calibration_main_status.csv",
    )
    parser.add_argument(
        "--md-out",
        type=Path,
        default=PROJECT_ROOT / "10_results" / "reports" / "j2_sparse_dt_posterior_calibration_main_status.md",
    )
    args = parser.parse_args()

    protocols = {name: PROTOCOLS[name] for name in _split_csv(args.protocols)}
    sparse_configs = _parse_sparse_configs(args.sparse_configs)
    expected_seeds = _split_csv(args.expected_seeds)

    rows = []
    for protocol_name in protocols:
        for config in sparse_configs:
            condition_root = args.report_root / protocol_name / config.name
            summary_json = condition_root / "summary.json"
            per_seed_csv = condition_root / "per_seed.csv"
            completed_seeds = _completed_seeds(condition_root / "seeds")
            payload = _load_json(summary_json)
            load_paths = sorted(payload.get("by_load_path", {})) if payload else []
            rows.append(
                {
                    "Protocol": protocol_name,
                    "Sparse config": config.name,
                    "Condition root": str(condition_root),
                    "Summary JSON": _yes_no(summary_json.exists()),
                    "Per-seed CSV": _yes_no(per_seed_csv.exists()),
                    "Completed seeds": str(len(completed_seeds)),
                    "Expected seeds": str(len(expected_seeds)),
                    "Missing seeds": ",".join(seed for seed in expected_seeds if seed not in completed_seeds),
                    "Eval paths": ",".join(load_paths),
                    "Has raw coverage": _yes_no(_has_metric(payload, "field_coverage_95")),
                    "Has calibrated coverage": _yes_no(_has_metric(payload, "calibrated_field_coverage_95")),
                    "Has NLL/ECE": _yes_no(
                        _has_metric(payload, "field_nll") and _has_metric(payload, "field_ece")
                    ),
                    "Status": _status(summary_json.exists(), len(completed_seeds), len(expected_seeds)),
                }
            )
    _write_rows(args.csv_out, rows)
    _write_markdown(args.md_out, rows)
    print(f"wrote {args.csv_out}")
    print(f"wrote {args.md_out}")


def _completed_seeds(seed_dir: Path) -> set[str]:
    if not seed_dir.exists():
        return set()
    seeds = set()
    for path in seed_dir.glob("seed_*.json"):
        seeds.add(path.stem.replace("seed_", ""))
    return seeds


def _load_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _has_metric(payload: dict | None, metric: str) -> bool:
    if not payload:
        return False
    for metrics in payload.get("by_load_path", {}).values():
        if metric in metrics:
            return True
    return False


def _status(has_summary: bool, completed: int, expected: int) -> str:
    if has_summary and completed >= expected:
        return "complete"
    if completed > 0 or has_summary:
        return "partial"
    return "missing"


def _yes_no(flag: bool) -> str:
    return "yes" if flag else "no"


def _write_rows(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    headers = list(rows[0])
    lines = [
        "# Sparse-DT posterior calibration formal campaign status",
        "",
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(header, "")).replace("|", "\\|") for header in headers) + " |")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
