from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]


CASE_TRAIN_LOAD_PATHS = {
    "strict": "monotonic",
    "curriculum": "monotonic,unload_reload",
    "upper_bound": "monotonic,unload_reload,cyclic,nonproportional,random_amplitude,pre_stress",
}
EVAL_LOAD_PATHS = "monotonic,unload_reload,cyclic,nonproportional,random_amplitude,pre_stress"
SUPPORTED_MESH_KINDS = (
    "structured",
    "jittered",
    "hole",
    "multi_hole",
    "random_holes",
    "notch",
    "crack",
    "crack_tip",
    "stress_concentration",
    "curved",
    "curved_hole",
)

PRIMARY_METRICS = (
    "displacement_relative_l2",
    "history_relative_l2",
    "history_increment_relative_l2",
    "eq_plastic_strain_increment_relative_l2",
    "plastic_work_increment_relative_l2",
    "yield_flag_mae",
    "reversal_history_increment_relative_l2",
    "reversal_yield_flag_mae",
    "predicted_yield_surface_relative_rms",
    "predicted_plastic_work_lower_bound_relative_violation",
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run and aggregate the 5-seed thermo-aware J2 path-OOD evidence suite."
    )
    parser.add_argument("--seeds", type=str, default="20260517,20260518,20260519,20260520,20260521")
    parser.add_argument("--cases", type=str, default="strict,curriculum,upper_bound")
    parser.add_argument("--epochs", type=int, default=50)
    parser.add_argument("--train-samples", type=int, default=32)
    parser.add_argument("--eval-samples", type=int, default=12)
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--eval-batch-size", type=int, default=8)
    parser.add_argument("--hidden-dim", type=int, default=96)
    parser.add_argument("--message-passing-layers", type=int, default=3)
    parser.add_argument("--learning-rate", type=float, default=1.0e-3)
    parser.add_argument("--teacher-forcing-ratio", type=float, default=0.5)
    parser.add_argument(
        "--model-kind",
        choices=("history_gno", "thermo_hard_hgo"),
        default="history_gno",
        help="Use thermo_hard_hgo to enable the differentiable J2 return-mapping layer.",
    )
    parser.add_argument("--nx", type=int, default=3)
    parser.add_argument("--ny", type=int, default=3)
    parser.add_argument(
        "--mesh-kind",
        choices=SUPPORTED_MESH_KINDS,
        default="structured",
    )
    parser.add_argument("--geometry-perturbation", type=float, default=0.0)
    parser.add_argument(
        "--mesh-file",
        type=Path,
        default=None,
        help="Optional external mesh for all J2 path-OOD runs.",
    )
    parser.add_argument(
        "--normalize-external-mesh",
        action=argparse.BooleanOptionalAction,
        default=True,
    )
    parser.add_argument("--load-steps", type=int, default=8)
    parser.add_argument("--max-newton-steps", type=int, default=14)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--force-regenerate", action="store_true")
    parser.add_argument("--aggregate-only", action="store_true")
    parser.add_argument(
        "--verbose-child-output",
        action="store_true",
        help="Stream each single-run JSON payload instead of keeping the suite log compact.",
    )
    parser.add_argument(
        "--data-root",
        type=Path,
        default=PROJECT_ROOT / "05_data_pipeline" / "processed" / "thermo_path_ood_5seed",
    )
    parser.add_argument(
        "--shared-data-root",
        type=Path,
        default=None,
        help=(
            "Reuse one pre-generated data root with load_path/train.npz and load_path/test.npz "
            "for every case/seed. Use this for complex-geometry validation tables."
        ),
    )
    parser.add_argument(
        "--report-dir",
        type=Path,
        default=PROJECT_ROOT / "10_results" / "reports" / "thermo_path_ood_5seed",
    )
    parser.add_argument(
        "--summary-json",
        type=Path,
        default=PROJECT_ROOT / "10_results" / "reports" / "thermo_path_ood_5seed_summary.json",
    )
    parser.add_argument(
        "--summary-csv",
        type=Path,
        default=PROJECT_ROOT / "11_paper" / "tables" / "thermo_path_ood_5seed_summary.csv",
    )
    args = parser.parse_args()

    seeds = _parse_int_list(args.seeds)
    cases = _parse_case_list(args.cases)
    if not args.aggregate_only:
        for case in cases:
            for seed in seeds:
                _run_case_seed(args, case, seed)

    summary = _aggregate(args.report_dir, cases, seeds)
    summary["metadata"]["shared_data_root"] = None if args.shared_data_root is None else str(args.shared_data_root)
    summary["metadata"]["data_root"] = str(args.data_root)
    summary["metadata"]["model_kind"] = args.model_kind
    args.summary_json.parent.mkdir(parents=True, exist_ok=True)
    args.summary_json.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    _write_summary_csv(args.summary_csv, summary)
    print(json.dumps(summary["cyclic_primary"], indent=2))
    print(f"wrote {args.summary_json}")
    print(f"wrote {args.summary_csv}")


