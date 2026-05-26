from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
TABLE_ROOT = PROJECT_ROOT / "11_paper" / "tables"
REPORT_ROOT = PROJECT_ROOT / "10_results" / "reports"


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate CMAME Level-6 readiness from audited evidence artifacts.")
    parser.add_argument(
        "--json-out",
        type=Path,
        default=REPORT_ROOT / "level6_readiness_status.json",
    )
    parser.add_argument(
        "--md-out",
        type=Path,
        default=REPORT_ROOT / "level6_readiness_status.md",
    )
    args = parser.parse_args()

    checks = [
        _check_file_rows("FEM fair baseline", TABLE_ROOT / "fem2d_final_fair_baseline_table.csv", min_rows=6),
        _check_file_rows("J2 stateful baseline", TABLE_ROOT / "j2_path_dependent_baseline_table.csv", min_rows=5),
        _check_file_rows("Complex T6/QP all-step audit", TABLE_ROOT / "level4_t6_qp_allstep_12case_main_table.csv", min_rows=12),
        _check_file_rows(
            "Multi-geometry multi-path matrix",
            TABLE_ROOT / "level4_multigeometry_multipath_matrix_case_path.csv",
            min_rows=144,
        ),
        _check_file_rows("Faithful frontier baseline", TABLE_ROOT / "frontier_faithful_baseline_table.csv", min_rows=5),
        _check_solver_in_loop(),
        _check_qp_history(),
        _check_posterior_calibration(),
    ]

    passed = sum(1 for check in checks if check["pass"])
    blocking = [check for check in checks if not check["pass"] and check["severity"] == "blocker"]
    warnings = [check for check in checks if not check["pass"] and check["severity"] == "warning"]
    level = _level_from_checks(checks)
    next_actions = _next_actions(checks)
    payload = {
        "level": level,
        "passed_checks": passed,
        "total_checks": len(checks),
        "blocking_gaps": [check["name"] for check in blocking],
        "warnings": [check["name"] for check in warnings],
        "checks": checks,
        "next_actions": next_actions,
    }

    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    args.md_out.write_text(_markdown(payload), encoding="utf-8")
    print(f"level={level}")
    print(f"passed={passed}/{len(checks)}")
    print(f"blocking_gaps={len(blocking)}")
    print(f"wrote {args.json_out}")
    print(f"wrote {args.md_out}")


def _check_file_rows(name: str, path: Path, min_rows: int, severity: str = "blocker") -> dict:
    rows = _read_rows(path)
    return {
        "name": name,
        "pass": len(rows) >= min_rows,
        "severity": severity,
        "path": str(path),
        "actual": len(rows),
        "required": min_rows,
        "note": f"requires at least {min_rows} rows",
    }


def _check_solver_in_loop() -> dict:
    official = TABLE_ROOT / "solver_in_loop_formal_main_table.csv"
    case_rows = TABLE_ROOT / "solver_in_loop_formal_main_case_rows.csv"
    tmp = TABLE_ROOT / "tmp_solver_in_loop_formal_main_table.csv"
    path = official if official.exists() else tmp
    rows = _read_rows(path)
    cases = {row.get("Case", "") for row in _read_rows(case_rows)}
    if not cases and tmp.exists():
        tmp_case_rows = TABLE_ROOT / "tmp_solver_in_loop_formal_main_case_rows.csv"
        cases = {row.get("Case", "") for row in _read_rows(tmp_case_rows)}
    load_paths = {row.get("Load path", "") for row in rows}
    ablations = {row.get("Ablation id", "") for row in rows}
    official_ready = official.exists() and case_rows.exists()
    pass_check = official_ready and len(cases) >= 3 and len(load_paths) >= 4 and len(ablations) >= 5
    return {
        "name": "Solver-in-loop formal evidence",
        "pass": pass_check,
        "severity": "blocker",
        "path": str(path),
        "actual": {
            "official_ready": official_ready,
            "main_rows": len(rows),
            "cases": len(cases),
            "load_paths": len(load_paths),
            "ablations": len(ablations),
        },
        "required": {
            "official_ready": True,
            "cases": ">=3",
            "load_paths": ">=4",
            "ablations": ">=5",
        },
        "note": "tmp single-case diagnostics do not count as Level-6 solver-in-loop evidence",
    }


