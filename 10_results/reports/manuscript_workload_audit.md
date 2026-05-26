# Manuscript workload audit

- generated_at: 2026-05-24T09:25:50.346653+00:00
- journal_fit: EAAI workload sufficient to strong
- main_risk: no major workload-format risk
- evidence_checks: 8 / 8

## Manuscript size

| Item | Value |
| --- | ---: |
| pdf_pages_from_log | 23 |
| sections | 4 |
| subsections | 2 |
| tables | 12 |
| figures | 14 |
| included_graphics | 14 |
| captions | 26 |
| citations | 10 |
| bib_entries | 45 |
| pdf_size_bytes | 1005635 |

## Evidence checks

| Evidence | Rows | Required | Pass |
| --- | ---: | ---: | --- |
| FEM fair baseline | 6 | 6 | True |
| J2 stateful baseline | 5 | 5 | True |
| Complex T6/QP all-step audit | 12 | 12 | True |
| Multi-geometry multi-path matrix | 144 | 144 | True |
| Faithful frontier baseline | 5 | 5 | True |
| Solver-in-loop formal main | 20 | 20 | True |
| Posterior calibration main | 45 | 4 | True |
| QP-history protocol reduction | 4 | 4 | True |

## File inventory

| Root | Files | Extension summary |
| --- | ---: | --- |
| figures | 34 | .pdf:17, .png:17 |
| paper_tables | 362 | .csv:185, .md:177 |
| result_reports | 1962 | .csv:879, .md:725, .json:354, .log:4 |
| result_tree | 1990 | .csv:879, .md:725, .json:354, .log:31, .txt:1 |

## Assessment notes

- Workload is judged from generated manuscript artifacts, not from claimed intent.
- QP-history evidence should be framed as failure/repair diagnosis unless relative errors clearly decrease.
- Posterior calibration is strong for EAAI if presented as digital-twin uncertainty evidence with honest scope.
- Existing readiness evaluator reports: Level 6+.
