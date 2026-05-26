from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path
from statistics import mean, median


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SUMMARY_ROOT = (
    PROJECT_ROOT
    / "10_results"
    / "reports"
    / "level4_multigeometry_multipath_qp_hgo"
)
DEFAULT_TABLE_ROOT = PROJECT_ROOT / "11_paper" / "tables"

QP_HISTORY_METRICS = (
    "qp_history_relative_l2",
    "qp_history_increment_relative_l2",
    "qp_reversal_eqp_increment_relative_l2",
    "qp_reversal_plastic_work_increment_relative_l2",
    "qp_reversal_yield_flag_mae",
)
DEFAULT_LOAD_PATHS = (
    "cyclic",
    "unload_reload",
    "nonproportional",
    "random_amplitude",
    "pre_stress",
)
DEFAULT_CANDIDATE_PROTOCOLS = (
    "reversal_curriculum",
    "family_upper_bound",
    "curriculum",
    "upper_bound",
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Build focused Level-6 QP-history evidence tables from case/protocol summary.json "
            "files. Lower values are treated as better for every configured metric."
        )
    )
    parser.add_argument("--summary-root", type=Path, default=DEFAULT_SUMMARY_ROOT)
    parser.add_argument("--metrics", default=",".join(QP_HISTORY_METRICS))
    parser.add_argument("--load-paths", default=",".join(DEFAULT_LOAD_PATHS))
    parser.add_argument("--reference-protocol", default="strict")
    parser.add_argument("--candidate-protocols", default=",".join(DEFAULT_CANDIDATE_PROTOCOLS))
    parser.add_argument("--models", default="all")
    parser.add_argument(
        "--raw-csv-out",
        type=Path,
        default=DEFAULT_TABLE_ROOT / "level6_qp_history_evidence_raw.csv",
    )
    parser.add_argument(
        "--raw-md-out",
        type=Path,
        default=DEFAULT_TABLE_ROOT / "level6_qp_history_evidence_raw.md",
    )
    parser.add_argument(
        "--reduction-csv-out",
        type=Path,
        default=DEFAULT_TABLE_ROOT / "level6_qp_history_protocol_reduction.csv",
    )
    parser.add_argument(
        "--reduction-md-out",
        type=Path,
        default=DEFAULT_TABLE_ROOT / "level6_qp_history_protocol_reduction.md",
    )
    parser.add_argument(
        "--summary-csv-out",
        type=Path,
        default=DEFAULT_TABLE_ROOT / "level6_qp_history_reduction_summary.csv",
    )
    parser.add_argument(
        "--summary-md-out",
        type=Path,
        default=DEFAULT_TABLE_ROOT / "level6_qp_history_reduction_summary.md",
    )
    args = parser.parse_args()

    metrics = _split_csv(args.metrics)
    load_paths = _split_csv(args.load_paths)
    models = None if args.models.strip().lower() == "all" else set(_split_csv(args.models))
    candidate_protocols = _split_csv(args.candidate_protocols)

    raw_rows = _collect_raw_rows(args.summary_root, metrics, load_paths, models)
    reduction_rows = _protocol_reduction_rows(
        raw_rows,
        reference_protocol=args.reference_protocol,
        candidate_protocols=candidate_protocols,
    )
    summary_rows = _reduction_summary_rows(reduction_rows)

    outputs = [
        (args.raw_csv_out, args.raw_md_out, raw_rows),
        (args.reduction_csv_out, args.reduction_md_out, reduction_rows),
        (args.summary_csv_out, args.summary_md_out, summary_rows),
    ]
    for csv_out, md_out, rows in outputs:
        _write_table_pair(csv_out, md_out, rows)
        print(f"wrote {csv_out}")
        print(f"wrote {md_out}")


