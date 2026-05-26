# J2 Path-Dependent Baseline Per-Seed Appendix

Per-seed cyclic-path metrics for diagnosing stochastic training stability and outliers.

| Model | Seed | Train final loss | Cyclic disp. rel. L2 | Cyclic history rel. L2 | History-increment rel. L2 | Eqp increment rel. L2 | Plastic-work inc. rel. L2 | Reversal hist-inc. rel. L2 | Reversal yield-flag MAE | Yield-surface RMS | Plastic-work violation abs. | Plastic-work violation target-norm. | Plastic-work violation pred-norm. | FEM residual rel. RMS | FEM energy rel. err. |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Thermo-hard HistoryGNO | 20260517 | 22354.3 | 309.975 | 1.34459 | 1.00042 | 21.6567 | 25.619 | 1.00033 | 0.717007 | 1.77186e-07 | 0 | 0 | 0 | 136.166 | 14847 |
| Thermo-hard HistoryGNO | 20260518 | 12458.9 | 292.634 | 1.34482 | 1.00044 | 21.561 | 25.3686 | 1.00033 | 0.717007 | 1.76083e-07 | 0 | 0 | 0 | 95.6226 | 10650.9 |
| Thermo-hard HistoryGNO | 20260519 | 1790.57 | 41.2751 | 1.34503 | 1.00462 | 29.898 | 41.4158 | 1.00915 | 0.717007 | 4.10071e-06 | 0 | 0 | 0 | 151.979 | 14451.6 |
| Thermo-hard HistoryGNO | 20260520 | 4465.08 | 179.435 | 1.34514 | 1.00049 | 23.7452 | 29.1911 | 1.00036 | 0.717007 | 1.86618e-07 | 0 | 0 | 0 | 248.887 | 29579.9 |
| Thermo-hard HistoryGNO | 20260521 | 7549.45 | 194.506 | 1.33211 | 1.0392 | 31.6536 | 41.2369 | 1.01598 | 0.715396 | 0.000460425 | 3.71429e-12 | 1.55222e-07 | 3.74056e-09 | 202.462 | 29909.9 |
| Thermo-projected neural CDE | 20260517 | 75158.2 | 468.732 | 0.993692 | 0.999978 | 1 | 1 | 0.999965 | 0.282994 | 7.4882e-07 | 0 | 0 | 0 | 780.996 | 264331 |
| Thermo-projected neural CDE | 20260518 | 12433.3 | 459.783 | 0.99569 | 0.999998 | 1 | 1 | 0.999997 | 0.282993 | 6.73408e-08 | 0 | 0 | 0 | 519.003 | 192800 |
| Thermo-projected neural CDE | 20260519 | 49256.7 | 362.362 | 0.8968 | 1.00809 | 1 | 1 | 0.851529 | 0.354198 | 0.00569411 | 0 | 0 | 0 | 1174.23 | 675020 |
| Thermo-projected neural CDE | 20260520 | 1.66691e+06 | 1176.04 | 0.997324 | 1 | 1 | 1 | 1 | 0.282993 | 1.57318e-08 | 0 | 0 | 0 | 1609.91 | 1.36801e+06 |
| Thermo-projected neural CDE | 20260521 | 17705.2 | 355.204 | 0.992614 | 0.999927 | 1 | 1 | 0.999952 | 0.282997 | 5.75604e-06 | 0 | 0 | 0 | 549.942 | 157129 |