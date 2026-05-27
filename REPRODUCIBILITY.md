# Reproducibility guide

## Environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e .[dev]
```

## Lightweight verification

```powershell
python -m pytest tests/unit -q
python examples\j2_stateful_fem_audit_example.py
```

For Windows `.cmd` and `.ps1` campaign launchers, set `PYTHON_EXE` to choose a
specific interpreter. If it is not set, the scripts use `python` from the active
environment.

```powershell
$env:PYTHON_EXE = "python"
```

## Smoke experiment

```powershell
python 12_reproducibility\scripts\run_minimal_operator_demo.py --family structural
```

## Formal evidence chain

The repository includes scripts and compact summaries for:

1. FEM snapshot fair baselines.
2. J2 path-dependent static and recurrent baselines.
3. Strict, curriculum, and upper-bound path-OOD diagnostics.
4. Complex T6/QP all-step audit.
5. Solver-in-loop diagnostics.
6. Sparse-observation posterior calibration.

Full formal reruns can be expensive and may require regenerating the large FEM
datasets that are not committed to GitHub. The entry points are under
`12_reproducibility/scripts`; curated main-paper artifacts are under `11_paper`.
New local reruns may write temporary outputs under `10_results`, which is not
part of the public main-paper artifact set.
