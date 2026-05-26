# J2 Path-Dependent Baseline Outlier Diagnostics

Outliers are detected on cyclic-path metrics using a 1.5 IQR rule when IQR is nonzero, otherwise a 3 sigma rule is used.

| Model | Metric | Rule | Lower | Upper | Outlier count | Outlier seeds | Mean | Std | Median | IQR | Min | Max |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| QP-thermo-hard HistoryGNO | History-increment rel. L2 | 1.5*IQR | 0.999975 | 1.00022 | 2 | 20260518=0.998645; 20260520=1.0007 | 0.999923 | 0.000680557 | 1.00008 | 6.05583e-05 | 0.998645 | 1.0007 |
| QP-thermo-hard HistoryGNO | Eqp increment rel. L2 | 1.5*IQR | 5.2318 | 8.46438 | 2 | 20260518=4.88295; 20260521=11.9925 | 7.47642 | 2.39502 | 6.81047 | 0.808146 | 4.88295 | 11.9925 |
| QP-thermo-hard HistoryGNO | Plastic-work inc. rel. L2 | 1.5*IQR | 5.6171 | 8.53771 | 2 | 20260518=4.94743; 20260521=12.7962 | 7.76751 | 2.65125 | 6.93915 | 0.730154 | 4.94743 | 12.7962 |