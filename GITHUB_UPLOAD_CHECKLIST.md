# GitHub upload checklist

## Included in this package

- Full code: `src/pcgno_dt`
- Tests: `tests`
- Reproducibility scripts: `12_reproducibility/scripts`
- Lightweight public data: `data/public_j2_smoke`
- Runnable example: `examples/j2_stateful_fem_audit_example.py`
- Compact reports, tables, and figures: `10_results` and `11_paper`
- CI workflow: `.github/workflows/python-tests.yml`
- Metadata: `AUTHORS.md`, `CITATION.cff`, `CODE_AVAILABILITY.md`,
  `DATA_MANIFEST.md`, `REPRODUCIBILITY.md`, `LICENSE_NOTICE.md`

## Excluded from GitHub

- Main manuscript PDFs and submission-only files.
- Large raw/processed FEM datasets.
- Checkpoints and trained weights.
- Logs, caches, compiled bytecode, and LaTeX intermediates.
- Old release-package snapshots.

## Required before public upload

- Decide whether to add a real open-source `LICENSE`.
- Confirm final author/citation metadata.
- If full data are to be public, deposit them in Zenodo, OSF, institutional
  storage, or another data archive and add the DOI/link here.
- Run the package checks below.

```powershell
python -m pip install -e .[dev]
python -m pytest tests/unit -q
python examples\j2_stateful_fem_audit_example.py
```

Suggested first commit message:

```text
Release mechanics-audited stateful operator research code
```
