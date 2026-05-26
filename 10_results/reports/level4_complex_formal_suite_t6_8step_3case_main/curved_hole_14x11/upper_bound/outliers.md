# J2 Path-Dependent Baseline Outlier Diagnostics

Outliers are detected on cyclic-path metrics using a 1.5 IQR rule when IQR is nonzero, otherwise a 3 sigma rule is used.

| Model | Metric | Rule | Lower | Upper | Outlier count | Outlier seeds | Mean | Std | Median | IQR | Min | Max |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Thermo-hard HistoryGNO | Cyclic disp. rel. L2 | 1.5*IQR | 54.9508 | 101.081 | 2 | 20260518=176.802; 20260521=39.5997 | 89.4198 | 46.178 | 74.6646 | 11.5327 | 39.5997 | 176.802 |
| Thermo-hard HistoryGNO | History-increment rel. L2 | 1.5*IQR | 0.919225 | 1.13582 | 1 | 20260519=1.16592 | 1.04557 | 0.063514 | 1.00652 | 0.0541495 | 1.00037 | 1.16592 |
| Thermo-hard HistoryGNO | Eqp increment rel. L2 | 1.5*IQR | 8.86274 | 18.551 | 1 | 20260519=24.3047 | 15.2095 | 4.72547 | 13.3761 | 2.42207 | 10.953 | 24.3047 |
| Thermo-hard HistoryGNO | Plastic-work inc. rel. L2 | 1.5*IQR | 8.86191 | 23.5138 | 1 | 20260519=32.2479 | 18.5151 | 7.10381 | 15.5545 | 3.66298 | 12.3974 | 32.2479 |
| Thermo-hard HistoryGNO | Reversal yield-flag MAE | 1.5*IQR | 0.430635 | 0.431051 | 2 | 20260518=0.4249; 20260519=0.437357 | 0.430947 | 0.00394215 | 0.430791 | 0.00010401 | 0.4249 | 0.437357 |
| HistoryGNO data-only | Cyclic disp. rel. L2 | 1.5*IQR | 21.0562 | 124.109 | 1 | 20260518=218.087 | 96.0386 | 63.4758 | 80.7775 | 25.7633 | 36.1633 | 218.087 |
| HistoryGNO data-only | Cyclic history rel. L2 | 1.5*IQR | 5.41995 | 8.52917 | 1 | 20260519=8.64314 | 7.11093 | 0.85293 | 6.76167 | 0.777306 | 6.2007 | 8.64314 |
| HistoryGNO data-only | Plastic-work inc. rel. L2 | 1.5*IQR | 18731 | 36206.9 | 1 | 20260517=8424.51 | 24539.5 | 8570.09 | 25909.9 | 4368.99 | 8424.51 | 33425.1 |
| HistoryGNO data-only | Plastic-work violation pred-norm. | 1.5*IQR | -6.82264 | 17.4221 | 1 | 20260517=33.7186 | 9.66026 | 12.2766 | 2.60492 | 6.06119 | 1.37827 | 33.7186 |
| HANO-window recent-history NO | Cyclic disp. rel. L2 | 1.5*IQR | 124.337 | 586.303 | 1 | 20260517=586.927 | 372.217 | 123.715 | 340.158 | 115.491 | 223.36 | 586.927 |
| HANO-window recent-history NO | History-increment rel. L2 | 1.5*IQR | 1.00166 | 1.00635 | 2 | 20260517=0.999662; 20260521=1.00716 | 1.00369 | 0.00241583 | 1.00359 | 0.00117445 | 0.999662 | 1.00716 |
| HANO-window recent-history NO | Yield-surface RMS | 1.5*IQR | -0.531308 | 1.04994 | 1 | 20260517=1.56314 | 0.495118 | 0.562396 | 0.388721 | 0.395312 | 0.00509755 | 1.56314 |
| INCDE Euler neural CDE | Cyclic disp. rel. L2 | 1.5*IQR | 37.7085 | 382.703 | 1 | 20260517=501.368 | 238.653 | 140.386 | 174.488 | 86.2486 | 96.9961 | 501.368 |
| INCDE Euler neural CDE | Cyclic history rel. L2 | 1.5*IQR | 0.785987 | 0.796915 | 1 | 20260517=0.785626 | 0.791051 | 0.00347582 | 0.790514 | 0.00273204 | 0.785626 | 0.796212 |
| INCDE Euler neural CDE | History-increment rel. L2 | 1.5*IQR | 0.996188 | 1.00464 | 1 | 20260520=0.981276 | 0.997033 | 0.00794364 | 1.00061 | 0.00211239 | 0.981276 | 1.00245 |
| INCDE Euler neural CDE | Reversal hist-inc. rel. L2 | 1.5*IQR | 0.990722 | 0.997139 | 2 | 20260520=0.972552; 20260521=1.0031 | 0.99146 | 0.0101191 | 0.993786 | 0.00160408 | 0.972552 | 1.0031 |
| Thermo-projected neural CDE | Cyclic disp. rel. L2 | 1.5*IQR | 36.8458 | 383.176 | 1 | 20260517=501.424 | 238.596 | 140.439 | 174.54 | 86.5826 | 96.9963 | 501.424 |
| Thermo-projected neural CDE | Cyclic history rel. L2 | 1.5*IQR | 0.987144 | 1.00042 | 1 | 20260519=0.98329 | 0.992094 | 0.00474255 | 0.992688 | 0.00331956 | 0.98329 | 0.996929 |
| Thermo-projected neural CDE | History-increment rel. L2 | 1.5*IQR | 0.999617 | 1.00056 | 1 | 20260519=1.00588 | 1.00119 | 0.00234465 | 1 | 0.000234485 | 0.999917 | 1.00588 |
| Thermo-projected neural CDE | Reversal hist-inc. rel. L2 | 1.5*IQR | 0.999433 | 1.00099 | 1 | 20260519=1.00626 | 1.00133 | 0.0024727 | 1.00003 | 0.000388503 | 0.999924 | 1.00626 |
| Thermo-projected neural CDE | Reversal yield-flag MAE | 1.5*IQR | 0.568974 | 0.56935 | 1 | 20260519=0.568886 | 0.569125 | 0.00012458 | 0.569204 | 9.40561e-05 | 0.568886 | 0.569209 |
| Thermo-projected neural CDE | Yield-surface RMS | 1.5*IQR | -0.000354511 | 0.000591361 | 1 | 20260519=0.00312287 | 0.000686367 | 0.00122131 | 7.20807e-05 | 0.000236468 | 3.40097e-08 | 0.00312287 |
| Non-recurrent GNO sequence | History-increment rel. L2 | 1.5*IQR | 0.999963 | 1.00034 | 1 | 20260521=0.99985 | 1.00011 | 0.000137178 | 1.00017 | 9.5129e-05 | 0.99985 | 1.00023 |
| Non-recurrent GNO sequence | Eqp increment rel. L2 | 1.5*IQR | 0.861208 | 1.09072 | 1 | 20260521=1.34067 | 1.0354 | 0.154609 | 0.953343 | 0.0573791 | 0.93106 | 1.34067 |
| Non-recurrent GNO sequence | Plastic-work inc. rel. L2 | 1.5*IQR | -1.23631 | 5.18556 | 1 | 20260521=9.43398 | 3.10289 | 3.23275 | 1.19752 | 1.60547 | 0.933709 | 9.43398 |
| Non-recurrent GNO sequence | Reversal hist-inc. rel. L2 | 1.5*IQR | 0.998806 | 1.00021 | 1 | 20260521=1.0005 | 0.999662 | 0.000446903 | 0.999535 | 0.000350654 | 0.999256 | 1.0005 |
| Non-recurrent GNO sequence | Plastic-work violation abs. | 1.5*IQR | -9.64325e-05 | 0.000160721 | 1 | 20260521=0.000230994 | 6.10164e-05 | 8.8286e-05 | 9.80004e-06 | 6.42883e-05 | 0 | 0.000230994 |
| Non-recurrent GNO sequence | Plastic-work violation target-norm. | 1.5*IQR | -3.76199 | 6.26999 | 1 | 20260521=9.01144 | 2.38035 | 3.44418 | 0.382316 | 2.50799 | 0 | 9.01144 |
| Static DeepONet sequence | Cyclic disp. rel. L2 | 1.5*IQR | 3.54814 | 5.12667 | 2 | 20260517=5.78266; 20260518=3.27176 | 4.42422 | 0.808393 | 4.39186 | 0.394631 | 3.27176 | 5.78266 |
| Static DeepONet sequence | History-increment rel. L2 | 1.5*IQR | 1.00002 | 1.00008 | 2 | 20260517=0.999969; 20260518=1.00025 | 1.00007 | 9.17671e-05 | 1.00005 | 1.45435e-05 | 0.999969 | 1.00025 |
| Static DeepONet sequence | Eqp increment rel. L2 | 1.5*IQR | 0.833224 | 1.26508 | 1 | 20260517=1.82677 | 1.19882 | 0.318224 | 1.09532 | 0.107964 | 0.97373 | 1.82677 |
| Static DeepONet sequence | Reversal hist-inc. rel. L2 | 1.5*IQR | 0.999657 | 1.00005 | 2 | 20260517=1.0001; 20260518=0.999201 | 0.999766 | 0.000301407 | 0.999818 | 9.88841e-05 | 0.999201 | 1.0001 |
| Static DeepONet sequence | Yield-surface RMS | 1.5*IQR | 0.150097 | 0.227995 | 1 | 20260520=0.248009 | 0.198196 | 0.0264827 | 0.191707 | 0.0194744 | 0.173172 | 0.248009 |
| Static DeepONet sequence | Plastic-work violation pred-norm. | 1.5*IQR | 0.996648 | 1.00559 | 2 | 20260519=0; 20260521=1.44753 | 0.889952 | 0.477437 | 1 | 0.00223446 | 0 | 1.44753 |