def _collect_raw_rows(
    summary_root: Path,
    metrics: list[str],
    load_paths: list[str],
    models: set[str] | None,
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for summary_path in sorted(summary_root.glob("*/*/summary.json")):
        case = summary_path.parent.parent.name
        protocol = summary_path.parent.name
        payload = json.loads(summary_path.read_text(encoding="utf-8"))
        for model_name, result in sorted(payload.get("results", {}).items()):
            if models is not None and model_name not in models:
                continue
            result_summary = result.get("summary", {})
            num_seeds = str(result_summary.get("num_seeds", ""))
            by_path = result_summary.get("by_load_path", {})
            for load_path in load_paths:
                path_stats = by_path.get(load_path, {})
                for metric in metrics:
                    stats = path_stats.get(metric)
                    if not stats or stats.get("mean") is None:
                        continue
                    rows.append(
                        {
                            "Case": case,
                            "Protocol": protocol,
                            "Model": model_name,
                            "Load path": load_path,
                            "Metric": metric,
                            "Mean": _format_float(stats.get("mean")),
                            "Std": _format_float(stats.get("std")),
                            "Median": _format_float(stats.get("median")),
                            "IQR": _format_float(stats.get("iqr")),
                            "Seeds": num_seeds,
                            "Source": str(summary_path),
                        }
                    )
    return rows


def _protocol_reduction_rows(
    raw_rows: list[dict[str, str]],
    reference_protocol: str,
    candidate_protocols: list[str],
) -> list[dict[str, str]]:
    index: dict[tuple[str, str, str, str, str], dict[str, str]] = {}
    for row in raw_rows:
        key = (
            row["Case"],
            row["Protocol"],
            row["Model"],
            row["Load path"],
            row["Metric"],
        )
        index[key] = row

    rows: list[dict[str, str]] = []
    group_keys = sorted(
        {
            (row["Case"], row["Model"], row["Load path"], row["Metric"])
            for row in raw_rows
            if row["Protocol"] == reference_protocol
        }
    )
    for case, model, load_path, metric in group_keys:
        ref_row = index.get((case, reference_protocol, model, load_path, metric))
        if ref_row is None:
            continue
        ref_mean = _as_float(ref_row["Mean"])
        ref_median = _as_float(ref_row["Median"])
        for protocol in candidate_protocols:
            cand_row = index.get((case, protocol, model, load_path, metric))
            if cand_row is None:
                continue
            cand_mean = _as_float(cand_row["Mean"])
            cand_median = _as_float(cand_row["Median"])
            mean_drop = _difference(ref_mean, cand_mean)
            median_drop = _difference(ref_median, cand_median)
            rows.append(
                {
                    "Case": case,
                    "Model": model,
                    "Load path": load_path,
                    "Metric": metric,
                    "Reference protocol": reference_protocol,
                    "Candidate protocol": protocol,
                    "Reference mean": _format_float(ref_mean),
                    "Candidate mean": _format_float(cand_mean),
                    "Mean drop": _format_float(mean_drop),
                    "Mean drop %": _format_percent(_drop_fraction(ref_mean, cand_mean)),
                    "Mean improved": _improved_label(ref_mean, cand_mean),
                    "Reference median": _format_float(ref_median),
                    "Candidate median": _format_float(cand_median),
                    "Median drop": _format_float(median_drop),
                    "Median drop %": _format_percent(_drop_fraction(ref_median, cand_median)),
                    "Median improved": _improved_label(ref_median, cand_median),
                }
            )
    return rows


def _reduction_summary_rows(reduction_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    grouped: dict[tuple[str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in reduction_rows:
        grouped[(row["Model"], row["Candidate protocol"], row["Metric"])].append(row)

    rows = []
    for (model, protocol, metric), items in sorted(grouped.items()):
        mean_drop_fractions = [
            _percent_to_float(item["Mean drop %"])
            for item in items
            if item["Mean drop %"]
        ]
        median_drop_fractions = [
            _percent_to_float(item["Median drop %"])
            for item in items
            if item["Median drop %"]
        ]
        mean_improved = [item for item in items if item["Mean improved"] == "yes"]
        median_improved = [item for item in items if item["Median improved"] == "yes"]
        total = len(items)
        rows.append(
            {
                "Model": model,
                "Candidate protocol": protocol,
                "Metric": metric,
                "Comparisons": str(total),
                "Mean improved count": str(len(mean_improved)),
                "Mean improved rate": _format_percent_ratio(len(mean_improved), total),
                "Mean drop % median": _format_float(median(mean_drop_fractions) if mean_drop_fractions else None),
                "Mean drop % mean": _format_float(mean(mean_drop_fractions) if mean_drop_fractions else None),
                "Median improved count": str(len(median_improved)),
                "Median improved rate": _format_percent_ratio(len(median_improved), total),
                "Median drop % median": _format_float(
                    median(median_drop_fractions) if median_drop_fractions else None
                ),
            }
        )
    return rows


def _write_rows(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames = list(rows[0])
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    headers = list(rows[0])
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(row.get(header, "") for header in headers) + " |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_table_pair(csv_path: Path, md_path: Path, rows: list[dict[str, str]]) -> None:
    _write_rows(csv_path, rows)
    _write_markdown(md_path, rows)


def _split_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def _as_float(value: str | None) -> float | None:
    if value in (None, ""):
        return None
    try:
        number = float(value)
    except ValueError:
        return None
    if math.isnan(number) or math.isinf(number):
        return None
    return number


def _drop_fraction(reference: float | None, candidate: float | None) -> float | None:
    if reference is None or candidate is None:
        return None
    denom = abs(reference)
    if denom <= 1.0e-12:
        return None
    return 100.0 * (reference - candidate) / denom


def _difference(reference: float | None, candidate: float | None) -> float | None:
    if reference is None or candidate is None:
        return None
    return reference - candidate


def _improved_label(reference: float | None, candidate: float | None) -> str:
    if reference is None or candidate is None:
        return ""
    return "yes" if candidate < reference else "no"


def _format_float(value: object) -> str:
    if value is None:
        return ""
    try:
        number = float(value)
    except (TypeError, ValueError):
        return ""
    if math.isnan(number) or math.isinf(number):
        return ""
    return f"{number:.6g}"


def _format_percent(value: float | None) -> str:
    if value is None:
        return ""
    return f"{value:.3f}"


def _format_percent_ratio(count: int, total: int) -> str:
    if total <= 0:
        return ""
    return f"{100.0 * count / total:.3f}"


def _percent_to_float(value: str) -> float:
    return float(value)


if __name__ == "__main__":
    main()
