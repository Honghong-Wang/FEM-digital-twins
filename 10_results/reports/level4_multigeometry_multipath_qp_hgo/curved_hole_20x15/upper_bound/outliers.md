# J2 Path-Dependent Baseline Outlier Diagnostics

Outliers are detected on cyclic-path metrics using a 1.5 IQR rule when IQR is nonzero, otherwise a 3 sigma rule is used.

| Model | Metric | Rule | Lower | Upper | Outlier count | Outlier seeds | Mean | Std | Median | IQR | Min | Max |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| QP-thermo-hard HistoryGNO | Cyclic history rel. L2 | 1.5*IQR | 1.05673 | 1.05724 | 1 | 20260521=1.05764 | 1.05708 | 0.000298566 | 1.05705 | 0.000126123 | 1.05676 | 1.05764 |
| QP-thermo-hard HistoryGNO | History-increment rel. L2 | 1.5*IQR | 1.00006 | 1.0001 | 1 | 20260521=1.00011 | 1.00008 | 1.75631e-05 | 1.00008 | 9.89437e-06 | 1.00006 | 1.00011 |
| QP-thermo-hard HistoryGNO | QP history rel. L2 | 1.5*IQR | 1.81511 | 1.81565 | 1 | 20260521=1.81608 | 1.81548 | 0.00032081 | 1.81541 | 0.000135303 | 1.81512 | 1.81608 |
| QP-thermo-hard HistoryGNO | QP history-inc. rel. L2 | 1.5*IQR | 1.00009 | 1.0002 | 1 | 20260521=1.00022 | 1.00015 | 3.74337e-05 | 1.00014 | 2.86102e-05 | 1.00011 | 1.00022 |
| QP-thermo-hard HistoryGNO | Eqp increment rel. L2 | 1.5*IQR | 4.29719 | 6.60048 | 1 | 20260521=8.24346 | 5.84201 | 1.30251 | 5.71871 | 0.575822 | 4.35019 | 8.24346 |
| QP-thermo-hard HistoryGNO | Plastic-work inc. rel. L2 | 1.5*IQR | 4.50934 | 7.16604 | 1 | 20260521=9.20692 | 6.32279 | 1.55527 | 6.15744 | 0.664174 | 4.57418 | 9.20692 |
| QP-thermo-hard HistoryGNO | Reversal hist-inc. rel. L2 | 1.5*IQR | 1.00008 | 1.00018 | 1 | 20260521=1.00022 | 1.00014 | 4.24263e-05 | 1.00013 | 2.47955e-05 | 1.0001 | 1.00022 |
| QP-thermo-hard HistoryGNO | Reversal yield-flag MAE | 1.5*IQR | 0.439174 | 0.439179 | 1 | 20260519=0.43918 | 0.439177 | 1.49682e-06 | 0.439176 | 1.2815e-06 | 0.439175 | 0.43918 |
| QP-thermo-hard HistoryGNO | Yield-surface RMS | 1.5*IQR | 1.76217e-08 | 1.05985e-07 | 1 | 20260519=1.52736e-07 | 7.85298e-08 | 3.85359e-08 | 7.00802e-08 | 2.20908e-08 | 4.62261e-08 | 1.52736e-07 |
| QP-thermo-hard HistoryGNO | FEM energy rel. err. | 1.5*IQR | -1237.15 | 2994.03 | 1 | 20260517=3279.26 | 1308.08 | 1085.18 | 1229.47 | 1057.79 | 274.777 | 3279.26 |