# J2 Path-Dependent Baseline Outlier Diagnostics

Outliers are detected on cyclic-path metrics using a 1.5 IQR rule when IQR is nonzero, otherwise a 3 sigma rule is used.

| Model | Metric | Rule | Lower | Upper | Outlier count | Outlier seeds | Mean | Std | Median | IQR | Min | Max |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| QP-thermo-hard HistoryGNO | History-increment rel. L2 | 1.5*IQR | 0.999837 | 1.00016 | 2 | 20260518=0.997584; 20260520=1.07549 | 1.01462 | 0.030449 | 1.00004 | 8.08239e-05 | 0.997584 | 1.07549 |
| QP-thermo-hard HistoryGNO | QP history-inc. rel. L2 | 1.5*IQR | 0.999776 | 1.00027 | 2 | 20260518=0.998219; 20260520=1.12583 | 1.02483 | 0.0505027 | 1.00007 | 0.000123441 | 0.998219 | 1.12583 |
| QP-thermo-hard HistoryGNO | Reversal hist-inc. rel. L2 | 1.5*IQR | 0.999252 | 1.00105 | 1 | 20260520=1.05174 | 1.01034 | 0.0207045 | 0.999929 | 0.000448465 | 0.999718 | 1.05174 |
| QP-thermo-hard HistoryGNO | Yield-surface RMS | 1.5*IQR | -0.0647156 | 0.10786 | 1 | 20260518=0.180469 | 0.0447239 | 0.0698988 | 6.74825e-06 | 0.0431438 | 5.1874e-08 | 0.180469 |
| QP-thermo-hard HistoryGNO | FEM energy rel. err. | 1.5*IQR | 1469.91 | 2831.97 | 2 | 20260518=113.613; 20260520=5052.91 | 2345.57 | 1578.13 | 2259.46 | 340.516 | 113.613 | 5052.91 |