# Full code release check

Date: 2026-05-24

Package:

```text
github_full_code_release_20260524_v2
```

## Scope

This package is prepared for a public GitHub upload of the full research code.
It includes source code, tests, reproducibility scripts, compact evidence
artifacts, a small public dataset, and a runnable example.

## Verification

| Check | Result |
| --- | --- |
| Unit tests | `35 passed` |
| Public example | completed and wrote summary/figure during verification |
| Python bytecode/cache scan | clean after verification cleanup |
| Logs/checkpoints/archives scan | clean |
| Manuscript PDF scan | no main manuscript PDFs included |
| Sensitive-string scan | no obvious API keys, passwords, or tokens found |
| Largest-file scan | largest files are compact JSON/CSV reports and figure assets |

## Public boundary

Included:

- Full package code under `src/pcgno_dt`.
- Tests under `tests`.
- Reproducibility scripts under `12_reproducibility/scripts`.
- Public smoke data under `data/public_j2_smoke`.
- Compact evidence artifacts under `10_results` and `11_paper`.

Excluded:

- Large raw and processed FEM datasets.
- Model checkpoints and trained weights.
- Runtime logs and caches.
- Main manuscript PDFs and submission-only files.

## Remaining pre-upload decision

An explicit `LICENSE` file has not been selected. The package currently includes
`LICENSE_NOTICE.md`; choose a real license before making the GitHub repository
public if reuse is intended.
