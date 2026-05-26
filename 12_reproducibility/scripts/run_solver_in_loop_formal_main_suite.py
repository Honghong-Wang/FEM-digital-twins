from __future__ import annotations

import argparse
import csv
import subprocess
import sys
from collections import defaultdict
from pathlib import Path
from statistics import mean, median


PROJECT_ROOT = Path(__file__).resolve().parents[2]
ABLATION_SCRIPT = PROJECT_ROOT / "12_reproducibility" / "scripts" / "run_solver_in_loop_ablation.py"
DEFAULT_MATRIX_ROOT = (
    PROJECT_ROOT / "05_data_pipeline" / "processed" / "level4_formal_complex_j2_t6_8step_qp_9case"
)
DEFAULT_OUT_ROOT = PROJECT_ROOT / "10_results" / "reports" / "solver_in_loop_formal_main"
DEFAULT_TABLE_ROOT = PROJECT_ROOT / "11_paper" / "tables"

KEY_METRICS = (
    "displacement_relative_l2",
    "qp_history_relative_l2",
    "qp_history_increment_relative_l2",
    "fem_residual_relative_rms",
    "fem_energy_relative_error",
    "fem_solver_linearized_residual_relative_rms",
    "fem_newton_initial_residual_relative_rms",
    "fem_newton_final_residual_relative_rms",
    "fem_newton_residual_ratio",
    "fem_newton_residual_decrease_fraction",
    "fem_newton_step_residual_decrease_fraction",
    "fem_newton_correction_relative_norm",
    "fem_newton_accepted_damping",
    "fem_newton_convergence_rate",
    "fem_newton_failure_rate",
)

