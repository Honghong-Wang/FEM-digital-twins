# Data manifest

This GitHub package includes a small public smoke dataset for testing data
loading, path rollout, and FEM-audit utilities. It does not include the full
formal FEM benchmark.

Dataset root:

```text
data/public_j2_smoke/j2_path_operator_evidence_smoke
```

| File | Bytes | SHA256 |
| --- | ---: | --- |
| `data/public_j2_smoke/j2_path_operator_evidence_smoke/cyclic/test.npz` | 28986 | `EA646748F2D88D90B6CF240562CC0462A6FE7E1D8EFA6BC64104B2174B5C8590` |
| `data/public_j2_smoke/j2_path_operator_evidence_smoke/monotonic/test.npz` | 28998 | `7B1B2C458949EFD7132A4D4E5A86FD36D008C99C90BCD36B3B88FEDD76F1FBD7` |
| `data/public_j2_smoke/j2_path_operator_evidence_smoke/monotonic/train.npz` | 29002 | `162E2443D8192C4AB99B24F87FAD238AF2EDAE12362C8B3CC9BE0C96C9245AC4` |
| `data/public_j2_smoke/j2_path_operator_evidence_smoke/nonproportional/test.npz` | 29022 | `4A5AD3887339F9170F374EEAF6E7D3E6894C81BC972726D1CA22870753BA5CAC` |
| `data/public_j2_smoke/j2_path_operator_evidence_smoke/unload_reload/test.npz` | 29014 | `B66AFEE33FA3739498D99A91D6E0867C471DA7B9B8F0D28D9F682AB3A2C6D5DB` |

The full formal benchmark should be released through a data archive rather than
committed directly to GitHub.
