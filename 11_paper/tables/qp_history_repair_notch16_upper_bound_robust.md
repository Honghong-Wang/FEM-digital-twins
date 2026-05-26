# J2 Path-Dependent Baseline Robust Statistics

Each row reports both mean/std and robust median/IQR statistics on the cyclic primary test path.
All evaluated paths are stored in JSON: `monotonic, cyclic`.

| Model | Metric | Mean | Std | Median | Q1 | Q3 | IQR | Min | Max | N |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| QP-aware thermo-hard HistoryGNO | Cyclic disp. rel. L2 | 96.2133 | 46.5057 | 76.6422 | 65.3271 | 115.992 | 50.6647 | 45.9206 | 177.185 | 5 |
| QP-aware thermo-hard HistoryGNO | Cyclic history rel. L2 | 0.997899 | 0.00336851 | 0.999886 | 0.998486 | 0.999934 | 0.00144792 | 0.991254 | 0.999935 | 5 |
| QP-aware thermo-hard HistoryGNO | History-increment rel. L2 | 1.00004 | 7.41894e-05 | 1 | 1 | 1.00001 | 1.18017e-05 | 1 | 1.00019 | 5 |
| QP-aware thermo-hard HistoryGNO | QP history rel. L2 | 0.995465 | 0.00730203 | 0.999761 | 0.996788 | 0.99986 | 0.00307238 | 0.981052 | 0.999864 | 5 |
| QP-aware thermo-hard HistoryGNO | QP history-inc. rel. L2 | 1.00008 | 0.000146984 | 1 | 1 | 1.00003 | 2.57492e-05 | 1 | 1.00037 | 5 |
| QP-aware thermo-hard HistoryGNO | QP eqp rel. L2 | 1 | 0 | 1 | 1 | 1 | 0 | 1 | 1 | 5 |
| QP-aware thermo-hard HistoryGNO | QP plastic-work rel. L2 | 1 | 0 | 1 | 1 | 1 | 0 | 1 | 1 | 5 |
| QP-aware thermo-hard HistoryGNO | QP von-Mises rel. L2 | 0.894731 | 0.176128 | 0.995509 | 0.937896 | 0.997372 | 0.0594764 | 0.545443 | 0.997437 | 5 |
| QP-aware thermo-hard HistoryGNO | Eqp increment rel. L2 | 1 | 0 | 1 | 1 | 1 | 0 | 1 | 1 | 5 |
| QP-aware thermo-hard HistoryGNO | Plastic-work inc. rel. L2 | 1 | 0 | 1 | 1 | 1 | 0 | 1 | 1 | 5 |
| QP-aware thermo-hard HistoryGNO | Reversal hist-inc. rel. L2 | 0.999924 | 0.000137175 | 0.999998 | 0.999971 | 0.999999 | 2.7895e-05 | 0.99965 | 1 | 5 |
| QP-aware thermo-hard HistoryGNO | Reversal yield-flag MAE | 0.136166 | 1.00732e-06 | 0.136166 | 0.136166 | 0.136166 | 0 | 0.136166 | 0.136168 | 5 |
| QP-aware thermo-hard HistoryGNO | Yield-surface RMS | 9.63959e-06 | 1.92737e-05 | 2.17549e-09 | 2.1265e-09 | 4.48302e-09 | 2.35652e-09 | 2.12507e-09 | 4.8187e-05 | 5 |
| QP-aware thermo-hard HistoryGNO | Plastic-work violation abs. | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 5 |
| QP-aware thermo-hard HistoryGNO | Plastic-work violation target-norm. | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 5 |
| QP-aware thermo-hard HistoryGNO | Plastic-work violation pred-norm. | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 5 |
| QP-aware thermo-hard HistoryGNO | FEM residual rel. RMS | 82.2053 | 26.1598 | 86.3542 | 75.6395 | 91.7997 | 16.1601 | 38.3454 | 118.888 | 5 |
| QP-aware thermo-hard HistoryGNO | FEM energy rel. err. | 3062.94 | 1980.55 | 2360.45 | 2238.51 | 3650.5 | 1412 | 561.653 | 6503.58 | 5 |