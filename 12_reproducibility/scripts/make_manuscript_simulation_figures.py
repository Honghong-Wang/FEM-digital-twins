from __future__ import annotations

import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, Polygon, Rectangle


PROJECT_ROOT = Path(__file__).resolve().parents[2]
TABLE_DIR = PROJECT_ROOT / "11_paper" / "tables"
FIG_DIR = PROJECT_ROOT / "11_paper" / "figures"
REPORT_DIR = PROJECT_ROOT / "10_results" / "reports"
J2_DATA_DIR = PROJECT_ROOT / "05_data_pipeline" / "processed" / "j2_complex_geometry_shared_path_fem2d"


def main() -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    make_theory_chain()
    make_j2_dataset_protocol()
    make_pcgno_repair()
    make_fem_baseline()
    make_j2_memory()
    make_j2_history_rollout()
    make_path_ood_summary()
    make_t6_complex_scale()
    make_t6_qp_fem_audit()
    make_t6_qp_representative_allstep()
    make_t6_qp_12case_allstep_matrix()
    print(f"wrote figures to {FIG_DIR}")


def panel_label(ax: plt.Axes, label: str) -> None:
    ax.text(
        0.018,
        0.975,
        f"({label})",
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=10.5,
        fontweight="bold",
        color="#111111",
        bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.82, "pad": 1.8},
        zorder=20,
    )


def panel_from_title(ax: plt.Axes, title: str) -> None:
    if len(title) >= 3 and title[0] == "(" and title[2] == ")":
        panel_label(ax, title[1])


def _make_theory_chain_legacy() -> None:
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    nodes = [
        {
            "xy": (0.060, 0.565),
            "w": 0.405,
            "h": 0.270,
            "color": "#f8f8f8",
            "edge": "#7a2e2e",
            "tag": "(a) failure",
            "title": "Static map failure",
            "body": "$X_t=(\\Omega_h,E,\\mu,f_t,s_t)$\n"
            "hidden $h_t\\Rightarrow \\mathrm{Cov}(u_t\\mid X_t)>0$\n"
            "irreducible static-map risk",
        },
        {
            "xy": (0.535, 0.565),
            "w": 0.405,
            "h": 0.270,
            "color": "#f8f8f8",
            "edge": "#2f6b3f",
            "tag": "(b) state lift",
            "title": "Lifted Markov operator",
            "body": "$z_t=(u_t,h_t)$\n"
            "$z_{t+1}=\\mathcal{S}_{\\Delta t}(z_t,\\cdot)$\n"
            "$\\widehat z_{t+1}=\\mathcal{G}_\\theta(\\widehat z_t,\\cdot)$",
        },
        {
            "xy": (0.535, 0.220),
            "w": 0.405,
            "h": 0.270,
            "color": "#f8f8f8",
            "edge": "#8a641f",
            "tag": "(c) mechanics prior",
            "title": "Soft admissibility",
            "body": "$C_h=[B\\widehat u-g,\\,R,\\,r_\\phi,\\,r_{el},\\,r_W]$\n"
            "$\\mathbb{E}\\|C_h\\|_2^2\\leq\\eta$\n"
            "FEM and thermodynamic defects",
        },
        {
            "xy": (0.060, 0.220),
            "w": 0.405,
            "h": 0.270,
            "color": "#f8f8f8",
            "edge": "#2f5f80",
            "tag": "(d) evidence",
            "title": "Path-OOD diagnostics",
            "body": "$P_{mono}(z)\\rightarrow P_{cyc}(z)$\n"
            "strict / curriculum / upper bound\n"
            "$\\Delta h$, reversal, yield, plastic work",
        },
    ]

    for node in nodes:
        x, y = node["xy"]
        patch = FancyBboxPatch(
            (x, y),
            node["w"],
            node["h"],
            boxstyle="round,pad=0.012,rounding_size=0.012",
            linewidth=1.25,
            edgecolor=node["edge"],
            facecolor=node["color"],
            alpha=1.0,
        )
        ax.add_patch(patch)
        ax.text(
            x + 0.016,
            y + node["h"] - 0.036,
            node["tag"],
            ha="left",
            va="center",
            fontsize=7.6,
            color=node["edge"],
            fontweight="bold",
        )
        ax.plot(
            [x + 0.014, x + node["w"] - 0.014],
            [y + node["h"] - 0.060, y + node["h"] - 0.060],
            color="#d6d6d6",
            linewidth=0.8,
        )
        ax.text(
            x + node["w"] / 2,
            y + node["h"] - 0.088,
            node["title"],
            ha="center",
            va="center",
            fontsize=8.6,
            fontweight="bold",
            color="#1f1f1f",
        )
        ax.text(
            x + node["w"] / 2,
            y + 0.103,
            node["body"],
            ha="center",
            va="center",
            fontsize=8.0,
            color="#222222",
            linespacing=1.30,
        )

    arrow_specs = [
        ("lift state", nodes[0], nodes[1], "right"),
        ("add mechanics defects", nodes[1], nodes[2], "down"),
        ("evaluate path shift", nodes[2], nodes[3], "left"),
    ]
    for label, left, right, direction in arrow_specs:
        if direction == "right":
            x0 = left["xy"][0] + left["w"] + 0.020
            y0 = left["xy"][1] + left["h"] / 2
            x1 = right["xy"][0] - 0.020
            y1 = y0
            tx, ty = (x0 + x1) / 2, y0 + 0.034
        elif direction == "down":
            x0 = left["xy"][0] + left["w"] / 2
            y0 = left["xy"][1] - 0.018
            x1 = x0
            y1 = right["xy"][1] + right["h"] + 0.018
            tx, ty = x0 + 0.115, (y0 + y1) / 2
        else:
            x0 = left["xy"][0] - 0.020
            y0 = left["xy"][1] + left["h"] / 2
            x1 = right["xy"][0] + right["w"] + 0.020
            y1 = y0
            tx, ty = (x0 + x1) / 2, y0 + 0.034
        arrow = FancyArrowPatch(
            (x0, y0),
            (x1, y1),
            arrowstyle="-|>",
            mutation_scale=13,
            linewidth=1.2,
            color="#555555",
            shrinkA=0,
            shrinkB=0,
        )
        ax.add_patch(arrow)
        ax.text(
            tx,
            ty,
            label,
            ha="center",
            va="center",
            fontsize=7.2,
            color="#555555",
        )

    ax.text(
        0.060,
        0.93,
        "Theory chain",
        ha="left",
        va="center",
        fontsize=10.5,
        fontweight="bold",
        color="#111111",
    )
    ax.text(
        0.060,
        0.885,
        "from a failed static map to a stateful, mechanics-constrained, path-OOD-tested operator",
        ha="left",
        va="center",
        fontsize=8.0,
        color="#444444",
    )
    ax.plot([0.060, 0.940], [0.855, 0.855], color="#c7c7c7", linewidth=0.8)

    save(fig, "theory_chain_schematic")


