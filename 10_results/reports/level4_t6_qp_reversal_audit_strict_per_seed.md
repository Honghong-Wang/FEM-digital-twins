# J2 Path-Dependent Baseline Per-Seed Appendix

Per-seed cyclic-path metrics for diagnosing stochastic training stability and outliers.

| Model | Seed | Train final loss | Cyclic disp. rel. L2 | Cyclic history rel. L2 | History-increment rel. L2 | Eqp increment rel. L2 | Plastic-work inc. rel. L2 | Reversal hist-inc. rel. L2 | Reversal yield-flag MAE | Yield-surface RMS | Plastic-work violation abs. | Plastic-work violation target-norm. | Plastic-work violation pred-norm. | FEM residual rel. RMS | FEM energy rel. err. |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Thermo-hard HistoryGNO | 20260517 | 12137.4 | 217.857 | 1.18118 | 1.00067 | 18.1474 | 22.2591 | 1.00037 | 0.455988 | 1.76926e-07 | 0 | 0 | 0 | 122.476 | 14127.1 |
| Thermo-hard HistoryGNO | 20260518 | 6151.27 | 248.996 | 1.17457 | 1.03 | 11.8096 | 13.7451 | 1.12039 | 0.457943 | 0.000655537 | 0 | 0 | 0 | 52.6942 | 1693.35 |
| Thermo-hard HistoryGNO | 20260519 | 1160.06 | 31.0837 | 1.18137 | 1.00136 | 24.778 | 34.8857 | 1.00117 | 0.455988 | 2.19752e-07 | 0 | 0 | 0 | 135.702 | 14996.9 |
| Thermo-hard HistoryGNO | 20260520 | 2045.49 | 120.516 | 1.1816 | 1.0008 | 19.732 | 24.9491 | 1.00051 | 0.455988 | 1.88641e-07 | 0 | 0 | 0 | 202.78 | 25212.1 |
| Thermo-hard HistoryGNO | 20260521 | 4498.33 | 134.987 | 1.16311 | 1.05538 | 26.9816 | 36.3302 | 1.00565 | 0.456833 | 0.000395987 | 0 | 0 | 0 | 180.509 | 28017.2 |
| Thermo-projected neural CDE | 20260517 | 40998.3 | 331.941 | 0.994531 | 1.00001 | 1 | 1 | 1.00015 | 0.544011 | 7.80192e-07 | 0 | 0 | 0 | 679.471 | 248875 |
| Thermo-projected neural CDE | 20260518 | 6858.17 | 325.607 | 0.996262 | 1 | 1 | 1 | 1.00001 | 0.544012 | 6.8054e-08 | 0 | 0 | 0 | 448.433 | 179346 |
| Thermo-projected neural CDE | 20260519 | 27650.1 | 262.012 | 0.957131 | 1.16251 | 1 | 1 | 1.36755 | 0.53317 | 0.00570179 | 0 | 0 | 0 | 1054.04 | 670203 |
| Thermo-projected neural CDE | 20260520 | 904135 | 832.392 | 0.992554 | 1.00009 | 1 | 1 | 0.999829 | 0.543967 | 0.000209188 | 0 | 0 | 0 | 1408.37 | 1.29873e+06 |
| Thermo-projected neural CDE | 20260521 | 9703.43 | 252.012 | 0.993609 | 0.99993 | 1 | 1 | 1.00033 | 0.544011 | 6.08005e-06 | 0 | 0 | 0 | 470.599 | 144050 |