def _check_qp_history() -> dict:
    summary = TABLE_ROOT / "qp_history_repair_notch16_summary.csv"
    rows = _read_rows(summary)
    has_formal_rows = len(rows) >= 7
    # This remains a warning rather than a hard failure because CMAME can accept a strong failure-analysis story
    # if the manuscript does not claim that QP memory is fully solved.
    return {
        "name": "QP history learning evidence",
        "pass": has_formal_rows,
        "severity": "warning",
        "path": str(summary),
        "actual": len(rows),
        "required": ">=7 diagnostic rows plus honest limitation framing",
        "note": "passes only as failure/repair diagnosis unless QP history relative errors demonstrably decrease",
    }


def _check_posterior_calibration() -> dict:
    audit = REPORT_ROOT / "j2_sparse_dt_posterior_calibration_formal_audit.md"
    status_json = REPORT_ROOT / "level6_readiness_status.json"
    main = TABLE_ROOT / "j2_sparse_dt_posterior_calibration_main_table.csv"
    rows = _read_rows(main)
    text = audit.read_text(encoding="utf-8") if audit.exists() else ""
    formal_pass = "audit_pass: True" in text or "audit_pass=True" in text
    current_evidence = len(rows) >= 4
    return {
        "name": "Digital-twin posterior calibration formal evidence",
        "pass": formal_pass,
        "severity": "warning",
        "path": str(audit if audit.exists() else main),
        "actual": {
            "formal_audit_pass": formal_pass,
            "current_rows": len(rows),
            "current_evidence_available": current_evidence,
        },
        "required": "9-condition formal audit pass for Level-6+ digital-twin claim",
        "note": "current 5-seed/2-sample evidence is usable as auxiliary evidence, not a full formal main claim",
    }


def _level_from_checks(checks: list[dict]) -> str:
    blockers = [check for check in checks if check["severity"] == "blocker"]
    warning_failures = [check for check in checks if check["severity"] == "warning" and not check["pass"]]
    if any(not check["pass"] for check in blockers):
        return "Level 4A+"
    if warning_failures:
        return "Level 6-CMAME-ready with warnings"
    return "Level 6+"


def _next_actions(checks: list[dict]) -> list[str]:
    failed = {check["name"]: check for check in checks if not check["pass"]}
    actions: list[str] = []
    if "Solver-in-loop formal evidence" in failed:
        actions.append(
            "Run solver-in-loop formal suite on at least 3 complex cases and 4 eval paths, then write official tables."
        )
    if "Digital-twin posterior calibration formal evidence" in failed:
        actions.append(
            "Keep posterior calibration as auxiliary evidence until the 9-condition formal matrix can be run and audited; do not block CMAME Level-6 readiness on this warning."
        )
    if "QP history learning evidence" in failed:
        actions.append("Run a 5-seed QP-history repair table and report history-increment/reversal metrics.")
    if not actions:
        actions.append("Update manuscript language to Level-6 CMAME strong-claim mode and recompile.")
    return actions


def _read_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists() or path.stat().st_size == 0:
        return []
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def _markdown(payload: dict) -> str:
    lines = [
        "# Level-6 readiness status",
        "",
        f"- current_level: {payload['level']}",
        f"- passed_checks: {payload['passed_checks']} / {payload['total_checks']}",
        f"- blocking_gaps: {', '.join(payload['blocking_gaps']) if payload['blocking_gaps'] else 'none'}",
        f"- warnings: {', '.join(payload['warnings']) if payload['warnings'] else 'none'}",
        "",
        "## Checks",
        "",
        "| Check | Pass | Severity | Actual | Required | Note |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for check in payload["checks"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    str(check["name"]),
                    str(check["pass"]),
                    str(check["severity"]),
                    str(check["actual"]).replace("|", "/"),
                    str(check["required"]).replace("|", "/"),
                    str(check["note"]).replace("|", "/"),
                ]
            )
            + " |"
        )
    lines.extend(["", "## Next Actions", ""])
    for item in payload["next_actions"]:
        lines.append(f"- {item}")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
