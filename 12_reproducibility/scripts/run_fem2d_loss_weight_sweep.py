from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from itertools import product
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RUNNER = PROJECT_ROOT / "12_reproducibility" / "scripts" / "run_fem2d_baseline_runner.py"
RUNNER_REPORT = PROJECT_ROOT / "10_results" / "reports" / "fem2d_baseline_runner_results.json"
SWEEP_DATA_ROOT = PROJECT_ROOT / "05_data_pipeline" / "processed" / "fem2d_plane_stress_sweeps"
BALANCERS = ("static", "uncertainty", "gradnorm", "softadapt", "residual_adaptive")
CURRICULA = ("constant", "linear", "cosine", "step")


def main() -> None:
    parser = argparse.ArgumentParser(description="Paper-scale PCGNO FEM training-strategy sweep.")
    parser.add_argument("--pde-weights", default="0,1e-5,1e-4")
    parser.add_argument("--boundary-weights", default="0,1e-3,1e-2")
    parser.add_argument("--energy-weights", default="0,1e-7,1e-6")
    parser.add_argument(
        "--balancers",
        default="static,uncertainty,gradnorm,softadapt,residual_adaptive",
        help="Comma-separated subset of static, uncertainty, gradnorm, softadapt, residual_adaptive.",
    )
    parser.add_argument(
        "--include-uncertainty",
        action="store_true",
        help="Backward-compatible alias that ensures uncertainty is included in --balancers.",
    )
    parser.add_argument(
        "--curricula",
        default="constant,linear,cosine",
        help="Comma-separated subset of constant, linear, cosine, step.",
    )
    parser.add_argument("--physics-warmup-epochs", type=int, default=10)
    parser.add_argument("--physics-start-scale", type=float, default=0.0)
    parser.add_argument("--physics-end-scale", type=float, default=1.0)
    parser.add_argument("--gradnorm-penalty-weight", type=float, default=0.1)
    parser.add_argument(
        "--grid-sizes",
        default="9x7,13x9",
        help="Comma-separated grid sizes such as 9x7,13x9.",
    )
    parser.add_argument(
        "--mesh-kind",
        choices=("structured", "jittered", "hole", "notch", "curved"),
        default="structured",
    )
    parser.add_argument("--geometry-perturbation", type=float, default=0.0)
    parser.add_argument(
        "--mesh-file",
        type=Path,
        default=None,
        help="External mesh file (.msh, .inp, .xml, inline .xdmf, or .npz).",
    )
    parser.add_argument(
        "--normalize-external-mesh",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Normalize imported external mesh coordinates to a unit bounding box.",
    )
    parser.add_argument("--train-sample-counts", default="64,128")
    parser.add_argument("--epochs", type=int, default=50)
    parser.add_argument("--eval-samples", type=int, default=24)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--pcgno-data-loss", choices=("mse", "nll"), default="mse")
    parser.add_argument("--pcgno-hidden-dim", type=int, default=96)
    parser.add_argument("--pcgno-latent-dim", type=int, default=16)
    parser.add_argument("--pcgno-fourier-modes", type=int, default=8)
    parser.add_argument("--seed", type=int, default=20260516)
    parser.add_argument("--num-seeds", type=int, default=5)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--force-regenerate", action="store_true")
    parser.add_argument(
        "--max-configs",
        type=int,
        default=None,
        help="Optional cap for smoke tests or quick triage.",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=PROJECT_ROOT / "10_results" / "reports" / "fem2d_loss_weight_sweep_results.json",
    )
    args = parser.parse_args()

    configs = _build_configs(args)
    if args.max_configs is not None:
        configs = configs[: args.max_configs]

    results = []
    regenerated_data_dirs: set[Path] = set()
    for index, config in enumerate(configs):
        print(f"[{index + 1}/{len(configs)}] {config['name']}")
        data_dir = Path(config["data_dir"])
        force_regenerate = args.force_regenerate and data_dir not in regenerated_data_dirs
        _run_config(args, config, force_regenerate=force_regenerate)
        regenerated_data_dirs.add(data_dir)
        report = json.loads(RUNNER_REPORT.read_text(encoding="utf-8"))
        summary = report["pcgno"]["summary"]
        row = {
            **config,
            "objective": _objective(summary),
            "summary": summary,
        }
        results.append(row)

    ranked = sorted(results, key=lambda item: item["objective"])
    args.out.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "metadata": {
            "epochs": args.epochs,
            "num_seeds": args.num_seeds,
            "eval_samples": args.eval_samples,
            "batch_size": args.batch_size,
            "seed": args.seed,
            "device": args.device,
            "pcgno_data_loss": args.pcgno_data_loss,
            "pcgno_hidden_dim": args.pcgno_hidden_dim,
            "pcgno_latent_dim": args.pcgno_latent_dim,
            "pcgno_fourier_modes": args.pcgno_fourier_modes,
        },
        "ranked": ranked,
    }
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    _write_csv(args.out.with_suffix(".csv"), ranked)
    print(f"wrote {args.out}")
    print(f"wrote {args.out.with_suffix('.csv')}")
    print("best:", ranked[0]["name"], "objective=", ranked[0]["objective"])


