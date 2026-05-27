# Mechanics-audited stateful operators for path-dependent FEM digital twins

This repository contains the full research code for the study

> Mechanics-audited stateful operators for path-dependent finite-element digital twins

The code supports experiments on stateful neural operators for nonlinear
finite-element J2 plasticity paths. The main question is whether learned
finite-element digital twins should be judged only by field accuracy, or also by
history rollout, finite-element residuals, energy audits, path out-of-distribution
behavior, and sparse-observation calibration.

## Authorship

- Author: HH
- Affiliations: UCL; FYNU
- Repository status: GitHub-ready full code release package

See `AUTHORS.md` and `CITATION.cff` for citation metadata.

## What is included

- Full Python package under `src/pcgno_dt`.
- Unit and integration tests under `tests`.
- Dataset generation, experiment, audit, table, and figure scripts under
  `12_reproducibility/scripts`.
- Public smoke data under `data/public_j2_smoke`.
- Lightweight runnable example under `examples`.
- Curated result tables, reports, and paper figures under `10_results` and
  `11_paper`.
- GitHub Actions workflow for unit-test validation.

The paper PDF is not included in this code-release package. The repository
contains code, public example data, and compact evidence artifacts needed to
inspect the computational chain.

## Quick start

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e .[dev]
python -m pytest tests/unit -q
```

Run a small smoke example:

```powershell
python examples\j2_stateful_fem_audit_example.py
```

Run a minimal operator demo:

```powershell
python 12_reproducibility\scripts\run_minimal_operator_demo.py --family structural
```

For Windows campaign scripts, set `PYTHON_EXE` to select a specific interpreter;
otherwise the scripts use `python` from the active environment.

```powershell
$env:PYTHON_EXE = "python"
```

The supported lightweight release checks are Python compilation, unit tests,
integration tests, example execution, and evidence artifact audits. Static
typing is partial for the NumPy/SciPy/Torch numerical kernels and is not used as
a release gate.

## Reproducibility entry points

The formal campaigns are represented by executable scripts and frozen compact
result summaries. Full reruns can be computationally expensive; the package
therefore separates lightweight checks from formal long-run campaigns.

```text
FEM snapshot baseline:
  12_reproducibility/scripts/run_fem2d_baseline_runner.py

J2 path-dependent baselines:
  12_reproducibility/scripts/run_j2_path_dependent_baseline_table.py

Path-OOD comparison:
  12_reproducibility/scripts/run_j2_path_ood_comparison.py

Complex T6/QP all-step audit:
  12_reproducibility/scripts/run_level4_t6_qp_allstep_12case_suite.py

Solver audit:
  12_reproducibility/scripts/run_solver_in_loop_formal_main_suite.py

Sparse-observation posterior calibration:
  12_reproducibility/scripts/run_j2_sparse_dt_posterior_calibration_main_suite.py
```

## Data policy

GitHub is used for code, compact evidence tables, figures, and a small public
smoke dataset. Large processed FEM datasets, raw archives, checkpoints, and long
training folders are intentionally excluded and should be deposited in a data
archive if the full formal campaign is released.

See `DATA_MANIFEST.md` and `CODE_AVAILABILITY.md`.

## License

No open-source license has been selected in this package. Until a `LICENSE` file
is added, the default legal status is all rights reserved by the copyright
holder. See `LICENSE_NOTICE.md`.
