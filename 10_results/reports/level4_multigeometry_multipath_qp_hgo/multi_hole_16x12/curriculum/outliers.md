# J2 Path-Dependent Baseline Outlier Diagnostics

Outliers are detected on cyclic-path metrics using a 1.5 IQR rule when IQR is nonzero, otherwise a 3 sigma rule is used.

| Model | Metric | Rule | Lower | Upper | Outlier count | Outlier seeds | Mean | Std | Median | IQR | Min | Max |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| QP-thermo-hard HistoryGNO | Reversal yield-flag MAE | 1.5*IQR | 0.357856 | 0.357865 | 1 | 20260519=0.357919 | 0.357872 | 2.37074e-05 | 0.35786 | 2.38419e-06 | 0.35786 | 0.357919 |
| QP-thermo-hard HistoryGNO | Yield-surface RMS | 1.5*IQR | -1.25105e-09 | 1.25622e-07 | 1 | 20260519=9.65001e-07 | 2.36368e-07 | 3.64525e-07 | 4.65264e-08 | 3.17182e-08 | 4.59418e-08 | 9.65001e-07 |
| QP-thermo-hard HistoryGNO | FEM energy rel. err. | 1.5*IQR | 556.745 | 2980.59 | 2 | 20260518=449.593; 20260519=5577.76 | 2220.83 | 1758.58 | 1539.48 | 605.961 | 449.593 | 5577.76 |