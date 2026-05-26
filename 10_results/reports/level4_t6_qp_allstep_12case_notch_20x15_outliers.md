# J2 Path-Dependent Baseline Outlier Diagnostics

Outliers are detected on cyclic-path metrics using a 1.5 IQR rule when IQR is nonzero, otherwise a 3 sigma rule is used.

| Model | Metric | Rule | Lower | Upper | Outlier count | Outlier seeds | Mean | Std | Median | IQR | Min | Max |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| QP-thermo-hard HistoryGNO | Cyclic history rel. L2 | 1.5*IQR | 1.84685 | 1.91498 | 1 | 20260518=1.74126 | 1.85387 | 0.0568106 | 1.87485 | 0.0170306 | 1.74126 | 1.8914 |
| QP-thermo-hard HistoryGNO | History-increment rel. L2 | 1.5*IQR | 0.99809 | 1.00138 | 1 | 20260518=0.992815 | 0.998504 | 0.00286157 | 1.00005 | 0.000822365 | 0.992815 | 1.00018 |
| QP-thermo-hard HistoryGNO | QP history rel. L2 | 1.5*IQR | 2.77951 | 2.88596 | 1 | 20260518=2.64584 | 2.79711 | 0.0764703 | 2.82569 | 0.0266128 | 2.64584 | 2.84855 |
| QP-thermo-hard HistoryGNO | QP history-inc. rel. L2 | 1.5*IQR | 0.998031 | 1.00167 | 1 | 20260518=0.995729 | 0.999183 | 0.00176113 | 1.00011 | 0.000909686 | 0.995729 | 1.00037 |
| QP-thermo-hard HistoryGNO | Eqp increment rel. L2 | 1.5*IQR | 4.14267 | 8.93178 | 2 | 20260518=3.99426; 20260521=13.3985 | 7.30432 | 3.21098 | 6.05436 | 1.19728 | 3.99426 | 13.3985 |
| QP-thermo-hard HistoryGNO | Plastic-work inc. rel. L2 | 1.5*IQR | 4.12037 | 9.19592 | 2 | 20260518=4.07767; 20260521=14.4081 | 7.59702 | 3.55934 | 6.18302 | 1.26889 | 4.07767 | 14.4081 |
| QP-thermo-hard HistoryGNO | Reversal hist-inc. rel. L2 | 1.5*IQR | 0.994808 | 1.00312 | 1 | 20260518=0.968939 | 0.993185 | 0.0121489 | 0.99895 | 0.00207812 | 0.968939 | 1.00011 |
| QP-thermo-hard HistoryGNO | Reversal yield-flag MAE | 1.5*IQR | 0.816238 | 0.837389 | 1 | 20260518=0.773293 | 0.816466 | 0.0216886 | 0.825796 | 0.00528759 | 0.773293 | 0.829615 |
| QP-thermo-hard HistoryGNO | Yield-surface RMS | 1.5*IQR | -3.559e-05 | 6.46657e-05 | 1 | 20260518=9.72324e-05 | 3.00996e-05 | 3.53353e-05 | 2.4123e-05 | 2.50639e-05 | 6.70129e-08 | 9.72324e-05 |
| QP-thermo-hard HistoryGNO | FEM energy rel. err. | 1.5*IQR | -10222 | 25752.2 | 1 | 20260520=54345.9 | 16008.3 | 19648.1 | 9846.15 | 8993.57 | 319.212 | 54345.9 |