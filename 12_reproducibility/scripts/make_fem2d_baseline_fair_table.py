from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

TABLE_METRICS = (
    ("test", "relative_l2", "Test rel. L2"),
    ("test", "pde_residual_relative", "Test FEM residual rel."),
    ("test", "boundary_relative", "Test boundary rel."),
    ("test", "energy_error_relative", "Test energy rel."),
    ("ood_material", "relative_l2", "OOD material rel. L2"),
    ("ood_loading", "relative_l2", "OOD loading rel. L2"),
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert run_fem2d_baseline_runner JSON output into final fair-comparison tables."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=PROJECT_ROOT / "10_results" / "reports" / "fem2d_baseline_runner_results.json",
    )
    parser.add_argument(
        "--csv-out",
        type=Path,
        default=PROJECT_ROOT / "11_paper" / "tables" / "fem2d_final_fair_baseline_table.csv",
    )
    parser.add_argument(
        "--md-out",
        type=Path,
        default=PROJECT_ROOT / "11_paper" / "tables" / "fem2d_final_fair_baseline_table.md",
    )
    args = parser.parse_args()

    payload = json.loads(args.input.read_text(encoding="utf-8"))
    rows = _table_rows(payload)
    _write_csv(args.csv_out, rows)
    _write_markdown(args.md_out, rows, args.input)
    print(f"wrote {args.csv_out}")
    print(f"wrote {args.md_out}")


def _table_rows(payload: dict) -> list[dict[str, str]]:
    rows = []
    for model_name, result in payload.items():
        summary = result["summary"]
        row: dict[str, str] = {
            "model": model_name,
            "num_seeds": str(summary.get("num_seeds", "")),
            "training_strategy": _strategy_label(summary.get("training_strategy", {})),
        }
        for split, metric, label in TABLE_METRICS:
            stats = summary.get(split, {}).get(metric)
            row[label] = _format_stat(stats)
            row[f"{label} mean"] = "" if stats is None else f"{stats['mean']:.10g}"
            row[f"{label} std"] = "" if stats is None else f"{stats['std']:.10g}"
        rows.append(row)
    return rows


def _write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    fieldnames = ["model", "num_seeds", "training_strategy"]
    for _, _, label in TABLE_METRICS:
        fieldnames.extend([label, f"{label} mean", f"{label} std"])
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _write_markdown(path: Path, rows: list[dict[str, str]], source: Path) -> None:
    headers = ["Model", "Seeds", "Strategy", *[label for _, _, label in TABLE_METRICS]]
    lines = [
        "# FEM2D Final Fair Baseline Table",
        "",
        "All rows are generated from the same baseline-runner JSON artifact.",
        "",
        f"Source: `{source}`",
        "",
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---", "---:", "---", *["---:" for _ in TABLE_METRICS]]) + " |",
    ]
    for row in rows:
        values = [
            row["model"],
            row["num_seeds"],
            row["training_strategy"],
            *[row[label] for _, _, label in TABLE_METRICS],
        ]
        lines.append("| " + " | ".join(values) + " |")
    lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _format_stat(stats: dict | None) -> str:
    if stats is None:
        return ""
    return f"{stats['mean']:.4f} +/- {stats['std']:.4f}"


def _strategy_label(strategy: dict) -> str:
    if not strategy:
        return ""
    data_loss = strategy.get("pcgno_data_loss")
    curriculum = strategy.get("physics_curriculum")
    balancer_bits = []
    if data_loss:
        balancer_bits.append(f"data={data_loss}")
    if curriculum:
        balancer_bits.append(f"curriculum={curriculum}")
    return ", ".join(balancer_bits)


if __name__ == "__main__":
    main()