def _build_configs(args: argparse.Namespace) -> list[dict]:
    balancers = _parse_names(args.balancers, BALANCERS)
    if args.include_uncertainty and "uncertainty" not in balancers:
        balancers.append("uncertainty")
    curricula = _parse_names(args.curricula, CURRICULA)
    grids = _parse_grid_sizes(args.grid_sizes)
    train_counts = _parse_ints(args.train_sample_counts)

    configs = []
    for nx, ny in grids:
        for train_samples in train_counts:
            data_dir = _data_dir(args, nx, ny, train_samples)
            for curriculum in curricula:
                if "static" in balancers:
                    configs.extend(_static_configs(args, nx, ny, train_samples, data_dir, curriculum))
                for balancer in balancers:
                    if balancer == "static":
                        continue
                    configs.append(
                        {
                            "name": (
                                f"{balancer}_grid={nx}x{ny}_n={train_samples}_"
                                f"curriculum={curriculum}"
                            ),
                            "loss_balancer": balancer,
                            "pde_weight": 0.0,
                            "boundary_weight": 0.0,
                            "energy_weight": 0.0,
                            "nx": nx,
                            "ny": ny,
                            "train_samples": train_samples,
                            "eval_samples": args.eval_samples,
                            "data_dir": str(data_dir),
                            "physics_curriculum": curriculum,
                        }
                    )
    return configs


def _static_configs(
    args: argparse.Namespace,
    nx: int,
    ny: int,
    train_samples: int,
    data_dir: Path,
    curriculum: str,
) -> list[dict]:
    pde_weights = _parse_floats(args.pde_weights)
    boundary_weights = _parse_floats(args.boundary_weights)
    energy_weights = _parse_floats(args.energy_weights)
    configs = []
    for pde, boundary, energy in product(pde_weights, boundary_weights, energy_weights):
        configs.append(
            {
                "name": (
                    f"static_pde={pde:g}_bc={boundary:g}_energy={energy:g}_"
                    f"grid={nx}x{ny}_n={train_samples}_curriculum={curriculum}"
                ),
                "loss_balancer": "static",
                "pde_weight": pde,
                "boundary_weight": boundary,
                "energy_weight": energy,
                "nx": nx,
                "ny": ny,
                "train_samples": train_samples,
                "eval_samples": args.eval_samples,
                "data_dir": str(data_dir),
                "physics_curriculum": curriculum,
            }
        )
    return configs


def _run_config(args: argparse.Namespace, config: dict, force_regenerate: bool) -> None:
    command = [
        sys.executable,
        str(RUNNER),
        "--model",
        "pcgno",
        "--data-dir",
        str(config["data_dir"]),
        "--epochs",
        str(args.epochs),
        "--train-samples",
        str(config["train_samples"]),
        "--eval-samples",
        str(config["eval_samples"]),
        "--batch-size",
        str(args.batch_size),
        "--nx",
        str(config["nx"]),
        "--ny",
        str(config["ny"]),
        "--mesh-kind",
        args.mesh_kind,
        "--geometry-perturbation",
        str(args.geometry_perturbation),
        "--seed",
        str(args.seed),
        "--num-seeds",
        str(args.num_seeds),
        "--device",
        args.device,
        "--loss-balancer",
        config["loss_balancer"],
        "--pcgno-data-loss",
        args.pcgno_data_loss,
        "--pcgno-hidden-dim",
        str(args.pcgno_hidden_dim),
        "--pcgno-latent-dim",
        str(args.pcgno_latent_dim),
        "--pcgno-fourier-modes",
        str(args.pcgno_fourier_modes),
        "--pde-weight",
        str(config["pde_weight"]),
        "--boundary-weight",
        str(config["boundary_weight"]),
        "--energy-weight",
        str(config["energy_weight"]),
        "--physics-curriculum",
        config["physics_curriculum"],
        "--physics-warmup-epochs",
        str(args.physics_warmup_epochs),
        "--physics-start-scale",
        str(args.physics_start_scale),
        "--physics-end-scale",
        str(args.physics_end_scale),
        "--gradnorm-penalty-weight",
        str(args.gradnorm_penalty_weight),
    ]
    if args.mesh_file is not None:
        command.extend(["--mesh-file", str(args.mesh_file)])
    if not args.normalize_external_mesh:
        command.append("--no-normalize-external-mesh")
    if force_regenerate:
        command.append("--force-regenerate")
    subprocess.run(command, cwd=PROJECT_ROOT, check=True)


def _objective(summary: dict) -> float:
    """Small scalar ranking objective for sweep triage.

    This is not the final paper metric. It combines ID/OOD error, FEM equilibrium residual,
    boundary violation, and energy consistency so poor physics cannot hide behind low data error.
    """

    test = summary["test"]
    ood_material = summary["ood_material"]
    ood_loading = summary["ood_loading"]
    return (
        test["relative_l2"]["mean"]
        + 0.25 * ood_material["relative_l2"]["mean"]
        + 0.50 * ood_loading["relative_l2"]["mean"]
        + 0.25 * test["pde_residual_relative"]["mean"]
        + 0.25 * test["boundary_relative"]["mean"]
        + 0.10 * test["energy_error_relative"]["mean"]
    )


