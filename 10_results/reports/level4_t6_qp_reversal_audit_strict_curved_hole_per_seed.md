# J2 Path-Dependent Baseline Per-Seed Appendix

Per-seed cyclic-path metrics for diagnosing stochastic training stability and outliers.

| Model | Seed | Train final loss | Cyclic disp. rel. L2 | Cyclic history rel. L2 | History-increment rel. L2 | Eqp increment rel. L2 | Plastic-work inc. rel. L2 | Reversal hist-inc. rel. L2 | Reversal yield-flag MAE | Yield-surface RMS | Plastic-work violation abs. | Plastic-work violation target-norm. | Plastic-work violation pred-norm. | FEM residual rel. RMS | FEM energy rel. err. |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Thermo-hard HistoryGNO | 20260517 | 14507.3 | 219.572 | 1.12757 | 1.00063 | 17.2419 | 20.9589 | 0.99982 | 0.430791 | 1.69743e-07 | 0 | 0 | 0 | 111.317 | 7032.07 |
| Thermo-hard HistoryGNO | 20260518 | 8151.35 | 265.949 | 1.1128 | 1.36351 | 28.595 | 37.8634 | 1.80806 | 0.423198 | 0.00161148 | 6.20273e-13 | 2.41979e-08 | 6.37558e-10 | 117.501 | 3958.93 |
| Thermo-hard HistoryGNO | 20260519 | 1818.3 | 34.9859 | 1.13074 | 1.05017 | 32.3723 | 47.483 | 1.08303 | 0.432247 | 0.000588188 | 0 | 0 | 0 | 187.08 | 10685.2 |
| Thermo-hard HistoryGNO | 20260520 | 2281.87 | 106.512 | 1.12861 | 1.00088 | 21.0526 | 27.9413 | 0.999939 | 0.430791 | 1.89271e-07 | 0 | 0 | 0 | 231.564 | 16255.1 |
| Thermo-hard HistoryGNO | 20260521 | 5460.76 | 136.114 | 1.11662 | 1.04937 | 27.1331 | 37.691 | 1.0358 | 0.43079 | 0.000598051 | 0 | 0 | 0 | 186.988 | 16998.1 |
| Thermo-projected neural CDE | 20260517 | 49883.4 | 343.752 | 0.994575 | 0.99999 | 1 | 1 | 1.00014 | 0.569209 | 7.6631e-07 | 0 | 0 | 0 | 782.325 | 163651 |
| Thermo-projected neural CDE | 20260518 | 9040.3 | 332.651 | 0.996291 | 0.999998 | 1 | 1 | 1.00001 | 0.569209 | 6.85289e-08 | 0 | 0 | 0 | 503.586 | 115861 |
| Thermo-projected neural CDE | 20260519 | 32792 | 260.8 | 0.93141 | 1.1172 | 1 | 1 | 1.24331 | 0.563633 | 0.00570265 | 0 | 0 | 0 | 1144.6 | 404227 |
| Thermo-projected neural CDE | 20260520 | 1.11489e+06 | 867.745 | 0.994809 | 0.999964 | 1 | 1 | 0.999851 | 0.569209 | 6.56876e-07 | 0 | 0 | 0 | 1575.38 | 805363 |
| Thermo-projected neural CDE | 20260521 | 11772.4 | 260.285 | 0.993588 | 0.999904 | 1 | 1 | 1.0003 | 0.569209 | 6.4213e-06 | 0 | 0 | 0 | 534.541 | 93032.3 |