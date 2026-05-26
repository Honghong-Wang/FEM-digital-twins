# J2 Path-Dependent Baseline Outlier Diagnostics

Outliers are detected on cyclic-path metrics using a 1.5 IQR rule when IQR is nonzero, otherwise a 3 sigma rule is used.

| Model | Metric | Rule | Lower | Upper | Outlier count | Outlier seeds | Mean | Std | Median | IQR | Min | Max |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Thermo-hard HistoryGNO | Plastic-work inc. rel. L2 | 1.5*IQR | 21.2188 | 41.3013 | 1 | 20260517=20.995 | 31.0824 | 6.32421 | 31.5781 | 5.02062 | 20.995 | 40.3188 |
| Thermo-hard HistoryGNO | Reversal hist-inc. rel. L2 | 1.5*IQR | 0.922631 | 1.12883 | 1 | 20260518=1.28691 | 1.07632 | 0.107452 | 1.0434 | 0.0515494 | 0.999821 | 1.28691 |
| Thermo-hard HistoryGNO | Reversal yield-flag MAE | 1.5*IQR | 0.429792 | 0.432455 | 2 | 20260518=0.414733; 20260521=0.432992 | 0.428153 | 0.00675793 | 0.430791 | 0.000665754 | 0.414733 | 0.432992 |
| HistoryGNO data-only | Cyclic history rel. L2 | 1.5*IQR | 6.05369 | 7.13763 | 2 | 20260517=6.0324; 20260519=9.10593 | 6.99347 | 1.08314 | 6.6377 | 0.270984 | 6.0324 | 9.10593 |
| HistoryGNO data-only | History-increment rel. L2 | 1.5*IQR | 2.30023 | 2.40975 | 2 | 20260517=2.22024; 20260519=3.22298 | 2.50319 | 0.363916 | 2.36275 | 0.0273802 | 2.22024 | 3.22298 |
| HistoryGNO data-only | Plastic-work inc. rel. L2 | 1.5*IQR | 23692.5 | 31331.9 | 2 | 20260517=10238.5; 20260519=31908 | 24831.9 | 7535 | 26988.5 | 1909.85 | 10238.5 | 31908 |
| HistoryGNO data-only | Reversal hist-inc. rel. L2 | 1.5*IQR | 3.11371 | 3.30183 | 2 | 20260517=3.00541; 20260519=4.50838 | 3.43108 | 0.544912 | 3.22609 | 0.0470309 | 3.00541 | 4.50838 |
| HistoryGNO data-only | Plastic-work violation pred-norm. | 1.5*IQR | -6.79666 | 17.6326 | 1 | 20260517=19.8371 | 6.93375 | 6.91246 | 2.46781 | 6.10732 | 1.52785 | 19.8371 |
| HANO-window recent-history NO | History-increment rel. L2 | 1.5*IQR | 0.991016 | 1.04655 | 1 | 20260521=1.12732 | 1.03698 | 0.0459015 | 1.01894 | 0.013883 | 1.00107 | 1.12732 |
| HANO-window recent-history NO | Eqp increment rel. L2 | 1.5*IQR | 37.1227 | 731.156 | 1 | 20260521=1051.63 | 460.572 | 320.242 | 384.104 | 173.508 | 98.8486 | 1051.63 |
| HANO-window recent-history NO | Reversal hist-inc. rel. L2 | 1.5*IQR | 0.975078 | 1.10026 | 1 | 20260521=1.24693 | 1.07228 | 0.0890204 | 1.03795 | 0.0312958 | 1.00116 | 1.24693 |
| HANO-window recent-history NO | Yield-surface RMS | 1.5*IQR | -0.247354 | 0.676072 | 1 | 20260517=0.752191 | 0.275612 | 0.259334 | 0.177018 | 0.230856 | 0.0201319 | 0.752191 |
| HANO-window recent-history NO | Plastic-work violation abs. | 1.5*IQR | -0.0352489 | 0.154277 | 1 | 20260521=0.41051 | 0.115169 | 0.149937 | 0.0447044 | 0.0473814 | 0.00160445 | 0.41051 |
| HANO-window recent-history NO | Plastic-work violation target-norm. | 1.5*IQR | -1375.12 | 6018.59 | 1 | 20260521=16014.7 | 4492.95 | 5849.3 | 1743.99 | 1848.43 | 62.5924 | 16014.7 |
| INCDE Euler neural CDE | Cyclic disp. rel. L2 | 1.5*IQR | 254.914 | 398.643 | 1 | 20260520=860.651 | 421.935 | 221.354 | 335.872 | 35.9323 | 259.594 | 860.651 |
| INCDE Euler neural CDE | Cyclic history rel. L2 | 1.5*IQR | 0.718956 | 1.03106 | 1 | 20260518=1.03567 | 0.90212 | 0.073417 | 0.889415 | 0.078025 | 0.8355 | 1.03567 |
| INCDE Euler neural CDE | History-increment rel. L2 | 1.5*IQR | 0.99604 | 1.00931 | 1 | 20260520=1.01026 | 1.00341 | 0.00369594 | 1.00106 | 0.00331652 | 1.00037 | 1.01026 |
| INCDE Euler neural CDE | Yield-surface RMS | 1.5*IQR | 0.0682223 | 0.164953 | 1 | 20260520=0.196007 | 0.126296 | 0.0373647 | 0.114847 | 0.0241828 | 0.0874501 | 0.196007 |
| Thermo-projected neural CDE | Cyclic disp. rel. L2 | 1.5*IQR | 252.508 | 400.201 | 1 | 20260520=860.651 | 421.754 | 221.446 | 335.786 | 36.9232 | 259.621 | 860.651 |
| Thermo-projected neural CDE | Cyclic history rel. L2 | 1.5*IQR | 0.991289 | 0.997419 | 1 | 20260519=0.931047 | 0.982125 | 0.0255537 | 0.994578 | 0.00153244 | 0.931047 | 0.996291 |
| Thermo-projected neural CDE | History-increment rel. L2 | 1.5*IQR | 0.999902 | 1.00006 | 1 | 20260519=1.11739 | 1.02345 | 0.0469695 | 0.999989 | 3.85046e-05 | 0.999904 | 1.11739 |
| Thermo-projected neural CDE | Reversal hist-inc. rel. L2 | 1.5*IQR | 0.99959 | 1.00072 | 1 | 20260519=1.24677 | 1.04942 | 0.0986774 | 1.00014 | 0.000283122 | 0.999863 | 1.24677 |
| Thermo-projected neural CDE | Reversal yield-flag MAE | 1.5*IQR | 0.569208 | 0.56921 | 1 | 20260519=0.563476 | 0.568062 | 0.00229297 | 0.569209 | 4.76837e-07 | 0.563476 | 0.569209 |
| Thermo-projected neural CDE | Yield-surface RMS | 1.5*IQR | -8.62496e-06 | 1.54338e-05 | 1 | 20260519=0.0057195 | 0.00114543 | 0.00228704 | 7.62647e-07 | 6.01469e-06 | 6.84824e-08 | 0.0057195 |
| Non-recurrent GNO sequence | Cyclic disp. rel. L2 | 1.5*IQR | 16.2719 | 193.216 | 1 | 20260521=225.734 | 115.134 | 59.9322 | 86.0214 | 44.236 | 54.4284 | 225.734 |
| Non-recurrent GNO sequence | History-increment rel. L2 | 1.5*IQR | 0.999885 | 1.00029 | 1 | 20260521=0.999874 | 1.00007 | 0.000109327 | 1.0001 | 0.000100136 | 0.999874 | 1.00019 |
| Non-recurrent GNO sequence | Plastic-work inc. rel. L2 | 1.5*IQR | -1.75016 | 17.5811 | 1 | 20260521=20.8668 | 9.36634 | 6.57428 | 9.00323 | 4.83282 | 1.13074 | 20.8668 |
| Non-recurrent GNO sequence | Reversal hist-inc. rel. L2 | 1.5*IQR | 0.99921 | 1.00028 | 1 | 20260521=1.00044 | 0.999811 | 0.000348842 | 0.999718 | 0.000268519 | 0.999407 | 1.00044 |
| Non-recurrent GNO sequence | Reversal yield-flag MAE | 1.5*IQR | 0.524064 | 0.553738 | 1 | 20260519=0.467944 | 0.526311 | 0.029336 | 0.542182 | 0.00741857 | 0.467944 | 0.543629 |
| Non-recurrent GNO sequence | Yield-surface RMS | 1.5*IQR | 0.0411792 | 0.249014 | 1 | 20260519=0.512201 | 0.203292 | 0.158038 | 0.144461 | 0.0519588 | 0.0696069 | 0.512201 |
| Non-recurrent GNO sequence | Plastic-work violation pred-norm. | 1.5*IQR | 0.779016 | 1.36831 | 2 | 20260518=0; 20260519=1.96133 | 1.02596 | 0.623368 | 1.02115 | 0.147323 | 0 | 1.96133 |
| Static DeepONet sequence | Cyclic disp. rel. L2 | 1.5*IQR | 7.68814 | 13.4895 | 1 | 20260517=16.1467 | 11.554 | 2.38002 | 10.8438 | 1.45034 | 9.60195 | 16.1467 |
| Static DeepONet sequence | History-increment rel. L2 | 1.5*IQR | 0.999894 | 1.0001 | 1 | 20260518=1.00025 | 1.00004 | 0.000105686 | 0.999976 | 5.26905e-05 | 0.999972 | 1.00025 |
| Static DeepONet sequence | Eqp increment rel. L2 | 1.5*IQR | 0.62243 | 1.5783 | 1 | 20260517=5.41479 | 1.91739 | 1.75137 | 1.03614 | 0.238969 | 0.935306 | 5.41479 |
| Static DeepONet sequence | Plastic-work inc. rel. L2 | 1.5*IQR | -4.69458 | 10.3614 | 1 | 20260518=16.8752 | 4.90996 | 6.15463 | 1.06427 | 3.76399 | 0.943506 | 16.8752 |
| Static DeepONet sequence | Reversal hist-inc. rel. L2 | 1.5*IQR | 0.999658 | 1.00036 | 1 | 20260518=0.999208 | 0.99989 | 0.000349136 | 1.00008 | 0.000174522 | 0.999208 | 1.00015 |
| Static DeepONet sequence | Reversal yield-flag MAE | 1.5*IQR | 0.537522 | 0.554777 | 2 | 20260518=0.528521; 20260521=0.55635 | 0.544399 | 0.00906146 | 0.544823 | 0.00431383 | 0.528521 | 0.55635 |
| Static DeepONet sequence | Plastic-work violation abs. | 1.5*IQR | -0.000163248 | 0.00027208 | 1 | 20260518=0.000423903 | 0.000108697 | 0.000162837 | 1.07476e-05 | 0.000108832 | 0 | 0.000423903 |
| Static DeepONet sequence | Plastic-work violation target-norm. | 1.5*IQR | -6.36858 | 10.6143 | 1 | 20260518=16.5372 | 4.24043 | 6.35253 | 0.41928 | 4.24572 | 0 | 16.5372 |
| Static DeepONet sequence | Plastic-work violation pred-norm. | 1.5*IQR | -1.50588 | 2.50979 | 1 | 20260521=2.83931 | 0.968646 | 1.03713 | 1 | 1.00392 | 0 | 2.83931 |