def _write_csv(path: Path, ranked: list[dict]) -> None:
    fields = [
        "rank",
        "name",
        "nx",
        "ny",
        "train_samples",
        "eval_samples",
        "physics_curriculum",
        "loss_balancer",
        "pde_weight",
        "boundary_weight",
        "energy_weight",
        "objective",
        "test_relative_l2",
        "test_pde_residual_relative",
        "test_boundary_relative",
        "test_energy_error_relative",
        "test_crps",
        "test_sharpness",
        "test_interval_width_95",
        "test_gaussian_nll",
        "ood_material_relative_l2",
        "ood_loading_relative_l2",
        "ood_material_sharpness_ratio",
        "ood_loading_sharpness_ratio",
        "w_data",
        "w_pde_residual",
        "w_boundary",
        "w_energy",
        "w_calibration",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for rank, item in enumerate(ranked, start=1):
            summary = item["summary"]
            writer.writerow(
                {
                    "rank": rank,
                    "name": item["name"],
                    "nx": item["nx"],
                    "ny": item["ny"],
                    "train_samples": item["train_samples"],
                    "eval_samples": item["eval_samples"],
                    "physics_curriculum": item["physics_curriculum"],
                    "loss_balancer": item["loss_balancer"],
                    "pde_weight": item["pde_weight"],
                    "boundary_weight": item["boundary_weight"],
                    "energy_weight": item["energy_weight"],
                    "objective": item["objective"],
                    "test_relative_l2": summary["test"]["relative_l2"]["mean"],
                    "test_pde_residual_relative": summary["test"]["pde_residual_relative"]["mean"],
                    "test_boundary_relative": summary["test"]["boundary_relative"]["mean"],
                    "test_energy_error_relative": summary["test"]["energy_error_relative"]["mean"],
                    "test_crps": _metric(summary, "test", "crps"),
                    "test_sharpness": _metric(summary, "test", "sharpness"),
                    "test_interval_width_95": _metric(summary, "test", "interval_width_95"),
                    "test_gaussian_nll": _metric(summary, "test", "gaussian_nll"),
                    "ood_material_relative_l2": summary["ood_material"]["relative_l2"]["mean"],
                    "ood_loading_relative_l2": summary["ood_loading"]["relative_l2"]["mean"],
                    "ood_material_sharpness_ratio": _separation_metric(
                        summary, "ood_material_sharpness_ratio"
                    ),
                    "ood_loading_sharpness_ratio": _separation_metric(
                        summary, "ood_loading_sharpness_ratio"
                    ),
                    "w_data": _loss_balancer_weight(summary, "data"),
                    "w_pde_residual": _loss_balancer_weight(summary, "pde_residual"),
                    "w_boundary": _loss_balancer_weight(summary, "boundary"),
                    "w_energy": _loss_balancer_weight(summary, "energy"),
                    "w_calibration": _loss_balancer_weight(summary, "calibration"),
                }
            )


def _data_dir(args: argparse.Namespace, nx: int, ny: int, train_samples: int) -> Path:
    if args.mesh_file is not None:
        mesh_tag = f"external_{args.mesh_file.stem}"
        return SWEEP_DATA_ROOT / f"{mesh_tag}_train{train_samples}_eval{args.eval_samples}"
    perturb = int(round(args.geometry_perturbation * 1000))
    return (
        SWEEP_DATA_ROOT
        / f"{args.mesh_kind}_p{perturb}_nx{nx}_ny{ny}_train{train_samples}_eval{args.eval_samples}"
    )


def _parse_floats(text: str) -> list[float]:
    return [float(part.strip()) for part in text.split(",") if part.strip()]


def _parse_ints(text: str) -> list[int]:
    return [int(part.strip()) for part in text.split(",") if part.strip()]


def _parse_names(text: str, choices: tuple[str, ...]) -> list[str]:
    names = [part.strip().lower() for part in text.split(",") if part.strip()]
    unknown = sorted(set(names) - set(choices))
    if unknown:
        raise ValueError(f"unknown values {unknown}; choices are {choices}")
    return names


def _parse_grid_sizes(text: str) -> list[tuple[int, int]]:
    grids = []
    for part in text.split(","):
        value = part.strip().lower()
        if not value:
            continue
        pieces = value.split("x")
        if len(pieces) != 2:
            raise ValueError(f"grid size must look like 9x7, got {part!r}")
        grids.append((int(pieces[0]), int(pieces[1])))
    return grids


def _loss_balancer_weight(summary: dict, key: str) -> float | str:
    weights = summary.get("loss_balancer_weights", {})
    if key not in weights:
        return ""
    return weights[key]["mean"]


def _metric(summary: dict, split: str, key: str) -> float | str:
    if key not in summary.get(split, {}):
        return ""
    return summary[split][key]["mean"]


def _separation_metric(summary: dict, key: str) -> float | str:
    separation = summary.get("ood_uncertainty_separation", {})
    if key not in separation:
        return ""
    return separation[key]["mean"]


if __name__ == "__main__":
    main()
