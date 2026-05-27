from __future__ import annotations

import csv
import json
import math
import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


PROJECT_ROOT = Path(__file__).resolve().parents[2]
TABLE_DIR = PROJECT_ROOT / "11_paper" / "tables"
FIG_DIR = PROJECT_ROOT / "11_paper" / "figures"
REPORT_DIR = PROJECT_ROOT / "10_results" / "reports"


PATH_ORDER = ["monotonic", "unload_reload", "cyclic", "nonproportional"]
PATH_LABELS = {
    "monotonic": "mono",
    "unload_reload": "unload",
    "cyclic": "cyclic",
    "nonproportional": "nonprop",
}
ABLATION_ORDER = [
    "No solver loss",
    "Tangent-linearized solver loss",
    "One-step dense Newton",
    "Multi-step damped Newton",
    "Multi-step line-search Newton",
]
ABLATION_LABELS = {
    "No solver loss": "none",
    "Tangent-linearized solver loss": "tangent",
    "One-step dense Newton": "1-step",
    "Multi-step damped Newton": "3-step",
    "Multi-step line-search Newton": "3-step+LS",
}
COLORS = {
    "No solver loss": "#6b7280",
    "Tangent-linearized solver loss": "#7c3aed",
    "One-step dense Newton": "#2563eb",
    "Multi-step damped Newton": "#059669",
    "Multi-step line-search Newton": "#dc2626",
}

plt.rcParams.update(
    {
        "font.size": 8,
        "axes.titlesize": 8.5,
        "axes.labelsize": 8,
        "xtick.labelsize": 7.5,
        "ytick.labelsize": 7.5,
        "legend.fontsize": 7,
        "figure.titlesize": 10,
    }
)


def main() -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    make_level6_readiness_dashboard()
    make_solver_in_loop_formal_evidence()
    make_solver_in_loop_reduction_heatmap()
    make_multigeometry_path_matrix()
    make_qp_history_repair_diagnostic()
    print(f"wrote Level-6 hard-evidence figures to {FIG_DIR}")


def _read_csv(name: str) -> list[dict[str, str]]:
    path = TABLE_DIR / name
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def _mean(value: str | None) -> float:
    if value is None:
        return math.nan
    text = str(value).strip()
    if not text:
        return math.nan
    return _float(text.split("+/-", 1)[0].strip())


def _std(value: str | None) -> float:
    if value is None:
        return math.nan
    text = str(value).strip()
    if "+/-" not in text:
        return math.nan
    return _float(text.split("+/-", 1)[1].strip())


def _float(value: str | None) -> float:
    if value is None:
        return math.nan
    text = str(value).strip().replace(",", "")
    if text in {"", "nan", "None"}:
        return math.nan
    try:
        return float(text)
    except ValueError:
        match = re.search(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", text)
        return float(match.group(0)) if match else math.nan


def _write(fig: plt.Figure, stem: str) -> None:
    for suffix, dpi in [("pdf", None), ("png", 360)]:
        fig.savefig(
            FIG_DIR / f"{stem}.{suffix}",
            dpi=dpi,
            bbox_inches="tight",
            facecolor="white",
        )
    plt.close(fig)


def _style_axis(ax: plt.Axes) -> None:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", color="#e5e7eb", lw=0.8)
    ax.set_axisbelow(True)


def _annotate_panel(ax: plt.Axes, label: str, title: str) -> None:
    ax.text(
        0.01,
        0.98,
        label,
        transform=ax.transAxes,
        fontsize=8.5,
        fontweight="bold",
        va="top",
        ha="left",
        bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.75, "pad": 1.5},
    )


def _annotate_panel_above(ax: plt.Axes, label: str) -> None:
    ax.text(
        0.00,
        1.08,
        label,
        transform=ax.transAxes,
        fontsize=8.5,
        fontweight="bold",
        va="bottom",
        ha="left",
        clip_on=False,
    )