def _run_case_seed(args: argparse.Namespace, case: str, seed: int) -> None:
    runner = PROJECT_ROOT / "12_reproducibility" / "scripts" / "run_j2_path_ood_comparison.py"
    data_root = args.shared_data_root if args.shared_data_root is not None else args.data_root / case / f"seed_{seed}"
    out = args.report_dir / f"{case}_seed_{seed}.json"
    if out.exists() and not args.force_regenerate:
        print(f"skip existing {out}")
        return
    command = [
        sys.executable,
        str(runner),
        "--data-root",
        str(data_root),
        "--train-load-paths",
        CASE_TRAIN_LOAD_PATHS[case],
        "--eval-load-paths",
        EVAL_LOAD_PATHS,
        "--history-increment-weight",
        "0.25",
        "--eqp-increment-weight",
        "0.10",
        "--plastic-work-increment-weight",
        "0.10",
        "--yield-flag-weight",
        "0.05",
        "--yield-surface-weight",
        "0.001",
        "--elastic-overstress-weight",
        "0.001",
        "--plastic-work-lower-bound-weight",
        "0.001",
        "--epochs",
        str(args.epochs),
        "--train-samples",
        str(args.train_samples),
        "--eval-samples",
        str(args.eval_samples),
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
        "--teacher-forcing-ratio",
        str(args.teacher_forcing_ratio),
        "--model-kind",
        args.model_kind,
        "--nx",
        str(args.nx),
        "--ny",
        str(args.ny),
        "--mesh-kind",
        args.mesh_kind,
        "--geometry-perturbation",
        str(args.geometry_perturbation),
        "--load-steps",
        str(args.load_steps),
        "--max-newton-steps",
        str(args.max_newton_steps),
        "--seed",
        str(seed),
        "--device",
        args.device,
        "--out",
        str(out),
    ]
    if args.mesh_file is not None:
        command.extend(["--mesh-file", str(args.mesh_file)])
        if not args.normalize_external_mesh:
            command.append("--no-normalize-external-mesh")
    if args.force_regenerate and args.shared_data_root is None:
        command.append("--force-regenerate")
    print(f"running {case} seed={seed}")
    if args.verbose_child_output:
        subprocess.run(command, cwd=PROJECT_ROOT, check=True)
    else:
        completed = subprocess.run(command, cwd=PROJECT_ROOT, text=True, capture_output=True)
        if completed.returncode != 0:
            print(completed.stdout)
            print(completed.stderr, file=sys.stderr)
            completed.check_returncode()
        print(f"completed {case} seed={seed}: {out}")


def _aggregate(report_dir: Path, cases: tuple[str, ...], seeds: tuple[int, ...]) -> dict:
    payloads: dict[str, list[dict]] = {case: [] for case in cases}
    for case in cases:
        for seed in seeds:
            path = report_dir / f"{case}_seed_{seed}.json"
            if not path.exists():
                raise FileNotFoundError(f"missing run artifact: {path}")
            payloads[case].append(json.loads(path.read_text(encoding="utf-8")))

    summary: dict[str, object] = {
        "metadata": {
            "cases": list(cases),
            "seeds": list(seeds),
            "num_seeds": len(seeds),
            "primary_metrics": list(PRIMARY_METRICS),
        },
        "by_case": {},
        "cyclic_primary": {},
    }
    by_case = summary["by_case"]
    cyclic_primary = summary["cyclic_primary"]
    for case, runs in payloads.items():
        load_paths = sorted({load_path for run in runs for load_path in run["evaluations"]})
        case_summary = {}
        for load_path in load_paths:
            metric_names = sorted(
                {metric for run in runs for metric in run["evaluations"].get(load_path, {})}
            )
            case_summary[load_path] = {
                metric: _mean_std(
                    [
                        run["evaluations"][load_path][metric]
                        for run in runs
                        if metric in run["evaluations"].get(load_path, {})
                    ]
                )
                for metric in metric_names
            }
        by_case[case] = case_summary
        cyclic_primary[case] = {
            metric: case_summary["cyclic"][metric]
            for metric in PRIMARY_METRICS
            if metric in case_summary.get("cyclic", {})
        }
    return summary


def _write_summary_csv(path: Path, summary: dict) -> None:
    rows = []
    for case, load_paths in summary["by_case"].items():
        for load_path, metrics in load_paths.items():
            for metric, stats in metrics.items():
                rows.append(
                    {
                        "case": case,
                        "load_path": load_path,
                        "metric": metric,
                        "mean": stats["mean"],
                        "std": stats["std"],
                    }
                )
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["case", "load_path", "metric", "mean", "std"])
        writer.writeheader()
        writer.writerows(rows)


def _mean_std(values: list[float]) -> dict[str, float]:
    if not values:
        return {"mean": float("nan"), "std": float("nan")}
    mean = sum(values) / len(values)
    variance = sum((value - mean) ** 2 for value in values) / len(values)
    return {"mean": mean, "std": variance**0.5}


def _parse_int_list(value: str) -> tuple[int, ...]:
    parsed = tuple(int(item.strip()) for item in value.split(",") if item.strip())
    if not parsed:
        raise argparse.ArgumentTypeError("at least one seed is required")
    return parsed


def _parse_case_list(value: str) -> tuple[str, ...]:
    parsed = tuple(item.strip() for item in value.split(",") if item.strip())
    unknown = sorted(set(parsed).difference(CASE_TRAIN_LOAD_PATHS))
    if unknown:
        raise argparse.ArgumentTypeError(f"unknown cases {unknown}; options are {sorted(CASE_TRAIN_LOAD_PATHS)}")
    if not parsed:
        raise argparse.ArgumentTypeError("at least one case is required")
    return parsed


if __name__ == "__main__":
    main()
