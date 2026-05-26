# J2 Path-Dependent Baseline Outlier Diagnostics

Outliers are detected on cyclic-primary metrics using a 1.5 IQR rule when IQR is nonzero, otherwise a 3 sigma rule is used.
All evaluated paths are stored in JSON: `monotonic, cyclic`.

| Model | Metric | Rule | Lower | Upper | Outlier count | Outlier seeds | Mean | Std | Median | IQR | Min | Max |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| QP-aware active-zone thermo-hard HistoryGNO | Cyclic history rel. L2 | 1.5*IQR | 0.934597 | 1.10592 | 1 | 20260519=2.20373 | 1.24707 | 0.478657 | 0.999892 | 0.0428303 | 0.991218 | 2.20373 |
| QP-aware active-zone thermo-hard HistoryGNO | History-increment rel. L2 | 1.5*IQR | 0.999876 | 1.00021 | 1 | 20260521=1.13428 | 1.02686 | 0.0537127 | 1.00001 | 8.32081e-05 | 0.999915 | 1.13428 |
| QP-aware active-zone thermo-hard HistoryGNO | QP history rel. L2 | 1.5*IQR | 0.688237 | 1.51307 | 1 | 20260519=3.38805 | 1.51407 | 0.940566 | 0.999775 | 0.206207 | 0.981207 | 3.38805 |
| QP-aware active-zone thermo-hard HistoryGNO | QP history-inc. rel. L2 | 1.5*IQR | 0.999744 | 1.00043 | 1 | 20260521=1.2257 | 1.04516 | 0.0902664 | 1.00001 | 0.000171781 | 0.999938 | 1.2257 |
| QP-aware active-zone thermo-hard HistoryGNO | QP von-Mises rel. L2 | 1.5*IQR | 0.813782 | 1.10496 | 2 | 20260519=1.27515; 20260520=0.54946 | 0.939259 | 0.231693 | 0.952947 | 0.0727943 | 0.54946 | 1.27515 |
| QP-aware active-zone thermo-hard HistoryGNO | Reversal hist-inc. rel. L2 | 1.5*IQR | 0.999396 | 1.00032 | 1 | 20260521=0.94407 | 0.988727 | 0.0223288 | 0.999851 | 0.000231147 | 0.94407 | 0.999998 |
| QP-aware active-zone thermo-hard HistoryGNO | Reversal yield-flag MAE | 1.5*IQR | 0.102839 | 0.191709 | 1 | 20260519=0.863115 | 0.285999 | 0.288686 | 0.136168 | 0.0222175 | 0.136166 | 0.863115 |
| QP-aware active-zone thermo-hard HistoryGNO | Yield-surface RMS | 1.5*IQR | -2.26676e-05 | 3.77892e-05 | 1 | 20260521=0.00522356 | 0.00104984 | 0.00208687 | 1.053e-05 | 1.51142e-05 | 2.16875e-09 | 0.00522356 |
| QP-aware active-zone thermo-hard HistoryGNO | FEM residual rel. RMS | 1.5*IQR | 60.0642 | 111.161 | 2 | 20260518=38.9858; 20260520=119.225 | 83.0567 | 25.8953 | 85.8479 | 12.7741 | 38.9858 | 119.225 |
| QP-aware active-zone thermo-hard HistoryGNO | FEM energy rel. err. | 1.5*IQR | 302.812 | 5606.18 | 1 | 20260520=6536.67 | 3079.07 | 1980.77 | 2370.73 | 1325.84 | 578.966 | 6536.67 |