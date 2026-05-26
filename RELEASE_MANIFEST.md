# Release manifest

Package name:

```text
github_full_code_release_20260524_v2
```

Purpose:

```text
Full public code package for GitHub upload.
```

Main contents:

| Path | Purpose |
| --- | --- |
| `src/pcgno_dt` | Core Python package for data interfaces, models, physics callbacks, training losses, evaluation, inverse problems, and uncertainty calibration. |
| `tests` | Unit and integration tests. |
| `12_reproducibility/scripts` | Dataset generators, formal campaign runners, table builders, figure builders, and audit utilities. |
| `examples` | Lightweight J2 path/FEM-audit example. |
| `data/public_j2_smoke` | Small public J2 path smoke dataset. |
| `10_results` | Compact reports, tables, and figures. |
| `11_paper` | Paper figures and curated evidence tables, without main manuscript PDFs. |
| `.github/workflows` | GitHub Actions unit-test workflow. |

Excluded:

```text
large FEM datasets, checkpoints, logs, caches, old release snapshots, manuscript PDFs
```
