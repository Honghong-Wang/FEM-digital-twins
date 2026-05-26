# J2 Path-Dependent Baseline Outlier Diagnostics

Outliers are detected on cyclic-path metrics using a 1.5 IQR rule when IQR is nonzero, otherwise a 3 sigma rule is used.

| Model | Metric | Rule | Lower | Upper | Outlier count | Outlier seeds | Mean | Std | Median | IQR | Min | Max |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| QP-thermo-hard HistoryGNO | Eqp increment rel. L2 | 1.5*IQR | 2.6986 | 5.82139 | 1 | 20260521=8.57053 | 4.84922 | 1.95939 | 4.32469 | 0.780699 | 2.83089 | 8.57053 |
| QP-thermo-hard HistoryGNO | Plastic-work inc. rel. L2 | 1.5*IQR | 2.77621 | 6.14485 | 1 | 20260521=9.51915 | 5.18198 | 2.26662 | 4.53886 | 0.842161 | 2.93084 | 9.51915 |
| QP-thermo-hard HistoryGNO | FEM residual rel. RMS | 1.5*IQR | -24.4588 | 212.838 | 1 | 20260520=289.338 | 123.363 | 92.2395 | 123.116 | 59.3241 | 15.9811 | 289.338 |
| QP-thermo-hard HistoryGNO | FEM energy rel. err. | 1.5*IQR | -4098.19 | 11872.5 | 1 | 20260520=26890.1 | 7540.31 | 9855.81 | 2947.51 | 3992.68 | 89.576 | 26890.1 |