CORE_COMPACT_METRICS = (
    ("displacement_relative_l2", "Disp. L2"),
    ("qp_history_relative_l2", "QP hist. L2"),
    ("fem_residual_relative_rms", "FEM residual"),
    ("fem_energy_relative_error", "FEM energy"),
    ("fem_newton_final_residual_relative_rms", "Newton final residual"),
    ("fem_newton_residual_ratio", "Newton ratio"),
    ("fem_newton_residual_decrease_fraction", "Newton decrease"),
    ("fem_newton_convergence_rate", "Newton conv."),
    ("fem_newton_failure_rate", "Newton fail"),
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Promote solver-in-loop smoke experiments into a formal multi-case main table. "
            "The suite runs no-solver, tangent-linearized, one-step dense Newton, "
            "multi-step damped Newton, and line-search Newton arms through the existing "
            "solver-in-loop ablation runner, then aggregates across geometry/mesh cases."
        )
    )
    parser.add_argument("--matrix-root", type=Path, default=DEFAULT_MATRIX_ROOT)
    parser.add_argument(
        "--case-names",
        default="",
        help="Comma-separated case directory names. Empty means every child directory under matrix-root.",
    )
    parser.add_argument("--out-root", type=Path, default=DEFAULT_OUT_ROOT)
    parser.add_argument("--models", default="hgo_qp_true_j2")
    parser.add_argument("--train-load-paths", default="monotonic")
    parser.add_argument(
        "--eval-load-paths",
        default="monotonic,unload_reload,cyclic,nonproportional,random_amplitude,pre_stress",
    )
    parser.add_argument("--seeds", default="20260517,20260518,20260519,20260520,20260521")
    parser.add_argument("--epochs", type=int, default=50)
    parser.add_argument("--batch-size", type=int, default=1)
    parser.add_argument("--eval-batch-size", type=int, default=1)
    parser.add_argument("--hidden-dim", type=int, default=96)
    parser.add_argument("--message-passing-layers", type=int, default=3)
    parser.add_argument("--learning-rate", type=float, default=1.0e-3)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--residual-weight", type=float, default=5.0e-5)
    parser.add_argument("--energy-weight", type=float, default=5.0e-6)
    parser.add_argument("--solver-weight", type=float, default=1.0e-5)
    parser.add_argument("--step-policy", choices=("final", "all", "reversal", "reversal_final"), default="all")
    parser.add_argument("--fem-training-models", default="hgo_qp_true_j2,hgo_qp_thermo_hard,tinn")
    parser.add_argument("--include-regularization-sweep", action="store_true")
    parser.add_argument("--regularization-sweep", default="1e-8,1e-6,1e-4")
    parser.add_argument("--aggregate-only", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--skip-existing", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument(
        "--main-csv-out",
        type=Path,
        default=DEFAULT_TABLE_ROOT / "solver_in_loop_formal_main_table.csv",
    )
    parser.add_argument(
        "--main-md-out",
        type=Path,
        default=DEFAULT_TABLE_ROOT / "solver_in_loop_formal_main_table.md",
    )
    parser.add_argument(
        "--case-csv-out",
        type=Path,
        default=DEFAULT_TABLE_ROOT / "solver_in_loop_formal_main_case_rows.csv",
    )
    parser.add_argument(
        "--case-md-out",
        type=Path,
        default=DEFAULT_TABLE_ROOT / "solver_in_loop_formal_main_case_rows.md",
    )
    parser.add_argument(
        "--case-aggregate-csv-out",
        type=Path,
        default=DEFAULT_TABLE_ROOT / "solver_in_loop_formal_main_case_aggregate.csv",
    )
    parser.add_argument(
        "--case-aggregate-md-out",
        type=Path,
        default=DEFAULT_TABLE_ROOT / "solver_in_loop_formal_main_case_aggregate.md",
    )
    parser.add_argument(
        "--reduction-csv-out",
        type=Path,
        default=DEFAULT_TABLE_ROOT / "solver_in_loop_formal_main_reduction.csv",
    )
    parser.add_argument(
        "--reduction-md-out",
        type=Path,
        default=DEFAULT_TABLE_ROOT / "solver_in_loop_formal_main_reduction.md",
    )
    parser.add_argument(
        "--reduction-aggregate-csv-out",
        type=Path,
        default=DEFAULT_TABLE_ROOT / "solver_in_loop_formal_main_reduction_aggregate.csv",
    )
    parser.add_argument(
        "--reduction-aggregate-md-out",
        type=Path,
        default=DEFAULT_TABLE_ROOT / "solver_in_loop_formal_main_reduction_aggregate.md",
    )
    args = parser.parse_args()

    cases = _discover_cases(args.matrix_root, args.case_names)
    if not cases:
        raise FileNotFoundError(f"no case directories found under {args.matrix_root}")

    case_rows: list[dict[str, str]] = []
    reduction_rows: list[dict[str, str]] = []
    for case_path in cases:
        case_out = args.out_root / case_path.name
        if not args.aggregate_only:
            command = _case_command(args, case_path, case_out)
            if args.dry_run:
                print(" ".join(command))
                continue
            else:
                subprocess.run(command, cwd=PROJECT_ROOT, check=True)
        table_path = case_out / "solver_in_loop_ablation_table.csv"
        reduction_path = case_out / "solver_in_loop_ablation_reduction.csv"
        case_rows.extend(_case_rows(table_path, case_path.name, args.matrix_root))
        reduction_rows.extend(_case_rows(reduction_path, case_path.name, args.matrix_root))

    aggregate_rows = _aggregate_metric_rows(case_rows)
    reduction_aggregate_rows = _aggregate_reduction_rows(reduction_rows)
    main_rows = _compact_main_rows(aggregate_rows)

    if not args.dry_run:
        _write_rows(args.case_csv_out, case_rows)
        _write_markdown(args.case_md_out, case_rows)
        _write_rows(args.case_aggregate_csv_out, aggregate_rows)
        _write_markdown(args.case_aggregate_md_out, aggregate_rows)
        _write_rows(args.reduction_csv_out, reduction_rows)
        _write_markdown(args.reduction_md_out, reduction_rows)
        _write_rows(args.reduction_aggregate_csv_out, reduction_aggregate_rows)
        _write_markdown(args.reduction_aggregate_md_out, reduction_aggregate_rows)
        _write_rows(args.main_csv_out, main_rows)
        _write_markdown(args.main_md_out, main_rows)
        print(f"cases: {', '.join(case.name for case in cases)}")
        print(f"wrote {args.main_csv_out}")
        print(f"wrote {args.case_aggregate_csv_out}")
        print(f"wrote {args.reduction_aggregate_csv_out}")


def _discover_cases(matrix_root: Path, case_names: str) -> list[Path]:
    if case_names.strip():
        names = [item.strip() for item in case_names.split(",") if item.strip()]
        cases = [matrix_root / name for name in names]
    else:
        cases = [path for path in matrix_root.iterdir() if path.is_dir()]
    missing = [path for path in cases if not path.is_dir()]
    if missing:
        joined = ", ".join(str(path) for path in missing)
        raise FileNotFoundError(f"missing case directories: {joined}")
    return sorted(cases, key=lambda path: _case_sort_key(path.name))


