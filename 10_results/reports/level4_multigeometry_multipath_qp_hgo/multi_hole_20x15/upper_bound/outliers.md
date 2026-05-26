# J2 Path-Dependent Baseline Outlier Diagnostics

Outliers are detected on cyclic-path metrics using a 1.5 IQR rule when IQR is nonzero, otherwise a 3 sigma rule is used.

| Model | Metric | Rule | Lower | Upper | Outlier count | Outlier seeds | Mean | Std | Median | IQR | Min | Max |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| QP-thermo-hard HistoryGNO | Yield-surface RMS | 1.5*IQR | 5.13959e-08 | 6.66866e-08 | 1 | 20260518=5.06894e-08 | 5.82357e-08 | 4.19691e-09 | 5.96373e-08 | 3.82268e-09 | 5.06894e-08 | 6.27694e-08 |
| QP-thermo-hard HistoryGNO | FEM residual rel. RMS | 1.5*IQR | 36.279 | 54.6938 | 2 | 20260519=66.4201; 20260520=16.9733 | 44.365 | 15.8708 | 47.4588 | 4.60369 | 16.9733 | 66.4201 |