# J2 Path-Dependent Baseline Outlier Diagnostics

Outliers are detected on cyclic-path metrics using a 1.5 IQR rule when IQR is nonzero, otherwise a 3 sigma rule is used.

| Model | Metric | Rule | Lower | Upper | Outlier count | Outlier seeds | Mean | Std | Median | IQR | Min | Max |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| QP-thermo-hard HistoryGNO | Reversal yield-flag MAE | 1.5*IQR | 0.357857 | 0.357865 | 1 | 20260519=0.357882 | 0.357865 | 8.4668e-06 | 0.357861 | 2.02656e-06 | 0.35786 | 0.357882 |
| QP-thermo-hard HistoryGNO | Yield-surface RMS | 1.5*IQR | -2.05108e-08 | 1.62402e-07 | 1 | 20260519=4.06824e-07 | 1.30942e-07 | 1.38983e-07 | 5.9105e-08 | 4.57281e-08 | 4.68913e-08 | 4.06824e-07 |
| QP-thermo-hard HistoryGNO | FEM energy rel. err. | 1.5*IQR | 587.528 | 2955.7 | 2 | 20260518=454.287; 20260519=5486.4 | 2207.86 | 1720.78 | 1555.4 | 592.043 | 454.287 | 5486.4 |