# Shared-Geometry J2 Thermo-Aware Path-OOD Primary Evidence

Source: `10_results\reports\j2_complex_geometry_shared_thermo_path_ood_5seed_summary.json`

Shared data root: `05_data_pipeline\processed\j2_complex_geometry_shared_path_fem2d`

| metric | Strict path-OOD | Unload curriculum | Cyclic-seen upper bound |
| --- | ---: | ---: | ---: |
| Displacement relative L2 | 0.9132 +/- 0.0883 | 0.8756 +/- 0.0317 | 0.8704 +/- 0.0930 |
| History relative L2 | 1.0903 +/- 0.0954 | 0.9092 +/- 0.0355 | 0.8021 +/- 0.0500 |
| History-increment relative L2 | 1.0160 +/- 0.0022 | 1.0109 +/- 0.0021 | 1.0008 +/- 0.0020 |
| Eq. plastic strain increment relative L2 | 2.0700 +/- 0.4899 | 1.4737 +/- 0.2270 | 1.1834 +/- 0.2174 |
| Plastic-work increment relative L2 | 3.7015 +/- 0.6555 | 3.0074 +/- 0.3014 | 2.6189 +/- 0.3821 |
| Yield-flag MAE | 0.5412 +/- 0.0120 | 0.5394 +/- 0.0069 | 0.5057 +/- 0.0024 |
| Reversal history-increment relative L2 | 1.0206 +/- 0.0046 | 1.0155 +/- 0.0041 | 0.9958 +/- 0.0026 |
| Reversal yield-flag MAE | 0.6824 +/- 0.0427 | 0.6499 +/- 0.0058 | 0.5608 +/- 0.0059 |
| Predicted yield-surface relative RMS | 0.5578 +/- 0.0324 | 0.5073 +/- 0.0253 | 0.3858 +/- 0.0408 |
| Plastic-work lower-bound violation | 1.0951 +/- 0.9186 | 0.3220 +/- 0.2484 | 0.0870 +/- 0.1686 |
