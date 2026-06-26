"""Medium-difficulty public example for path-dependent FEM digital twins.

This script is intentionally self-contained and smaller than the full research
implementation under ``src/pcgno_dt``. It demonstrates the public-facing
workflow:

1. load a small J2 finite-element path dataset;
2. fit a simple stateful rollout baseline on monotonic paths;
3. compare it with a static baseline on path-OOD loading paths;
4. report field, history, linearized FEM residual, energy, and plastic-work
   diagnostics.

The model here is a small ridge-regression transition model, not the full
HistoryGraphOperator. Its purpose is to show the data interface and audit logic
with a fast, inspectable baseline.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, Tuple

import matplotlib.pyplot as plt
import numpy as np


EPS = 1.0e-12


@dataclass
class PathDataset:
    name: str
    coords: np.ndarray
    params: np.ndarray
    fields_sequence: np.ndarray
    forcing_sequence: np.ndarray
    material_history_sequence: np.ndarray
    tangent_stiffness_sequence: np.ndarray
    newton_residual_sequence: np.ndarray
    reference_energy_sequence: np.ndarray
    load_factors: np.ndarray


def load_path_dataset(path: Path, name: str) -> PathDataset:
    data = np.load(path, allow_pickle=True)
    return PathDataset(
        name=name,
        coords=np.asarray(data["coords"], dtype=float),
        params=np.asarray(data["params"], dtype=float),
        fields_sequence=np.asarray(data["fields_sequence"], dtype=float),
        forcing_sequence=np.asarray(data["forcing_sequence"], dtype=float),
        material_history_sequence=np.asarray(data["material_history_sequence"], dtype=float),
        tangent_stiffness_sequence=np.asarray(data["tangent_stiffness_sequence"], dtype=float),
        newton_residual_sequence=np.asarray(data["newton_residual_sequence"], dtype=float),
        reference_energy_sequence=np.asarray(data["reference_energy_sequence"], dtype=float),
        load_factors=np.asarray(data["load_factors"], dtype=float),
    )


def flatten_state(u: np.ndarray, h: np.ndarray, f_next: np.ndarray, p: np.ndarray) -> np.ndarray:
    return np.concatenate([u.ravel(), h.ravel(), f_next.ravel(), p.ravel()])


def flatten_static(f_next: np.ndarray, p: np.ndarray) -> np.ndarray:
    return np.concatenate([f_next.ravel(), p.ravel()])


def build_transition_system(dataset: PathDataset, stateful: bool) -> Tuple[np.ndarray, np.ndarray]:
    u = dataset.fields_sequence
    h = dataset.material_history_sequence
    f = dataset.forcing_sequence
    p = dataset.params
    x_rows = []
    y_rows = []
    n_samples, n_steps = u.shape[:2]
    for s in range(n_samples):
        for t in range(n_steps - 1):
            if stateful:
                x_rows.append(flatten_state(u[s, t], h[s, t], f[s, t + 1], p[s]))
            else:
                x_rows.append(flatten_static(f[s, t + 1], p[s]))
            du = (u[s, t + 1] - u[s, t]).ravel()
            dh = (h[s, t + 1] - h[s, t]).ravel()
            y_rows.append(np.concatenate([du, dh]))
    return np.vstack(x_rows), np.vstack(y_rows)


def fit_ridge_transition(x: np.ndarray, y: np.ndarray, ridge: float) -> np.ndarray:
    x_aug = np.hstack([x, np.ones((x.shape[0], 1))])
    gram = x_aug.T @ x_aug
    penalty = ridge * np.eye(gram.shape[0])
    penalty[-1, -1] = 0.0
    return np.linalg.solve(gram + penalty, x_aug.T @ y)


def predict_transition(weights: np.ndarray, x: np.ndarray) -> np.ndarray:
    x_aug = np.concatenate([x, np.ones(1)])
    return x_aug @ weights


def rollout(dataset: PathDataset, weights: np.ndarray, stateful: bool) -> Tuple[np.ndarray, np.ndarray]:
    u_true = dataset.fields_sequence
    h_true = dataset.material_history_sequence
    f = dataset.forcing_sequence
    p = dataset.params
    n_samples, n_steps, n_nodes, n_dim = u_true.shape
    _, _, n_cells, n_hist = h_true.shape

    u_pred = np.zeros_like(u_true)
    h_pred = np.zeros_like(h_true)
    u_pred[:, 0] = u_true[:, 0]
    h_pred[:, 0] = h_true[:, 0]

    split = n_nodes * n_dim
    for s in range(n_samples):
        for t in range(n_steps - 1):
            if stateful:
                x = flatten_state(u_pred[s, t], h_pred[s, t], f[s, t + 1], p[s])
            else:
                x = flatten_static(f[s, t + 1], p[s])
            delta = predict_transition(weights, x)
            u_pred[s, t + 1] = u_pred[s, t] + delta[:split].reshape(n_nodes, n_dim)
            h_pred[s, t + 1] = h_pred[s, t] + delta[split:].reshape(n_cells, n_hist)
    return u_pred, h_pred


def relative_l2(pred: np.ndarray, true: np.ndarray) -> float:
    return float(np.linalg.norm(pred - true) / (np.linalg.norm(true) + EPS))


def linearized_residual_and_energy(dataset: PathDataset, u_pred: np.ndarray) -> Tuple[float, float]:
    u_true = dataset.fields_sequence
    k_seq = dataset.tangent_stiffness_sequence
    r_true = dataset.newton_residual_sequence.reshape(u_true.shape[0], u_true.shape[1], -1)
    residual_norms = []
    energy_terms = []
    for s in range(u_true.shape[0]):
        for t in range(1, u_true.shape[1]):
            err = (u_pred[s, t] - u_true[s, t]).ravel()
            k_t = k_seq[s, t]
            residual_proxy = r_true[s, t] + k_t @ err
            residual_norms.append(np.linalg.norm(residual_proxy) / (np.linalg.norm(r_true[s, t]) + EPS))
            energy_terms.append(abs(0.5 * float(err @ k_t @ err)))
    return float(np.mean(residual_norms)), float(np.mean(energy_terms))


def plastic_work_violation(h_pred: np.ndarray, h_true: np.ndarray) -> float:
    # Channel convention used by the public J2 data: channel 1 stores plastic work.
    pred_inc = np.diff(h_pred[..., 1], axis=1)
    true_inc = np.diff(h_true[..., 1], axis=1)
    negative_part = np.maximum(-pred_inc, 0.0)
    return float(np.sum(negative_part) / (np.sum(np.abs(true_inc)) + EPS))


def yield_flag_mae(h_pred: np.ndarray, h_true: np.ndarray) -> float:
    # Channel convention used by the public J2 data: channel 3 stores yield activity.
    return float(np.mean(np.abs(h_pred[..., 3] - h_true[..., 3])))


def evaluate_rollout(dataset: PathDataset, u_pred: np.ndarray, h_pred: np.ndarray) -> Dict[str, float]:
    h_true = dataset.material_history_sequence
    u_true = dataset.fields_sequence
    residual, energy = linearized_residual_and_energy(dataset, u_pred)
    return {
        "field_relative_l2": relative_l2(u_pred[:, 1:], u_true[:, 1:]),
        "history_relative_l2": relative_l2(h_pred[:, 1:], h_true[:, 1:]),
        "history_increment_relative_l2": relative_l2(np.diff(h_pred, axis=1), np.diff(h_true, axis=1)),
        "linearized_residual_ratio": residual,
        "linearized_energy_error": energy,
        "plastic_work_negative_increment_ratio": plastic_work_violation(h_pred, h_true),
        "yield_flag_mae": yield_flag_mae(h_pred, h_true),
    }


def make_diagnostic_figure(
    output_path: Path,
    datasets: Iterable[PathDataset],
    metrics: Dict[str, Dict[str, Dict[str, float]]],
) -> None:
    names = [d.name for d in datasets]
    x = np.arange(len(names))
    width = 0.35

    stateful_field = [metrics[n]["stateful"]["field_relative_l2"] for n in names]
    static_field = [metrics[n]["static"]["field_relative_l2"] for n in names]
    stateful_hist = [metrics[n]["stateful"]["history_increment_relative_l2"] for n in names]
    static_hist = [metrics[n]["static"]["history_increment_relative_l2"] for n in names]

    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.0), constrained_layout=True)
    axes[0].bar(x - width / 2, static_field, width, label="static")
    axes[0].bar(x + width / 2, stateful_field, width, label="stateful")
    axes[0].set_title("Field rollout error")
    axes[0].set_ylabel("relative L2")
    axes[0].set_xticks(x, names, rotation=20, ha="right")
    axes[0].legend(frameon=False)

    axes[1].bar(x - width / 2, static_hist, width, label="static")
    axes[1].bar(x + width / 2, stateful_hist, width, label="stateful")
    axes[1].set_title("History-increment error")
    axes[1].set_ylabel("relative L2")
    axes[1].set_xticks(x, names, rotation=20, ha="right")
    axes[1].legend(frameon=False)

    fig.suptitle("Public J2 path-OOD example: static versus stateful transition")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=220)
    plt.close(fig)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data-root",
        type=Path,
        default=(
            Path(__file__).resolve().parents[1]
            / "data"
            / "public_j2_smoke"
            / "j2_path_operator_evidence_smoke"
        ),
        help="Root containing monotonic/cyclic/unload_reload/nonproportional NPZ files.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "outputs",
        help="Directory for JSON and figure outputs.",
    )
    parser.add_argument("--ridge", type=float, default=1.0e-6, help="Ridge penalty.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    package_root = Path(__file__).resolve().parents[1]
    train = load_path_dataset(args.data_root / "monotonic" / "train.npz", "monotonic_train")
    tests = [
        load_path_dataset(args.data_root / "cyclic" / "test.npz", "cyclic"),
        load_path_dataset(args.data_root / "unload_reload" / "test.npz", "unload_reload"),
        load_path_dataset(args.data_root / "nonproportional" / "test.npz", "nonproportional"),
    ]

    x_stateful, y_stateful = build_transition_system(train, stateful=True)
    x_static, y_static = build_transition_system(train, stateful=False)
    w_stateful = fit_ridge_transition(x_stateful, y_stateful, args.ridge)
    w_static = fit_ridge_transition(x_static, y_static, args.ridge)

    all_metrics: Dict[str, Dict[str, Dict[str, float]]] = {}
    for dataset in tests:
        u_stateful, h_stateful = rollout(dataset, w_stateful, stateful=True)
        u_static, h_static = rollout(dataset, w_static, stateful=False)
        all_metrics[dataset.name] = {
            "stateful": evaluate_rollout(dataset, u_stateful, h_stateful),
            "static": evaluate_rollout(dataset, u_static, h_static),
        }

    args.output_dir.mkdir(parents=True, exist_ok=True)
    summary_path = args.output_dir / "j2_stateful_fem_audit_example_summary.json"
    figure_path = args.output_dir / "j2_stateful_fem_audit_example.png"
    try:
        train_path_for_report = str((args.data_root / "monotonic" / "train.npz").resolve().relative_to(package_root))
        summary_path_for_report = str(summary_path.resolve().relative_to(package_root))
        figure_path_for_report = str(figure_path.resolve().relative_to(package_root))
    except ValueError:
        train_path_for_report = str(args.data_root / "monotonic" / "train.npz")
        summary_path_for_report = str(summary_path)
        figure_path_for_report = str(figure_path)
    summary = {
        "note": (
            "Public medium-difficulty example for the released code package; "
            "this script demonstrates the data interface and audit logic."
        ),
        "train_path": train_path_for_report,
        "metrics": all_metrics,
    }
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    make_diagnostic_figure(figure_path, tests, all_metrics)

    print(json.dumps(summary, indent=2))
    print(f"\nWrote {summary_path_for_report}")
    print(f"Wrote {figure_path_for_report}")


if __name__ == "__main__":
    main()
