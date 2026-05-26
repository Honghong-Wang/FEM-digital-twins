# J2 Path-Dependent Baseline Outlier Diagnostics

Outliers are detected on cyclic-path metrics using a 1.5 IQR rule when IQR is nonzero, otherwise a 3 sigma rule is used.

| Model | Metric | Rule | Lower | Upper | Outlier count | Outlier seeds | Mean | Std | Median | IQR | Min | Max |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| QP-thermo-hard HistoryGNO | History-increment rel. L2 | 1.5*IQR | 0.9985 | 1.00105 | 1 | 20260519=0.998332 | 0.999512 | 0.000650142 | 0.999553 | 0.000636697 | 0.998332 | 1.00013 |
| QP-thermo-hard HistoryGNO | QP history-inc. rel. L2 | 1.5*IQR | 0.999707 | 1.00048 | 2 | 20260518=1.00365; 20260519=0.999636 | 1.00073 | 0.0014733 | 1.00016 | 0.000194311 | 0.999636 | 1.00365 |
| QP-thermo-hard HistoryGNO | Reversal hist-inc. rel. L2 | 1.5*IQR | 0.98864 | 1.01862 | 1 | 20260518=1.01994 | 1.00554 | 0.00773022 | 1.00063 | 0.00749552 | 0.999879 | 1.01994 |
| QP-thermo-hard HistoryGNO | Reversal yield-flag MAE | 1.5*IQR | 0.425044 | 0.440401 | 1 | 20260518=0.440517 | 0.433596 | 0.00374913 | 0.431218 | 0.00383922 | 0.430798 | 0.440517 |
| QP-thermo-hard HistoryGNO | FEM energy rel. err. | 1.5*IQR | -624.965 | 4474.22 | 1 | 20260520=11327.3 | 3352.22 | 4057.13 | 1386.12 | 1274.8 | 198.462 | 11327.3 |