# J2 Path-Dependent Baseline Per-Seed Appendix

Per-seed cyclic-path metrics for diagnosing stochastic training stability and outliers.

| Model | Seed | Train final loss | Cyclic disp. rel. L2 | Cyclic history rel. L2 | History-increment rel. L2 | QP history rel. L2 | QP history-inc. rel. L2 | Eqp increment rel. L2 | Plastic-work inc. rel. L2 | Reversal hist-inc. rel. L2 | Reversal yield-flag MAE | Yield-surface RMS | Plastic-work violation abs. | Plastic-work violation target-norm. | Plastic-work violation pred-norm. | FEM residual rel. RMS | FEM energy rel. err. |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| QP-thermo-hard HistoryGNO | 20260517 | 3137.91 | 32.1389 | 1.42958 | 1.0001 | 2.30114 | 1.0002 | 9.37321 | 9.88073 | 1.00007 | 0.730874 | 5.71222e-08 | 0 | 0 | 0 | 24.2028 | 66.1264 |
| QP-thermo-hard HistoryGNO | 20260518 | 6503.17 | 51.9613 | 1.42873 | 1.00004 | 2.30002 | 1.00009 | 4.97916 | 5.00792 | 1.00003 | 0.73087 | 1.91467e-07 | 0 | 0 | 0 | 38.4763 | 2097.51 |
| QP-thermo-hard HistoryGNO | 20260519 | 12986.9 | 38.153 | 1.42938 | 1.00008 | 2.30088 | 1.00016 | 8.18794 | 8.49613 | 1.00006 | 0.730874 | 5.7414e-08 | 0 | 0 | 0 | 59.3127 | 4314.66 |
| QP-thermo-hard HistoryGNO | 20260520 | 3647.11 | 62.3993 | 1.42019 | 0.999676 | 2.28546 | 0.999951 | 4.27405 | 4.3363 | 0.998509 | 0.729411 | 1.94003e-05 | 0 | 0 | 0 | 198.167 | 16322.5 |
| QP-thermo-hard HistoryGNO | 20260521 | 14628.8 | 93.4582 | 1.43122 | 1.00019 | 2.30313 | 1.0004 | 16.4625 | 18.5262 | 1.00016 | 0.730874 | 6.02472e-08 | 0 | 0 | 0 | 47.5594 | 1067.47 |