def make_level6_readiness_dashboard() -> None:
    report_path = REPORT_DIR / "level6_readiness_status.json"
    if not report_path.exists():
        return
    report = json.loads(report_path.read_text(encoding="utf-8"))
    checks = report.get("checks", [])
    rows = []
    for item in checks:
        rows.append(
            {
                "name": str(item.get("name", "")),
                "pass": bool(item.get("pass", False)),
                "severity": str(item.get("severity", "")),
            }
        )

    fig, ax = plt.subplots(figsize=(7.2, 3.6))
    fig.subplots_adjust(left=0.36, right=0.98, top=0.88, bottom=0.12)
    y = np.arange(len(rows))
    colors = [
        "#059669" if row["pass"] else ("#f59e0b" if row["severity"] == "warning" else "#dc2626")
        for row in rows
    ]
    ax.barh(y, [1] * len(rows), color=colors, height=0.72)
    ax.set_yticks(y)
    ax.set_yticklabels([row["name"] for row in rows], fontsize=8)
    ax.set_xlim(0, 1.05)
    ax.set_xticks([])
    ax.invert_yaxis()
    ax.spines[:].set_visible(False)
    for yi, row in zip(y, rows):
        label = "pass" if row["pass"] else ("warning" if row["severity"] == "warning" else "gap")
        ax.text(0.50, yi, label, color="white", ha="center", va="center", fontsize=8, fontweight="bold")
    ax.text(
        0,
        -0.85,
        f"Status: {report.get('level', '')}; hard blockers: {len(report.get('blocking_gaps', []))}",
        fontsize=8.5,
        color="#374151",
    )
    _write(fig, "level6_readiness_dashboard")


def make_solver_in_loop_formal_evidence() -> None:
    rows = _read_csv("solver_in_loop_formal_main_table.csv")
    fig, axes = plt.subplots(2, 2, figsize=(7.4, 5.0))
    fig.subplots_adjust(left=0.11, right=0.98, bottom=0.10, top=0.82, wspace=0.28, hspace=0.48)

    metric_specs = [
        ("FEM residual", "FEM residual", False, "(a)", "All-step FEM residual"),
        ("FEM energy", "FEM energy", True, "(b)", "Total potential energy error"),
        ("Newton final residual", "Final residual", True, "(c)", "Post-Newton equilibrium residual"),
        ("QP hist. L2", "QP hist. L2", False, "(d)", "QP history remains the bottleneck"),
    ]
    x = np.arange(len(PATH_ORDER))
    width = 0.15
    offsets = np.linspace(-2, 2, len(ABLATION_ORDER)) * width

    for ax, (col, ylabel, logy, panel, title) in zip(axes.flat, metric_specs):
        for offset, ablation in zip(offsets, ABLATION_ORDER):
            vals = []
            errs = []
            for path in PATH_ORDER:
                match = next(
                    (
                        row
                        for row in rows
                        if row["Ablation"] == ablation and row["Load path"] == path
                    ),
                    None,
                )
                vals.append(_mean(match.get(col) if match else ""))
                errs.append(_std(match.get(col) if match else ""))
            ax.bar(
                x + offset,
                vals,
                width=width * 0.92,
                label=ABLATION_LABELS[ablation],
                color=COLORS[ablation],
                alpha=0.88,
                edgecolor="white",
                linewidth=0.4,
            )
            if not logy:
                ax.errorbar(x + offset, vals, yerr=errs, fmt="none", ecolor="#111827", elinewidth=0.45, capsize=1.2)
        ax.set_xticks(x)
        ax.set_xticklabels([PATH_LABELS[p] for p in PATH_ORDER], fontsize=8)
        ax.set_ylabel(ylabel, fontsize=8.5)
        if logy:
            ax.set_yscale("log")
        _style_axis(ax)
        _annotate_panel(ax, panel, title)

    axes[0, 0].legend(
        ncol=3,
        fontsize=6.8,
        frameon=False,
        loc="lower left",
        bbox_to_anchor=(0.00, 1.08),
        columnspacing=0.8,
        handlelength=1.0,
    )
    _write(fig, "solver_in_loop_formal_evidence")


