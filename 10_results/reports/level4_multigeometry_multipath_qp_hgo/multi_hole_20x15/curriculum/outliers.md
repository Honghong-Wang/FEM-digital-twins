# J2 Path-Dependent Baseline Outlier Diagnostics

Outliers are detected on cyclic-path metrics using a 1.5 IQR rule when IQR is nonzero, otherwise a 3 sigma rule is used.

| Model | Metric | Rule | Lower | Upper | Outlier count | Outlier seeds | Mean | Std | Median | IQR | Min | Max |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| QP-thermo-hard HistoryGNO | Cyclic disp. rel. L2 | 1.5*IQR | 47.3333 | 59.9582 | 2 | 20260517=25.0236; 20260521=97.0894 | 56.4602 | 23.1193 | 52.8966 | 3.15624 | 25.0236 | 97.0894 |
| QP-thermo-hard HistoryGNO | Cyclic history rel. L2 | 1.5*IQR | 1.65676 | 1.6605 | 1 | 20260520=1.2136 | 1.56988 | 0.178141 | 1.65827 | 0.000935078 | 1.2136 | 1.66026 |
| QP-thermo-hard HistoryGNO | History-increment rel. L2 | 1.5*IQR | 0.99992 | 1.00049 | 1 | 20260520=1.04741 | 1.00963 | 0.018893 | 1.00019 | 0.000142336 | 1.00012 | 1.04741 |
| QP-thermo-hard HistoryGNO | QP history rel. L2 | 1.5*IQR | 2.54379 | 2.54878 | 1 | 20260520=2.12037 | 2.46141 | 0.170522 | 2.54581 | 0.00124717 | 2.12037 | 2.54831 |
| QP-thermo-hard HistoryGNO | QP history-inc. rel. L2 | 1.5*IQR | 0.999818 | 1.00098 | 1 | 20260520=1.23521 | 1.04732 | 0.0939428 | 1.00036 | 0.000289917 | 1.00025 | 1.23521 |
| QP-thermo-hard HistoryGNO | Reversal hist-inc. rel. L2 | 1.5*IQR | 1 | 1.00018 | 2 | 20260520=0.998815; 20260521=1.00018 | 0.999849 | 0.000518754 | 1.00007 | 4.45843e-05 | 0.998815 | 1.00018 |
| QP-thermo-hard HistoryGNO | Reversal yield-flag MAE | 1.5*IQR | 0.765739 | 0.765782 | 1 | 20260520=0.588578 | 0.730326 | 0.070874 | 0.765766 | 1.06096e-05 | 0.588578 | 0.765766 |
| QP-thermo-hard HistoryGNO | Yield-surface RMS | 1.5*IQR | -5.6728e-07 | 1.10693e-06 | 1 | 20260520=0.127277 | 0.0254556 | 0.0509109 | 6.06358e-08 | 4.18553e-07 | 5.80374e-08 | 0.127277 |
| QP-thermo-hard HistoryGNO | FEM residual rel. RMS | 1.5*IQR | -28.2859 | 179.093 | 1 | 20260520=284.053 | 110.218 | 89.7602 | 78.9519 | 51.8446 | 37.2773 | 284.053 |
| QP-thermo-hard HistoryGNO | FEM energy rel. err. | 1.5*IQR | -4234.71 | 11399.3 | 1 | 20260520=18425.3 | 5844.29 | 6521.24 | 3233.76 | 3908.5 | 397.79 | 18425.3 |