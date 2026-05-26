# J2 Path-Dependent Baseline Robust Statistics

Each row reports both mean/std and robust median/IQR statistics on the cyclic test path.

| Model | Metric | Mean | Std | Median | Q1 | Q3 | IQR | Min | Max | N |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Thermo-hard HistoryGNO | Cyclic disp. rel. L2 | 203.565 | 96.186 | 194.506 | 179.435 | 292.634 | 113.199 | 41.2751 | 309.975 | 5 |
| Thermo-hard HistoryGNO | Cyclic history rel. L2 | 1.34234 | 0.0051184 | 1.34482 | 1.34459 | 1.34503 | 0.00043869 | 1.33211 | 1.34514 | 5 |
| Thermo-hard HistoryGNO | History-increment rel. L2 | 1.00904 | 0.0151685 | 1.00049 | 1.00044 | 1.00462 | 0.0041821 | 1.00042 | 1.0392 | 5 |
| Thermo-hard HistoryGNO | Eqp increment rel. L2 | 25.7029 | 4.25135 | 23.7452 | 21.6567 | 29.898 | 8.2413 | 21.561 | 31.6536 | 5 |
| Thermo-hard HistoryGNO | Plastic-work inc. rel. L2 | 32.5663 | 7.27951 | 29.1911 | 25.619 | 41.2369 | 15.6178 | 25.3686 | 41.4158 | 5 |
| Thermo-hard HistoryGNO | Reversal hist-inc. rel. L2 | 1.00523 | 0.00636601 | 1.00036 | 1.00033 | 1.00915 | 0.00882006 | 1.00033 | 1.01598 | 5 |
| Thermo-hard HistoryGNO | Reversal yield-flag MAE | 0.716685 | 0.000644302 | 0.717007 | 0.717007 | 0.717007 | 0 | 0.715396 | 0.717007 | 5 |
| Thermo-hard HistoryGNO | Yield-surface RMS | 9.30132e-05 | 0.000183712 | 1.86618e-07 | 1.77186e-07 | 4.10071e-06 | 3.92353e-06 | 1.76083e-07 | 0.000460425 | 5 |
| Thermo-hard HistoryGNO | Plastic-work violation abs. | 7.42858e-13 | 1.48572e-12 | 0 | 0 | 0 | 0 | 0 | 3.71429e-12 | 5 |
| Thermo-hard HistoryGNO | Plastic-work violation target-norm. | 3.10445e-08 | 6.2089e-08 | 0 | 0 | 0 | 0 | 0 | 1.55222e-07 | 5 |
| Thermo-hard HistoryGNO | Plastic-work violation pred-norm. | 7.48112e-10 | 1.49622e-09 | 0 | 0 | 0 | 0 | 0 | 3.74056e-09 | 5 |
| Thermo-hard HistoryGNO | FEM residual rel. RMS | 167.024 | 53.3558 | 151.979 | 136.166 | 202.462 | 66.2964 | 95.6226 | 248.887 | 5 |
| Thermo-hard HistoryGNO | FEM energy rel. err. | 19887.8 | 8181.22 | 14847 | 14451.6 | 29579.9 | 15128.3 | 10650.9 | 29909.9 | 5 |
| Thermo-projected neural CDE | Cyclic disp. rel. L2 | 564.425 | 309.447 | 459.783 | 362.362 | 468.732 | 106.37 | 355.204 | 1176.04 | 5 |
| Thermo-projected neural CDE | Cyclic history rel. L2 | 0.975224 | 0.0392456 | 0.993692 | 0.992614 | 0.99569 | 0.00307602 | 0.8968 | 0.997324 | 5 |
| Thermo-projected neural CDE | History-increment rel. L2 | 1.0016 | 0.00324538 | 0.999998 | 0.999978 | 1 | 2.5034e-05 | 0.999927 | 1.00809 | 5 |
| Thermo-projected neural CDE | Eqp increment rel. L2 | 1 | 0 | 1 | 1 | 1 | 0 | 1 | 1 | 5 |
| Thermo-projected neural CDE | Plastic-work inc. rel. L2 | 1 | 0 | 1 | 1 | 1 | 0 | 1 | 1 | 5 |
| Thermo-projected neural CDE | Reversal hist-inc. rel. L2 | 0.970289 | 0.0593801 | 0.999965 | 0.999952 | 0.999997 | 4.45843e-05 | 0.851529 | 1 | 5 |
| Thermo-projected neural CDE | Reversal yield-flag MAE | 0.297235 | 0.0284814 | 0.282994 | 0.282993 | 0.282997 | 3.27826e-06 | 0.282993 | 0.354198 | 5 |
| Thermo-projected neural CDE | Yield-surface RMS | 0.00114014 | 0.00227699 | 7.4882e-07 | 6.73408e-08 | 5.75604e-06 | 5.6887e-06 | 1.57318e-08 | 0.00569411 | 5 |
| Thermo-projected neural CDE | Plastic-work violation abs. | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 5 |
| Thermo-projected neural CDE | Plastic-work violation target-norm. | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 5 |
| Thermo-projected neural CDE | Plastic-work violation pred-norm. | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 5 |
| Thermo-projected neural CDE | FEM residual rel. RMS | 926.817 | 414.112 | 780.996 | 549.942 | 1174.23 | 624.29 | 519.003 | 1609.91 | 5 |
| Thermo-projected neural CDE | FEM energy rel. err. | 531457 | 457513 | 264331 | 192800 | 675020 | 482220 | 157129 | 1.36801e+06 | 5 |