def make_solver_in_loop_reduction_heatmap() -> None:
    rows = _read_csv("solver_in_loop_formal_main_reduction_aggregate.csv")
    metrics = [
        ("fem_residual_relative_rms", "FEM residual"),
        ("fem_energy_relative_error", "Energy error"),
        ("qp_history_relative_l2", "QP history"),
        ("qp_reversal_eqp_increment_relative_l2", "Reversal eqp inc."),
    ]
    ablations = ABLATION_ORDER[1:]
    fig, axes = plt.subplots(1, 4, figsize=(7.8, 2.8), sharey=True)
    fig.subplots_adjust(wspace=0.20, left=0.16, right=0.91, bottom=0.22, top=0.74)

    vmax = 60.0
    for idx, (ax, (metric, title)) in enumerate(zip(axes, metrics)):
        matrix = np.full((len(ablations), len(PATH_ORDER)), np.nan)
        labels = [["" for _ in PATH_ORDER] for _ in ablations]
        for i, ablation in enumerate(ablations):
            for j, path in enumerate(PATH_ORDER):
                match = next(
                    (
                        row
                        for row in rows
                        if row["Ablation"] == ablation
                        and row["Load path"] == path
                        and row["Metric"] == metric
                    ),
                    None,
                )
                if match:
                    matrix[i, j] = _float(match.get("Mean improvement % case mean"))
                    labels[i][j] = str(match.get("Improved cases", "")) + "/3"
        im = ax.imshow(matrix, cmap="RdBu", vmin=-vmax, vmax=vmax, aspect="auto")
        ax.set_xticks(np.arange(len(PATH_ORDER)))
        ax.set_xticklabels([PATH_LABELS[p] for p in PATH_ORDER], rotation=35, ha="right", fontsize=7.5)
        ax.set_yticks(np.arange(len(ablations)))
        if ax is axes[0]:
            ax.set_yticklabels([ABLATION_LABELS[a] for a in ablations], fontsize=7.5)
        else:
            ax.tick_params(axis="y", labelleft=False)
        _annotate_panel_above(ax, f"({chr(ord('a') + idx)})")
        for i in range(matrix.shape[0]):
            for j in range(matrix.shape[1]):
                value = matrix[i, j]
                if math.isnan(value):
                    continue
                color = "white" if abs(value) > 32 else "#111827"
                ax.text(j, i, f"{value:.0f}%\n{labels[i][j]}", ha="center", va="center", fontsize=6.5, color=color)
        ax.tick_params(length=0)
        ax.spines[:].set_visible(False)

    cax = fig.add_axes([0.93, 0.26, 0.018, 0.46])
    cb = fig.colorbar(im, cax=cax)
    cb.set_label("Improvement vs no solver loss (%)", fontsize=7.5)
    cb.ax.tick_params(labelsize=7)
    _write(fig, "solver_in_loop_reduction_heatmap")