def make_theory_chain() -> None:
    fig, ax = plt.subplots(figsize=(12.8, 4.35))
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    ax.add_patch(Rectangle((0, 0), 1, 1, facecolor="#ffffff", edgecolor="none"))
    ax.text(
        0.055,
        0.920,
        "Theory chain",
        ha="left",
        va="center",
        fontsize=18.0,
        fontweight="bold",
        color="#141414",
    )
    ax.text(
        0.055,
        0.858,
        "from static surrogate failure to stateful, mechanics-audited prediction",
        ha="left",
        va="center",
        fontsize=13.0,
        color="#4b5563",
    )
    ax.plot([0.055, 0.945], [0.815, 0.815], color="#d2d6dc", linewidth=1.1)

    nodes = [
        {
            "xy": (0.050, 0.365),
            "w": 0.140,
            "h": 0.390,
            "color": "#fff7f7",
            "edge": "#7a2e2e",
            "tag": "01",
            "title": "Static map",
            "body": "missing\nhistory",
            "icon": "failure",
        },
        {
            "xy": (0.251, 0.365),
            "w": 0.140,
            "h": 0.390,
            "color": "#f4fbf6",
            "edge": "#2f6b3f",
            "tag": "02",
            "title": "State lift",
            "body": "$z_t=(u_t,h_t)$\nrollout",
            "icon": "state",
        },
        {
            "xy": (0.452, 0.365),
            "w": 0.140,
            "h": 0.390,
            "color": "#fffaf0",
            "edge": "#8a641f",
            "tag": "03",
            "title": "Mechanics",
            "body": "yield\nplastic work",
            "icon": "mechanics",
        },
        {
            "xy": (0.653, 0.365),
            "w": 0.140,
            "h": 0.390,
            "color": "#f3f8fc",
            "edge": "#2f5f80",
            "tag": "04",
            "title": "FEM audit",
            "body": "residual\nenergy",
            "icon": "audit",
        },
        {
            "xy": (0.850, 0.365),
            "w": 0.140,
            "h": 0.390,
            "color": "#f8f6ff",
            "edge": "#57408f",
            "tag": "05",
            "title": "Path-OOD",
            "body": "cyclic\ncalibration",
            "icon": "ood",
        },
    ]

    def draw_icon(node: dict) -> None:
        x, y = node["xy"]
        w, h = node["w"], node["h"]
        c = node["edge"]
        cx = x + w / 2
        cy = y + 0.230
        kind = node["icon"]
        if kind == "failure":
            left = Circle((cx - 0.030, cy + 0.010), 0.017, edgecolor=c, facecolor="#ffffff", linewidth=1.6)
            right = Circle((cx + 0.032, cy + 0.010), 0.017, edgecolor=c, facecolor="#ffffff", linewidth=1.6)
            hidden = Circle((cx, cy - 0.042), 0.017, edgecolor=c, facecolor="#ffffff", linewidth=1.4, linestyle="--")
            ax.add_patch(left)
            ax.add_patch(right)
            ax.add_patch(hidden)
            ax.add_patch(FancyArrowPatch((cx - 0.012, cy + 0.010), (cx + 0.014, cy + 0.010), arrowstyle="-|>", mutation_scale=10, linewidth=1.3, color=c))
            ax.plot([cx - 0.013, cx + 0.013], [cy - 0.055, cy - 0.029], color=c, linewidth=1.6)
        elif kind == "state":
            ax.add_patch(Circle((cx - 0.032, cy + 0.018), 0.018, edgecolor=c, facecolor="#ffffff", linewidth=1.5))
            ax.add_patch(Circle((cx - 0.032, cy - 0.030), 0.018, edgecolor=c, facecolor="#ffffff", linewidth=1.5))
            ax.add_patch(Circle((cx + 0.035, cy - 0.006), 0.024, edgecolor=c, facecolor="#ffffff", linewidth=1.7))
            ax.plot([cx - 0.014, cx + 0.012], [cy + 0.018, cy + 0.001], color=c, linewidth=1.3)
            ax.plot([cx - 0.014, cx + 0.012], [cy - 0.030, cy - 0.011], color=c, linewidth=1.3)
            ax.add_patch(FancyArrowPatch((cx + 0.023, cy + 0.030), (cx + 0.052, cy + 0.025), connectionstyle="arc3,rad=-0.55", arrowstyle="-|>", mutation_scale=9, linewidth=1.2, color=c))
        elif kind == "mechanics":
            shield = Polygon(
                [(cx, cy + 0.045), (cx + 0.043, cy + 0.022), (cx + 0.034, cy - 0.036), (cx, cy - 0.061), (cx - 0.034, cy - 0.036), (cx - 0.043, cy + 0.022)],
                closed=True,
                edgecolor=c,
                facecolor="#ffffff",
                linewidth=1.7,
            )
            ax.add_patch(shield)
            ax.plot([cx - 0.020, cx - 0.004, cx + 0.025], [cy - 0.010, cy - 0.029, cy + 0.018], color=c, linewidth=2.0, solid_capstyle="round")
        elif kind == "audit":
            pts = np.array([
                [cx - 0.048, cy - 0.040],
                [cx + 0.050, cy - 0.040],
                [cx + 0.000, cy + 0.048],
                [cx - 0.012, cy - 0.004],
                [cx + 0.032, cy - 0.010],
            ])
            for i, j in [(0, 2), (1, 2), (0, 1), (0, 3), (3, 2), (3, 1), (2, 4), (4, 1)]:
                ax.plot([pts[i, 0], pts[j, 0]], [pts[i, 1], pts[j, 1]], color=c, linewidth=1.25)
            for px, py in pts:
                ax.add_patch(Circle((px, py), 0.0065, edgecolor=c, facecolor="#ffffff", linewidth=1.2))
        elif kind == "ood":
            xs = np.linspace(cx - 0.048, cx + 0.048, 80)
            mono = cy - 0.030 + 0.120 * (xs - (cx - 0.048))
            cyc = cy + 0.003 + 0.022 * np.sin((xs - cx) * 70)
            ax.plot(xs, mono, color=c, linewidth=1.6)
            ax.plot(xs, cyc, color=c, linewidth=1.8)
            ax.add_patch(FancyArrowPatch((cx + 0.025, cy + 0.010), (cx + 0.050, cy + 0.010), arrowstyle="-|>", mutation_scale=10, linewidth=1.3, color=c))

    for node in nodes:
        x, y = node["xy"]
        shadow = FancyBboxPatch(
            (x + 0.006, y - 0.010),
            node["w"],
            node["h"],
            boxstyle="round,pad=0.009,rounding_size=0.014",
            linewidth=0,
            facecolor="#dfe5ee",
            alpha=0.55,
        )
        ax.add_patch(shadow)
        patch = FancyBboxPatch(
            (x, y),
            node["w"],
            node["h"],
            boxstyle="round,pad=0.009,rounding_size=0.014",
            linewidth=1.45,
            edgecolor=node["edge"],
            facecolor=node["color"],
            alpha=1.0,
        )
        ax.add_patch(patch)
        ax.add_patch(
            Rectangle(
                (x, y + node["h"] - 0.014),
                node["w"],
                0.012,
                facecolor=node["edge"],
                edgecolor="none",
                alpha=0.90,
            )
        )
        badge = Circle(
            (x + 0.031, y + node["h"] - 0.052),
            0.018,
            facecolor=node["edge"],
            edgecolor="#ffffff",
            linewidth=1.0,
            zorder=5,
        )
        ax.add_patch(badge)
        ax.text(
            x + 0.031,
            y + node["h"] - 0.050,
            node["tag"],
            ha="center",
            va="center",
            fontsize=8.4,
            color="#ffffff",
            fontweight="bold",
            zorder=6,
        )
        ax.plot(
            [x + 0.059, x + node["w"] - 0.018],
            [y + node["h"] - 0.052, y + node["h"] - 0.052],
            color=node["edge"],
            linewidth=1.15,
            alpha=0.26,
            solid_capstyle="round",
        )
        ax.add_patch(
            Circle(
                (x + node["w"] / 2, y + 0.232),
                0.061,
                facecolor="#ffffff",
                edgecolor="#d9dee7",
                linewidth=0.9,
                alpha=0.88,
            )
        )
        draw_icon(node)
        ax.text(
            x + node["w"] / 2,
            y + 0.142,
            node["title"],
            ha="center",
            va="center",
            fontsize=12.4,
            fontweight="bold",
            color="#1f1f1f",
        )
        ax.text(
            x + node["w"] / 2,
            y + 0.075,
            node["body"],
            ha="center",
            va="center",
            fontsize=10.9,
            color="#222222",
            linespacing=1.35,
        )

    for idx in range(len(nodes) - 1):
        left = nodes[idx]
        right = nodes[idx + 1]
        x0 = left["xy"][0] + left["w"] + 0.014
        y0 = left["xy"][1] + left["h"] * 0.52
        x1 = right["xy"][0] - 0.014
        y1 = y0
        arrow = FancyArrowPatch(
            (x0, y0),
            (x1, y1),
            arrowstyle="-|>",
            mutation_scale=17,
            linewidth=1.55,
            color="#59616c",
            shrinkA=0,
            shrinkB=0,
        )
        ax.add_patch(arrow)

    band = FancyBboxPatch(
        (0.055, 0.105),
        0.938,
        0.165,
        boxstyle="round,pad=0.012,rounding_size=0.014",
        linewidth=1.0,
        edgecolor="#b9c0ca",
        facecolor="#f5f7fb",
    )
    ax.add_patch(band)
    ax.text(
        0.075,
        0.235,
        "Evidence chain",
        ha="left",
        va="center",
        fontsize=15.0,
        fontweight="bold",
        color="#273142",
    )
    metrics = [
        "field",
        "history",
        "residual",
        "energy",
        "yield/work",
        "reversal",
        "calibration",
    ]
    x_positions = np.linspace(0.085, 0.930, len(metrics))
    metric_colors = ["#7a2e2e", "#2f6b3f", "#2f5f80", "#8a641f", "#8a641f", "#57408f", "#57408f"]
    ax.plot(
        [x_positions[0], x_positions[-1]],
        [0.151, 0.151],
        color="#d4dae3",
        linewidth=1.2,
        zorder=0,
    )
    for x_pos, metric, metric_color in zip(x_positions, metrics, metric_colors):
        ax.add_patch(
            Circle(
                (x_pos, 0.151),
                0.0080,
                facecolor=metric_color,
                edgecolor="#ffffff",
                linewidth=0.8,
                zorder=3,
            )
        )
        ax.text(
            x_pos,
            0.185,
            metric,
            ha="center",
            va="center",
            fontsize=12.6,
            color="#344054",
        )

    save(fig, "theory_chain_schematic")


