# J2 Path-Dependent Baseline Outlier Diagnostics

Outliers are detected on cyclic-path metrics using a 1.5 IQR rule when IQR is nonzero, otherwise a 3 sigma rule is used.

| Model | Metric | Rule | Lower | Upper | Outlier count | Outlier seeds | Mean | Std | Median | IQR | Min | Max |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| QP-thermo-hard HistoryGNO | Cyclic history rel. L2 | 1.5*IQR | 1.1701 | 1.18055 | 1 | 20260519=1.15852 | 1.17208 | 0.00686994 | 1.17444 | 0.00261247 | 1.15852 | 1.17678 |
| QP-thermo-hard HistoryGNO | History-increment rel. L2 | 1.5*IQR | 0.998586 | 1.00096 | 1 | 20260519=0.998041 | 0.999546 | 0.00078734 | 1.00007 | 0.00059253 | 0.998041 | 1.00008 |
| QP-thermo-hard HistoryGNO | QP history rel. L2 | 1.5*IQR | 1.94292 | 1.95973 | 1 | 20260519=1.92567 | 1.94631 | 0.0104796 | 1.94962 | 0.00420117 | 1.92567 | 1.9536 |
| QP-thermo-hard HistoryGNO | QP history-inc. rel. L2 | 1.5*IQR | 0.999699 | 1.00042 | 1 | 20260519=0.998476 | 0.999786 | 0.000659787 | 1.00012 | 0.000179529 | 0.998476 | 1.00022 |
| QP-thermo-hard HistoryGNO | Eqp increment rel. L2 | 1.5*IQR | 2.35837 | 4.0539 | 1 | 20260518=1.7128 | 3.00475 | 0.686639 | 3.20241 | 0.423884 | 1.7128 | 3.69628 |
| QP-thermo-hard HistoryGNO | Plastic-work inc. rel. L2 | 1.5*IQR | 2.40813 | 4.09716 | 1 | 20260518=1.68788 | 3.04804 | 0.727339 | 3.23193 | 0.422258 | 1.68788 | 3.81511 |
| QP-thermo-hard HistoryGNO | Reversal yield-flag MAE | 1.5*IQR | 0.455738 | 0.456413 | 1 | 20260519=0.457186 | 0.456294 | 0.000451548 | 0.456147 | 0.000168532 | 0.455989 | 0.457186 |
| QP-thermo-hard HistoryGNO | Yield-surface RMS | 1.5*IQR | -1.37324e-05 | 2.36081e-05 | 1 | 20260519=3.7298e-05 | 1.13655e-05 | 1.36349e-05 | 9.58841e-06 | 9.33512e-06 | 6.5378e-08 | 3.7298e-05 |
| QP-thermo-hard HistoryGNO | FEM energy rel. err. | 1.5*IQR | -1193.86 | 5172.03 | 1 | 20260520=16064.9 | 4356.61 | 5910.91 | 1510.14 | 1591.47 | 229.818 | 16064.9 |