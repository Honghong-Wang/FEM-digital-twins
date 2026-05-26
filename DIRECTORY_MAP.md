# Directory map

This package is organized as a public code repository rather than as a manuscript
submission folder.

## Core code

- `src/pcgno_dt/physics`: residuals, thermodynamic diagnostics, material-state
  utilities, and J2 return/projection helpers.
- `src/pcgno_dt/numerics`: FEM adapters, solver callbacks, J2 plasticity
  utilities, and numerical baselines.
- `src/pcgno_dt/data`: schemas, loaders, mesh I/O, normalizers, and dataset
  wrappers.
- `src/pcgno_dt/models`: static, graph, recurrent, history-aware, and
  frontier-style neural operators.
- `src/pcgno_dt/training`: loss terms, balancing utilities, path losses, and
  training support.
- `src/pcgno_dt/evaluation`: field metrics, mechanics diagnostics, robust
  statistics, and path-history metrics.
- `src/pcgno_dt/inverse`: sparse-observation and parameter/history assimilation
  utilities.
- `src/pcgno_dt/uq`: conformal and calibration utilities.

## Experiments and verification

- `12_reproducibility/scripts`: dataset generation, experiment runners, formal
  campaign entry points, table builders, figure builders, and audit scripts.
- `tests`: unit and integration tests.
- `.github/workflows`: GitHub Actions workflow for unit tests and the public
  smoke example.
- `examples`: lightweight J2 path/FEM-audit demonstration.

## Data and compact evidence

- `data/public_j2_smoke`: small public smoke dataset.
- `05_data_pipeline`: data schema and protocol notes, without large processed
  datasets.
- `10_results`: compact reports, tables, and figures.
- `11_paper`: paper figures and evidence tables only; manuscript PDFs and
  submission files are not included.

## Research notes retained for context

- `03_physics_models`: modeling-scope notes.
- `04_numerics_baselines`: baseline-plan notes.
- `06_models`: architecture notes.
- `07_training`: training protocol and base config.
- `08_experiments`: experiment-matrix notes.
- `09_validation_verification`: verification and validation notes.
