# J2 Path-Dependent Baseline Outlier Diagnostics

Outliers are detected on cyclic-path metrics using a 1.5 IQR rule when IQR is nonzero, otherwise a 3 sigma rule is used.

| Model | Metric | Rule | Lower | Upper | Outlier count | Outlier seeds | Mean | Std | Median | IQR | Min | Max |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Thermo-hard HistoryGNO | History-increment rel. L2 | 1.5*IQR | 0.926948 | 1.1241 | 1 | 20260518=1.36351 | 1.09291 | 0.137063 | 1.04937 | 0.049287 | 1.00063 | 1.36351 |
| Thermo-hard HistoryGNO | Reversal hist-inc. rel. L2 | 1.5*IQR | 0.875302 | 1.20767 | 1 | 20260518=1.80806 | 1.18533 | 0.31286 | 1.0358 | 0.0830917 | 0.99982 | 1.80806 |
| Thermo-hard HistoryGNO | Reversal yield-flag MAE | 1.5*IQR | 0.430788 | 0.430793 | 2 | 20260518=0.423198; 20260519=0.432247 | 0.429563 | 0.00323248 | 0.430791 | 1.37091e-06 | 0.423198 | 0.432247 |
| Thermo-hard HistoryGNO | Yield-surface RMS | 1.5*IQR | -0.000896604 | 0.00149484 | 1 | 20260518=0.00161148 | 0.000559616 | 0.000589009 | 0.000588188 | 0.000597862 | 1.69743e-07 | 0.00161148 |
| Thermo-projected neural CDE | Cyclic disp. rel. L2 | 1.5*IQR | 136.372 | 468.179 | 1 | 20260520=867.745 | 413.046 | 230.014 | 332.651 | 82.9519 | 260.285 | 867.745 |
| Thermo-projected neural CDE | Cyclic history rel. L2 | 1.5*IQR | 0.991757 | 0.99664 | 1 | 20260519=0.93141 | 0.982134 | 0.0253769 | 0.994575 | 0.00122082 | 0.93141 | 0.996291 |
| Thermo-projected neural CDE | History-increment rel. L2 | 1.5*IQR | 0.999913 | 1.00005 | 2 | 20260519=1.1172; 20260521=0.999904 | 1.02341 | 0.046893 | 0.99999 | 3.40343e-05 | 0.999904 | 1.1172 |
| Thermo-projected neural CDE | Reversal hist-inc. rel. L2 | 1.5*IQR | 0.999589 | 1.00072 | 1 | 20260519=1.24331 | 1.04872 | 0.0972932 | 1.00014 | 0.00028348 | 0.999851 | 1.24331 |
| Thermo-projected neural CDE | Reversal yield-flag MAE | 1.5*IQR | 0.569208 | 0.56921 | 1 | 20260519=0.563633 | 0.568094 | 0.00223016 | 0.569209 | 4.76837e-07 | 0.563633 | 0.569209 |
| Thermo-projected neural CDE | Yield-surface RMS | 1.5*IQR | -7.98977e-06 | 1.50679e-05 | 1 | 20260519=0.00570265 | 0.00114211 | 0.00228027 | 7.6631e-07 | 5.76443e-06 | 6.85289e-08 | 0.00570265 |