def _case_sort_key(name: str) -> tuple[str, int, int, str]:
    geometry, mesh = _case_parts(name)
    width, height = _mesh_size(mesh)
    return geometry, width, height, name


def _case_command(args: argparse.Namespace, case_path: Path, case_out: Path) -> list[str]:
    command = [
        sys.executable,
        str(ABLATION_SCRIPT),
        "--data-root",
        str(case_path),
        "--out-root",
        str(case_out / "arms"),
        "--models",
        args.models,
        "--train-load-paths",
        args.train_load_paths,
        "--eval-load-paths",
        args.eval_load_paths,
        "--seeds",
        args.seeds,
        "--epochs",
        str(args.epochs),
        "--batch-size",
        str(args.batch_size),
        "--eval-batch-size",
        str(args.eval_batch_size),
        "--hidden-dim",
        str(args.hidden_dim),
        "--message-passing-layers",
        str(args.message_passing_layers),
        "--learning-rate",
        str(args.learning_rate),
        "--device",
        args.device,
        "--residual-weight",
        str(args.residual_weight),
        "--energy-weight",
        str(args.energy_weight),
        "--solver-weight",
        str(args.solver_weight),
        "--step-policy",
        args.step_policy,
        "--fem-training-models",
        args.fem_training_models,
        "--table-csv-out",
        str(case_out / "solver_in_loop_ablation_table.csv"),
        "--table-md-out",
        str(case_out / "solver_in_loop_ablation_table.md"),
        "--reduction-csv-out",
        str(case_out / "solver_in_loop_ablation_reduction.csv"),
        "--reduction-md-out",
        str(case_out / "solver_in_loop_ablation_reduction.md"),
    ]
    if args.include_regularization_sweep:
        command.extend(["--include-regularization-sweep", "--regularization-sweep", args.regularization_sweep])
    if not args.skip_existing:
        command.append("--no-skip-existing")
    return command


def _case_rows(path: Path, case_name: str, matrix_root: Path) -> list[dict[str, str]]:
    if not path.exists():
        print(f"[missing] {path}")
        return []
    geometry, mesh = _case_parts(case_name)
    output = []
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            enriched = {
                "Matrix": matrix_root.name,
                "Case": case_name,
                "Geometry": geometry,
                "Mesh": mesh,
            }
            enriched.update(row)
            output.append(enriched)
    return output


