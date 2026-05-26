# J2 Path-Dependent Baseline Outlier Diagnostics

Outliers are detected on cyclic-path metrics using a 1.5 IQR rule when IQR is nonzero, otherwise a 3 sigma rule is used.

| Model | Metric | Rule | Lower | Upper | Outlier count | Outlier seeds | Mean | Std | Median | IQR | Min | Max |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| QP-thermo-hard HistoryGNO | Cyclic history rel. L2 | 1.5*IQR | 2.18849 | 2.2194 | 1 | 20260518=1.88315 | 2.14101 | 0.128977 | 2.20364 | 0.00772762 | 1.88315 | 2.21036 |
| QP-thermo-hard HistoryGNO | History-increment rel. L2 | 1.5*IQR | 0.999748 | 1.0004 | 1 | 20260518=1.00646 | 1.0013 | 0.00257871 | 1.00007 | 0.000163496 | 0.99984 | 1.00646 |
| QP-thermo-hard HistoryGNO | QP history rel. L2 | 1.5*IQR | 3.36267 | 3.41305 | 1 | 20260518=2.99284 | 3.31079 | 0.159071 | 3.38784 | 0.0125947 | 2.99284 | 3.39756 |
| QP-thermo-hard HistoryGNO | QP history-inc. rel. L2 | 1.5*IQR | 0.99985 | 1.00067 | 1 | 20260518=1.03202 | 1.00656 | 0.0127347 | 1.00017 | 0.000204325 | 1.00007 | 1.03202 |
| QP-thermo-hard HistoryGNO | Eqp increment rel. L2 | 1.5*IQR | 6.13115 | 13.6063 | 1 | 20260521=20.9233 | 11.48 | 4.96138 | 10.3207 | 1.86878 | 6.41863 | 20.9233 |
| QP-thermo-hard HistoryGNO | Plastic-work inc. rel. L2 | 1.5*IQR | 6.15762 | 14.339 | 1 | 20260521=23.1828 | 12.2459 | 5.69207 | 10.802 | 2.04534 | 6.7482 | 23.1828 |
| QP-thermo-hard HistoryGNO | Reversal hist-inc. rel. L2 | 1.5*IQR | 0.998927 | 1.00081 | 1 | 20260518=0.962895 | 0.992531 | 0.0148198 | 0.999749 | 0.00047189 | 0.962895 | 1.00027 |
| QP-thermo-hard HistoryGNO | Reversal yield-flag MAE | 1.5*IQR | 0.859428 | 0.866386 | 1 | 20260518=0.753336 | 0.841163 | 0.0439184 | 0.86283 | 0.00173956 | 0.753336 | 0.863834 |
| QP-thermo-hard HistoryGNO | Yield-surface RMS | 1.5*IQR | -2.31541e-05 | 4.07495e-05 | 1 | 20260518=0.00410464 | 0.000826375 | 0.00163914 | 9.58324e-06 | 1.59759e-05 | 6.17698e-08 | 0.00410464 |