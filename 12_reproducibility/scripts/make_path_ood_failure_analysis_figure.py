from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUTS = {
    "structured J2": PROJECT_ROOT / "10_results" / "reports" / "thermo_path_ood_5seed_summary.json",
    "shared-hole J2": PROJECT_ROOT
    / "10_results"
    / "reports"
    / "j2_complex_geometry_shared_thermo_path_ood_5seed_summary.json",
}
DEFAULT_CSV = PROJECT_ROOT / "11_paper" / "tables" / "path_ood_failure_analysis_metrics.csv"
DEFAULT_PNG = PROJECT_ROOT / "11_paper" / "figures" / "path_ood_failure_analysis.png"
DEFAULT_PDF = PROJECT_ROOT / "11_paper" / "figures" / "path_ood_failure_analysis.pdf"

CASES = ("strict", "curriculum", "upper_bound")
CASE_LABELS = {
    "strict": "Strict\nmonotonic",
    "curriculum": "Unload\ncurriculum",
    "upper_bound": "Cyclic-seen\nupper bound",
}
METRICS = (
    ("history_relative_l2", "Cyclic history rel. L2", "lower is better"),
    ("eq_plastic_strain_increment_relative_l2", "Eqp increment rel. L2", "lower is better"),
    ("reversal_yield_flag_mae", "Reversal yield-flag MAE", "lower is better"),
    ("predicted_yield_surface_relative_rms", "Yield-surface RMS", "lower is better"),
    (
        "predicted_plastic_work_lower_bound_relative_violation",
        "Plastic-work lower-bound violation",
        "lower is better",
    ),
)


def main() -> None:
    rows = _collect_rows(DEFAULT_INPUTS)
    _write_csv(DEFAULT_CSV, rows)
    _write_figure(DEFAULT_PNG, DEFAULT_PDF, rows)
    print(f"wrote {DEFAULT_CSV}")
    print(f"wrote {DEFAULT_PNG}")
    print(f"wrote {DEFAULT_PDF}")


def _collect_rows(inputs: dict[str, Path]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for dataset, path in inputs.items():
        payload = json.loads(path.read_text(encoding="utf-8"))
        cyclic = payload["cyclic_primary"]
        for case in CASES:
            case_metrics = cyclic[case]
            for metric, label, direction in METRICS:
                stats = case_metrics[metric]
                rows.append(
                    {
                        "dataset": dataset,
                        "case": case,
                        "case_label": CASE_LABELS[case].replace("\n", " "),
                        "metric": metric,
                        "metric_label": label,
                        "direction": direction,
                        "mean": float(stats["mean"]),
                        "std": float(stats["std"]),
                    }
                )
    return rows


def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _write_figure(png_path: Path, pdf_path: Path, rows: list[dict[str, object]]) -> None:
    png_path.parent.mkdir(parents=True, exist_ok=True)
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    datasets = list(DEFAULT_INPUTS)
    colors = {"structured J2": "#1f77b4", "shared-hole J2": "#d62728"}
    markers = {"structured J2": "o", "shared-hole J2": "s"}
    x_values = list(range(len(CASES)))
    fig, axes = plt.subplots(2, 3, figsize=(13.5, 7.2), constrained_layout=True)
    axes_flat = axes.reshape(-1)
    for ax, (metric, label, direction) in zip(axes_flat, METRICS):
        for dataset in datasets:
            means = [
                _lookup(rows, dataset, case, metric, "mean")
                for case in CASES
            ]
            stds = [
                _lookup(rows, dataset, case, metric, "std")
                for case in CASES
            ]
            ax.errorbar(
                x_values,
                means,
                yerr=stds,
                label=dataset,
                color=colors[dataset],
                marker=markers[dataset],
                linewidth=2.0,
                capsize=4,
            )
        ax.set_title(label, fontsize=11)
        ax.set_xticks(x_values)
        ax.set_xticklabels([CASE_LABELS[case] for case in CASES], fontsize=9)
        ax.grid(True, axis="y", alpha=0.25)
        ax.set_ylabel(direction)
    axes_flat[-1].axis("off")
    axes_flat[-1].text(
        0.0,
        0.96,
        "Failure-analysis reading",
        fontsize=12,
        fontweight="bold",
        va="top",
    )
    axes_flat[-1].text(
        0.0,
        0.78,
        "Strict path-OOD is the stress test.\n"
        "Curriculum probes whether unload/reload\n"
        "exposure repairs reversal memory.\n"
        "Cyclic-seen is an architectural upper bound,\n"
        "not the main generalization claim.",
        fontsize=10,
        va="top",
        linespacing=1.35,
    )
    handles, labels = axes_flat[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=2, frameon=False, bbox_to_anchor=(0.5, 1.04))
    fig.suptitle(
        "Cyclic path-OOD failure analysis for thermodynamic HistoryGNO",
        fontsize=14,
        fontweight="bold",
        y=1.08,
    )
    fig.savefig(png_path, dpi=300, bbox_inches="tight")
    fig.savefig(pdf_path, bbox_inches="tight")
    plt.close(fig)


def _lookup(rows: list[dict[str, object]], dataset: str, case: str, metric: str, field: str) -> float:
    for row in rows:
        if row["dataset"] == dataset and row["case"] == case and row["metric"] == metric:
            return float(row[field])
    raise KeyError(f"missing {dataset=} {case=} {metric=} {field=}")


if __name__ == "__main__":
    main()
