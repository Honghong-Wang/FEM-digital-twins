# J2 Path-Dependent Baseline Outlier Diagnostics

Outliers are detected on cyclic-path metrics using a 1.5 IQR rule when IQR is nonzero, otherwise a 3 sigma rule is used.

| Model | Metric | Rule | Lower | Upper | Outlier count | Outlier seeds | Mean | Std | Median | IQR | Min | Max |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| QP-thermo-hard HistoryGNO | Cyclic history rel. L2 | 1.5*IQR | 1.13845 | 1.1912 | 1 | 20260520=0.927381 | 1.11974 | 0.0963882 | 1.16469 | 0.0131879 | 0.927381 | 1.177 |
| QP-thermo-hard HistoryGNO | History-increment rel. L2 | 1.5*IQR | 0.996164 | 1.00224 | 1 | 20260520=1.14233 | 1.02757 | 0.0573838 | 0.999292 | 0.00151932 | 0.997825 | 1.14233 |
| QP-thermo-hard HistoryGNO | QP history rel. L2 | 1.5*IQR | 1.88086 | 1.98398 | 1 | 20260520=1.61721 | 1.87415 | 0.128969 | 1.93505 | 0.0257794 | 1.61721 | 1.95363 |
| QP-thermo-hard HistoryGNO | QP history-inc. rel. L2 | 1.5*IQR | 0.998268 | 1.00126 | 1 | 20260520=1.27282 | 1.05423 | 0.109294 | 1.00011 | 0.000747025 | 0.99871 | 1.27282 |
| QP-thermo-hard HistoryGNO | Reversal hist-inc. rel. L2 | 1.5*IQR | 0.998412 | 1.00233 | 1 | 20260518=1.00297 | 1.00084 | 0.00113372 | 1.0006 | 0.000979066 | 0.999874 | 1.00297 |
| QP-thermo-hard HistoryGNO | Reversal yield-flag MAE | 1.5*IQR | 0.454842 | 0.458838 | 1 | 20260520=0.485329 | 0.462357 | 0.0114947 | 0.456771 | 0.000998974 | 0.456006 | 0.485329 |
| QP-thermo-hard HistoryGNO | Yield-surface RMS | 1.5*IQR | -1.41495e-05 | 6.72594e-05 | 1 | 20260520=0.12262 | 0.0245409 | 0.0490396 | 2.94314e-05 | 2.03522e-05 | 1.78205e-06 | 0.12262 |
| QP-thermo-hard HistoryGNO | FEM energy rel. err. | 1.5*IQR | -691.144 | 6506.6 | 1 | 20260520=20464.6 | 5841.02 | 7397.49 | 2601.96 | 1799.44 | 323.11 | 20464.6 |