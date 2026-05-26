# J2 Path-Dependent Baseline Robust Statistics

Each row reports both mean/std and robust median/IQR statistics on the cyclic primary test path.
All evaluated paths are stored in JSON: `monotonic, cyclic`.

| Model | Metric | Mean | Std | Median | Q1 | Q3 | IQR | Min | Max | N |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| QP-aware thermo-hard HistoryGNO | Cyclic disp. rel. L2 | 2700.74 | 0 | 2700.74 | 2700.74 | 2700.74 | 0 | 2700.74 | 2700.74 | 1 |
| QP-aware thermo-hard HistoryGNO | Cyclic history rel. L2 | 0.993545 | 0 | 0.993545 | 0.993545 | 0.993545 | 0 | 0.993545 | 0.993545 | 1 |
| QP-aware thermo-hard HistoryGNO | History-increment rel. L2 | 1.00001 | 0 | 1.00001 | 1.00001 | 1.00001 | 0 | 1.00001 | 1.00001 | 1 |
| QP-aware thermo-hard HistoryGNO | QP history rel. L2 | 0.986401 | 0 | 0.986401 | 0.986401 | 0.986401 | 0 | 0.986401 | 0.986401 | 1 |
| QP-aware thermo-hard HistoryGNO | QP history-inc. rel. L2 | 1.00001 | 0 | 1.00001 | 1.00001 | 1.00001 | 0 | 1.00001 | 1.00001 | 1 |
| QP-aware thermo-hard HistoryGNO | QP eqp rel. L2 | 1 | 0 | 1 | 1 | 1 | 0 | 1 | 1 | 1 |
| QP-aware thermo-hard HistoryGNO | QP plastic-work rel. L2 | 1 | 0 | 1 | 1 | 1 | 0 | 1 | 1 | 1 |
| QP-aware thermo-hard HistoryGNO | QP von-Mises rel. L2 | 0.702255 | 0 | 0.702255 | 0.702255 | 0.702255 | 0 | 0.702255 | 0.702255 | 1 |
| QP-aware thermo-hard HistoryGNO | Eqp increment rel. L2 | 1 | 0 | 1 | 1 | 1 | 0 | 1 | 1 | 1 |
| QP-aware thermo-hard HistoryGNO | Plastic-work inc. rel. L2 | 1 | 0 | 1 | 1 | 1 | 0 | 1 | 1 | 1 |
| QP-aware thermo-hard HistoryGNO | Reversal hist-inc. rel. L2 | 0.999983 | 0 | 0.999983 | 0.999983 | 0.999983 | 0 | 0.999983 | 0.999983 | 1 |
| QP-aware thermo-hard HistoryGNO | Reversal yield-flag MAE | 0.136166 | 0 | 0.136166 | 0.136166 | 0.136166 | 0 | 0.136166 | 0.136166 | 1 |
| QP-aware thermo-hard HistoryGNO | Yield-surface RMS | 1.17112e-07 | 0 | 1.17112e-07 | 1.17112e-07 | 1.17112e-07 | 0 | 1.17112e-07 | 1.17112e-07 | 1 |
| QP-aware thermo-hard HistoryGNO | Plastic-work violation abs. | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| QP-aware thermo-hard HistoryGNO | Plastic-work violation target-norm. | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| QP-aware thermo-hard HistoryGNO | Plastic-work violation pred-norm. | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| QP-aware thermo-hard HistoryGNO | FEM residual rel. RMS | 769.031 | 0 | 769.031 | 769.031 | 769.031 | 0 | 769.031 | 769.031 | 1 |
| QP-aware thermo-hard HistoryGNO | FEM energy rel. err. | 269744 | 0 | 269744 | 269744 | 269744 | 0 | 269744 | 269744 | 1 |