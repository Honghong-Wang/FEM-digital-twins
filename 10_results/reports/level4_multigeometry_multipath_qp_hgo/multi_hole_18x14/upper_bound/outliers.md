# J2 Path-Dependent Baseline Outlier Diagnostics

Outliers are detected on cyclic-path metrics using a 1.5 IQR rule when IQR is nonzero, otherwise a 3 sigma rule is used.

| Model | Metric | Rule | Lower | Upper | Outlier count | Outlier seeds | Mean | Std | Median | IQR | Min | Max |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| QP-thermo-hard HistoryGNO | Cyclic disp. rel. L2 | 1.5*IQR | 6.25189 | 25.4719 | 1 | 20260521=55.8807 | 23.294 | 16.5101 | 17.7463 | 4.805 | 11.1193 | 55.8807 |
| QP-thermo-hard HistoryGNO | Cyclic history rel. L2 | 1.5*IQR | 1.07021 | 1.17203 | 1 | 20260520=0.960218 | 1.09371 | 0.0674458 | 1.13189 | 0.0254546 | 0.960218 | 1.13422 |
| QP-thermo-hard HistoryGNO | History-increment rel. L2 | 1.5*IQR | 0.991356 | 1.0147 | 1 | 20260520=1.0507 | 1.01139 | 0.0197844 | 1.00013 | 0.00583529 | 1.00008 | 1.0507 |
| QP-thermo-hard HistoryGNO | QP history rel. L2 | 1.5*IQR | 1.76829 | 1.93886 | 1 | 20260520=1.61393 | 1.81377 | 0.10124 | 1.87244 | 0.0426424 | 1.61393 | 1.87535 |
| QP-thermo-hard HistoryGNO | QP history-inc. rel. L2 | 1.5*IQR | 0.990322 | 1.01668 | 1 | 20260520=1.11858 | 1.0252 | 0.0467615 | 1.00022 | 0.00658894 | 1.00018 | 1.11858 |
| QP-thermo-hard HistoryGNO | Reversal hist-inc. rel. L2 | 1.5*IQR | 0.999164 | 1.00097 | 2 | 20260519=0.993625; 20260520=1.12796 | 1.02439 | 0.0518457 | 1.00022 | 0.000452757 | 0.993625 | 1.12796 |
| QP-thermo-hard HistoryGNO | Reversal yield-flag MAE | 1.5*IQR | 0.454385 | 0.473831 | 1 | 20260520=0.497082 | 0.469778 | 0.0137771 | 0.461926 | 0.00486144 | 0.461667 | 0.497082 |
| QP-thermo-hard HistoryGNO | Yield-surface RMS | 1.5*IQR | -7.40302e-05 | 0.000124622 | 1 | 20260520=0.0366923 | 0.00735013 | 0.0146711 | 7.70612e-06 | 4.9663e-05 | 6.45379e-08 | 0.0366923 |
| QP-thermo-hard HistoryGNO | FEM residual rel. RMS | 1.5*IQR | 7.08896 | 36.8321 | 1 | 20260518=38.4144 | 24.0129 | 8.35003 | 23.9697 | 7.4358 | 13.7591 | 38.4144 |