# J2 Path-Dependent Baseline Per-Seed Appendix

Per-seed cyclic-primary metrics for diagnosing stochastic training stability and outliers.
All evaluated paths are stored in JSON: `monotonic, cyclic`.

| Model | Seed | Train final loss | Cyclic disp. rel. L2 | Cyclic history rel. L2 | History-increment rel. L2 | Eqp increment rel. L2 | Plastic-work inc. rel. L2 | Reversal hist-inc. rel. L2 | Reversal yield-flag MAE | Yield-surface RMS | Plastic-work violation abs. | Plastic-work violation target-norm. | Plastic-work violation pred-norm. | HANO strain rel. L2 | HANO stress rel. L2 | FEM residual rel. RMS | FEM energy rel. err. | FEM tangent-solver rel. RMS |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Faithful HANO strain-stress spectral-window NO | 20260517 | 1.04374e+07 | 2366.08 | 3.54078 | 1.29567 | 287.748 | 8131.12 | 1.19813 | 0.448232 | 0.0511347 | 0 | 0 | 0 | 54.7561 | 2.35422 | 242.557 | 186376 | 242.557 |
| INCDE-style Euler neural CDE | 20260517 | 1.67351e+07 | 4301.85 | 17.3827 | 6.40908 | 2118.6 | 62787.1 | 5.38382 | 0.548601 | 0.850425 | 0.940961 | 14524.1 | 0.231321 |  |  | 121.009 | 3.3283e+06 | 121.009 |
| TINN-style thermo-projected neural CDE | 20260517 | 1.6735e+07 | 4301.85 | 1.17405 | 1.00006 | 2.10878 | 2.12048 | 1.00003 | 0.558824 | 0 | 0 | 0 | 0 |  |  | 121.007 | 51625.3 | 121.007 |
| Non-recurrent GNO sequence | 20260517 | 338105 | 308.379 | 4.69941 | 0.999325 | 0.96711 | 41.3479 | 0.999343 | 0.529957 | 0.714497 | 0 | 0 | 0 |  |  | 604.21 | 277253 | 604.21 |
| Static FNO sequence | 20260517 | 112807 | 429.217 | 6.54639 | 0.999939 | 3.5628 | 1.17307 | 0.999957 | 0.558696 | 0.654415 | 2.86299e-05 | 0.441913 | 0.598455 |  |  | 17.1742 | 2.29097e+06 | 17.1742 |
| Static DeepONet sequence | 20260517 | 124400 | 160.06 | 3.31674 | 1.00033 | 0.956932 | 17.8782 | 1.00031 | 0.49605 | 0.4094 | 0.00234198 | 36.1494 | 2.0773 |  |  | 19820.1 | 1.73192e+08 | 19820.1 |