from __future__ import annotations

import argparse
import csv
from pathlib import Path

import numpy as np


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA_ROOT = (
    PROJECT_ROOT / "05_data_pipeline" / "processed" / "level4_formal_complex_j2_t6_8step_qp_9case"
)
REPORT_DIR = PROJECT_ROOT / "10_results" / "reports"
CHANNELS = (
    ("eqp", 0),
    ("plastic_work", 1),
    ("plastic_multiplier", 2),
    ("yield_flag", 3),
    ("von_mises", 4),
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Diagnose why QP-level material history is hard to learn in complex J2 path data."
    )
    parser.add_argument("--data-root", type=Path, default=DEFAULT_DATA_ROOT)
    parser.add_argument(
        "--cases",
        default="notch_16x12,notch_20x15,multi_hole_18x14,curved_hole_18x14",
        help="Comma-separated case directories to inspect.",
    )
    parser.add_argument("--paths", default="monotonic,cyclic,nonproportional")
    parser.add_argument("--split", default="test")
    parser.add_argument("--csv-out", type=Path, default=REPORT_DIR / "qp_history_learning_gap_diagnostics.csv")
    parser.add_argument("--md-out", type=Path, default=REPORT_DIR / "qp_history_learning_gap_diagnostics.md")
    args = parser.parse_args()

    rows: list[dict[str, str]] = []
    for case in _items(args.cases):
        for load_path in _items(args.paths):
            path = args.data_root / case / load_path / f"{args.split}.npz"
            if not path.exists():
                continue
            rows.extend(_diagnose_file(case, load_path, args.split, path))
    _write_csv(args.csv_out, rows)
    _write_markdown(args.md_out, rows)
    print(f"wrote {args.csv_out}")
    print(f"wrote {args.md_out}")


def _diagnose_file(case: str, load_path: str, split: str, path: Path) -> list[dict[str, str]]:
    with np.load(path) as data:
        qp = data["material_history_qp_sequence"].astype(np.float64)
        element = data["material_history_sequence"].astype(np.float64)
        nodes = int(data["coords"].shape[1])
        elements = int(qp.shape[2])
    if qp.ndim != 5:
        raise ValueError(f"{path} material_history_qp_sequence must have [sample, step, element, qp, channel]")
    expanded_element = np.repeat(element[:, :, :, None, :], qp.shape[3], axis=3)
    persistence = np.zeros_like(qp)
    if qp.shape[1] > 1:
        persistence[:, 1:] = qp[:, :-1]
    rows = []
    for channel_name, channel in CHANNELS:
        target = qp[..., channel]
        elem_pred = expanded_element[..., channel]
        persist_pred = persistence[..., channel]
        qp_mean = target.mean(axis=3, keepdims=True)
        rows.append(
            {
                "Case": case,
                "Path": load_path,
                "Split": split,
                "Samples": str(int(qp.shape[0])),
                "Steps": str(int(qp.shape[1])),
                "Nodes": str(nodes),
                "Elements": str(elements),
                "QPs": str(int(qp.shape[3])),
                "Channel": channel_name,
                "Target RMS": _fmt(_rms(target)),
                "Target nonzero frac": _fmt(float(np.mean(np.abs(target) > 1.0e-12))),
                "QP spread / target": _fmt(_relative_rmse(target, np.repeat(qp_mean, qp.shape[3], axis=3))),
                "Element-mean baseline rel. L2": _fmt(_relative_rmse(elem_pred, target)),
                "Persistence baseline rel. L2": _fmt(_relative_rmse(persist_pred, target)),
            }
        )
    rows.append(
        {
            "Case": case,
            "Path": load_path,
            "Split": split,
            "Samples": str(int(qp.shape[0])),
            "Steps": str(int(qp.shape[1])),
            "Nodes": str(nodes),
            "Elements": str(elements),
            "QPs": str(int(qp.shape[3])),
            "Channel": "all",
            "Target RMS": _fmt(_rms(qp)),
            "Target nonzero frac": _fmt(float(np.mean(np.abs(qp) > 1.0e-12))),
            "QP spread / target": _fmt(_relative_rmse(qp, np.repeat(qp.mean(axis=3, keepdims=True), qp.shape[3], axis=3))),
            "Element-mean baseline rel. L2": _fmt(_relative_rmse(expanded_element, qp)),
            "Persistence baseline rel. L2": _fmt(_relative_rmse(persistence, qp)),
        }
    )
    return rows


def _relative_rmse(prediction: np.ndarray, target: np.ndarray, eps: float = 1.0e-12) -> float:
    return float(np.sqrt(np.mean((prediction - target) ** 2)) / max(np.sqrt(np.mean(target**2)), eps))


def _rms(values: np.ndarray) -> float:
    return float(np.sqrt(np.mean(values**2)))


def _write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    lines = [
        "# QP History Learning-Gap Diagnostics",
        "",
        "The element-mean baseline expands the exported element history to all quadrature points. "
        "A large gap indicates that element-averaged state is insufficient for QP-level memory.",
        "",
    ]
    if rows:
        headers = list(rows[0])
        lines.append("| " + " | ".join(headers) + " |")
        lines.append("| " + " | ".join(["---", *["---:" for _ in headers[1:]]]) + " |")
        for row in rows:
            lines.append("| " + " | ".join(row.get(header, "") for header in headers) + " |")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _items(value: str) -> tuple[str, ...]:
    return tuple(item.strip() for item in value.split(",") if item.strip())


def _fmt(value: float) -> str:
    return f"{value:.6g}"


if __name__ == "__main__":
    main()
