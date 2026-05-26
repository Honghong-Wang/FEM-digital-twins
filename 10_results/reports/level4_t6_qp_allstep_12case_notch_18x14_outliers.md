# J2 Path-Dependent Baseline Outlier Diagnostics

Outliers are detected on cyclic-path metrics using a 1.5 IQR rule when IQR is nonzero, otherwise a 3 sigma rule is used.

| Model | Metric | Rule | Lower | Upper | Outlier count | Outlier seeds | Mean | Std | Median | IQR | Min | Max |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| QP-thermo-hard HistoryGNO | Cyclic history rel. L2 | 1.5*IQR | 1.53532 | 1.53949 | 1 | 20260520=1.13159 | 1.45658 | 0.162496 | 1.53772 | 0.00104332 | 1.13159 | 1.53877 |
| QP-thermo-hard HistoryGNO | History-increment rel. L2 | 1.5*IQR | 0.999968 | 1.0002 | 1 | 20260520=1.04417 | 1.00888 | 0.017644 | 1.00006 | 5.68628e-05 | 1.00001 | 1.04417 |
| QP-thermo-hard HistoryGNO | QP history rel. L2 | 1.5*IQR | 2.43363 | 2.43926 | 1 | 20260520=2.01284 | 2.35215 | 0.169654 | 2.43685 | 0.00140929 | 2.01284 | 2.43816 |
| QP-thermo-hard HistoryGNO | QP history-inc. rel. L2 | 1.5*IQR | 0.999934 | 1.0004 | 1 | 20260520=1.18204 | 1.0365 | 0.0727679 | 1.00013 | 0.000115991 | 1.00003 | 1.18204 |
| QP-thermo-hard HistoryGNO | Reversal yield-flag MAE | 1.5*IQR | 0.76268 | 0.763104 | 1 | 20260520=0.58761 | 0.727856 | 0.0701232 | 0.762942 | 0.000106096 | 0.58761 | 0.762945 |
| QP-thermo-hard HistoryGNO | Yield-surface RMS | 1.5*IQR | -1.57302e-06 | 2.80057e-06 | 1 | 20260520=0.148595 | 0.0297193 | 0.0594379 | 9.51244e-08 | 1.0934e-06 | 6.5951e-08 | 0.148595 |
| QP-thermo-hard HistoryGNO | FEM residual rel. RMS | 1.5*IQR | 32.8992 | 102.136 | 2 | 20260520=156.655; 20260521=30.8899 | 78.4521 | 42.0566 | 69.6804 | 17.3091 | 30.8899 | 156.655 |
| QP-thermo-hard HistoryGNO | FEM energy rel. err. | 1.5*IQR | -3040.39 | 7889.38 | 1 | 20260520=12659 | 3866.31 | 4536.46 | 1256.11 | 2732.44 | 567.48 | 12659 |