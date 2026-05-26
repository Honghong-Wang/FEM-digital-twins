from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
BASELINE_SCRIPT = PROJECT_ROOT / "12_reproducibility" / "scripts" / "run_j2_path_dependent_baseline_table.py"


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Run the Level-4 complex-geometry J2 path-OOD evidence suite case by case. "
            "Each geometry-mesh case has its own shared nodes/connectivity, so this wrapper "
            "keeps the split/seed/epoch/model protocol fixed while avoiding invalid tensor "
            "concatenation across different meshes."
        )
    )
    parser.add_argument(
        "--data-root",
        type=Path,
        default=PROJECT_ROOT / "05_data_pipeline" / "processed" / "level4_formal_complex_j2_t6",
    )
    parser.add_argument(
        "--cases",
        type=str,
        default="all",
        help="Comma-separated case directories, or 'all' to scan directories under data-root.",
    )
    parser.add_argument(
        "--models",
        type=str,
        default="hgo_thermo,hgo_thermo_hard,hgo_data,hano,incde,tinn,static_gno_sequence,static_deeponet_sequence",
        help="Models passed to run_j2_path_dependent_baseline_table.py. Static FNO is omitted by default for cutout meshes.",
    )
    parser.add_argument(
        "--seeds",
        type=str,
        default="20260517,20260518,20260519,20260520,20260521",
    )
    parser.add_argument("--epochs", type=int, default=50)
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--eval-batch-size", type=int, default=4)
    parser.add_argument("--hidden-dim", type=int, default=96)
    parser.add_argument("--message-passing-layers", type=int, default=3)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--fem-audit-loss-weight", type=float, default=0.0)
    parser.add_argument("--fem-audit-energy-weight", type=float, default=0.0)
    parser.add_argument("--fem-audit-every-step", action="store_true")
    parser.add_argument(
        "--fem-audit-step-policy",
        choices=("final", "all", "reversal", "reversal_final"),
        default="final",
    )
    parser.add_argument("--fem-audit-metrics", action="store_true")
    parser.add_argument("--fem-audit-models", type=str, default="hgo_thermo_hard,tinn")
    parser.add_argument(
        "--protocols",
        type=str,
        default="strict,curriculum,upper_bound",
        help=(
            "strict trains on monotonic; curriculum trains on monotonic+unload_reload; "
            "upper_bound trains on monotonic+unload_reload+cyclic+nonproportional."
        ),
    )
    parser.add_argument(
        "--eval-load-paths",
        type=str,
        default="monotonic,unload_reload,cyclic,nonproportional",
        help="Comma-separated load paths to evaluate for every case/protocol.",
    )
    parser.add_argument(
        "--out-root",
        type=Path,
        default=PROJECT_ROOT / "10_results" / "reports" / "level4_complex_formal_suite",
    )
    parser.add_argument("--force", action="store_true", help="Re-run a case/protocol even if summary.json exists.")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    cases = _resolve_cases(args.data_root, args.cases)
    protocols = _parse_protocols(args.protocols)
    rows = []
    for case in cases:
        for protocol_name, train_paths in protocols.items():
            out_dir = args.out_root / case.name / protocol_name
            command = _baseline_command(case, protocol_name, train_paths, out_dir, args)
            if args.dry_run:
                print(" ".join(command))
                continue
            summary_path = out_dir / "summary.json"
            if summary_path.exists() and not args.force:
                print(f"[skip] {case.name}/{protocol_name}: {summary_path} exists")
                rows.extend(_summary_rows(case.name, protocol_name, summary_path))
                continue
            out_dir.mkdir(parents=True, exist_ok=True)
            subprocess.run(command, check=True, cwd=PROJECT_ROOT)
            rows.extend(_summary_rows(case.name, protocol_name, summary_path))
    if not args.dry_run:
        _write_rows(args.out_root / "level4_complex_formal_suite_summary.csv", rows)
        _write_markdown(args.out_root / "level4_complex_formal_suite_summary.md", rows)
        print(f"wrote {args.out_root / 'level4_complex_formal_suite_summary.csv'}")
        print(f"wrote {args.out_root / 'level4_complex_formal_suite_summary.md'}")


