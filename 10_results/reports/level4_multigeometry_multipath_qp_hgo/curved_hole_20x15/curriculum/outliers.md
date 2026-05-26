# J2 Path-Dependent Baseline Outlier Diagnostics

Outliers are detected on cyclic-path metrics using a 1.5 IQR rule when IQR is nonzero, otherwise a 3 sigma rule is used.

| Model | Metric | Rule | Lower | Upper | Outlier count | Outlier seeds | Mean | Std | Median | IQR | Min | Max |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| QP-thermo-hard HistoryGNO | History-increment rel. L2 | 1.5*IQR | 0.999978 | 1.00017 | 2 | 20260517=0.999906; 20260518=1.06742 | 1.01351 | 0.0269565 | 1.00007 | 4.80413e-05 | 0.999906 | 1.06742 |
| QP-thermo-hard HistoryGNO | QP history-inc. rel. L2 | 1.5*IQR | 1.00006 | 1.00027 | 2 | 20260517=0.99997; 20260518=1.23307 | 1.0467 | 0.0931832 | 1.00014 | 5.17368e-05 | 0.99997 | 1.23307 |
| QP-thermo-hard HistoryGNO | Reversal hist-inc. rel. L2 | 1.5*IQR | 0.999829 | 1.0004 | 2 | 20260517=0.999609; 20260518=1.00077 | 1.00015 | 0.000369984 | 1.00013 | 0.000142336 | 0.999609 | 1.00077 |
| QP-thermo-hard HistoryGNO | FEM residual rel. RMS | 1.5*IQR | 20.6441 | 71.4729 | 1 | 20260519=104.224 | 54.7471 | 26.089 | 48.9046 | 12.7072 | 28.4904 | 104.224 |