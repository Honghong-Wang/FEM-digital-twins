# J2 Path-Dependent Baseline Outlier Diagnostics

Outliers are detected on cyclic-path metrics using a 1.5 IQR rule when IQR is nonzero, otherwise a 3 sigma rule is used.

| Model | Metric | Rule | Lower | Upper | Outlier count | Outlier seeds | Mean | Std | Median | IQR | Min | Max |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| QP-thermo-hard HistoryGNO | Cyclic disp. rel. L2 | 1.5*IQR | 38.9353 | 101.233 | 1 | 20260518=109.937 | 75.4893 | 19.8059 | 76.2341 | 15.5745 | 51.1074 | 109.937 |
| QP-thermo-hard HistoryGNO | Cyclic history rel. L2 | 1.5*IQR | 2.20187 | 2.21257 | 1 | 20260518=2.17686 | 2.20205 | 0.0127427 | 2.20716 | 0.00267506 | 2.17686 | 2.21176 |
| QP-thermo-hard HistoryGNO | History-increment rel. L2 | 1.5*IQR | 0.999849 | 1.00024 | 1 | 20260518=0.999009 | 0.999867 | 0.000436827 | 1.00002 | 9.7096e-05 | 0.999009 | 1.00023 |
| QP-thermo-hard HistoryGNO | QP history rel. L2 | 1.5*IQR | 3.38527 | 3.40121 | 1 | 20260518=3.35025 | 3.38585 | 0.0180118 | 3.39302 | 0.00398493 | 3.35025 | 3.3995 |
| QP-thermo-hard HistoryGNO | QP history-inc. rel. L2 | 1.5*IQR | 0.99988 | 1.00039 | 2 | 20260518=0.999106; 20260521=1.00051 | 1.00001 | 0.000474636 | 1.00015 | 0.000128388 | 0.999106 | 1.00051 |
| QP-thermo-hard HistoryGNO | Eqp increment rel. L2 | 1.5*IQR | 5.11883 | 18.3882 | 1 | 20260521=27.227 | 13.4266 | 7.26625 | 10.1737 | 3.31735 | 6.22536 | 27.227 |
| QP-thermo-hard HistoryGNO | Plastic-work inc. rel. L2 | 1.5*IQR | 4.98495 | 19.7266 | 1 | 20260521=31.1405 | 14.5441 | 8.66796 | 10.5784 | 3.68542 | 6.28994 | 31.1405 |
| QP-thermo-hard HistoryGNO | Reversal hist-inc. rel. L2 | 1.5*IQR | 0.999739 | 1.00041 | 1 | 20260518=0.997802 | 0.999682 | 0.000948941 | 1.00008 | 0.000168681 | 0.997802 | 1.00038 |
| QP-thermo-hard HistoryGNO | Reversal yield-flag MAE | 1.5*IQR | 0.862762 | 0.864475 | 1 | 20260518=0.856559 | 0.862262 | 0.00285602 | 0.863681 | 0.00042814 | 0.856559 | 0.863834 |
| QP-thermo-hard HistoryGNO | Yield-surface RMS | 1.5*IQR | -8.24996e-06 | 1.39381e-05 | 1 | 20260518=3.89063e-05 | 9.53655e-06 | 1.48304e-05 | 3.02878e-06 | 5.54702e-06 | 5.95461e-08 | 3.89063e-05 |
| QP-thermo-hard HistoryGNO | FEM residual rel. RMS | 1.5*IQR | -76.5691 | 369.329 | 1 | 20260520=369.419 | 172.283 | 113.831 | 162.105 | 111.475 | 37.1312 | 369.419 |
| QP-thermo-hard HistoryGNO | FEM energy rel. err. | 1.5*IQR | -15568.7 | 37376.6 | 1 | 20260520=43741.9 | 14689.8 | 15599.8 | 7539.72 | 13236.3 | 359.37 | 43741.9 |