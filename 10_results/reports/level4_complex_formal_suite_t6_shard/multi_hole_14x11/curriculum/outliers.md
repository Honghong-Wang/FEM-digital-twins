# J2 Path-Dependent Baseline Outlier Diagnostics

Outliers are detected on cyclic-path metrics using a 1.5 IQR rule when IQR is nonzero, otherwise a 3 sigma rule is used.

| Model | Metric | Rule | Lower | Upper | Outlier count | Outlier seeds | Mean | Std | Median | IQR | Min | Max |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Thermo-hard HistoryGNO | History-increment rel. L2 | 1.5*IQR | 0.789665 | 1.90963 | 1 | 20260518=2.13009 | 1.42621 | 0.385429 | 1.30037 | 0.279991 | 1.00127 | 2.13009 |
| Thermo-hard HistoryGNO | Yield-surface RMS | 1.5*IQR | -7.06156e-05 | 0.00265822 | 1 | 20260518=0.00329267 | 0.00145051 | 0.00107565 | 0.00137214 | 0.000682208 | 1.34369e-07 | 0.00329267 |
| HistoryGNO data-only | Cyclic history rel. L2 | 1.5*IQR | 5.99953 | 6.91551 | 2 | 20260517=5.45681; 20260521=7.15334 | 6.37366 | 0.545845 | 6.34312 | 0.228994 | 5.45681 | 7.15334 |
| HistoryGNO data-only | Plastic-work inc. rel. L2 | 1.5*IQR | 155431 | 417462 | 1 | 20260517=148018 | 275809 | 70144.6 | 318431 | 65507.6 | 148018 | 339701 |
| HistoryGNO data-only | Yield-surface RMS | 1.5*IQR | 0.329354 | 0.521434 | 1 | 20260519=0.55548 | 0.434284 | 0.0701147 | 0.422782 | 0.0480199 | 0.342368 | 0.55548 |
| HANO-window recent-history NO | Cyclic disp. rel. L2 | 1.5*IQR | 218.607 | 306.884 | 2 | 20260517=374.373; 20260519=164.888 | 266.502 | 66.6855 | 267.759 | 22.0693 | 164.888 | 374.373 |
| HANO-window recent-history NO | History-increment rel. L2 | 1.5*IQR | 1.00949 | 1.0173 | 2 | 20260517=1.00202; 20260521=1.02508 | 1.01342 | 0.00731879 | 1.01322 | 0.00195384 | 1.00202 | 1.02508 |
| HANO-window recent-history NO | Yield-surface RMS | 1.5*IQR | -0.726534 | 1.37533 | 1 | 20260517=2.09523 | 0.594699 | 0.776731 | 0.21486 | 0.525465 | 0.0146137 | 2.09523 |
| INCDE Euler neural CDE | Cyclic history rel. L2 | 1.5*IQR | 1.08411 | 1.15591 | 1 | 20260520=1.15615 | 1.1247 | 0.0174176 | 1.11996 | 0.0179507 | 1.10737 | 1.15615 |
| INCDE Euler neural CDE | History-increment rel. L2 | 1.5*IQR | 1.00082 | 1.06249 | 1 | 20260520=1.10871 | 1.04228 | 0.0346341 | 1.03017 | 0.0154179 | 1.00921 | 1.10871 |
| Thermo-projected neural CDE | Cyclic history rel. L2 | 1.5*IQR | 0.980871 | 1.00309 | 1 | 20260519=0.975043 | 0.989684 | 0.00779666 | 0.992148 | 0.00555551 | 0.975043 | 0.997268 |
| Thermo-projected neural CDE | History-increment rel. L2 | 1.5*IQR | 0.999624 | 1.00001 | 2 | 20260519=1.02457; 20260521=0.998062 | 1.00442 | 0.0100982 | 0.999848 | 9.7394e-05 | 0.998062 | 1.02457 |
| Thermo-projected neural CDE | Yield-surface RMS | 1.5*IQR | -0.000239719 | 0.000399746 | 1 | 20260519=0.00531969 | 0.0010972 | 0.00211213 | 6.27253e-06 | 0.000159866 | 5.58093e-09 | 0.00531969 |
| Non-recurrent GNO sequence | History-increment rel. L2 | 1.5*IQR | 0.999886 | 1.00169 | 1 | 20260521=0.999039 | 1.00056 | 0.000840814 | 1.00064 | 0.000450373 | 0.999039 | 1.00157 |
| Non-recurrent GNO sequence | Plastic-work inc. rel. L2 | 1.5*IQR | -227.15 | 402.847 | 1 | 20260521=424.845 | 149.057 | 152.861 | 139.885 | 157.499 | 4.859 | 424.845 |
| Non-recurrent GNO sequence | Plastic-work violation pred-norm. | 1.5*IQR | 0.451638 | 1.91394 | 2 | 20260517=3.48729; 20260518=0 | 1.37057 | 1.15184 | 1 | 0.365574 | 0 | 3.48729 |
| Static DeepONet sequence | Cyclic disp. rel. L2 | 1.5*IQR | 8.81468 | 11.5629 | 2 | 20260517=12.1496; 20260518=7.59438 | 10.0539 | 1.4644 | 10.1478 | 0.687067 | 7.59438 | 12.1496 |
| Static DeepONet sequence | Eqp increment rel. L2 | 1.5*IQR | -7.68854 | 20.3763 | 1 | 20260517=77.5157 | 19.1331 | 29.3349 | 4.20633 | 7.01622 | 1.25563 | 77.5157 |
| Static DeepONet sequence | Plastic-work violation pred-norm. | 1.5*IQR | 0.994758 | 1.00874 | 2 | 20260519=0; 20260521=1.14752 | 0.830202 | 0.418955 | 1 | 0.00349498 | 0 | 1.14752 |