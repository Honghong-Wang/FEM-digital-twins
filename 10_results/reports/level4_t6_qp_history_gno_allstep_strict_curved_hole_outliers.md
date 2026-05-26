# J2 Path-Dependent Baseline Outlier Diagnostics

Outliers are detected on cyclic-path metrics using a 1.5 IQR rule when IQR is nonzero, otherwise a 3 sigma rule is used.

| Model | Metric | Rule | Lower | Upper | Outlier count | Outlier seeds | Mean | Std | Median | IQR | Min | Max |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| QP-thermo-hard HistoryGNO | Cyclic history rel. L2 | 1.5*IQR | 1.08619 | 1.14651 | 1 | 20260518=1.07237 | 1.11012 | 0.0196951 | 1.12142 | 0.0150814 | 1.07237 | 1.1241 |
| QP-thermo-hard HistoryGNO | QP history rel. L2 | 1.5*IQR | 1.75196 | 1.83873 | 1 | 20260518=1.73545 | 1.78691 | 0.0269631 | 1.80186 | 0.0216919 | 1.73545 | 1.80656 |
| QP-thermo-hard HistoryGNO | QP history-inc. rel. L2 | 1.5*IQR | 0.999718 | 1.00046 | 2 | 20260518=1.00317; 20260519=0.999492 | 1.0006 | 0.00130987 | 1.00016 | 0.000186622 | 0.999492 | 1.00317 |
| QP-thermo-hard HistoryGNO | Reversal hist-inc. rel. L2 | 1.5*IQR | 0.992318 | 1.01249 | 1 | 20260518=1.0189 | 1.00485 | 0.00727528 | 1.00063 | 0.0050441 | 0.999881 | 1.0189 |
| QP-thermo-hard HistoryGNO | Reversal yield-flag MAE | 1.5*IQR | 0.426858 | 0.437374 | 1 | 20260518=0.440061 | 0.433262 | 0.00353709 | 0.43122 | 0.00262913 | 0.430798 | 0.440061 |
| QP-thermo-hard HistoryGNO | FEM energy rel. err. | 1.5*IQR | -1086.3 | 3601.87 | 1 | 20260520=8683.72 | 2455.74 | 3162.37 | 937.04 | 1172.04 | 142.362 | 8683.72 |