def _resolve_cases(data_root: Path, value: str) -> list[Path]:
    if value.strip().lower() == "all":
        cases = sorted(path for path in data_root.iterdir() if path.is_dir())
    else:
        cases = [data_root / item.strip() for item in value.split(",") if item.strip()]
    missing = [str(case) for case in cases if not case.exists()]
    if missing:
        raise FileNotFoundError(f"missing Level-4 case directories: {missing}")
    return cases


def _parse_protocols(value: str) -> dict[str, str]:
    supported = {
        "strict": "monotonic",
        "curriculum": "monotonic,unload_reload",
        "upper_bound": "monotonic,unload_reload,cyclic,nonproportional",
    }
    protocols = {}
    for name in (item.strip() for item in value.split(",") if item.strip()):
        if name not in supported:
            raise argparse.ArgumentTypeError(f"unknown protocol {name!r}; options are {sorted(supported)}")
        protocols[name] = supported[name]
    if not protocols:
        raise argparse.ArgumentTypeError("at least one protocol is required")
    return protocols


def _baseline_command(
    case: Path,
    protocol_name: str,
    train_paths: str,
    out_dir: Path,
    args: argparse.Namespace,
) -> list[str]:
    del protocol_name
    command = [
        sys.executable,
        str(BASELINE_SCRIPT),
        "--data-root",
        str(case),
        "--models",
        args.models,
        "--train-load-paths",
        train_paths,
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
        "--device",
        args.device,
        "--fem-audit-loss-weight",
        str(args.fem_audit_loss_weight),
        "--fem-audit-energy-weight",
        str(args.fem_audit_energy_weight),
        "--fem-audit-models",
        args.fem_audit_models,
        "--fem-audit-step-policy",
        args.fem_audit_step_policy,
        "--out",
        str(out_dir / "summary.json"),
        "--csv-out",
        str(out_dir / "table.csv"),
        "--md-out",
        str(out_dir / "table.md"),
        "--robust-csv-out",
        str(out_dir / "robust.csv"),
        "--robust-md-out",
        str(out_dir / "robust.md"),
        "--per-seed-csv-out",
        str(out_dir / "per_seed.csv"),
        "--per-seed-md-out",
        str(out_dir / "per_seed.md"),
        "--outlier-csv-out",
        str(out_dir / "outliers.csv"),
        "--outlier-md-out",
        str(out_dir / "outliers.md"),
    ]
    if args.fem_audit_every_step:
        command.append("--fem-audit-every-step")
    if args.fem_audit_metrics:
        command.append("--fem-audit-metrics")
    return command


def _summary_rows(case_name: str, protocol_name: str, summary_path: Path) -> list[dict[str, str]]:
    payload = json.loads(summary_path.read_text(encoding="utf-8"))
    rows = []
    for model_name, result in payload["results"].items():
        cyclic = result["summary"].get("cyclic_primary", {})
        rows.append(
            {
                "Case": case_name,
                "Protocol": protocol_name,
                "Model": model_name,
                "Seeds": str(result["summary"]["num_seeds"]),
                "Cyclic disp rel L2": _format_stat(cyclic.get("displacement_relative_l2")),
                "Cyclic history rel L2": _format_stat(cyclic.get("history_relative_l2")),
                "Reversal hist-inc rel L2": _format_stat(cyclic.get("reversal_history_increment_relative_l2")),
                "Yield-surface RMS": _format_stat(cyclic.get("predicted_yield_surface_relative_rms")),
                "Plastic-work violation target-norm": _format_stat(
                    cyclic.get("predicted_plastic_work_lower_bound_target_normalized_violation")
                ),
                "FEM residual rel RMS": _format_stat(cyclic.get("fem_residual_relative_rms")),
                "FEM energy rel err": _format_stat(cyclic.get("fem_energy_relative_error")),
            }
        )
    return rows


def _format_stat(stats: dict | None) -> str:
    if not stats:
        return ""
    return f"{stats['mean']:.4g} +/- {stats['std']:.4g}"


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
    if not rows:
        path.write_text("No completed Level-4 formal runs.\n", encoding="utf-8")
        return
    headers = list(rows[0])
    lines = [
        "# Level-4 Complex J2 Formal Suite Summary",
        "",
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---", *["---:" for _ in headers[1:]]]) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(row.get(header, "") for header in headers) + " |")
    lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
