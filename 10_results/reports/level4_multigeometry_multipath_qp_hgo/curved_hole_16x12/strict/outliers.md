# J2 Path-Dependent Baseline Outlier Diagnostics

Outliers are detected on cyclic-path metrics using a 1.5 IQR rule when IQR is nonzero, otherwise a 3 sigma rule is used.

| Model | Metric | Rule | Lower | Upper | Outlier count | Outlier seeds | Mean | Std | Median | IQR | Min | Max |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| QP-thermo-hard HistoryGNO | Cyclic disp. rel. L2 | 1.5*IQR | 127.21 | 226.982 | 1 | 20260518=103.123 | 169.09 | 37.1098 | 173.486 | 24.943 | 103.123 | 214.647 |
| QP-thermo-hard HistoryGNO | Cyclic history rel. L2 | 1.5*IQR | 1.07484 | 1.07526 | 2 | 20260518=0.754976; 20260521=1.07527 | 1.01108 | 0.128052 | 1.07505 | 0.000103354 | 0.754976 | 1.07527 |
| QP-thermo-hard HistoryGNO | History-increment rel. L2 | 1.5*IQR | 1.00002 | 1.00006 | 2 | 20260518=1.00007; 20260519=1.00002 | 1.00004 | 1.83031e-05 | 1.00004 | 9.41753e-06 | 1.00002 | 1.00007 |
| QP-thermo-hard HistoryGNO | QP history rel. L2 | 1.5*IQR | 1.88236 | 1.88273 | 2 | 20260518=1.52976; 20260521=1.88276 | 1.81203 | 0.141134 | 1.88255 | 9.17912e-05 | 1.52976 | 1.88276 |
| QP-thermo-hard HistoryGNO | QP history-inc. rel. L2 | 1.5*IQR | 1.00002 | 1.00012 | 1 | 20260518=1.00015 | 1.00008 | 3.76092e-05 | 1.00008 | 2.563e-05 | 1.00004 | 1.00015 |
| QP-thermo-hard HistoryGNO | Eqp increment rel. L2 | 1.5*IQR | 5.4619 | 8.87055 | 2 | 20260518=2.03635; 20260521=9.14101 | 6.57976 | 2.40451 | 7.38898 | 0.852162 | 2.03635 | 9.14101 |
| QP-thermo-hard HistoryGNO | Plastic-work inc. rel. L2 | 1.5*IQR | 5.54754 | 9.39121 | 2 | 20260518=2.0922; 20260521=9.73662 | 6.90121 | 2.56805 | 7.73847 | 0.960918 | 2.0922 | 9.73662 |
| QP-thermo-hard HistoryGNO | Reversal hist-inc. rel. L2 | 1.5*IQR | 0.999918 | 0.999941 | 1 | 20260518=0.999991 | 0.999941 | 2.55093e-05 | 0.999932 | 5.60284e-06 | 0.999921 | 0.999991 |
| QP-thermo-hard HistoryGNO | Reversal yield-flag MAE | 1.5*IQR | 0.423623 | 0.423654 | 1 | 20260518=0.525455 | 0.444 | 0.0407274 | 0.423635 | 7.86781e-06 | 0.423634 | 0.525455 |
| QP-thermo-hard HistoryGNO | Yield-surface RMS | 1.5*IQR | -2.81302e-07 | 6.02943e-07 | 1 | 20260518=0.170533 | 0.0341067 | 0.0682132 | 5.30999e-08 | 2.21061e-07 | 4.98693e-08 | 0.170533 |
| QP-thermo-hard HistoryGNO | FEM energy rel. err. | 1.5*IQR | -17372 | 33397.9 | 1 | 20260520=74637.4 | 18695.8 | 28420 | 2520.28 | 12692.5 | 295.181 | 74637.4 |