def make_multigeometry_path_matrix() -> None:
    rows = _read_csv("level4_multigeometry_multipath_matrix_case_path.csv")
    # Focus on the hardest all-step evidence row used in the main claim: strict monotonic training.
    rows = [row for row in rows if row.get("Protocol") == "strict" and row.get("Train paths") == "monotonic"]
    cases = sorted({row["Case"] for row in rows})
    families = ["multi_hole", "notch", "curved_hole"]
    def case_key(case: str) -> tuple[int, str]:
        for i, family in enumerate(families):
            if case.startswith(family + "_"):
                return (i, case)
        return (99, case)

    cases = sorted(cases, key=case_key)

    metrics = [
        ("FEM residual rel. RMS mean", "FEM residual"),
        ("FEM energy rel. err. mean", "Energy error"),
        ("QP hist. rel. L2 mean", "QP history"),
    ]
    fig, axes = plt.subplots(1, 3, figsize=(8.1, 5.0), sharey=True)
    fig.subplots_adjust(left=0.27, right=0.97, bottom=0.13, top=0.86, wspace=0.18)

    for idx, (ax, (col, title)) in enumerate(zip(axes, metrics)):
        matrix = np.full((len(cases), len(PATH_ORDER)), np.nan)
        for i, case in enumerate(cases):
            for j, path in enumerate(PATH_ORDER):
                match = next(
                    (
                        row
                        for row in rows
                        if row["Case"] == case and row["Eval path"] == path
                    ),
                    None,
                )
                if match:
                    matrix[i, j] = _float(match.get(col))
        plot_matrix = np.log10(np.maximum(matrix, 1e-12))
        ax.imshow(plot_matrix, cmap="viridis", aspect="auto")
        ax.set_xticks(np.arange(len(PATH_ORDER)))
        ax.set_xticklabels([PATH_LABELS[p] for p in PATH_ORDER], rotation=35, ha="right", fontsize=7.5)
        ax.set_yticks(np.arange(len(cases)))
        if ax is axes[0]:
            ax.set_yticklabels([c.replace("_", " ") for c in cases], fontsize=6.8)
        else:
            ax.tick_params(axis="y", labelleft=False)
        _annotate_panel(ax, f"({chr(ord('a') + idx)})", title)
        for i in range(matrix.shape[0]):
            for j in range(matrix.shape[1]):
                value = matrix[i, j]
                if math.isnan(value):
                    continue
                text = f"{value:.2g}" if value < 100 else f"{value:.0f}"
                ax.text(j, i, text, ha="center", va="center", fontsize=5.8, color="white")
        ax.tick_params(length=0)
        ax.spines[:].set_visible(False)
    _write(fig, "level6_multigeometry_path_matrix")


def make_qp_history_repair_diagnostic() -> None:
    rows = _read_csv("qp_history_repair_notch16_summary.csv")
    labels = [
        "Strict\nbaseline",
        "QP-aware\nstrict",
        "QP-aware\ncurr.",
        "QP-aware\nUB",
        "Active-zone\nUB",
        "Plastic\ncorrector",
        "True J2\nUB",
    ]
    metrics = [
        ("Qp history rel. L2", "QP history L2", "#2563eb"),
        ("Qp eqp rel. L2", "eqp L2", "#059669"),
        ("Qp plastic-work rel. L2", "p-work L2", "#dc2626"),
        ("FEM residual rel. RMS", "FEM residual", "#7c3aed"),
    ]
    fig, axes = plt.subplots(2, 2, figsize=(7.4, 4.8))
    fig.subplots_adjust(wspace=0.26, hspace=0.52, left=0.09, right=0.98, bottom=0.17, top=0.86)
    x = np.arange(len(rows))
    for ax, (col, ylabel, color) in zip(axes.flat, metrics):
        vals = [_mean(row.get(col)) for row in rows]
        errs = [_std(row.get(col)) for row in rows]
        ax.bar(x, vals, color=color, alpha=0.82, edgecolor="white", linewidth=0.5)
        ax.errorbar(x, vals, yerr=errs, fmt="none", ecolor="#111827", elinewidth=0.6, capsize=1.6)
        ax.axhline(1.0, color="#111827", lw=0.8, ls="--", alpha=0.70)
        ax.set_xticks(x)
        ax.set_xticklabels(labels, fontsize=6.8, rotation=0)
        ax.set_ylabel(ylabel, fontsize=8.5)
        if col == "FEM residual rel. RMS":
            ax.set_yscale("log")
        _style_axis(ax)
    for ax, label in zip(axes.flat, ["(a)", "(b)", "(c)", "(d)"]):
        _annotate_panel(ax, label, "")
    _write(fig, "qp_history_repair_diagnostic")


if __name__ == "__main__":
    main()