def make_j2_dataset_protocol() -> None:
    families = ["monotonic", "unload_reload", "cyclic", "nonproportional"]
    labels = ["monotonic", "unload/reload", "cyclic", "non-proportional"]
    colors = ["#4c78a8", "#f58518", "#e45756", "#54a24b"]

    cyclic = load_j2_npz("cyclic", "test")
    coords = cyclic["coords"][0]
    conn = cyclic["connectivity"]
    fixed_nodes = np.unique(cyclic["fixed_dofs"] // 2)

    fig = plt.figure(figsize=(11.2, 6.6), constrained_layout=True)
    gs = fig.add_gridspec(2, 3, width_ratios=[1.15, 1.35, 1.25], height_ratios=[1.0, 0.9])
    ax_mesh = fig.add_subplot(gs[:, 0])
    ax_paths = fig.add_subplot(gs[0, 1:])
    ax_protocol = fig.add_subplot(gs[1, 1])
    ax_tensors = fig.add_subplot(gs[1, 2])

    ax_mesh.triplot(coords[:, 0], coords[:, 1], conn, color="#6f6f6f", linewidth=0.75)
    ax_mesh.scatter(coords[:, 0], coords[:, 1], s=12, color="#222222", zorder=3)
    ax_mesh.scatter(
        coords[fixed_nodes, 0],
        coords[fixed_nodes, 1],
        s=34,
        marker="s",
        color="#d62728",
        label="fixed dofs",
        zorder=4,
    )
    ax_mesh.set_aspect("equal")
    panel_label(ax_mesh, "a")
    ax_mesh.set_xlabel("$x$")
    ax_mesh.set_ylabel("$y$")
    ax_mesh.legend(frameon=False, loc="lower left", fontsize=8)
    ax_mesh.grid(True, alpha=0.18)

    for family, label, color in zip(families, labels, colors):
        data = load_j2_npz(family, "test")
        load = data["load_factors"]
        steps = np.arange(1, load.shape[0] + 1)
        ax_paths.plot(steps, load[:, 0], marker="o", linewidth=1.7, color=color, label=f"{label}: $f_x$")
        if family == "nonproportional":
            ax_paths.plot(steps, load[:, 1], marker="s", linewidth=1.2, linestyle="--", color=color, alpha=0.75, label=f"{label}: $f_y$")
    ax_paths.axhline(0.0, color="#555555", linewidth=0.8)
    panel_label(ax_paths, "b")
    ax_paths.set_xlabel("load step")
    ax_paths.set_ylabel("load factor")
    ax_paths.set_xticks(np.arange(1, 9))
    ax_paths.grid(True, alpha=0.25)
    ax_paths.legend(frameon=False, ncol=2, fontsize=7.5)

    ax_protocol.axis("off")
    protocol = [
        ("strict", "train: monotonic\nprimary test: cyclic"),
        ("curriculum", "train: monotonic + unload/reload\ntest: cyclic"),
        ("upper bound", "train: monotonic + unload/reload + cyclic\ntest: cyclic"),
    ]
    y_positions = [0.74, 0.45, 0.16]
    for (title, body), y, color in zip(protocol, y_positions, ["#d62728", "#ff7f0e", "#2ca02c"]):
        box = FancyBboxPatch(
            (0.03, y),
            0.90,
            0.18,
            boxstyle="round,pad=0.014,rounding_size=0.012",
            linewidth=1.0,
            edgecolor=color,
            facecolor="#f8f8f8",
        )
        ax_protocol.add_patch(box)
        ax_protocol.text(0.08, y + 0.122, title, ha="left", va="center", fontsize=8.7, fontweight="bold", color=color)
        ax_protocol.text(0.08, y + 0.057, body, ha="left", va="center", fontsize=7.7, color="#222222")
    panel_label(ax_protocol, "c")

    ax_tensors.axis("off")
    panel_label(ax_tensors, "d")
    rows = [
        ("mesh", "$x_i, E$"),
        ("parameters", "$\\mu$"),
        ("loads", "$f_{1:T}$"),
        ("fields", "$u_{1:T}$"),
        ("history", "$h_{1:T}$"),
        ("callbacks", "$R,K_t,\\Pi,\\phi,\\Delta W^p$"),
    ]
    for idx, (name, value) in enumerate(rows):
        y = 0.76 - 0.12 * idx
        ax_tensors.text(0.08, y, name, ha="left", va="center", fontsize=8.4, fontweight="bold", color="#222222")
        ax_tensors.text(0.47, y, value, ha="left", va="center", fontsize=8.4, color="#222222")
        ax_tensors.plot([0.06, 0.94], [y - 0.055, y - 0.055], color="#dddddd", linewidth=0.8)
    ax_tensors.text(
        0.06,
        0.045,
        "same runner, split, seed, epochs, and metrics",
        ha="left",
        va="center",
        fontsize=7.8,
        color="#555555",
    )

    save(fig, "j2_dataset_protocol")


def make_pcgno_repair() -> None:
    rows = read_csv(TABLE_DIR / "pcgno_fem_repair_evidence.csv")
    metrics = [
        ("test_relative_l2", "Test\nrel. L2"),
        ("test_fem_residual_relative", "FEM\nresidual"),
        ("test_energy_relative", "Energy\nerror"),
        ("ood_loading_relative_l2", "OOD loading\nrel. L2"),
    ]
    labels = [row["training_mode"].replace(" paper preset", "") for row in rows]
    colors = ["#8c8c8c", "#1f77b4"]
    fig, ax = plt.subplots(figsize=(7.2, 4.2), constrained_layout=True)
    x = list(range(len(metrics)))
    width = 0.34
    for i, row in enumerate(rows):
        values = [float(row[key]) for key, _ in metrics]
        offsets = [v + (i - 0.5) * width for v in x]
        ax.bar(offsets, values, width=width, label=labels[i], color=colors[i], alpha=0.9)
    ax.set_xticks(x)
    ax.set_xticklabels([label for _, label in metrics])
    ax.set_ylabel("Lower is better")
    panel_label(ax, "a")
    ax.grid(True, axis="y", alpha=0.25)
    ax.legend(frameon=False)
    save(fig, "pcgno_repair_evidence")


def make_fem_baseline() -> None:
    rows = read_csv(TABLE_DIR / "fem2d_final_fair_baseline_table.csv")
    models = [pretty_model(row["model"]) for row in rows]
    metrics = [
        ("Test rel. L2 mean", "Test L2"),
        ("Test FEM residual rel. mean", "FEM residual"),
        ("Test energy rel. mean", "Energy"),
    ]
    colors = ["#4c78a8", "#f58518", "#54a24b"]
    fig, axes = plt.subplots(1, 3, figsize=(11.5, 3.8), constrained_layout=True)
    for ax, (metric, title), color, panel in zip(axes, metrics, colors, ["a", "b", "c"]):
        values = [float(row[metric]) for row in rows]
        ax.bar(models, values, color=color, alpha=0.9)
        panel_label(ax, panel)
        ax.set_ylabel("Relative metric")
        ax.tick_params(axis="x", rotation=35, labelsize=8)
        ax.grid(True, axis="y", alpha=0.25)
    save(fig, "fem_snapshot_baseline_evidence")


def make_j2_memory() -> None:
    rows = read_csv(TABLE_DIR / "j2_path_dependent_baseline_table.csv")
    models = [short_model(row["Model"]) for row in rows]
    metrics = [
        ("Cyclic history rel. L2", "History L2"),
        ("History-increment rel. L2", "Hist. inc."),
        ("Eqp increment rel. L2", "Eqp inc."),
        ("Plastic-work inc. rel. L2", "Work inc."),
        ("Yield-surface RMS", "Yield RMS"),
    ]
    fig, axes = plt.subplots(1, len(metrics), figsize=(14.0, 4.0), constrained_layout=True)
    colors = ["#1f77b4", "#6baed6", "#9467bd", "#ff7f0e", "#2ca02c"]
    for ax, (metric, title), panel in zip(axes, metrics, ["a", "b", "c", "d", "e"]):
        values = [parse_mean(row[metric]) for row in rows]
        ax.bar(models, values, color=colors[: len(models)], alpha=0.9)
        panel_label(ax, panel)
        ax.tick_params(axis="x", rotation=50, labelsize=8)
        ax.grid(True, axis="y", alpha=0.25)
    axes[0].set_ylabel("Lower is better")
    save(fig, "j2_memory_diagnostics")


def make_j2_history_rollout() -> None:
    data = load_j2_npz("cyclic", "test")
    history = data["material_history_sequence"]
    loads = data["load_factors"][:, 0]
    steps = np.arange(1, history.shape[1] + 1)

    eqp = history[..., 0].mean(axis=(0, 2))
    plastic_work = history[..., 1].mean(axis=(0, 2))
    plastic_multiplier = history[..., 2].mean(axis=(0, 2))
    yield_fraction = history[..., 3].mean(axis=(0, 2))

    rows = read_csv(TABLE_DIR / "j2_complex_geometry_shared_thermo_path_ood_5seed_primary_table.csv")
    row_by_metric = {row["metric"]: row for row in rows}
    case_keys = ["Strict path-OOD", "Unload curriculum", "Cyclic-seen upper bound"]
    case_labels = ["strict", "curr.", "upper"]
    diagnostic_metrics = [
        ("History-increment relative L2", "history\ninc. L2"),
        ("Eq. plastic strain increment relative L2", "eqp\ninc. L2"),
        ("Reversal yield-flag MAE", "reversal\nyield MAE"),
        ("Plastic-work lower-bound violation", "work\nviolation"),
    ]

    fig, axes = plt.subplots(2, 3, figsize=(12.0, 6.8), constrained_layout=True)
    ax_load, ax_eqp, ax_work, ax_dgamma, ax_yield, ax_diag = axes.ravel()

    ax_load.plot(steps, loads, marker="o", color="#e45756", linewidth=1.8)
    ax_load.axhline(0.0, color="#555555", linewidth=0.8)
    panel_label(ax_load, "a")
    ax_load.set_xlabel("step")
    ax_load.set_ylabel("$f_x$")

    ax_eqp.plot(steps, eqp, marker="o", color="#4c78a8", linewidth=1.8)
    panel_label(ax_eqp, "b")
    ax_eqp.set_xlabel("step")
    ax_eqp.set_ylabel("mean history")

    ax_work.plot(steps, plastic_work, marker="o", color="#f58518", linewidth=1.8)
    panel_label(ax_work, "c")
    ax_work.set_xlabel("step")
    ax_work.set_ylabel("mean history")

    ax_dgamma.plot(steps, plastic_multiplier, marker="o", color="#9467bd", linewidth=1.8)
    panel_label(ax_dgamma, "d")
    ax_dgamma.set_xlabel("step")
    ax_dgamma.set_ylabel("mean increment")

    ax_yield.plot(steps, yield_fraction, marker="o", color="#54a24b", linewidth=1.8)
    panel_label(ax_yield, "e")
    ax_yield.set_xlabel("step")
    ax_yield.set_ylabel("active element fraction")
    ax_yield.set_ylim(-0.05, 1.05)

    width = 0.22
    x = np.arange(len(diagnostic_metrics))
    colors = ["#d62728", "#ff7f0e", "#2ca02c"]
    for i, (case, label, color) in enumerate(zip(case_keys, case_labels, colors)):
        values = [parse_mean(row_by_metric[metric][case]) for metric, _ in diagnostic_metrics]
        ax_diag.bar(x + (i - 1) * width, values, width=width, label=label, color=color, alpha=0.9)
    ax_diag.set_xticks(x)
    ax_diag.set_xticklabels([label for _, label in diagnostic_metrics], fontsize=8)
    panel_label(ax_diag, "f")
    ax_diag.set_ylabel("lower is better")
    ax_diag.legend(frameon=False, fontsize=8)

    for ax in axes.ravel():
        ax.grid(True, alpha=0.25)
    save(fig, "j2_history_rollout_diagnostics")


def make_path_ood_summary() -> None:
    rows = read_csv(TABLE_DIR / "j2_complex_geometry_shared_thermo_path_ood_5seed_primary_table.csv")
    selected = [
        "History relative L2",
        "Eq. plastic strain increment relative L2",
        "Reversal yield-flag MAE",
        "Predicted yield-surface relative RMS",
        "Plastic-work lower-bound violation",
    ]
    case_keys = ["Strict path-OOD", "Unload curriculum", "Cyclic-seen upper bound"]
    case_labels = ["Strict", "Curriculum", "Upper bound"]
    colors = ["#d62728", "#ff7f0e", "#2ca02c"]
    fig, axes = plt.subplots(1, len(selected), figsize=(14.5, 4.0), constrained_layout=True)
    row_by_metric = {row["metric"]: row for row in rows}
    for ax, metric, panel in zip(axes, selected, ["a", "b", "c", "d", "e"]):
        row = row_by_metric[metric]
        values = [parse_mean(row[key]) for key in case_keys]
        ax.bar(case_labels, values, color=colors, alpha=0.9)
        panel_label(ax, panel)
        ax.tick_params(axis="x", rotation=25, labelsize=8)
        ax.grid(True, axis="y", alpha=0.25)
    axes[0].set_ylabel("Lower is better")
    save(fig, "j2_path_ood_summary")


def make_t6_complex_scale() -> None:
    rows = read_csv(REPORT_DIR / "level4_t6_8step_qp_12case_dataset_summary_case_summary.csv")
    family_order = ["multi_hole", "notch", "curved_hole"]
    family_labels = {
        "multi_hole": "multi-hole",
        "notch": "notch",
        "curved_hole": "curved hole",
    }
    colors = {
        "multi_hole": "#4c78a8",
        "notch": "#f58518",
        "curved_hole": "#54a24b",
    }
    mesh_order = ["14x11", "16x12", "18x14", "20x15"]
    mesh_x = np.arange(len(mesh_order))
    by_family = {family: [] for family in family_order}
    for row in rows:
        by_family[row["family"]].append(row)
    for family in family_order:
        by_family[family].sort(key=lambda item: mesh_order.index(item["geometry"].split("_")[-1]))

    fig, axes = plt.subplots(2, 2, figsize=(11.8, 7.2), constrained_layout=True)
    ax_nodes, ax_elements, ax_size, ax_residual = axes.ravel()

    for family in family_order:
        fam_rows = by_family[family]
        node_max = [float(row["node_max"]) for row in fam_rows]
        elem_max = [float(row["element_max"]) for row in fam_rows]
        size_mb = [float(row["size_mb"]) for row in fam_rows]
        ax_nodes.plot(
            mesh_x,
            node_max,
            marker="o",
            linewidth=2.0,
            color=colors[family],
            label=family_labels[family],
        )
        ax_elements.plot(
            mesh_x,
            elem_max,
            marker="o",
            linewidth=2.0,
            color=colors[family],
            label=family_labels[family],
        )
        ax_size.plot(
            mesh_x,
            size_mb,
            marker="o",
            linewidth=2.0,
            color=colors[family],
            label=family_labels[family],
        )

    for ax, ylabel, title in [
        (ax_nodes, "nodes per case", "(a) 1000+ node T6 meshes"),
        (ax_elements, "elements per case", "(b) T6 element counts"),
        (ax_size, "MB per geometry-mesh case", "(c) storage footprint"),
    ]:
        ax.set_xticks(mesh_x)
        ax.set_xticklabels(mesh_order)
        ax.set_xlabel("mesh size")
        ax.set_ylabel(ylabel)
        panel_from_title(ax, title)
        ax.grid(True, alpha=0.25)
    ax_nodes.axhline(1000, color="#8c564b", linewidth=1.0, linestyle="--")
    ax_nodes.text(2.05, 1017, "1000-node level", fontsize=8, color="#8c564b")
    ax_nodes.legend(frameon=False, fontsize=8, loc="upper left")

    residual = np.zeros((len(family_order), len(mesh_order)))
    for i, family in enumerate(family_order):
        for j, row in enumerate(by_family[family]):
            residual[i, j] = float(row["residual_rms_mean"])
    image = ax_residual.imshow(residual, cmap="YlGnBu_r", aspect="auto")
    ax_residual.set_xticks(mesh_x)
    ax_residual.set_xticklabels(mesh_order)
    ax_residual.set_yticks(np.arange(len(family_order)))
    ax_residual.set_yticklabels([family_labels[family] for family in family_order])
    panel_label(ax_residual, "d")
    for i in range(len(family_order)):
        for j in range(len(mesh_order)):
            ax_residual.text(j, i, f"{residual[i, j]:.1e}", ha="center", va="center", fontsize=7.5)
    cbar = fig.colorbar(image, ax=ax_residual, shrink=0.88)
    cbar.set_label("residual RMS")

    total_files = sum(int(row["files"]) for row in rows)
    total_samples = sum(int(row["samples"]) for row in rows)
    save(fig, "t6_complex_scale_matrix")


def make_t6_qp_fem_audit() -> None:
    rows = read_csv(REPORT_DIR / "level4_t6_qp_reversal_audit_three_geometry.csv")
    geometry_order = ["multi_hole", "notch", "curved_hole"]
    geometry_labels = ["multi-hole", "notch", "curved hole"]
    method_specs = [
        ("TINN-style", "reversal_final", "TINN-style", "#8c564b"),
        ("Thermo-hard HistoryGNO", "reversal_final", "HGO hard", "#4c78a8"),
        ("QP-thermo-hard HistoryGNO", "reversal_final", "QP-HGO sel.", "#f58518"),
        ("QP-thermo-hard HistoryGNO", "all", "QP-HGO all", "#54a24b"),
    ]
    by_key = {(row["Geometry"], row["Model"], row["Audit policy"]): row for row in rows}

    fig, axes = plt.subplots(2, 2, figsize=(12.4, 7.4), constrained_layout=True)
    ax_disp, ax_residual, ax_energy, ax_qp = axes.ravel()

    _plot_audit_metric(
        ax_disp,
        by_key,
        geometry_order,
        method_specs,
        "Displacement rel. L2",
        "displacement rel. L2",
        "(a) field prediction",
        log_y=True,
    )
    _plot_audit_metric(
        ax_residual,
        by_key,
        geometry_order,
        method_specs,
        "FEM residual rel. RMS",
        "FEM residual rel. RMS",
        "(b) matrix-free FEM residual",
        log_y=True,
    )
    _plot_audit_metric(
        ax_energy,
        by_key,
        geometry_order,
        method_specs,
        "FEM energy rel. err.",
        "FEM energy rel. error",
        "(c) total potential energy audit",
        log_y=True,
    )

    x = np.arange(len(geometry_order))
    width = 0.28
    qp_specs = [
        ("reversal_final", "selected step", "#f58518"),
        ("all", "all step", "#54a24b"),
    ]
    for offset, (policy, label, color) in zip([-0.16, 0.16], qp_specs):
        means = []
        inc_means = []
        for geometry in geometry_order:
            row = by_key[(geometry, "QP-thermo-hard HistoryGNO", policy)]
            means.append(parse_mean(row["QP history rel. L2"]))
            inc_means.append(parse_mean(row["QP history-inc. rel. L2"]))
        ax_qp.bar(x + offset, means, width=width, color=color, alpha=0.82, label=f"{label}: QP history")
        ax_qp.plot(x + offset, inc_means, marker="D", color="#222222", linewidth=1.1, linestyle="None")
    ax_qp.axhline(1.0, color="#777777", linewidth=0.9, linestyle="--")
    ax_qp.set_xticks(x)
    ax_qp.set_xticklabels(geometry_labels, rotation=15)
    ax_qp.set_ylabel("relative L2")
    panel_label(ax_qp, "d")
    ax_qp.grid(True, axis="y", alpha=0.25)
    ax_qp.legend(frameon=False, fontsize=8)

    save(fig, "t6_qp_fem_audit_evidence")


def make_t6_qp_representative_allstep() -> None:
    rows = read_csv(REPORT_DIR / "level4_t6_qp_allstep_representative_table.csv")
    labels = [
        row["Case"].replace("multi_hole", "multi").replace("curved_hole", "curved").replace("_", "\n")
        for row in rows
    ]
    nodes = [int(row["Nodes"].split("--")[-1]) for row in rows]
    colors = ["#4c78a8", "#4c78a8", "#f58518", "#54a24b"]
    metrics = [
        ("Displacement rel. L2", "disp. rel. L2", "(a) cyclic field error", True),
        ("FEM residual rel. RMS", "residual rel. RMS", "(b) all-step FEM residual", True),
        ("FEM energy rel. err.", "energy rel. error", "(c) all-step energy audit", True),
        ("QP history rel. L2", "QP history rel. L2", "(d) QP memory difficulty", False),
    ]
    fig, axes = plt.subplots(2, 2, figsize=(12.0, 7.0), constrained_layout=True)
    x = np.arange(len(rows))
    for ax, (metric, ylabel, title, log_y) in zip(axes.ravel(), metrics):
        means = []
        stds = []
        for row in rows:
            mean, std = parse_mean_std(row[metric])
            means.append(mean)
            stds.append(std)
        means_arr = np.asarray(means)
        stds_arr = np.asarray(stds)
        if log_y:
            yerr = np.vstack([np.minimum(stds_arr, means_arr * 0.85), stds_arr])
        else:
            yerr = stds_arr
        ax.bar(x, means_arr, color=colors, alpha=0.88, yerr=yerr, capsize=2.5, edgecolor="#333333", linewidth=0.35)
        ax.set_xticks(x)
        ax.set_xticklabels(labels, fontsize=8)
        ax.set_ylabel(ylabel)
        panel_from_title(ax, title)
        if log_y:
            ax.set_yscale("log")
        ax.grid(True, axis="y", alpha=0.25)
        if metric == "QP history rel. L2":
            ax.axhline(1.0, color="#777777", linestyle="--", linewidth=0.9)
    for ax in axes[0]:
        top = ax.get_ylim()[1]
        for idx, node_count in enumerate(nodes):
            if node_count >= 1000:
                ax.text(idx, top * 0.82, "1000+", ha="center", va="center", fontsize=8, color="#8c564b")
    save(fig, "t6_qp_allstep_representative_evidence")


def make_t6_qp_12case_allstep_matrix() -> None:
    rows = read_csv(REPORT_DIR / "level4_t6_qp_allstep_12case_main_table.csv")
    families = ["curved_hole", "multi_hole", "notch"]
    family_labels = ["curved hole", "multi-hole", "notch"]
    sizes = ["14x11", "16x12", "18x14", "20x15"]
    by_case = {row["Case"]: row for row in rows}
    metric_specs = [
        ("Displacement rel. L2", "cyclic field error", False),
        ("FEM residual rel. RMS", "all-step FEM residual", True),
        ("FEM energy rel. err.", "all-step energy audit", True),
        ("QP history rel. L2", "QP memory error", False),
    ]
    fig, axes = plt.subplots(2, 2, figsize=(11.4, 6.8), constrained_layout=True)
    for ax, (metric, title, log_scale), panel in zip(axes.ravel(), metric_specs, ["a", "b", "c", "d"]):
        values = np.zeros((len(families), len(sizes)))
        labels = np.empty(values.shape, dtype=object)
        for i, family in enumerate(families):
            for j, size in enumerate(sizes):
                mean, std = parse_mean_std(by_case[f"{family}_{size}"][metric])
                values[i, j] = mean
                labels[i, j] = f"{mean:.2g}\n±{std:.1g}"
        plotted = np.log10(np.clip(values, 1.0e-12, None)) if log_scale else values
        image = ax.imshow(plotted, cmap="viridis", aspect="auto")
        ax.set_xticks(np.arange(len(sizes)))
        ax.set_xticklabels(sizes)
        ax.set_yticks(np.arange(len(families)))
        ax.set_yticklabels(family_labels)
        panel_label(ax, panel)
        for i in range(values.shape[0]):
            for j in range(values.shape[1]):
                color = "white" if plotted[i, j] > np.nanmean(plotted) else "#111111"
                ax.text(j, i, labels[i, j], ha="center", va="center", fontsize=7.2, color=color)
        fig.colorbar(image, ax=ax, shrink=0.82)
    save(fig, "t6_qp_allstep_12case_matrix")


def _plot_audit_metric(
    ax: plt.Axes,
    by_key: dict[tuple[str, str, str], dict[str, str]],
    geometry_order: list[str],
    method_specs: list[tuple[str, str, str, str]],
    metric: str,
    ylabel: str,
    title: str,
    *,
    log_y: bool = False,
) -> None:
    x = np.arange(len(geometry_order))
    width = 0.18
    offsets = (np.arange(len(method_specs)) - (len(method_specs) - 1) / 2.0) * width
    for offset, (model, policy, label, color) in zip(offsets, method_specs):
        means = []
        stds = []
        for geometry in geometry_order:
            mean, std = parse_mean_std(by_key[(geometry, model, policy)][metric])
            means.append(mean)
            stds.append(std)
        means_arr = np.asarray(means)
        stds_arr = np.asarray(stds)
        if log_y:
            yerr = np.vstack([np.minimum(stds_arr, means_arr * 0.85), stds_arr])
        else:
            yerr = stds_arr
        ax.bar(
            x + offset,
            means_arr,
            width=width,
            color=color,
            alpha=0.85,
            label=label,
            yerr=yerr,
            capsize=2.0,
            linewidth=0.3,
            edgecolor="#333333",
        )
    ax.set_xticks(x)
    ax.set_xticklabels(["multi-hole", "notch", "curved hole"], rotation=15)
    ax.set_ylabel(ylabel)
    panel_from_title(ax, title)
    if log_y:
        ax.set_yscale("log")
    ax.grid(True, axis="y", alpha=0.25)
    ax.legend(frameon=False, fontsize=7.5)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        rows: list[dict[str, str]] = []
        for row in reader:
            rows.append({key.lstrip("\ufeff"): value for key, value in row.items()})
        return rows


def load_j2_npz(family: str, split: str) -> np.lib.npyio.NpzFile:
    return np.load(J2_DATA_DIR / family / f"{split}.npz", allow_pickle=True)


def parse_mean(value: str) -> float:
    return float(value.split("+/-", 1)[0].strip())


def parse_mean_std(value: str) -> tuple[float, float]:
    if "+/-" not in value:
        return float(value.strip()), 0.0
    mean, std = value.split("+/-", 1)
    return float(mean.strip()), float(std.strip())


def pretty_model(name: str) -> str:
    mapping = {
        "pinn": "PINN",
        "deeponet": "DeepONet",
        "fno": "FNO",
        "meshgno": "MeshGNO",
        "mesh2meshgno": "M2M-GNO",
        "pcgno": "PCGNO",
    }
    return mapping.get(name, name)


def short_model(name: str) -> str:
    return (
        name.replace("HistoryGNO thermo-aware", "HGO\nthermo")
        .replace("HistoryGNO data-only", "HGO\ndata")
        .replace("Non-recurrent GNO sequence", "GNO\nseq")
        .replace("Static FNO sequence", "FNO\nseq")
        .replace("Static DeepONet sequence", "DeepONet\nseq")
    )


def save(fig: plt.Figure, stem: str) -> None:
    png = FIG_DIR / f"{stem}.png"
    pdf = FIG_DIR / f"{stem}.pdf"
    fig.savefig(png, dpi=300, bbox_inches="tight")
    fig.savefig(pdf, bbox_inches="tight")
    plt.close(fig)
    print(f"wrote {png}")
    print(f"wrote {pdf}")


if __name__ == "__main__":
    main()
