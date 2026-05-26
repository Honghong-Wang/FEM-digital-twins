from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
MANUSCRIPT_ROOT = PROJECT_ROOT / "11_paper" / "manuscript"
FIGURE_ROOT = PROJECT_ROOT / "11_paper" / "figures"
TABLE_ROOT = PROJECT_ROOT / "11_paper" / "tables"
RESULT_ROOT = PROJECT_ROOT / "10_results"
REPORT_ROOT = RESULT_ROOT / "reports"


KEY_TABLES = (
    ("FEM fair baseline", "fem2d_final_fair_baseline_table.csv", 6),
    ("J2 stateful baseline", "j2_path_dependent_baseline_table.csv", 5),
    ("Complex T6/QP all-step audit", "level4_t6_qp_allstep_12case_main_table.csv", 12),
    ("Multi-geometry multi-path matrix", "level4_multigeometry_multipath_matrix_case_path.csv", 144),
    ("Faithful frontier baseline", "frontier_faithful_baseline_table.csv", 5),
    ("Solver-in-loop formal main", "solver_in_loop_formal_main_table.csv", 20),
    ("Posterior calibration main", "j2_sparse_dt_posterior_calibration_main_table.csv", 4),
    ("QP-history protocol reduction", "level6_qp_history_reduction_summary.csv", 4),
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Audit manuscript workload and evidence artifacts for the EAAI/CMAME paper."
    )
    parser.add_argument(
        "--tex",
        type=Path,
        default=MANUSCRIPT_ROOT / "eaai_main.tex",
        help="Main manuscript TeX file.",
    )
    parser.add_argument(
        "--bib",
        type=Path,
        default=MANUSCRIPT_ROOT / "references.bib",
        help="BibTeX database.",
    )
    parser.add_argument(
        "--json-out",
        type=Path,
        default=REPORT_ROOT / "manuscript_workload_audit.json",
    )
    parser.add_argument(
        "--md-out",
        type=Path,
        default=REPORT_ROOT / "manuscript_workload_audit.md",
    )
    args = parser.parse_args()

    payload = audit(args.tex, args.bib)
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    args.md_out.write_text(to_markdown(payload), encoding="utf-8")

    print(f"journal_fit={payload['assessment']['journal_fit']}")
    print(f"main_risk={payload['assessment']['main_risk']}")
    print(f"wrote {args.json_out}")
    print(f"wrote {args.md_out}")


def audit(tex_path: Path, bib_path: Path) -> dict:
    tex = _read_text(tex_path)
    bib = _read_text(bib_path)
    pdf_path = tex_path.with_suffix(".pdf")
    log_path = tex_path.with_suffix(".log")

    manuscript = {
        "tex": str(tex_path),
        "pdf": str(pdf_path),
        "pdf_exists": pdf_path.exists(),
        "pdf_size_bytes": pdf_path.stat().st_size if pdf_path.exists() else 0,
        "pdf_last_write": _mtime(pdf_path),
        "pdf_pages_from_log": _pages_from_log(log_path),
        "sections": _count(r"\\section\{", tex),
        "subsections": _count(r"\\subsection\{", tex),
        "tables": _count(r"\\begin\{table\}", tex),
        "figures": _count(r"\\begin\{figure\}", tex),
        "included_graphics": _count(r"\\includegraphics", tex),
        "captions": _count(r"\\caption\{", tex),
        "citations": _count(r"\\cite", tex),
        "bib_entries": _count(r"(?m)^@", bib),
    }

    files = {
        "figures": _file_summary(FIGURE_ROOT),
        "paper_tables": _file_summary(TABLE_ROOT),
        "result_reports": _file_summary(REPORT_ROOT),
        "result_tree": _file_summary(RESULT_ROOT),
    }
    evidence = [_check_table_rows(name, TABLE_ROOT / filename, min_rows) for name, filename, min_rows in KEY_TABLES]
    readiness = _read_json(REPORT_ROOT / "level6_readiness_status.json")
    assessment = _assessment(manuscript, evidence, readiness)

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "manuscript": manuscript,
        "files": files,
        "evidence_checks": evidence,
        "level6_readiness": readiness,
        "assessment": assessment,
    }


