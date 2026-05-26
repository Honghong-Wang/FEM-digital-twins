# J2 Path-Dependent Baseline Per-Seed Appendix

Per-seed cyclic-primary metrics for diagnosing stochastic training stability and outliers.
All evaluated paths are stored in JSON: `monotonic, cyclic`.

| Model | Seed | Train final loss | Cyclic disp. rel. L2 | Cyclic history rel. L2 | History-increment rel. L2 | QP history rel. L2 | QP history-inc. rel. L2 | QP eqp rel. L2 | QP plastic-work rel. L2 | QP von-Mises rel. L2 | Eqp increment rel. L2 | Plastic-work inc. rel. L2 | Reversal hist-inc. rel. L2 | Reversal yield-flag MAE | Yield-surface RMS | Plastic-work violation abs. | Plastic-work violation target-norm. | Plastic-work violation pred-norm. | FEM residual rel. RMS | FEM energy rel. err. |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| QP-aware active-zone thermo-hard HistoryGNO | 20260517 | 956.549 | 73.3838 | 0.999863 | 1 | 0.999714 | 1 | 1 | 1 | 0.994625 | 1 | 1 | 0.999996 | 0.136166 | 2.19864e-09 | 0 | 0 | 0 | 72.6155 | 3751.05 |
| QP-aware active-zone thermo-hard HistoryGNO | 20260518 | 3412.79 | 31.803 | 0.991003 | 1.00017 | 0.981671 | 1.00027 | 1 | 1 | 0.566333 | 1 | 1 | 0.999769 | 0.136184 | 8.981e-05 | 0 | 0 | 0 | 31.9271 | 386.771 |
| QP-aware active-zone thermo-hard HistoryGNO | 20260519 | 1052.7 | 42.535 | 0.992372 | 1.00014 | 0.983619 | 1.00031 | 1 | 1 | 0.624785 | 1 | 1 | 0.999841 | 0.136166 | 1.8296e-06 | 0 | 0 | 0 | 167.014 | 14812.8 |
| QP-aware active-zone thermo-hard HistoryGNO | 20260520 | 5318.57 | 150.158 | 0.991471 | 1.00006 | 0.981518 | 1.00013 | 1 | 1 | 0.559673 | 1 | 1 | 0.999779 | 0.136167 | 9.54412e-06 | 0 | 0 | 0 | 121.163 | 6981.42 |
| QP-aware active-zone thermo-hard HistoryGNO | 20260521 | 9717.45 | 72.4802 | 0.991002 | 1.00014 | 0.981995 | 1.00023 | 1 | 1 | 0.577098 | 1 | 1 | 0.999698 | 0.136176 | 8.94919e-05 | 0 | 0 | 0 | 103.757 | 2981.27 |