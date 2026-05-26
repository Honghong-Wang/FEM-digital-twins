from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class StageSpec:
    name: str
    claim: str
    command: list[str]
    artifacts: list[str]
    acceptance_criteria: list[str]


@dataclass
class StageResult:
    name: str
    status: str
    returncode: int | None
    artifacts: list[str]
    stdout_tail: str = ""
    stderr_tail: str = ""


SMOKE_SETTINGS = {
    "operator_model": "pcgno",
    "operator_epochs": 1,
    "operator_train_samples": 4,
    "operator_eval_samples": 2,
    "operator_batch_size": 2,
    "operator_grid": "4x3",
    "operator_num_seeds": 1,
    "operator_pcgno_data_loss": "mse",
    "operator_pcgno_hidden_dim": 96,
    "operator_pcgno_latent_dim": 16,
    "operator_pcgno_fourier_modes": 8,
    "path_epochs": 1,
    "path_train_samples": 1,
    "path_eval_samples": 1,
    "path_batch_size": 1,
    "path_eval_batch_size": 1,
    "path_hidden_dim": 12,
    "path_message_passing_layers": 1,
    "path_load_steps": 4,
    "path_max_newton_steps": 8,
    "path_history_increment_weight": 0.0,
    "path_eqp_increment_weight": 0.0,
    "path_plastic_work_increment_weight": 0.0,
    "path_yield_flag_weight": 0.0,
}

