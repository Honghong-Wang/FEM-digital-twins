# J2 Path-Dependent Baseline Outlier Diagnostics

Outliers are detected on cyclic-primary metrics using a 1.5 IQR rule when IQR is nonzero, otherwise a 3 sigma rule is used.
All evaluated paths are stored in JSON: `monotonic, cyclic`.

| Model | Metric | Rule | Lower | Upper | Outlier count | Outlier seeds | Mean | Std | Median | IQR | Min | Max |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| QP plastic-memory corrector HistoryGNO | Cyclic disp. rel. L2 | 1.5*IQR | 52.843 | 112.184 | 2 | 20260519=183.024; 20260520=34.8749 | 94.2533 | 48.6346 | 88.3407 | 14.8353 | 34.8749 | 183.024 |
| QP plastic-memory corrector HistoryGNO | QP eqp rel. L2 | 1.5*IQR | 0.796046 | 1.30437 | 1 | 20260519=2.02931 | 1.22981 | 0.402688 | 1.04188 | 0.127082 | 0.977445 | 2.02931 |
| QP plastic-memory corrector HistoryGNO | QP plastic-work rel. L2 | 1.5*IQR | 0.816394 | 1.27288 | 1 | 20260519=1.9683 | 1.21449 | 0.379427 | 1.0361 | 0.114122 | 0.978768 | 1.9683 |
| QP plastic-memory corrector HistoryGNO | QP von-Mises rel. L2 | 1.5*IQR | 1.16983 | 1.1995 | 1 | 20260519=1.2042 | 1.18798 | 0.00872187 | 1.18651 | 0.00741935 | 1.17987 | 1.2042 |
| QP plastic-memory corrector HistoryGNO | Eqp increment rel. L2 | 1.5*IQR | 0.719422 | 1.42738 | 1 | 20260519=2.2838 | 1.29363 | 0.499601 | 1.06239 | 0.176989 | 0.975141 | 2.2838 |
| QP plastic-memory corrector HistoryGNO | Plastic-work inc. rel. L2 | 1.5*IQR | 0.745481 | 1.38636 | 1 | 20260519=2.21987 | 1.27647 | 0.475593 | 1.05428 | 0.160221 | 0.97633 | 2.21987 |
| QP plastic-memory corrector HistoryGNO | FEM residual rel. RMS | 1.5*IQR | 48.1298 | 149.241 | 2 | 20260518=35.5119; 20260520=196.9 | 105.85 | 52.3458 | 99.4662 | 25.2778 | 35.5119 | 196.9 |