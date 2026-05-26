# J2 Path-Dependent Baseline Outlier Diagnostics

Outliers are detected on cyclic-path metrics using a 1.5 IQR rule when IQR is nonzero, otherwise a 3 sigma rule is used.

| Model | Metric | Rule | Lower | Upper | Outlier count | Outlier seeds | Mean | Std | Median | IQR | Min | Max |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| QP-thermo-hard HistoryGNO | Cyclic disp. rel. L2 | 1.5*IQR | 10.8046 | 14.0071 | 1 | 20260518=23.148 | 14.3718 | 4.4272 | 12.7228 | 0.800631 | 11.1765 | 23.148 |
| QP-thermo-hard HistoryGNO | Cyclic history rel. L2 | 1.5*IQR | 1.36872 | 1.36916 | 2 | 20260518=1.32659; 20260521=1.36994 | 1.36067 | 0.0170451 | 1.36896 | 0.000109553 | 1.32659 | 1.36994 |
| QP-thermo-hard HistoryGNO | History-increment rel. L2 | 1.5*IQR | 1.00003 | 1.0001 | 2 | 20260518=0.998117; 20260521=1.00012 | 0.999687 | 0.000785399 | 1.00007 | 1.60933e-05 | 0.998117 | 1.00012 |
| QP-thermo-hard HistoryGNO | QP history rel. L2 | 1.5*IQR | 2.08121 | 2.08218 | 2 | 20260518=2.02851; 20260521=2.08285 | 2.0713 | 0.0213971 | 2.08173 | 0.000242949 | 2.02851 | 2.08285 |
| QP-thermo-hard HistoryGNO | QP history-inc. rel. L2 | 1.5*IQR | 1.00011 | 1.00011 | 2 | 20260518=0.999491; 20260521=1.0002 | 1 | 0.000258999 | 1.00011 | 8.34465e-07 | 0.999491 | 1.0002 |
| QP-thermo-hard HistoryGNO | Eqp increment rel. L2 | 1.5*IQR | 6.80827 | 7.01065 | 2 | 20260520=6.57149; 20260521=10.9875 | 7.65343 | 1.67206 | 6.88923 | 0.0505953 | 6.57149 | 10.9875 |
| QP-thermo-hard HistoryGNO | Plastic-work inc. rel. L2 | 1.5*IQR | 6.97057 | 8.26296 | 1 | 20260521=12.6708 | 8.53677 | 2.0805 | 7.68666 | 0.323098 | 7.0929 | 12.6708 |
| QP-thermo-hard HistoryGNO | Reversal hist-inc. rel. L2 | 1.5*IQR | 0.999926 | 0.999956 | 1 | 20260518=1.01002 | 1.00195 | 0.00403068 | 0.999939 | 7.39098e-06 | 0.999937 | 1.01002 |
| QP-thermo-hard HistoryGNO | Yield-surface RMS | 1.5*IQR | 8.86428e-09 | 1.17776e-07 | 1 | 20260518=4.75692e-05 | 9.55927e-06 | 1.9005e-05 | 5.12309e-08 | 2.72278e-08 | 4.92718e-08 | 4.75692e-05 |
| QP-thermo-hard HistoryGNO | FEM residual rel. RMS | 1.5*IQR | 19.9689 | 61.1684 | 1 | 20260518=110.32 | 52.1584 | 30.1753 | 45.5406 | 10.2999 | 23.7944 | 110.32 |
| QP-thermo-hard HistoryGNO | FEM energy rel. err. | 1.5*IQR | -285.827 | 1137.14 | 1 | 20260518=1660.65 | 605.647 | 553.025 | 410.678 | 355.742 | 105.589 | 1660.65 |