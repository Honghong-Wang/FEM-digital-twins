# J2 Path-Dependent Baseline Outlier Diagnostics

Outliers are detected on cyclic-path metrics using a 1.5 IQR rule when IQR is nonzero, otherwise a 3 sigma rule is used.

| Model | Metric | Rule | Lower | Upper | Outlier count | Outlier seeds | Mean | Std | Median | IQR | Min | Max |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| QP-thermo-hard HistoryGNO | Cyclic disp. rel. L2 | 1.5*IQR | 47.6133 | 69.4347 | 2 | 20260517=17.7906; 20260521=87.5838 | 56.6054 | 22.3807 | 60.6046 | 5.45537 | 17.7906 | 87.5838 |
| QP-thermo-hard HistoryGNO | Cyclic history rel. L2 | 1.5*IQR | 1.36626 | 1.37097 | 1 | 20260520=0.970462 | 1.28927 | 0.159407 | 1.36901 | 0.00117779 | 0.970462 | 1.36967 |
| QP-thermo-hard HistoryGNO | History-increment rel. L2 | 1.5*IQR | 1 | 1.00016 | 2 | 20260517=0.999936; 20260520=1.00017 | 1.00007 | 7.63343e-05 | 1.00008 | 4.08888e-05 | 0.999936 | 1.00017 |
| QP-thermo-hard HistoryGNO | QP history rel. L2 | 1.5*IQR | 2.07798 | 2.08449 | 1 | 20260520=1.68919 | 2.00318 | 0.156996 | 2.08171 | 0.00162911 | 1.68919 | 2.08254 |
| QP-thermo-hard HistoryGNO | QP history-inc. rel. L2 | 1.5*IQR | 0.999996 | 1.00027 | 2 | 20260517=0.99999; 20260520=1.00042 | 1.00016 | 0.000144513 | 1.00012 | 6.79493e-05 | 0.99999 | 1.00042 |
| QP-thermo-hard HistoryGNO | Reversal hist-inc. rel. L2 | 1.5*IQR | 0.999912 | 0.999985 | 1 | 20260517=1.00008 | 0.999971 | 5.51311e-05 | 0.99994 | 1.81198e-05 | 0.999937 | 1.00008 |
| QP-thermo-hard HistoryGNO | Yield-surface RMS | 1.5*IQR | -4.85851e-06 | 8.23018e-06 | 1 | 20260520=0.165827 | 0.0331662 | 0.0663306 | 5.01028e-08 | 3.27217e-06 | 4.71335e-08 | 0.165827 |
| QP-thermo-hard HistoryGNO | FEM residual rel. RMS | 1.5*IQR | -14.878 | 168.675 | 1 | 20260520=246.689 | 99.503 | 76.9245 | 66.5257 | 45.8884 | 30.5031 | 246.689 |
| QP-thermo-hard HistoryGNO | FEM energy rel. err. | 1.5*IQR | -529.249 | 2884 | 1 | 20260520=8463.7 | 2383.35 | 3071.33 | 860.131 | 853.311 | 238.178 | 8463.7 |