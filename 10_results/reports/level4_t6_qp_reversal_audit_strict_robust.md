# J2 Path-Dependent Baseline Robust Statistics

Each row reports both mean/std and robust median/IQR statistics on the cyclic test path.

| Model | Metric | Mean | Std | Median | Q1 | Q3 | IQR | Min | Max | N |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Thermo-hard HistoryGNO | Cyclic disp. rel. L2 | 150.688 | 76.9912 | 134.987 | 120.516 | 217.857 | 97.3419 | 31.0837 | 248.996 | 5 |
| Thermo-hard HistoryGNO | Cyclic history rel. L2 | 1.17637 | 0.00713368 | 1.18118 | 1.17457 | 1.18137 | 0.00680113 | 1.16311 | 1.1816 | 5 |
| Thermo-hard HistoryGNO | History-increment rel. L2 | 1.01764 | 0.0219714 | 1.00136 | 1.0008 | 1.03 | 0.0292057 | 1.00067 | 1.05538 | 5 |
| Thermo-hard HistoryGNO | Eqp increment rel. L2 | 20.2897 | 5.32427 | 19.732 | 18.1474 | 24.778 | 6.63064 | 11.8096 | 26.9816 | 5 |
| Thermo-hard HistoryGNO | Plastic-work inc. rel. L2 | 26.4338 | 8.36673 | 24.9491 | 22.2591 | 34.8857 | 12.6266 | 13.7451 | 36.3302 | 5 |
| Thermo-hard HistoryGNO | Reversal hist-inc. rel. L2 | 1.02562 | 0.047425 | 1.00117 | 1.00051 | 1.00565 | 0.00513506 | 1.00037 | 1.12039 | 5 |
| Thermo-hard HistoryGNO | Reversal yield-flag MAE | 0.456548 | 0.000770339 | 0.455988 | 0.455988 | 0.456833 | 0.000844657 | 0.455988 | 0.457943 | 5 |
| Thermo-hard HistoryGNO | Yield-surface RMS | 0.000210422 | 0.00027024 | 2.19752e-07 | 1.88641e-07 | 0.000395987 | 0.000395799 | 1.76926e-07 | 0.000655537 | 5 |
| Thermo-hard HistoryGNO | Plastic-work violation abs. | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 5 |
| Thermo-hard HistoryGNO | Plastic-work violation target-norm. | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 5 |
| Thermo-hard HistoryGNO | Plastic-work violation pred-norm. | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 5 |
| Thermo-hard HistoryGNO | FEM residual rel. RMS | 138.832 | 52.0064 | 135.702 | 122.476 | 180.509 | 58.0332 | 52.6942 | 202.78 | 5 |
| Thermo-hard HistoryGNO | FEM energy rel. err. | 16809.3 | 9329.46 | 14996.9 | 14127.1 | 25212.1 | 11085 | 1693.35 | 28017.2 | 5 |
| Thermo-projected neural CDE | Cyclic disp. rel. L2 | 400.793 | 218.205 | 325.607 | 262.012 | 331.941 | 69.9287 | 252.012 | 832.392 | 5 |
| Thermo-projected neural CDE | Cyclic history rel. L2 | 0.986818 | 0.0148931 | 0.993609 | 0.992554 | 0.994531 | 0.00197732 | 0.957131 | 0.996262 | 5 |
| Thermo-projected neural CDE | History-increment rel. L2 | 1.03251 | 0.064999 | 1.00001 | 1 | 1.00009 | 9.32813e-05 | 0.99993 | 1.16251 | 5 |
| Thermo-projected neural CDE | Eqp increment rel. L2 | 1 | 0 | 1 | 1 | 1 | 0 | 1 | 1 | 5 |
| Thermo-projected neural CDE | Plastic-work inc. rel. L2 | 1 | 0 | 1 | 1 | 1 | 0 | 1 | 1 | 5 |
| Thermo-projected neural CDE | Reversal hist-inc. rel. L2 | 1.07357 | 0.146986 | 1.00015 | 1.00001 | 1.00033 | 0.000316739 | 0.999829 | 1.36755 | 5 |
| Thermo-projected neural CDE | Reversal yield-flag MAE | 0.541834 | 0.00433219 | 0.544011 | 0.543967 | 0.544011 | 4.4167e-05 | 0.53317 | 0.544012 | 5 |
| Thermo-projected neural CDE | Yield-surface RMS | 0.00118358 | 0.00226053 | 6.08005e-06 | 7.80192e-07 | 0.000209188 | 0.000208408 | 6.8054e-08 | 0.00570179 | 5 |
| Thermo-projected neural CDE | Plastic-work violation abs. | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 5 |
| Thermo-projected neural CDE | Plastic-work violation target-norm. | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 5 |
| Thermo-projected neural CDE | Plastic-work violation pred-norm. | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 5 |
| Thermo-projected neural CDE | FEM residual rel. RMS | 812.184 | 368.93 | 679.471 | 470.599 | 1054.04 | 583.446 | 448.433 | 1408.37 | 5 |
| Thermo-projected neural CDE | FEM energy rel. err. | 508241 | 437992 | 248875 | 179346 | 670203 | 490857 | 144050 | 1.29873e+06 | 5 |