# Code availability

This package is prepared as a full public code release for the project

> Mechanics-audited stateful operators for path-dependent finite-element digital twins.

## Public code contents

- Full source package: `src/pcgno_dt`.
- Unit and integration tests: `tests`.
- Reproducibility scripts: `12_reproducibility/scripts`.
- Configuration and protocol notes: `05_data_pipeline`, `06_models`,
  `07_training`, `08_experiments`, and `09_validation_verification`.
- Compact evidence artifacts: `10_results` and `11_paper`.
- Public smoke data and runnable example: `data/public_j2_smoke` and `examples`.

## Excluded large artifacts

- Large raw FEM archives.
- Regenerated full processed datasets.
- Long formal training directories.
- Model checkpoints and temporary logs.
- Local caches and build intermediates.
- Main paper PDF and private editorial files.

## Reproduction boundary

The repository is intended to make the computational method inspectable and to
support local smoke tests. Complete formal reruns require additional compute and
may require regenerating or separately downloading large FEM datasets.

## Maintainer

- HH
- Affiliations: UCL; FYNU
