# J2 Path-Dependent Baseline Per-Seed Appendix

Per-seed cyclic-path metrics for diagnosing stochastic training stability and outliers.

| Model | Seed | Train final loss | Cyclic disp. rel. L2 | Cyclic history rel. L2 | History-increment rel. L2 | Eqp increment rel. L2 | Plastic-work inc. rel. L2 | Reversal hist-inc. rel. L2 | Reversal yield-flag MAE | Yield-surface RMS | Plastic-work violation abs. | Plastic-work violation target-norm. | Plastic-work violation pred-norm. | FEM residual rel. RMS | FEM energy rel. err. |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Thermo-hard HistoryGNO | 20260517 | 12137.3 | 217.857 | 1.18118 | 1.00067 | 18.1461 | 22.2569 | 1.00037 | 0.455988 | 1.74531e-07 | 0 | 0 | 0 | 182.233 | 11495.9 |
| Thermo-hard HistoryGNO | 20260518 | 6468.52 | 252.923 | 1.17842 | 1.00028 | 10.5912 | 11.7806 | 0.999964 | 0.455988 | 1.38174e-07 | 0 | 0 | 0 | 96.8559 | 2242.65 |
| Thermo-hard HistoryGNO | 20260519 | 1152.56 | 31.3014 | 1.18108 | 1.00129 | 24.6067 | 34.5472 | 1.00116 | 0.455988 | 2.15343e-07 | 0 | 0 | 0 | 213.903 | 12101.8 |
| Thermo-hard HistoryGNO | 20260520 | 2044.74 | 120.498 | 1.1816 | 1.0008 | 19.7316 | 24.9485 | 1.00051 | 0.455988 | 1.8799e-07 | 0 | 0 | 0 | 306.755 | 20525 |
| Thermo-hard HistoryGNO | 20260521 | 4491.09 | 134.43 | 1.16418 | 1.05432 | 27.2051 | 36.763 | 1.01839 | 0.457606 | 0.000458522 | 0 | 0 | 0 | 248.678 | 23053.3 |
| Thermo-projected neural CDE | 20260517 | 41008.1 | 331.939 | 0.994531 | 1.00001 | 1 | 1 | 1.00015 | 0.544011 | 7.80222e-07 | 0 | 0 | 0 | 970.196 | 202703 |
| Thermo-projected neural CDE | 20260518 | 6873.1 | 325.57 | 0.996262 | 1 | 1 | 1 | 1.00001 | 0.544012 | 6.80547e-08 | 0 | 0 | 0 | 680.486 | 145621 |
| Thermo-projected neural CDE | 20260519 | 27540 | 261.19 | 0.957138 | 1.16251 | 1 | 1 | 1.36752 | 0.533173 | 0.00570153 | 0 | 0 | 0 | 1535.75 | 539359 |
| Thermo-projected neural CDE | 20260520 | 904564 | 832.519 | 0.992612 | 1.00008 | 1 | 1 | 0.999833 | 0.543974 | 0.00018304 | 0 | 0 | 0 | 2055.73 | 1.05454e+06 |
| Thermo-projected neural CDE | 20260521 | 9704.44 | 252.02 | 0.993609 | 0.99993 | 1 | 1 | 1.00033 | 0.544011 | 6.08013e-06 | 0 | 0 | 0 | 744.472 | 116953 |