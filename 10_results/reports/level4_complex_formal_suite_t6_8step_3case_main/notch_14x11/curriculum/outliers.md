# J2 Path-Dependent Baseline Outlier Diagnostics

Outliers are detected on cyclic-path metrics using a 1.5 IQR rule when IQR is nonzero, otherwise a 3 sigma rule is used.

| Model | Metric | Rule | Lower | Upper | Outlier count | Outlier seeds | Mean | Std | Median | IQR | Min | Max |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Thermo-hard HistoryGNO | Cyclic disp. rel. L2 | 1.5*IQR | 22.4648 | 215.566 | 1 | 20260518=268.583 | 139.776 | 68.7685 | 120.812 | 48.2752 | 71.4574 | 268.583 |
| Thermo-hard HistoryGNO | Cyclic history rel. L2 | 1.5*IQR | 1.33708 | 1.34626 | 1 | 20260518=1.33495 | 1.34044 | 0.00291282 | 1.34098 | 0.00229609 | 1.33495 | 1.34295 |
| Thermo-hard HistoryGNO | History-increment rel. L2 | 1.5*IQR | 0.997728 | 1.00987 | 1 | 20260519=1.01449 | 1.00507 | 0.00497448 | 1.00294 | 0.00303602 | 1.00032 | 1.01449 |
| Thermo-hard HistoryGNO | Eqp increment rel. L2 | 1.5*IQR | 14.8271 | 18.1901 | 1 | 20260519=26.2617 | 18.3596 | 3.96589 | 16.5515 | 0.840731 | 15.9674 | 26.2617 |
| Thermo-hard HistoryGNO | Plastic-work inc. rel. L2 | 1.5*IQR | 16.8599 | 20.3981 | 1 | 20260519=34.1679 | 21.6461 | 6.27692 | 18.9307 | 0.884554 | 17.8737 | 34.1679 |
| Thermo-hard HistoryGNO | Reversal hist-inc. rel. L2 | 1.5*IQR | 0.991952 | 1.01395 | 1 | 20260519=1.03228 | 1.00713 | 0.0128717 | 1.00022 | 0.0054996 | 0.997227 | 1.03228 |
| Thermo-hard HistoryGNO | Reversal yield-flag MAE | 1.5*IQR | 0.708001 | 0.72241 | 1 | 20260518=0.702501 | 0.713246 | 0.00553492 | 0.716312 | 0.00360227 | 0.702501 | 0.717007 |
| HistoryGNO data-only | Cyclic disp. rel. L2 | 1.5*IQR | 61.3002 | 219.154 | 2 | 20260518=317.098; 20260519=52.3905 | 160.334 | 87.0493 | 151.727 | 39.4634 | 52.3905 | 317.098 |
| HistoryGNO data-only | Cyclic history rel. L2 | 1.5*IQR | 6.2285 | 8.75092 | 1 | 20260519=9.92399 | 7.84975 | 1.07888 | 7.43961 | 0.630606 | 6.90573 | 9.92399 |
| HistoryGNO data-only | History-increment rel. L2 | 1.5*IQR | 1.64443 | 2.08897 | 1 | 20260519=2.35152 | 1.93071 | 0.217906 | 1.82369 | 0.111133 | 1.74495 | 2.35152 |
| HistoryGNO data-only | Plastic-work inc. rel. L2 | 1.5*IQR | 17985.8 | 42569.5 | 1 | 20260517=9598.29 | 26433.5 | 8792.26 | 28475 | 6145.94 | 9598.29 | 33538.8 |
| HistoryGNO data-only | Reversal hist-inc. rel. L2 | 1.5*IQR | 1.77891 | 2.30582 | 1 | 20260519=2.60866 | 2.11719 | 0.254873 | 1.99607 | 0.131727 | 1.89647 | 2.60866 |
| HistoryGNO data-only | Reversal yield-flag MAE | 1.5*IQR | 0.479685 | 0.532489 | 1 | 20260517=0.478886 | 0.504094 | 0.0145879 | 0.507343 | 0.0132011 | 0.478886 | 0.522065 |
| HistoryGNO data-only | Plastic-work violation pred-norm. | 1.5*IQR | -6.71437 | 17.1827 | 1 | 20260517=27.9003 | 8.45939 | 10.0158 | 2.51709 | 5.97426 | 1.4113 | 27.9003 |
| HANO-window recent-history NO | History-increment rel. L2 | 1.5*IQR | 0.998466 | 1.00882 | 1 | 20260521=1.01006 | 1.00421 | 0.00325149 | 1.00321 | 0.0025897 | 1.00051 | 1.01006 |
| HANO-window recent-history NO | Reversal hist-inc. rel. L2 | 1.5*IQR | 0.997749 | 1.0094 | 1 | 20260521=1.01291 | 1.00509 | 0.00410091 | 1.00382 | 0.00291228 | 1.00156 | 1.01291 |
| HANO-window recent-history NO | Yield-surface RMS | 1.5*IQR | -0.371116 | 0.815642 | 1 | 20260517=1.2056 | 0.376226 | 0.43348 | 0.225678 | 0.29669 | 0.00531942 | 1.2056 |
| INCDE Euler neural CDE | Cyclic disp. rel. L2 | 1.5*IQR | 37.0367 | 555.583 | 1 | 20260517=689.688 | 352.634 | 183.041 | 324.059 | 129.637 | 156.802 | 689.688 |
| INCDE Euler neural CDE | Cyclic history rel. L2 | 1.5*IQR | 0.846693 | 0.857562 | 2 | 20260517=0.839297; 20260518=0.896564 | 0.858416 | 0.0197242 | 0.851964 | 0.0027172 | 0.839297 | 0.896564 |
| INCDE Euler neural CDE | History-increment rel. L2 | 1.5*IQR | 0.996225 | 1.00559 | 1 | 20260520=1.00739 | 1.00181 | 0.00293408 | 1.00041 | 0.00234216 | 0.99944 | 1.00739 |
| INCDE Euler neural CDE | Reversal hist-inc. rel. L2 | 1.5*IQR | 0.991525 | 1.01311 | 1 | 20260520=1.02271 | 1.00533 | 0.00912526 | 1.00257 | 0.00539619 | 0.996734 | 1.02271 |
| INCDE Euler neural CDE | Reversal yield-flag MAE | 1.5*IQR | 0.361429 | 0.375862 | 1 | 20260520=0.358609 | 0.366868 | 0.00449441 | 0.367113 | 0.00360841 | 0.358609 | 0.371328 |
| INCDE Euler neural CDE | Yield-surface RMS | 1.5*IQR | 0.141682 | 0.189101 | 1 | 20260517=0.134168 | 0.161867 | 0.0149153 | 0.167909 | 0.0118547 | 0.134168 | 0.176478 |
| Thermo-projected neural CDE | Cyclic disp. rel. L2 | 1.5*IQR | 37.1557 | 555.416 | 1 | 20260517=689.735 | 352.83 | 183.026 | 325.043 | 129.565 | 156.802 | 689.735 |
| Thermo-projected neural CDE | Cyclic history rel. L2 | 1.5*IQR | 0.987744 | 1.00054 | 1 | 20260519=0.970495 | 0.990207 | 0.0100669 | 0.993684 | 0.00319779 | 0.970495 | 0.998575 |
| Thermo-projected neural CDE | History-increment rel. L2 | 1.5*IQR | 0.999819 | 1.00011 | 1 | 20260519=0.999218 | 0.999825 | 0.000304461 | 0.999981 | 7.16448e-05 | 0.999218 | 1 |
| Thermo-projected neural CDE | Reversal hist-inc. rel. L2 | 1.5*IQR | 0.999884 | 1.00006 | 1 | 20260519=0.985965 | 0.997177 | 0.00560629 | 0.999973 | 4.48227e-05 | 0.985965 | 1 |
| Thermo-projected neural CDE | Reversal yield-flag MAE | 1.5*IQR | 0.282987 | 0.283003 | 1 | 20260519=0.287029 | 0.283801 | 0.00161395 | 0.282994 | 3.8445e-06 | 0.282993 | 0.287029 |
| Thermo-projected neural CDE | Yield-surface RMS | 1.5*IQR | -9.76868e-06 | 1.64524e-05 | 1 | 20260519=0.0040206 | 0.000805601 | 0.0016075 | 7.10238e-07 | 6.55526e-06 | 5.78672e-09 | 0.0040206 |
| Non-recurrent GNO sequence | History-increment rel. L2 | 1.5*IQR | 1.00001 | 1.00013 | 2 | 20260518=1.00014; 20260521=0.99991 | 1.00005 | 7.69226e-05 | 1.00008 | 3.06368e-05 | 0.99991 | 1.00014 |
| Non-recurrent GNO sequence | Plastic-work inc. rel. L2 | 1.5*IQR | -5.39695 | 12.1804 | 1 | 20260521=13.6246 | 5.30653 | 4.55805 | 5.01532 | 4.39435 | 1.10928 | 13.6246 |
| Non-recurrent GNO sequence | Reversal hist-inc. rel. L2 | 1.5*IQR | 1.00005 | 1.00049 | 2 | 20260518=1.00055; 20260521=0.999635 | 1.0002 | 0.00030503 | 1.00027 | 0.000110269 | 0.999635 | 1.00055 |
| Non-recurrent GNO sequence | Yield-surface RMS | 1.5*IQR | 0.132001 | 0.14597 | 2 | 20260517=0.120733; 20260520=0.154741 | 0.138773 | 0.0108564 | 0.140417 | 0.00349222 | 0.120733 | 0.154741 |
| Non-recurrent GNO sequence | Plastic-work violation pred-norm. | 1.5*IQR | 0.423553 | 1.96074 | 1 | 20260518=0 | 1.01661 | 0.571763 | 1 | 0.384298 | 0 | 1.69876 |
| Static DeepONet sequence | Cyclic disp. rel. L2 | 1.5*IQR | 7.60715 | 9.7684 | 2 | 20260517=9.93298; 20260518=6.77047 | 8.51209 | 1.02575 | 8.48144 | 0.540313 | 6.77047 | 9.93298 |
| Static DeepONet sequence | History-increment rel. L2 | 1.5*IQR | 0.999917 | 1.00009 | 1 | 20260518=1.00014 | 1.00002 | 6.0422e-05 | 0.999994 | 4.37498e-05 | 0.999972 | 1.00014 |
| Static DeepONet sequence | Eqp increment rel. L2 | 1.5*IQR | 0.79091 | 1.33232 | 1 | 20260517=3.21583 | 1.46704 | 0.876039 | 1.02243 | 0.135352 | 0.973707 | 3.21583 |
| Static DeepONet sequence | Reversal hist-inc. rel. L2 | 1.5*IQR | 0.999625 | 1.0004 | 1 | 20260518=1.00056 | 1.00009 | 0.000246901 | 0.999974 | 0.000193119 | 0.999884 | 1.00056 |
| Static DeepONet sequence | Yield-surface RMS | 1.5*IQR | 0.0887701 | 0.185311 | 1 | 20260520=0.188409 | 0.144009 | 0.0265132 | 0.147363 | 0.0241351 | 0.11019 | 0.188409 |
| Static DeepONet sequence | Plastic-work violation pred-norm. | 1.5*IQR | 0.99613 | 1.00645 | 2 | 20260519=0; 20260521=2.00253 | 1.00102 | 0.633258 | 1 | 0.00257993 | 0 | 2.00253 |