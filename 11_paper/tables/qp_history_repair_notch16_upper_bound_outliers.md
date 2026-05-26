# J2 Path-Dependent Baseline Outlier Diagnostics

Outliers are detected on cyclic-primary metrics using a 1.5 IQR rule when IQR is nonzero, otherwise a 3 sigma rule is used.
All evaluated paths are stored in JSON: `monotonic, cyclic`.

| Model | Metric | Rule | Lower | Upper | Outlier count | Outlier seeds | Mean | Std | Median | IQR | Min | Max |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| QP-aware thermo-hard HistoryGNO | Cyclic history rel. L2 | 1.5*IQR | 0.996315 | 1.00211 | 1 | 20260520=0.991254 | 0.997899 | 0.00336851 | 0.999886 | 0.00144792 | 0.991254 | 0.999935 |
| QP-aware thermo-hard HistoryGNO | History-increment rel. L2 | 1.5*IQR | 0.999983 | 1.00003 | 1 | 20260520=1.00019 | 1.00004 | 7.41894e-05 | 1 | 1.18017e-05 | 1 | 1.00019 |
| QP-aware thermo-hard HistoryGNO | QP history rel. L2 | 1.5*IQR | 0.992179 | 1.00447 | 1 | 20260520=0.981052 | 0.995465 | 0.00730203 | 0.999761 | 0.00307238 | 0.981052 | 0.999864 |
| QP-aware thermo-hard HistoryGNO | QP history-inc. rel. L2 | 1.5*IQR | 0.999962 | 1.00007 | 1 | 20260520=1.00037 | 1.00008 | 0.000146984 | 1 | 2.57492e-05 | 1 | 1.00037 |
| QP-aware thermo-hard HistoryGNO | QP von-Mises rel. L2 | 1.5*IQR | 0.848681 | 1.08659 | 1 | 20260520=0.545443 | 0.894731 | 0.176128 | 0.995509 | 0.0594764 | 0.545443 | 0.997437 |
| QP-aware thermo-hard HistoryGNO | Reversal hist-inc. rel. L2 | 1.5*IQR | 0.999929 | 1.00004 | 1 | 20260520=0.99965 | 0.999924 | 0.000137175 | 0.999998 | 2.7895e-05 | 0.99965 | 1 |
| QP-aware thermo-hard HistoryGNO | Yield-surface RMS | 1.5*IQR | -1.40827e-09 | 8.01779e-09 | 1 | 20260520=4.8187e-05 | 9.63959e-06 | 1.92737e-05 | 2.17549e-09 | 2.35652e-09 | 2.12507e-09 | 4.8187e-05 |
| QP-aware thermo-hard HistoryGNO | FEM residual rel. RMS | 1.5*IQR | 51.3993 | 116.04 | 2 | 20260518=38.3454; 20260520=118.888 | 82.2053 | 26.1598 | 86.3542 | 16.1601 | 38.3454 | 118.888 |
| QP-aware thermo-hard HistoryGNO | FEM energy rel. err. | 1.5*IQR | 120.512 | 5768.49 | 1 | 20260520=6503.58 | 3062.94 | 1980.55 | 2360.45 | 1412 | 561.653 | 6503.58 |