PAPER_SETTINGS = {
    "operator_model": "all",
    "operator_epochs": 50,
    "operator_train_samples": 64,
    "operator_eval_samples": 24,
    "operator_batch_size": 8,
    "operator_grid": "9x7",
    "operator_num_seeds": 5,
    "operator_pcgno_data_loss": "mse",
    "operator_pcgno_hidden_dim": 96,
    "operator_pcgno_latent_dim": 16,
    "operator_pcgno_fourier_modes": 8,
    "path_epochs": 50,
    "path_train_samples": 32,
    "path_eval_samples": 12,
    "path_batch_size": 4,
    "path_eval_batch_size": 8,
    "path_hidden_dim": 96,
    "path_message_passing_layers": 3,
    "path_load_steps": 8,
    "path_max_newton_steps": 14,
    "path_history_increment_weight": 0.25,
    "path_eqp_increment_weight": 0.10,
    "path_plastic_work_increment_weight": 0.10,
    "path_yield_flag_weight": 0.05,
}


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Run the staged evidence ladder for two claims: "
            "surrogate -> operator + FEM evidence, and static operator -> stateful path-dependent operator."
        )
    )
    parser.add_argument("--preset", choices=("smoke", "paper"), default="smoke")
    parser.add_argument(
        "--track",
        choices=("all", "operator_fem", "stateful_path"),
        default="all",
        help="Which research track to materialize.",
    )
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--seed", type=int, default=20260517)
    parser.add_argument("--force-regenerate", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--python-executable", default=sys.executable)
    parser.add_argument(
        "--out",
        type=Path,
        default=PROJECT_ROOT / "10_results" / "reports" / "research_landing_ladder.json",
    )
    args = parser.parse_args()

    settings = dict(PAPER_SETTINGS if args.preset == "paper" else SMOKE_SETTINGS)
    stages = _build_stages(args, settings)
    results = _run_stages(stages, args) if not args.dry_run else [_dry_result(stage) for stage in stages]
    payload = {
        "metadata": {
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
            "preset": args.preset,
            "track": args.track,
            "device": args.device,
            "seed": args.seed,
            "dry_run": args.dry_run,
        },
        "research_ladder": [
            {
                "level": 1,
                "claim": "from surrogate to parameterized solution operator with FEM evidence",
                "evidence": [
                    "unified coords/params/fields/forcing protocol",
                    "FEM snapshots with residual, boundary, and energy callbacks",
                    "fair baseline comparison against PINN, DeepONet, FNO, graph operators, and PCGNO",
                ],
            },
            {
                "level": 2,
                "claim": "from static operator to stateful path-dependent history operator",
                "evidence": [
                    "J2 plasticity path sequences with material history variables",
                    "recurrent graph operator advancing history_t to history_t+1",
                    "path-OOD evaluation: monotonic training, unload-reload/cyclic/nonproportional testing",
                ],
            },
        ],
        "stages": [asdict(stage) for stage in stages],
        "results": [asdict(result) for result in results],
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps({"results": [asdict(result) for result in results]}, indent=2))
    print(f"wrote {args.out}")

    failed = [result for result in results if result.status == "failed"]
    if failed:
        raise SystemExit(1)


def _build_stages(args: argparse.Namespace, settings: dict[str, object]) -> list[StageSpec]:
    stages = []
    if args.track in {"all", "operator_fem"}:
        stages.append(_operator_fem_stage(args, settings))
    if args.track in {"all", "stateful_path"}:
        stages.append(_stateful_path_stage(args, settings))
    return stages


def _operator_fem_stage(args: argparse.Namespace, settings: dict[str, object]) -> StageSpec:
    nx, ny = _parse_grid(str(settings["operator_grid"]))
    data_dir = PROJECT_ROOT / "05_data_pipeline" / "processed" / f"fem2d_operator_evidence_{args.preset}"
    out = PROJECT_ROOT / "10_results" / "reports" / f"fem2d_operator_evidence_{args.preset}.json"
    command = [
        args.python_executable,
        str(PROJECT_ROOT / "12_reproducibility" / "scripts" / "run_fem2d_baseline_runner.py"),
        "--model",
        str(settings["operator_model"]),
        "--data-dir",
        str(data_dir),
        "--epochs",
        str(settings["operator_epochs"]),
        "--train-samples",
        str(settings["operator_train_samples"]),
        "--eval-samples",
        str(settings["operator_eval_samples"]),
        "--batch-size",
        str(settings["operator_batch_size"]),
        "--nx",
        str(nx),
        "--ny",
        str(ny),
        "--num-seeds",
        str(settings["operator_num_seeds"]),
        "--pcgno-data-loss",
        str(settings["operator_pcgno_data_loss"]),
        "--pcgno-hidden-dim",
        str(settings["operator_pcgno_hidden_dim"]),
        "--pcgno-latent-dim",
        str(settings["operator_pcgno_latent_dim"]),
        "--pcgno-fourier-modes",
        str(settings["operator_pcgno_fourier_modes"]),
        "--seed",
        str(args.seed),
        "--device",
        args.device,
        "--out",
        str(out),
    ]
    if args.force_regenerate:
        command.append("--force-regenerate")
    return StageSpec(
        name="operator_fem_evidence",
        claim="replace case-specific surrogates with a parameterized FEM-backed solution-operator benchmark",
        command=command,
        artifacts=[str(out), str(data_dir)],
        acceptance_criteria=[
            "same train/test/OOD splits and seeds are used across model families",
            "report includes field error, FEM residual, boundary violation, and energy consistency",
            "PCGNO is evaluated through FEMProblemAdapter physics callbacks, not only data MSE",
        ],
    )


def _stateful_path_stage(args: argparse.Namespace, settings: dict[str, object]) -> StageSpec:
    data_root = PROJECT_ROOT / "05_data_pipeline" / "processed" / f"j2_path_operator_evidence_{args.preset}"
    out = PROJECT_ROOT / "10_results" / "reports" / f"j2_path_operator_evidence_{args.preset}.json"
    command = [
        args.python_executable,
        str(PROJECT_ROOT / "12_reproducibility" / "scripts" / "run_j2_path_ood_comparison.py"),
        "--data-root",
        str(data_root),
        "--epochs",
        str(settings["path_epochs"]),
        "--train-samples",
        str(settings["path_train_samples"]),
        "--eval-samples",
        str(settings["path_eval_samples"]),
        "--batch-size",
        str(settings["path_batch_size"]),
        "--eval-batch-size",
        str(settings["path_eval_batch_size"]),
        "--hidden-dim",
        str(settings["path_hidden_dim"]),
        "--message-passing-layers",
        str(settings["path_message_passing_layers"]),
        "--load-steps",
        str(settings["path_load_steps"]),
        "--max-newton-steps",
        str(settings["path_max_newton_steps"]),
        "--history-increment-weight",
        str(settings["path_history_increment_weight"]),
        "--eqp-increment-weight",
        str(settings["path_eqp_increment_weight"]),
        "--plastic-work-increment-weight",
        str(settings["path_plastic_work_increment_weight"]),
        "--yield-flag-weight",
        str(settings["path_yield_flag_weight"]),
        "--eval-load-paths",
        "monotonic,unload_reload,cyclic,nonproportional",
        "--seed",
        str(args.seed),
        "--device",
        args.device,
        "--out",
        str(out),
    ]
    if args.force_regenerate:
        command.append("--force-regenerate")
    return StageSpec(
        name="stateful_path_operator",
        claim="replace static operators with a recurrent history operator that advances plastic internal variables",
        command=command,
        artifacts=[str(out), str(out.with_suffix(".csv")), str(data_root)],
        acceptance_criteria=[
            "training load path is monotonic only",
            "test load paths include unload-reload, cyclic, and nonproportional trajectories",
            "report includes history, history-increment, plastic work, plastic strain, yield-flag, and degradation metrics",
        ],
    )


def _run_stages(stages: list[StageSpec], args: argparse.Namespace) -> list[StageResult]:
    results = []
    for stage in stages:
        completed = subprocess.run(
            stage.command,
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
        )
        status = "completed" if completed.returncode == 0 else "failed"
        results.append(
            StageResult(
                name=stage.name,
                status=status,
                returncode=completed.returncode,
                artifacts=stage.artifacts,
                stdout_tail=_tail(completed.stdout),
                stderr_tail=_tail(completed.stderr),
            )
        )
        if completed.returncode != 0:
            break
    return results


def _dry_result(stage: StageSpec) -> StageResult:
    return StageResult(
        name=stage.name,
        status="planned",
        returncode=None,
        artifacts=stage.artifacts,
    )


def _parse_grid(value: str) -> tuple[int, int]:
    parts = value.lower().split("x")
    if len(parts) != 2:
        raise ValueError("grid must use NxM format, for example 9x7")
    return int(parts[0]), int(parts[1])


def _tail(text: str, max_chars: int = 4000) -> str:
    if len(text) <= max_chars:
        return text
    return text[-max_chars:]


if __name__ == "__main__":
    main()
