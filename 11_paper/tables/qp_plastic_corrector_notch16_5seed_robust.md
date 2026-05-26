# J2 Path-Dependent Baseline Robust Statistics

Each row reports both mean/std and robust median/IQR statistics on the cyclic primary test path.
All evaluated paths are stored in JSON: `monotonic, cyclic`.

| Model | Metric | Mean | Std | Median | Q1 | Q3 | IQR | Min | Max | N |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| QP plastic-memory corrector HistoryGNO | Cyclic disp. rel. L2 | 94.2533 | 48.6346 | 88.3407 | 75.0959 | 89.9311 | 14.8353 | 34.8749 | 183.024 | 5 |
| QP plastic-memory corrector HistoryGNO | Cyclic history rel. L2 | 1.57666 | 0.505444 | 1.76489 | 1.00218 | 1.95131 | 0.949125 | 0.961392 | 2.20355 | 5 |
| QP plastic-memory corrector HistoryGNO | History-increment rel. L2 | 0.999599 | 0.000633273 | 0.999998 | 0.998849 | 1.00003 | 0.00118035 | 0.998818 | 1.0003 | 5 |
| QP plastic-memory corrector HistoryGNO | QP history rel. L2 | 2.21462 | 1.02103 | 2.70206 | 1.00782 | 2.99735 | 1.98952 | 0.977973 | 3.3879 | 5 |
| QP plastic-memory corrector HistoryGNO | QP history-inc. rel. L2 | 0.999734 | 0.00047963 | 1 | 0.999176 | 1.00003 | 0.000852585 | 0.999148 | 1.00031 | 5 |
| QP plastic-memory corrector HistoryGNO | QP eqp rel. L2 | 1.22981 | 0.402688 | 1.04188 | 0.986668 | 1.11375 | 0.127082 | 0.977445 | 2.02931 | 5 |
| QP plastic-memory corrector HistoryGNO | QP plastic-work rel. L2 | 1.21449 | 0.379427 | 1.0361 | 0.987577 | 1.1017 | 0.114122 | 0.978768 | 1.9683 | 5 |
| QP plastic-memory corrector HistoryGNO | QP von-Mises rel. L2 | 1.18798 | 0.00872187 | 1.18651 | 1.18095 | 1.18837 | 0.00741935 | 1.17987 | 1.2042 | 5 |
| QP plastic-memory corrector HistoryGNO | Eqp increment rel. L2 | 1.29363 | 0.499601 | 1.06239 | 0.984905 | 1.16189 | 0.176989 | 0.975141 | 2.2838 | 5 |
| QP plastic-memory corrector HistoryGNO | Plastic-work inc. rel. L2 | 1.27647 | 0.475593 | 1.05428 | 0.985812 | 1.14603 | 0.160221 | 0.97633 | 2.21987 | 5 |
| QP plastic-memory corrector HistoryGNO | Reversal hist-inc. rel. L2 | 1.00216 | 0.00417476 | 1.00003 | 0.999826 | 1.00643 | 0.00660425 | 0.996831 | 1.00768 | 5 |
| QP plastic-memory corrector HistoryGNO | Reversal yield-flag MAE | 0.534331 | 0.312992 | 0.716318 | 0.172848 | 0.781186 | 0.608338 | 0.138141 | 0.86316 | 5 |
| QP plastic-memory corrector HistoryGNO | Yield-surface RMS | 0.000109325 | 0.00013454 | 1.39404e-05 | 8.50454e-07 | 0.000199318 | 0.000198467 | 3.38301e-07 | 0.000332179 | 5 |
| QP plastic-memory corrector HistoryGNO | Plastic-work violation abs. | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 5 |
| QP plastic-memory corrector HistoryGNO | Plastic-work violation target-norm. | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 5 |
| QP plastic-memory corrector HistoryGNO | Plastic-work violation pred-norm. | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 5 |
| QP plastic-memory corrector HistoryGNO | FEM residual rel. RMS | 105.85 | 52.3458 | 99.4662 | 86.0465 | 111.324 | 25.2778 | 35.5119 | 196.9 | 5 |
| QP plastic-memory corrector HistoryGNO | FEM energy rel. err. | 6744.98 | 5474.41 | 4400.06 | 2800.21 | 10801.5 | 8001.29 | 450.86 | 15272.3 | 5 |