def _aggregate_metric_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    groups: dict[tuple[str, ...], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        if row.get("Metric") not in KEY_METRICS:
            continue
        key = (
            row.get("Ablation", ""),
            row.get("Ablation id", ""),
            row.get("Solver mode", ""),
            row.get("Newton damping", ""),
            row.get("Newton steps", ""),
            row.get("Line search", ""),
            row.get("Regularization", ""),
            row.get("Model", ""),
            row.get("Load path", ""),
            row.get("Metric", ""),
            row.get("Metric label", ""),
        )
        groups[key].append(row)

    output = []
    for key, items in sorted(groups.items()):
        mean_values = [_as_float(item.get("Mean")) for item in items]
        median_values = [_as_float(item.get("Median")) for item in items]
        mean_values = [value for value in mean_values if value is not None]
        median_values = [value for value in median_values if value is not None]
        cases = sorted({item["Case"] for item in items})
        output.append(
            {
                "Ablation": key[0],
                "Ablation id": key[1],
                "Solver mode": key[2],
                "Newton damping": key[3],
                "Newton steps": key[4],
                "Line search": key[5],
                "Regularization": key[6],
                "Model": key[7],
                "Load path": key[8],
                "Metric": key[9],
                "Metric label": key[10],
                "Case mean": _format_float(_safe_mean(mean_values)),
                "Case std": _format_float(_safe_std(mean_values)),
                "Case median": _format_float(_safe_median(median_values or mean_values)),
                "Case IQR": _format_float(_safe_iqr(median_values or mean_values)),
                "Cases": str(len(cases)),
                "Case list": ",".join(cases),
            }
        )
    return output


def _aggregate_reduction_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    groups: dict[tuple[str, ...], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        key = (
            row.get("Ablation", ""),
            row.get("Model", ""),
            row.get("Load path", ""),
            row.get("Metric", ""),
        )
        groups[key].append(row)

    output = []
    for key, items in sorted(groups.items()):
        mean_improvements = [_as_float(item.get("Mean improvement %")) for item in items]
        median_improvements = [_as_float(item.get("Median improvement %")) for item in items]
        mean_improvements = [value for value in mean_improvements if value is not None]
        median_improvements = [value for value in median_improvements if value is not None]
        cases = sorted({item["Case"] for item in items})
        output.append(
            {
                "Ablation": key[0],
                "Model": key[1],
                "Load path": key[2],
                "Metric": key[3],
                "Mean improvement % case mean": _format_float(_safe_mean(mean_improvements)),
                "Mean improvement % case std": _format_float(_safe_std(mean_improvements)),
                "Median improvement % case mean": _format_float(_safe_mean(median_improvements)),
                "Median improvement % case std": _format_float(_safe_std(median_improvements)),
                "Improved cases": str(_count_positive(mean_improvements)),
                "Cases": str(len(cases)),
                "Case list": ",".join(cases),
            }
        )
    return output


def _compact_main_rows(aggregate_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    groups: dict[tuple[str, ...], dict[str, dict[str, str]]] = defaultdict(dict)
    metadata: dict[tuple[str, ...], dict[str, str]] = {}
    for row in aggregate_rows:
        key = (
            row["Ablation"],
            row["Ablation id"],
            row["Model"],
            row["Load path"],
        )
        groups[key][row["Metric"]] = row
        metadata[key] = row

    output = []
    for key, by_metric in sorted(groups.items()):
        meta = metadata[key]
        item = {
            "Ablation": key[0],
            "Ablation id": key[1],
            "Model": key[2],
            "Load path": key[3],
            "Solver mode": meta.get("Solver mode", ""),
            "Newton steps": meta.get("Newton steps", ""),
            "Line search": meta.get("Line search", ""),
            "Regularization": meta.get("Regularization", ""),
            "Cases": meta.get("Cases", ""),
        }
        for metric, label in CORE_COMPACT_METRICS:
            metric_row = by_metric.get(metric)
            item[label] = _mean_std(metric_row) if metric_row else ""
        output.append(item)
    return output


def _mean_std(row: dict[str, str] | None) -> str:
    if not row:
        return ""
    if row.get("Case std"):
        return f"{row.get('Case mean', '')} +/- {row.get('Case std', '')}"
    return row.get("Case mean", "")


def _case_parts(name: str) -> tuple[str, str]:
    parts = name.split("_")
    if len(parts) >= 2 and "x" in parts[-1]:
        return "_".join(parts[:-1]), parts[-1]
    return name, ""


def _mesh_size(mesh: str) -> tuple[int, int]:
    if "x" not in mesh:
        return 0, 0
    left, right = mesh.split("x", 1)
    try:
        return int(left), int(right)
    except ValueError:
        return 0, 0


def _as_float(value: str | None) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(value)
    except ValueError:
        return None


def _safe_mean(values: list[float]) -> float | None:
    return mean(values) if values else None


def _safe_median(values: list[float]) -> float | None:
    return median(values) if values else None


def _safe_std(values: list[float]) -> float | None:
    if not values:
        return None
    if len(values) == 1:
        return 0.0
    avg = mean(values)
    return (sum((value - avg) ** 2 for value in values) / (len(values) - 1)) ** 0.5


def _safe_iqr(values: list[float]) -> float | None:
    if not values:
        return None
    if len(values) == 1:
        return 0.0
    ordered = sorted(values)
    return _percentile(ordered, 75.0) - _percentile(ordered, 25.0)


def _percentile(ordered: list[float], percentile: float) -> float:
    if len(ordered) == 1:
        return ordered[0]
    position = (len(ordered) - 1) * percentile / 100.0
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    fraction = position - lower
    return ordered[lower] * (1.0 - fraction) + ordered[upper] * fraction


def _count_positive(values: list[float]) -> int:
    return sum(1 for value in values if value > 0.0)


def _format_float(value: object) -> str:
    if value is None:
        return ""
    try:
        return f"{float(value):.6g}"
    except (TypeError, ValueError):
        return ""


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
        lines.append("| " + " | ".join(_md_cell(row.get(header, "")) for header in headers) + " |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _md_cell(value: str) -> str:
    return str(value).replace("|", "\\|")


if __name__ == "__main__":
    main()
