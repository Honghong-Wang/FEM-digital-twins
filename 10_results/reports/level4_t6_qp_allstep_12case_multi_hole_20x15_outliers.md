# J2 Path-Dependent Baseline Outlier Diagnostics

Outliers are detected on cyclic-path metrics using a 1.5 IQR rule when IQR is nonzero, otherwise a 3 sigma rule is used.

| Model | Metric | Rule | Lower | Upper | Outlier count | Outlier seeds | Mean | Std | Median | IQR | Min | Max |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| QP-thermo-hard HistoryGNO | Cyclic disp. rel. L2 | 1.5*IQR | 24.0386 | 70.8413 | 2 | 20260517=23.516; 20260521=100.821 | 54.3714 | 25.6015 | 52.64 | 11.7007 | 23.516 | 100.821 |
| QP-thermo-hard HistoryGNO | Cyclic history rel. L2 | 1.5*IQR | 1.65677 | 1.66065 | 1 | 20260520=1.2693 | 1.5811 | 0.155904 | 1.65833 | 0.000971556 | 1.2693 | 1.66046 |
| QP-thermo-hard HistoryGNO | History-increment rel. L2 | 1.5*IQR | 1.00002 | 1.0003 | 1 | 20260520=0.971217 | 0.994393 | 0.0115882 | 1.00014 | 6.9499e-05 | 0.971217 | 1.00029 |
| QP-thermo-hard HistoryGNO | QP history rel. L2 | 1.5*IQR | 2.5438 | 2.54897 | 1 | 20260520=2.18567 | 2.47458 | 0.144456 | 2.54588 | 0.00129271 | 2.18567 | 2.54857 |
| QP-thermo-hard HistoryGNO | QP history-inc. rel. L2 | 1.5*IQR | 0.999785 | 1.00105 | 1 | 20260520=1.22999 | 1.04629 | 0.091848 | 1.00038 | 0.000315666 | 1.00026 | 1.22999 |
| QP-thermo-hard HistoryGNO | Plastic-work inc. rel. L2 | 1.5*IQR | 4.82992 | 26.629 | 1 | 20260521=26.6548 | 15.622 | 6.60894 | 13.0429 | 5.44976 | 6.95352 | 26.6548 |
| QP-thermo-hard HistoryGNO | Reversal hist-inc. rel. L2 | 1.5*IQR | 1 | 1.00019 | 2 | 20260520=0.897096; 20260521=1.0002 | 0.97951 | 0.0412073 | 1.00007 | 4.69685e-05 | 0.897096 | 1.0002 |
| QP-thermo-hard HistoryGNO | Reversal yield-flag MAE | 1.5*IQR | 0.765745 | 0.765778 | 1 | 20260520=0.589181 | 0.730447 | 0.0706332 | 0.765766 | 8.16584e-06 | 0.589181 | 0.765766 |
| QP-thermo-hard HistoryGNO | Yield-surface RMS | 1.5*IQR | -4.21654e-07 | 8.62766e-07 | 1 | 20260520=0.09708 | 0.0194161 | 0.0388319 | 6.11024e-08 | 3.21105e-07 | 5.81364e-08 | 0.09708 |
| QP-thermo-hard HistoryGNO | FEM residual rel. RMS | 1.5*IQR | -10.875 | 169.877 | 1 | 20260520=283.41 | 113.697 | 87.5702 | 85.9217 | 45.188 | 40.15 | 283.41 |
| QP-thermo-hard HistoryGNO | FEM energy rel. err. | 1.5*IQR | -3458.87 | 10974.8 | 1 | 20260520=18334.4 | 5992.66 | 6402.14 | 3658.72 | 3608.41 | 454.3 | 18334.4 |