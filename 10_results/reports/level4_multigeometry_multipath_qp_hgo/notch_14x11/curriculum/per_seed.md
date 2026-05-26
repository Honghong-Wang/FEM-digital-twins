# J2 Path-Dependent Baseline Per-Seed Appendix

Per-seed cyclic-path metrics for diagnosing stochastic training stability and outliers.

| Model | Seed | Train final loss | Cyclic disp. rel. L2 | Cyclic history rel. L2 | History-increment rel. L2 | QP history rel. L2 | QP history-inc. rel. L2 | Eqp increment rel. L2 | Plastic-work inc. rel. L2 | Reversal hist-inc. rel. L2 | Reversal yield-flag MAE | Yield-surface RMS | Plastic-work violation abs. | Plastic-work violation target-norm. | Plastic-work violation pred-norm. | FEM residual rel. RMS | FEM energy rel. err. |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| QP-thermo-hard HistoryGNO | 20260517 | 3582.07 | 39.3818 | 1.42913 | 1.00007 | 2.30054 | 1.00015 | 7.22448 | 7.46355 | 1.00005 | 0.730872 | 8.5028e-08 | 0 | 0 | 0 | 26.9826 | 76.86 |
| QP-thermo-hard HistoryGNO | 20260518 | 5381.43 | 51.3582 | 1.42817 | 1.00001 | 2.29927 | 1.00004 | 4.30576 | 4.32167 | 0.99996 | 0.730812 | 1.92139e-06 | 0 | 0 | 0 | 38.1951 | 2101.41 |
| QP-thermo-hard HistoryGNO | 20260519 | 11731.9 | 38.1221 | 1.42912 | 1.00007 | 2.30054 | 1.00013 | 6.86983 | 7.03413 | 1.00005 | 0.730874 | 5.1505e-08 | 0 | 0 | 0 | 59.4882 | 4386.84 |
| QP-thermo-hard HistoryGNO | 20260520 | 3471 | 61.8891 | 1.42521 | 0.999868 | 2.2941 | 0.999998 | 3.92463 | 3.92617 | 0.999421 | 0.730303 | 9.77757e-06 | 0 | 0 | 0 | 188.876 | 15063.7 |
| QP-thermo-hard HistoryGNO | 20260521 | 11991.6 | 93.6504 | 1.43068 | 1.00015 | 2.30243 | 1.00032 | 14.0051 | 15.4136 | 1.00013 | 0.730874 | 6.18954e-08 | 0 | 0 | 0 | 47.04 | 1048.35 |