def _assessment(manuscript: dict, evidence: list[dict], readiness: dict | None) -> dict:
    passed = sum(1 for item in evidence if item["pass"])
    pages = manuscript["pdf_pages_from_log"] or 0
    tables = manuscript["tables"]
    figures = manuscript["included_graphics"]
    refs = manuscript["bib_entries"]

    if passed >= 7 and tables >= 12 and figures >= 8 and refs >= 30:
        journal_fit = "EAAI workload sufficient to strong"
    elif passed >= 5 and tables >= 8 and figures >= 5 and refs >= 25:
        journal_fit = "EAAI workload borderline but usable"
    else:
        journal_fit = "Workload not yet submission-grade"

    if pages > 45 or tables > 18:
        main_risk = "main manuscript is evidence-rich but overlong; move secondary tables to supplement"
    elif refs < 40:
        main_risk = "reference base is acceptable but can be expanded for top-journal positioning"
    else:
        main_risk = "no major workload-format risk"

    notes = [
        "Workload is judged from generated manuscript artifacts, not from claimed intent.",
        "QP-history evidence should be framed as failure/repair diagnosis unless relative errors clearly decrease.",
        "Posterior calibration is strong for EAAI if presented as digital-twin uncertainty evidence with honest scope.",
    ]
    if readiness:
        notes.append(f"Existing readiness evaluator reports: {readiness.get('level', 'unknown')}.")

    return {
        "journal_fit": journal_fit,
        "main_risk": main_risk,
        "evidence_passed": passed,
        "evidence_total": len(evidence),
        "notes": notes,
    }


def _check_table_rows(name: str, path: Path, min_rows: int) -> dict:
    rows = _read_csv_rows(path)
    return {
        "name": name,
        "path": str(path),
        "rows": len(rows),
        "required_rows": min_rows,
        "pass": len(rows) >= min_rows,
    }


def _file_summary(root: Path) -> dict:
    if not root.exists():
        return {"root": str(root), "exists": False, "total_files": 0, "extensions": {}}
    files = [path for path in root.rglob("*") if path.is_file()]
    extensions = Counter(path.suffix.lower() or "<no_ext>" for path in files)
    return {
        "root": str(root),
        "exists": True,
        "total_files": len(files),
        "extensions": dict(sorted(extensions.items(), key=lambda item: (-item[1], item[0]))),
    }


def _read_csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists() or path.stat().st_size == 0:
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _read_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def _pages_from_log(path: Path) -> int | None:
    text = _read_text(path)
    matches = re.findall(r"Output written on .*?\((\d+) pages?", text)
    if not matches:
        return None
    return int(matches[-1])


def _mtime(path: Path) -> str | None:
    if not path.exists():
        return None
    return datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).isoformat()


def _read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="ignore")


def _count(pattern: str, text: str) -> int:
    return len(re.findall(pattern, text))


def to_markdown(payload: dict) -> str:
    manuscript = payload["manuscript"]
    assessment = payload["assessment"]
    lines = [
        "# Manuscript workload audit",
        "",
        f"- generated_at: {payload['generated_at']}",
        f"- journal_fit: {assessment['journal_fit']}",
        f"- main_risk: {assessment['main_risk']}",
        f"- evidence_checks: {assessment['evidence_passed']} / {assessment['evidence_total']}",
        "",
        "## Manuscript size",
        "",
        "| Item | Value |",
        "| --- | ---: |",
    ]
    for key in [
        "pdf_pages_from_log",
        "sections",
        "subsections",
        "tables",
        "figures",
        "included_graphics",
        "captions",
        "citations",
        "bib_entries",
        "pdf_size_bytes",
    ]:
        lines.append(f"| {key} | {manuscript.get(key)} |")

    lines.extend(
        [
            "",
            "## Evidence checks",
            "",
            "| Evidence | Rows | Required | Pass |",
            "| --- | ---: | ---: | --- |",
        ]
    )
    for check in payload["evidence_checks"]:
        lines.append(
            f"| {check['name']} | {check['rows']} | {check['required_rows']} | {check['pass']} |"
        )

    lines.extend(["", "## File inventory", "", "| Root | Files | Extension summary |", "| --- | ---: | --- |"])
    for key in ["figures", "paper_tables", "result_reports", "result_tree"]:
        summary = payload["files"][key]
        ext = ", ".join(f"{suffix}:{count}" for suffix, count in summary["extensions"].items())
        lines.append(f"| {key} | {summary['total_files']} | {ext} |")

    lines.extend(["", "## Assessment notes", ""])
    for note in assessment["notes"]:
        lines.append(f"- {note}")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
