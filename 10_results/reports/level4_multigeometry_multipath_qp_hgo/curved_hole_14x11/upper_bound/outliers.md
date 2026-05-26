# J2 Path-Dependent Baseline Outlier Diagnostics

Outliers are detected on cyclic-path metrics using a 1.5 IQR rule when IQR is nonzero, otherwise a 3 sigma rule is used.

| Model | Metric | Rule | Lower | Upper | Outlier count | Outlier seeds | Mean | Std | Median | IQR | Min | Max |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| QP-thermo-hard HistoryGNO | Cyclic history rel. L2 | 1.5*IQR | 1.06991 | 1.08104 | 1 | 20260520=1.0693 | 1.07492 | 0.00305921 | 1.07659 | 0.00278282 | 1.0693 | 1.07775 |
| QP-thermo-hard HistoryGNO | History-increment rel. L2 | 1.5*IQR | 0.99926 | 1.00049 | 1 | 20260520=0.998566 | 0.999644 | 0.000554525 | 0.999824 | 0.000307858 | 0.998566 | 1.00008 |
| QP-thermo-hard HistoryGNO | QP history rel. L2 | 1.5*IQR | 1.75793 | 1.77502 | 1 | 20260520=1.75504 | 1.76514 | 0.0053511 | 1.76813 | 0.00427198 | 1.75504 | 1.76957 |
| QP-thermo-hard HistoryGNO | Eqp increment rel. L2 | 1.5*IQR | 2.96592 | 5.33024 | 1 | 20260521=6.30795 | 4.46974 | 0.947008 | 3.9417 | 0.591079 | 3.8029 | 6.30795 |
| QP-thermo-hard HistoryGNO | Plastic-work inc. rel. L2 | 1.5*IQR | 3.04978 | 5.64097 | 1 | 20260521=6.84498 | 4.71981 | 1.09228 | 4.10836 | 0.647797 | 3.95496 | 6.84498 |
| QP-thermo-hard HistoryGNO | Reversal hist-inc. rel. L2 | 1.5*IQR | 0.998974 | 1.00156 | 1 | 20260520=1.00168 | 1.00041 | 0.000684801 | 0.99998 | 0.000645578 | 0.999861 | 1.00168 |
| QP-thermo-hard HistoryGNO | Reversal yield-flag MAE | 1.5*IQR | 0.40853 | 0.410631 | 1 | 20260520=0.410668 | 0.409702 | 0.000522959 | 0.409388 | 0.000525445 | 0.409292 | 0.410668 |
| QP-thermo-hard HistoryGNO | FEM residual rel. RMS | 1.5*IQR | -12.0373 | 96.7395 | 1 | 20260519=100.249 | 47.5165 | 28.7068 | 29.2762 | 27.1942 | 23.3547 | 100.249 |
| QP-thermo-hard HistoryGNO | FEM energy rel. err. | 1.5*IQR | -911.236 | 2215.61 | 1 | 20260519=2927.08 | 987.583 | 1016.3 | 536.782 | 781.711 | 169.683 | 2927.08 |