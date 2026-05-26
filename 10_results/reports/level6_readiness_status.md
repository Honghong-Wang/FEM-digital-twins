# Level-6 readiness status

- current_level: Level 6+
- passed_checks: 8 / 8
- blocking_gaps: none
- warnings: none

## Checks

| Check | Pass | Severity | Actual | Required | Note |
| --- | --- | --- | --- | --- | --- |
| FEM fair baseline | True | blocker | 6 | 6 | requires at least 6 rows |
| J2 stateful baseline | True | blocker | 5 | 5 | requires at least 5 rows |
| Complex T6/QP all-step audit | True | blocker | 12 | 12 | requires at least 12 rows |
| Multi-geometry multi-path matrix | True | blocker | 144 | 144 | requires at least 144 rows |
| Faithful frontier baseline | True | blocker | 5 | 5 | requires at least 5 rows |
| Solver-in-loop formal evidence | True | blocker | {'official_ready': True, 'main_rows': 20, 'cases': 3, 'load_paths': 4, 'ablations': 5} | {'official_ready': True, 'cases': '>=3', 'load_paths': '>=4', 'ablations': '>=5'} | tmp single-case diagnostics do not count as Level-6 solver-in-loop evidence |
| QP history learning evidence | True | warning | 7 | >=7 diagnostic rows plus honest limitation framing | passes only as failure/repair diagnosis unless QP history relative errors demonstrably decrease |
| Digital-twin posterior calibration formal evidence | True | warning | {'formal_audit_pass': True, 'current_rows': 45, 'current_evidence_available': True} | 9-condition formal audit pass for Level-6+ digital-twin claim | current 5-seed/2-sample evidence is usable as auxiliary evidence, not a full formal main claim |

## Next Actions

- Keep manuscript language aligned with the EAAI scope: mechanics-audited stateful operator evidence with explicit claim boundaries.
