# J2 Path-Dependent Baseline Per-Seed Appendix

Per-seed cyclic-primary metrics for diagnosing stochastic training stability and outliers.
All evaluated paths are stored in JSON: `monotonic, cyclic`.

| Model | Seed | Train final loss | Cyclic disp. rel. L2 | Cyclic history rel. L2 | History-increment rel. L2 | QP history rel. L2 | QP history-inc. rel. L2 | QP eqp rel. L2 | QP plastic-work rel. L2 | QP von-Mises rel. L2 | Eqp increment rel. L2 | Plastic-work inc. rel. L2 | Reversal hist-inc. rel. L2 | Reversal yield-flag MAE | Yield-surface RMS | Plastic-work violation abs. | Plastic-work violation target-norm. | Plastic-work violation pred-norm. | FEM residual rel. RMS | FEM energy rel. err. |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| QP-aware active-zone thermo-hard HistoryGNO | 20260517 | 977.56 | 65.8053 | 0.998842 | 1.00001 | 0.997548 | 1.00001 | 1 | 1 | 0.952947 | 1 | 1 | 0.999974 | 0.136166 | 3.68352e-09 | 0 | 0 | 0 | 85.8479 | 3617.42 |
| QP-aware active-zone thermo-hard HistoryGNO | 20260518 | 2230.12 | 45.1384 | 0.999892 | 1 | 0.999775 | 1 | 1 | 1 | 0.995768 | 1 | 1 | 0.999998 | 0.136166 | 2.16875e-09 | 0 | 0 | 0 | 38.9858 | 578.966 |
| QP-aware active-zone thermo-hard HistoryGNO | 20260519 | 5534.75 | 115.668 | 2.20373 | 0.999915 | 3.38805 | 0.999938 | 6.85426 | 6.73603 | 1.27515 | 5.04942 | 5.04558 | 0.999851 | 0.863115 | 1.053e-05 | 0 | 0 | 0 | 79.2254 | 2291.57 |
| QP-aware active-zone thermo-hard HistoryGNO | 20260520 | 6524.37 | 177.542 | 0.991218 | 1.00008 | 0.981207 | 1.00017 | 1 | 1 | 0.54946 | 1 | 1 | 0.999743 | 0.136168 | 1.51179e-05 | 0 | 0 | 0 | 119.225 | 6536.67 |
| QP-aware active-zone thermo-hard HistoryGNO | 20260521 | 11461.9 | 75.3247 | 1.04167 | 1.13428 | 1.20376 | 1.2257 | 0.995362 | 0.995683 | 0.922974 | 1 | 1 | 0.94407 | 0.158383 | 0.00522356 | 0 | 0 | 0 | 91.9996 | 2370.73 |