# J2 Path-Dependent Baseline Outlier Diagnostics

Outliers are detected on cyclic-path metrics using a 1.5 IQR rule when IQR is nonzero, otherwise a 3 sigma rule is used.

| Model | Metric | Rule | Lower | Upper | Outlier count | Outlier seeds | Mean | Std | Median | IQR | Min | Max |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Thermo-hard HistoryGNO | Cyclic disp. rel. L2 | 1.5*IQR | 80.7825 | 125.58 | 2 | 20260518=237.498; 20260521=58.162 | 120.185 | 61.1609 | 98.9005 | 11.1993 | 58.162 | 237.498 |
| Thermo-hard HistoryGNO | Cyclic history rel. L2 | 1.5*IQR | 1.33389 | 1.34985 | 1 | 20260521=1.32665 | 1.33993 | 0.00694196 | 1.34311 | 0.00399196 | 1.32665 | 1.34617 |
| Thermo-hard HistoryGNO | Reversal hist-inc. rel. L2 | 1.5*IQR | 0.889872 | 1.18314 | 1 | 20260519=1.20805 | 1.0557 | 0.0814045 | 1.00023 | 0.0733179 | 0.997218 | 1.20805 |
| Thermo-hard HistoryGNO | Reversal yield-flag MAE | 1.5*IQR | 0.71254 | 0.719604 | 1 | 20260519=0.710575 | 0.715076 | 0.00236071 | 0.715654 | 0.00176609 | 0.710575 | 0.717007 |
| HistoryGNO data-only | Cyclic disp. rel. L2 | 1.5*IQR | 17.6594 | 182.751 | 1 | 20260518=298.822 | 132.238 | 86.9162 | 111.499 | 41.273 | 50.4591 | 298.822 |
| HistoryGNO data-only | Cyclic history rel. L2 | 1.5*IQR | 6.06652 | 9.40567 | 1 | 20260519=9.66899 | 7.91778 | 0.962753 | 7.53224 | 0.834787 | 6.91546 | 9.66899 |
| HistoryGNO data-only | Plastic-work inc. rel. L2 | 1.5*IQR | 20009.4 | 39145.7 | 1 | 20260517=9004.89 | 26315.8 | 9174.66 | 27817.3 | 4784.08 | 9004.89 | 35601.7 |
| HistoryGNO data-only | Reversal yield-flag MAE | 1.5*IQR | 0.477808 | 0.528407 | 1 | 20260517=0.474713 | 0.502526 | 0.0163799 | 0.507724 | 0.0126496 | 0.474713 | 0.523979 |
| HistoryGNO data-only | Plastic-work violation pred-norm. | 1.5*IQR | -6.88586 | 17.5491 | 1 | 20260517=34.0093 | 9.72259 | 12.3931 | 2.55169 | 6.10874 | 1.38874 | 34.0093 |
| HANO-window recent-history NO | History-increment rel. L2 | 1.5*IQR | 1.00012 | 1.00309 | 1 | 20260521=1.00558 | 1.00214 | 0.00179641 | 1.00156 | 0.000742912 | 1.00038 | 1.00558 |
| HANO-window recent-history NO | Eqp increment rel. L2 | 1.5*IQR | 38.5837 | 266.765 | 1 | 20260521=302.448 | 162.031 | 84.2426 | 158.446 | 57.0454 | 43.9116 | 302.448 |
| HANO-window recent-history NO | Reversal hist-inc. rel. L2 | 1.5*IQR | 1.00051 | 1.00296 | 2 | 20260520=0.999851; 20260521=1.00711 | 1.0024 | 0.00246605 | 1.00158 | 0.00061202 | 0.999851 | 1.00711 |
| HANO-window recent-history NO | Plastic-work violation abs. | 1.5*IQR | -0.00976353 | 0.0181025 | 1 | 20260521=0.0227879 | 0.00730875 | 0.00825322 | 0.00541681 | 0.00696651 | 0 | 0.0227879 |
| HANO-window recent-history NO | Plastic-work violation target-norm. | 1.5*IQR | -408.024 | 756.515 | 1 | 20260521=952.321 | 305.437 | 344.907 | 226.372 | 291.135 | 0 | 952.321 |
| INCDE Euler neural CDE | Cyclic disp. rel. L2 | 1.5*IQR | 56.7869 | 519.76 | 1 | 20260517=684.045 | 327.766 | 190.051 | 241.073 | 115.743 | 137.165 | 684.045 |
| INCDE Euler neural CDE | Cyclic history rel. L2 | 1.5*IQR | 0.828945 | 0.847693 | 1 | 20260517=0.826052 | 0.836936 | 0.00651658 | 0.836191 | 0.00468701 | 0.826052 | 0.845796 |
| INCDE Euler neural CDE | Reversal hist-inc. rel. L2 | 1.5*IQR | 1.00159 | 1.00956 | 2 | 20260520=1.02645; 20260521=0.997575 | 1.00799 | 0.00972814 | 1.00476 | 0.00199425 | 0.997575 | 1.02645 |
| INCDE Euler neural CDE | Reversal yield-flag MAE | 1.5*IQR | 0.364537 | 0.38499 | 1 | 20260520=0.360691 | 0.373611 | 0.00740012 | 0.374746 | 0.00511318 | 0.360691 | 0.383091 |
| Thermo-projected neural CDE | Cyclic disp. rel. L2 | 1.5*IQR | 56.3851 | 519.978 | 1 | 20260517=684.085 | 327.735 | 190.084 | 241.063 | 115.898 | 137.165 | 684.085 |
| Thermo-projected neural CDE | Cyclic history rel. L2 | 1.5*IQR | 0.988201 | 0.996693 | 1 | 20260519=0.987904 | 0.991814 | 0.00231992 | 0.991541 | 0.00212312 | 0.987904 | 0.994728 |
| Thermo-projected neural CDE | Reversal hist-inc. rel. L2 | 1.5*IQR | 0.9997 | 1.00019 | 1 | 20260519=0.99799 | 0.999579 | 0.00079606 | 0.999998 | 0.000123382 | 0.99799 | 1.00002 |
| Thermo-projected neural CDE | Reversal yield-flag MAE | 1.5*IQR | 0.28275 | 0.2834 | 1 | 20260519=0.283973 | 0.283236 | 0.000373369 | 0.283063 | 0.000162363 | 0.282993 | 0.283973 |
| Thermo-projected neural CDE | Yield-surface RMS | 1.5*IQR | -0.000297541 | 0.000498246 | 1 | 20260519=0.00120551 | 0.000297384 | 0.000459885 | 8.05005e-05 | 0.000198947 | 2.07145e-07 | 0.00120551 |
| Non-recurrent GNO sequence | Cyclic history rel. L2 | 1.5*IQR | 0.829858 | 0.848314 | 1 | 20260517=0.829773 | 0.837398 | 0.00438934 | 0.836992 | 0.00461411 | 0.829773 | 0.842055 |
| Non-recurrent GNO sequence | History-increment rel. L2 | 1.5*IQR | 1.00001 | 1.0002 | 1 | 20260521=0.999895 | 1.00007 | 9.23066e-05 | 1.00009 | 4.79221e-05 | 0.999895 | 1.00016 |
| Non-recurrent GNO sequence | Eqp increment rel. L2 | 1.5*IQR | 0.93503 | 1.04364 | 1 | 20260521=1.34131 | 1.0531 | 0.144577 | 0.977184 | 0.0271534 | 0.968332 | 1.34131 |
| Non-recurrent GNO sequence | Plastic-work inc. rel. L2 | 1.5*IQR | -1.27213 | 5.25871 | 1 | 20260521=9.76818 | 3.19027 | 3.35402 | 1.2146 | 1.63271 | 0.98198 | 9.76818 |
| Non-recurrent GNO sequence | Reversal hist-inc. rel. L2 | 1.5*IQR | 0.999971 | 1.00083 | 1 | 20260521=0.999576 | 1.00027 | 0.000369123 | 1.00035 | 0.000215769 | 0.999576 | 1.00064 |
| Non-recurrent GNO sequence | Plastic-work violation abs. | 1.5*IQR | -9.82202e-05 | 0.000163784 | 1 | 20260521=0.000227245 | 6.06576e-05 | 8.67729e-05 | 1.04795e-05 | 6.55011e-05 | 0 | 0.000227245 |
| Non-recurrent GNO sequence | Plastic-work violation target-norm. | 1.5*IQR | -4.10468 | 6.84463 | 1 | 20260521=9.49668 | 2.53492 | 3.62629 | 0.437945 | 2.73733 | 0 | 9.49668 |
| Static DeepONet sequence | Cyclic disp. rel. L2 | 1.5*IQR | 4.81292 | 6.64651 | 2 | 20260517=7.76353; 20260518=4.30067 | 5.84458 | 1.11522 | 5.69927 | 0.458398 | 4.30067 | 7.76353 |
| Static DeepONet sequence | Cyclic history rel. L2 | 1.5*IQR | 0.827352 | 0.844365 | 1 | 20260521=0.825948 | 0.835605 | 0.00572293 | 0.837059 | 0.00425339 | 0.825948 | 0.8433 |
| Static DeepONet sequence | History-increment rel. L2 | 1.5*IQR | 1.00002 | 1.00004 | 2 | 20260517=0.999987; 20260518=1.00016 | 1.00005 | 5.89179e-05 | 1.00003 | 5.00679e-06 | 0.999987 | 1.00016 |
| Static DeepONet sequence | Eqp increment rel. L2 | 1.5*IQR | 0.855808 | 1.23057 | 1 | 20260517=1.86459 | 1.20286 | 0.333663 | 1.08055 | 0.0936909 | 0.982787 | 1.86459 |
| Static DeepONet sequence | Reversal hist-inc. rel. L2 | 1.5*IQR | 0.999988 | 1.00022 | 2 | 20260517=0.99996; 20260518=1.00065 | 1.00019 | 0.000239624 | 1.00012 | 5.84126e-05 | 0.99996 | 1.00065 |
| Static DeepONet sequence | Reversal yield-flag MAE | 1.5*IQR | 0.373009 | 0.380888 | 2 | 20260518=0.37193; 20260521=0.383194 | 0.377006 | 0.00366064 | 0.376007 | 0.00196972 | 0.37193 | 0.383194 |
| Static DeepONet sequence | Yield-surface RMS | 1.5*IQR | 0.129857 | 0.188303 | 1 | 20260520=0.204461 | 0.165815 | 0.0206964 | 0.161406 | 0.0146115 | 0.145048 | 0.204461 |
| Static DeepONet sequence | Plastic-work violation pred-norm. | 1.5*IQR | 0.996255 | 1.00624 | 2 | 20260519=0; 20260521=1.45196 | 0.890891 | 0.478487 | 1 | 0.00249672 | 0 | 1.45196 |