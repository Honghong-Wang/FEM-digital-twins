# J2 Path-Dependent Baseline Outlier Diagnostics

Outliers are detected on cyclic-path metrics using a 1.5 IQR rule when IQR is nonzero, otherwise a 3 sigma rule is used.

| Model | Metric | Rule | Lower | Upper | Outlier count | Outlier seeds | Mean | Std | Median | IQR | Min | Max |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Thermo-hard HistoryGNO | Cyclic history rel. L2 | 1.5*IQR | 1.31712 | 1.36108 | 1 | 20260518=1.30933 | 1.3354 | 0.0137238 | 1.34417 | 0.0109909 | 1.30933 | 1.34528 |
| Thermo-hard HistoryGNO | History-increment rel. L2 | 1.5*IQR | 0.946463 | 1.09058 | 1 | 20260518=1.16503 | 1.04064 | 0.0637399 | 1.0007 | 0.0360287 | 1.00042 | 1.16503 |
| Thermo-hard HistoryGNO | Reversal hist-inc. rel. L2 | 1.5*IQR | 0.988964 | 1.01939 | 1 | 20260518=1.2165 | 1.04512 | 0.0857419 | 1.0004 | 0.00760603 | 1.00033 | 1.2165 |
| Thermo-hard HistoryGNO | Reversal yield-flag MAE | 1.5*IQR | 0.71449 | 0.718517 | 1 | 20260518=0.706667 | 0.714738 | 0.00405388 | 0.717007 | 0.00100654 | 0.706667 | 0.717007 |
| HistoryGNO data-only | Cyclic history rel. L2 | 1.5*IQR | 6.71884 | 7.94185 | 1 | 20260519=10.1323 | 7.77827 | 1.20549 | 7.37561 | 0.305754 | 6.72269 | 10.1323 |
| HistoryGNO data-only | History-increment rel. L2 | 1.5*IQR | 1.77551 | 1.84981 | 2 | 20260517=1.73101; 20260519=2.3953 | 1.914 | 0.242898 | 1.81836 | 0.0185729 | 1.73101 | 2.3953 |
| HistoryGNO data-only | Plastic-work inc. rel. L2 | 1.5*IQR | 25339.7 | 33544.6 | 2 | 20260517=10938.7; 20260519=34206.6 | 26588.6 | 8083.89 | 28913.3 | 2051.23 | 10938.7 | 34206.6 |
| HistoryGNO data-only | Reversal hist-inc. rel. L2 | 1.5*IQR | 1.93263 | 2.02248 | 2 | 20260517=1.88657; 20260519=2.65943 | 2.09724 | 0.28352 | 1.98509 | 0.022464 | 1.88657 | 2.65943 |
| HistoryGNO data-only | Reversal yield-flag MAE | 1.5*IQR | 0.486863 | 0.528332 | 1 | 20260517=0.484067 | 0.505679 | 0.0124687 | 0.507816 | 0.0103672 | 0.484067 | 0.521319 |
| HistoryGNO data-only | Plastic-work violation pred-norm. | 1.5*IQR | -6.82129 | 17.6702 | 1 | 20260517=20.0478 | 6.97804 | 6.9922 | 2.46511 | 6.12287 | 1.52843 | 20.0478 |
| HANO-window recent-history NO | History-increment rel. L2 | 1.5*IQR | 0.995042 | 1.02309 | 1 | 20260521=1.06573 | 1.01889 | 0.0237279 | 1.00941 | 0.00701141 | 1.00117 | 1.06573 |
| HANO-window recent-history NO | Eqp increment rel. L2 | 1.5*IQR | 61.4989 | 794.36 | 1 | 20260521=1184.34 | 516.643 | 360.399 | 431.046 | 183.215 | 111.967 | 1184.34 |
| HANO-window recent-history NO | Reversal hist-inc. rel. L2 | 1.5*IQR | 0.991312 | 1.03055 | 1 | 20260521=1.08303 | 1.02395 | 0.0298768 | 1.01187 | 0.00980961 | 1.00299 | 1.08303 |
| HANO-window recent-history NO | Yield-surface RMS | 1.5*IQR | -0.26738 | 0.711721 | 1 | 20260517=0.827781 | 0.304819 | 0.284087 | 0.231953 | 0.244775 | 0.0200218 | 0.827781 |
| HANO-window recent-history NO | Plastic-work violation abs. | 1.5*IQR | -0.0291554 | 0.144534 | 1 | 20260521=0.409212 | 0.114067 | 0.149629 | 0.0440837 | 0.0434223 | 0.00165852 | 0.409212 |
| HANO-window recent-history NO | Plastic-work violation target-norm. | 1.5*IQR | -1218.42 | 6040.16 | 1 | 20260521=17101.2 | 4766.91 | 6253.07 | 1842.28 | 1814.65 | 69.3106 | 17101.2 |
| INCDE Euler neural CDE | Cyclic disp. rel. L2 | 1.5*IQR | 345.899 | 544.342 | 1 | 20260520=1169.1 | 575.438 | 299.674 | 463.385 | 49.6108 | 354.461 | 1169.1 |
| INCDE Euler neural CDE | Cyclic history rel. L2 | 1.5*IQR | 0.777412 | 1.08473 | 1 | 20260518=1.09941 | 0.961492 | 0.0770243 | 0.960832 | 0.0768294 | 0.885077 | 1.09941 |
| INCDE Euler neural CDE | History-increment rel. L2 | 1.5*IQR | 0.997872 | 1.00454 | 1 | 20260520=1.00464 | 1.00149 | 0.0017264 | 1.00041 | 0.00166678 | 0.999987 | 1.00464 |
| INCDE Euler neural CDE | Yield-surface RMS | 1.5*IQR | 0.0417685 | 0.0854609 | 1 | 20260520=0.141061 | 0.078476 | 0.0316687 | 0.0673501 | 0.0109231 | 0.0567392 | 0.141061 |
| Thermo-projected neural CDE | Cyclic disp. rel. L2 | 1.5*IQR | 343.636 | 545.809 | 1 | 20260520=1169.1 | 575.269 | 299.761 | 463.308 | 50.5433 | 354.486 | 1169.1 |
| Thermo-projected neural CDE | Cyclic history rel. L2 | 1.5*IQR | 0.988 | 1.00031 | 1 | 20260519=0.896949 | 0.975253 | 0.0391856 | 0.993696 | 0.00307637 | 0.896949 | 0.997314 |
| Thermo-projected neural CDE | History-increment rel. L2 | 1.5*IQR | 0.99994 | 1.00004 | 2 | 20260519=1.0081; 20260521=0.999927 | 1.0016 | 0.0032489 | 0.999998 | 2.52128e-05 | 0.999927 | 1.0081 |
| Thermo-projected neural CDE | Reversal hist-inc. rel. L2 | 1.5*IQR | 0.999885 | 1.00006 | 1 | 20260519=0.850358 | 0.970055 | 0.0598483 | 0.999965 | 4.45247e-05 | 0.850358 | 1 |
| Thermo-projected neural CDE | Reversal yield-flag MAE | 1.5*IQR | 0.282988 | 0.283001 | 1 | 20260519=0.356026 | 0.297601 | 0.0292129 | 0.282994 | 3.27826e-06 | 0.282993 | 0.356026 |
| Thermo-projected neural CDE | Yield-surface RMS | 1.5*IQR | -8.45608e-06 | 1.42729e-05 | 1 | 20260519=0.00570732 | 0.00114278 | 0.00228227 | 7.44764e-07 | 5.68226e-06 | 1.58724e-08 | 0.00570732 |
| Non-recurrent GNO sequence | Cyclic disp. rel. L2 | 1.5*IQR | 27.4088 | 259.769 | 1 | 20260521=307.399 | 157.252 | 81.3325 | 117.381 | 58.09 | 74.3043 | 307.399 |
| Non-recurrent GNO sequence | Cyclic history rel. L2 | 1.5*IQR | 0.787942 | 1.09269 | 1 | 20260519=1.12075 | 0.970562 | 0.0840712 | 0.970595 | 0.0761865 | 0.880834 | 1.12075 |
| Non-recurrent GNO sequence | Plastic-work inc. rel. L2 | 1.5*IQR | -3.99027 | 19.8957 | 1 | 20260521=22.0979 | 9.77316 | 7.10219 | 9.79847 | 5.97149 | 1.06404 | 22.0979 |
| Non-recurrent GNO sequence | Reversal yield-flag MAE | 1.5*IQR | 0.275786 | 0.44793 | 1 | 20260519=0.600801 | 0.402339 | 0.100575 | 0.350045 | 0.043036 | 0.337136 | 0.600801 |
| Non-recurrent GNO sequence | Yield-surface RMS | 1.5*IQR | -0.039683 | 0.281431 | 1 | 20260519=0.51199 | 0.180589 | 0.169665 | 0.0999557 | 0.0802785 | 0.0492522 | 0.51199 |
| Non-recurrent GNO sequence | Plastic-work violation pred-norm. | 1.5*IQR | 0.77503 | 1.37495 | 2 | 20260518=0; 20260519=1.95774 | 1.02585 | 0.622395 | 1.02154 | 0.14998 | 0 | 1.95774 |
| Static DeepONet sequence | Cyclic disp. rel. L2 | 1.5*IQR | 10.0335 | 19.2265 | 1 | 20260517=22.8092 | 15.9446 | 3.56568 | 14.6575 | 2.29825 | 12.9962 | 22.8092 |
| Static DeepONet sequence | History-increment rel. L2 | 1.5*IQR | 0.999977 | 1.00002 | 1 | 20260518=1.00017 | 1.00003 | 6.93817e-05 | 0.999998 | 1.03712e-05 | 0.999982 | 1.00017 |
| Static DeepONet sequence | Eqp increment rel. L2 | 1.5*IQR | 0.66894 | 1.52026 | 1 | 20260517=5.91041 | 2.02043 | 1.94668 | 1.02816 | 0.21283 | 0.974363 | 5.91041 |
| Static DeepONet sequence | Plastic-work inc. rel. L2 | 1.5*IQR | -4.8072 | 10.7719 | 1 | 20260518=17.9529 | 5.18924 | 6.55898 | 1.05388 | 3.89478 | 0.974654 | 17.9529 |
| Static DeepONet sequence | Reversal hist-inc. rel. L2 | 1.5*IQR | 0.99995 | 1.00005 | 2 | 20260518=1.00067; 20260519=0.999884 | 1.00011 | 0.000284608 | 1 | 2.59876e-05 | 0.999884 | 1.00067 |
| Static DeepONet sequence | Reversal yield-flag MAE | 1.5*IQR | 0.309605 | 0.355267 | 1 | 20260518=0.38608 | 0.34006 | 0.0241446 | 0.333105 | 0.0114155 | 0.316244 | 0.38608 |
| Static DeepONet sequence | Plastic-work violation abs. | 1.5*IQR | -0.000165386 | 0.000275643 | 1 | 20260518=0.0004252 | 0.000107091 | 0.000164687 | 0 | 0.000110257 | 0 | 0.0004252 |
| Static DeepONet sequence | Plastic-work violation target-norm. | 1.5*IQR | -6.91158 | 11.5193 | 1 | 20260518=17.7694 | 4.47542 | 6.88236 | 0 | 4.60772 | 0 | 17.7694 |