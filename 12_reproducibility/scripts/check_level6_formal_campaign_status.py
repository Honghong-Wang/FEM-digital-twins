from __future__ import annotations

import argparse
import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA_ROOT = PROJECT_ROOT / "05_data_pipeline" / "processed" / "level6_complex_j2_benchmark_formal_3geom"
DEFAULT_REPORT_ROOT = PROJECT_ROOT / "10_results" / "reports" / "level6_complex_j2_benchmark_formal_3geom"
DEFAULT_LOG = PROJECT_ROOT / "10_results" / "logs" / "level6_formal_3geom_campaign.out.log"
DEFAULT_ERR = PROJECT_ROOT / "10_results" / "logs" / "level6_formal_3geom_campaign.err.log"
PATHS = ("monotonic", "unload_reload", "cyclic", "nonproportional", "random_amplitude", "pre_stress")
SPLITS = ("train", "test")
PROTOCOLS = ("strict", "reversal_curriculum", "family_upper_bound")


def main() -> None:
    parser = argparse.ArgumentParser(description="Check progress of a Level-6 formal benchmark campaign.")
    parser.add_argument("--data-root", type=Path, default=DEFAULT_DATA_ROOT)
    parser.add_argument("--report-root", type=Path, default=DEFAULT_REPORT_ROOT)
    parser.add_argument("--log", type=Path, default=DEFAULT_LOG)
    parser.add_argument("--err", type=Path, default=DEFAULT_ERR)
    parser.add_argument(
        "--expected-cases",
        default="",
        help="Optional comma-separated case directory names, e.g. multi_hole_14x11,notch_14x11.",
    )
    parser.add_argument("--json-out", type=Path, default=None)
    args = parser.parse_args()
    expected_cases = _split_csv(args.expected_cases)

    status = {
        "data_root": str(args.data_root),
        "report_root": str(args.report_root),
        "data": _data_status(args.data_root, expected_cases),
        "tables": _table_status(args.report_root, expected_cases),
        "log_tail": _tail(args.log),
        "err_tail": _tail(args.err),
    }
    text = json.dumps(status, indent=2)
    print(text)
    if args.json_out is not None:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(text + "\n", encoding="utf-8")


def _data_status(root: Path, expected_cases: tuple[str, ...] = ()) -> dict[str, object]:
    case_dirs = sorted(path for path in root.iterdir() if path.is_dir()) if root.exists() else []
    merged = sorted(root.rglob("*.npz")) if root.exists() else []
    shard_files = sorted(root.rglob(".*_shards/*.npz")) if root.exists() else []
    tmp_files = sorted(root.rglob("*.tmp.npz")) if root.exists() else []
    case_names = tuple(path.name for path in case_dirs)
    expectation = expected_cases or case_names
    expected_merged = len(expectation) * len(PATHS) * len(SPLITS)
    present_merged = {str(path.relative_to(root)) for path in merged if "_shards" not in str(path)}
    missing_npz = []
    for case in expectation:
        for path_name in PATHS:
            for split in SPLITS:
                rel = str(Path(case) / path_name / f"{split}.npz")
                if rel not in present_merged:
                    missing_npz.append(rel)
    return {
        "cases_seen": list(case_names),
        "expected_cases": list(expectation),
        "merged_npz": len([path for path in merged if "_shards" not in str(path)]),
        "expected_merged_npz": expected_merged,
        "missing_merged_npz": missing_npz[:64],
        "missing_merged_npz_count": len(missing_npz),
        "shard_npz": len(shard_files),
        "tmp_npz": len(tmp_files),
        "latest_files": [str(path) for path in sorted(merged + tmp_files, key=lambda item: item.stat().st_mtime)[-8:]],
    }


def _table_status(root: Path, expected_cases: tuple[str, ...] = ()) -> dict[str, object]:
    summaries = sorted(root.rglob("summary.json")) if root.exists() else []
    completed = []
    for summary in summaries:
        try:
            payload = json.loads(summary.read_text(encoding="utf-8"))
            models = payload.get("metadata", {}).get("models", [])
        except Exception:
            models = []
        completed.append({"path": str(summary), "models": models})
    expected_summary_count = len(expected_cases) * len(PROTOCOLS) if expected_cases else None
    return {
        "completed_case_protocol_summaries": len(summaries),
        "expected_case_protocol_summaries": expected_summary_count,
        "summaries": completed,
    }


def _tail(path: Path, lines: int = 12) -> list[str]:
    if not path.exists():
        return []
    return path.read_text(encoding="utf-8", errors="replace").splitlines()[-lines:]


def _split_csv(value: str) -> tuple[str, ...]:
    return tuple(item.strip() for item in value.split(",") if item.strip())


if __name__ == "__main__":
    main()
