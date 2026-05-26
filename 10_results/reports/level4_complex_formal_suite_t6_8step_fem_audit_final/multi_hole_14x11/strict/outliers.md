# J2 Path-Dependent Baseline Outlier Diagnostics

Outliers are detected on cyclic-path metrics using a 1.5 IQR rule when IQR is nonzero, otherwise a 3 sigma rule is used.

| Model | Metric | Rule | Lower | Upper | Outlier count | Outlier seeds | Mean | Std | Median | IQR | Min | Max |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Thermo-hard HistoryGNO | Cyclic history rel. L2 | 1.5*IQR | 1.17427 | 1.18533 | 1 | 20260521=1.16418 | 1.17729 | 0.00665137 | 1.18108 | 0.00276411 | 1.16418 | 1.1816 |
| Thermo-hard HistoryGNO | History-increment rel. L2 | 1.5*IQR | 0.999736 | 1.00223 | 1 | 20260521=1.05432 | 1.01147 | 0.0214267 | 1.0008 | 0.000622869 | 1.00028 | 1.05432 |
| Thermo-hard HistoryGNO | Reversal hist-inc. rel. L2 | 1.5*IQR | 0.999198 | 1.00233 | 1 | 20260521=1.01839 | 1.00408 | 0.00716501 | 1.00051 | 0.000783682 | 0.999964 | 1.01839 |
| Thermo-hard HistoryGNO | Yield-surface RMS | 1.5*IQR | 1.13312e-07 | 2.76561e-07 | 1 | 20260521=0.000458522 | 9.18476e-05 | 0.000183337 | 1.8799e-07 | 4.08121e-08 | 1.38174e-07 | 0.000458522 |
| Thermo-projected neural CDE | Cyclic disp. rel. L2 | 1.5*IQR | 155.068 | 438.061 | 1 | 20260520=832.519 | 400.648 | 218.362 | 325.57 | 70.7482 | 252.02 | 832.519 |
| Thermo-projected neural CDE | Cyclic history rel. L2 | 1.5*IQR | 0.989732 | 0.997411 | 1 | 20260519=0.957138 | 0.98683 | 0.0148949 | 0.993609 | 0.00191969 | 0.957138 | 0.996262 |
| Thermo-projected neural CDE | History-increment rel. L2 | 1.5*IQR | 0.999872 | 1.00021 | 1 | 20260519=1.16251 | 1.03251 | 0.0650026 | 1.00001 | 8.50558e-05 | 0.99993 | 1.16251 |
| Thermo-projected neural CDE | Reversal hist-inc. rel. L2 | 1.5*IQR | 0.999538 | 1.00081 | 1 | 20260519=1.36752 | 1.07357 | 0.146977 | 1.00015 | 0.000316858 | 0.999833 | 1.36752 |
| Thermo-projected neural CDE | Reversal yield-flag MAE | 1.5*IQR | 0.543917 | 0.544068 | 1 | 20260519=0.533173 | 0.541836 | 0.00433176 | 0.544011 | 3.79086e-05 | 0.533173 | 0.544012 |
| Thermo-projected neural CDE | Yield-surface RMS | 1.5*IQR | -0.00027261 | 0.000456431 | 1 | 20260519=0.00570153 | 0.0011783 | 0.0022627 | 6.08013e-06 | 0.00018226 | 6.80547e-08 | 0.00570153 |