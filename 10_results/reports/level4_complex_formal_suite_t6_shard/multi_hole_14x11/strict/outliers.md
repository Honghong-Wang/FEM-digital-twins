# J2 Path-Dependent Baseline Outlier Diagnostics

Outliers are detected on cyclic-path metrics using a 1.5 IQR rule when IQR is nonzero, otherwise a 3 sigma rule is used.

| Model | Metric | Rule | Lower | Upper | Outlier count | Outlier seeds | Mean | Std | Median | IQR | Min | Max |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Thermo-hard HistoryGNO | Cyclic history rel. L2 | 1.5*IQR | 2.88284 | 2.88828 | 1 | 20260521=2.85789 | 2.88063 | 0.0114089 | 2.88621 | 0.00135899 | 2.85789 | 2.88793 |
| Thermo-hard HistoryGNO | History-increment rel. L2 | 1.5*IQR | 1.0004 | 1.00546 | 1 | 20260521=1.10239 | 1.02251 | 0.0399473 | 1.0028 | 0.00126553 | 1.00148 | 1.10239 |
| Thermo-hard HistoryGNO | Yield-surface RMS | 1.5*IQR | 1.09344e-07 | 2.45262e-07 | 1 | 20260521=0.000693423 | 0.000138814 | 0.000277305 | 1.63206e-07 | 3.39795e-08 | 1.27181e-07 | 0.000693423 |
| HistoryGNO data-only | History-increment rel. L2 | 1.5*IQR | 2.50391 | 3.06168 | 1 | 20260519=3.31395 | 2.85802 | 0.242866 | 2.80361 | 0.139442 | 2.60693 | 3.31395 |
| HistoryGNO data-only | Plastic-work inc. rel. L2 | 1.5*IQR | 185843 | 414132 | 1 | 20260517=147632 | 280765 | 70763.5 | 312907 | 57072.5 | 147632 | 343312 |
| HistoryGNO data-only | Yield-surface RMS | 1.5*IQR | 0.314145 | 0.512008 | 1 | 20260519=0.539895 | 0.428166 | 0.0631996 | 0.422633 | 0.0494659 | 0.352151 | 0.539895 |
| HANO-window recent-history NO | History-increment rel. L2 | 1.5*IQR | 0.994845 | 1.06323 | 1 | 20260521=1.13066 | 1.04475 | 0.0443369 | 1.03026 | 0.0170957 | 1.00476 | 1.13066 |
| HANO-window recent-history NO | Eqp increment rel. L2 | 1.5*IQR | -224.046 | 9139.94 | 1 | 20260521=10230.7 | 4980.38 | 3041.34 | 4687.85 | 2341 | 1067.43 | 10230.7 |
| HANO-window recent-history NO | Yield-surface RMS | 1.5*IQR | -0.516352 | 1.0852 | 1 | 20260517=1.5969 | 0.475323 | 0.583907 | 0.205787 | 0.400387 | 0.005087 | 1.5969 |
| HANO-window recent-history NO | Plastic-work violation abs. | 1.5*IQR | -0.0195986 | 0.0571855 | 1 | 20260521=0.0926716 | 0.0285287 | 0.0333545 | 0.0123851 | 0.019196 | 0 | 0.0926716 |
| HANO-window recent-history NO | Plastic-work violation target-norm. | 1.5*IQR | -9529.56 | 27805.7 | 1 | 20260521=45060.3 | 13871.7 | 16218.2 | 6022.1 | 9333.8 | 0 | 45060.3 |
| INCDE Euler neural CDE | Cyclic disp. rel. L2 | 1.5*IQR | 89.9237 | 353.512 | 1 | 20260520=608.595 | 286.662 | 164.509 | 226.882 | 65.8969 | 154.395 | 608.595 |
| INCDE Euler neural CDE | History-increment rel. L2 | 1.5*IQR | 0.969592 | 1.05184 | 1 | 20260520=1.0762 | 1.01929 | 0.0298208 | 1.00477 | 0.0205611 | 0.994024 | 1.0762 |
| INCDE Euler neural CDE | Plastic-work inc. rel. L2 | 1.5*IQR | 1236.3 | 15477.7 | 1 | 20260520=651.197 | 7788.77 | 4386.29 | 7606.42 | 3560.34 | 651.197 | 13972.3 |
| INCDE Euler neural CDE | Yield-surface RMS | 1.5*IQR | 0.145403 | 0.249426 | 1 | 20260517=0.143603 | 0.192619 | 0.028317 | 0.197406 | 0.0260056 | 0.143603 | 0.227255 |
| Thermo-projected neural CDE | Cyclic disp. rel. L2 | 1.5*IQR | 99.665 | 337.363 | 1 | 20260520=608.595 | 285.346 | 164.789 | 226.734 | 59.4245 | 154.373 | 608.595 |
| Thermo-projected neural CDE | Cyclic history rel. L2 | 1.5*IQR | 0.983543 | 0.998543 | 1 | 20260519=0.972503 | 0.987591 | 0.00773902 | 0.989753 | 0.00374997 | 0.972503 | 0.993614 |
| Thermo-projected neural CDE | History-increment rel. L2 | 1.5*IQR | 0.996347 | 1.00399 | 1 | 20260519=1.10912 | 1.02147 | 0.0438329 | 0.9998 | 0.00191003 | 0.998107 | 1.10912 |
| Thermo-projected neural CDE | Yield-surface RMS | 1.5*IQR | -7.66075e-05 | 0.000132715 | 1 | 20260519=0.00652907 | 0.00131809 | 0.00260557 | 5.2075e-06 | 5.23306e-05 | 4.75975e-08 | 0.00652907 |
| Non-recurrent GNO sequence | Cyclic disp. rel. L2 | 1.5*IQR | 35.7836 | 297.143 | 1 | 20260521=359.733 | 183.044 | 95.3761 | 136.576 | 65.3398 | 85.9856 | 359.733 |
| Non-recurrent GNO sequence | Cyclic history rel. L2 | 1.5*IQR | 0.700798 | 1.92708 | 1 | 20260519=2.32112 | 1.46443 | 0.451481 | 1.32546 | 0.30657 | 1.0477 | 2.32112 |
| Non-recurrent GNO sequence | History-increment rel. L2 | 1.5*IQR | 0.999458 | 1.00155 | 1 | 20260521=0.999166 | 1.00049 | 0.000778245 | 1.00075 | 0.000522614 | 0.999166 | 1.00152 |
| Non-recurrent GNO sequence | Plastic-work inc. rel. L2 | 1.5*IQR | -46.4462 | 555.479 | 1 | 20260521=684.59 | 302.826 | 222.148 | 309.184 | 150.481 | 11.3241 | 684.59 |
| Non-recurrent GNO sequence | Yield-surface RMS | 1.5*IQR | 0.152104 | 0.216602 | 2 | 20260517=0.10082; 20260519=0.513179 | 0.234023 | 0.143463 | 0.187408 | 0.0161245 | 0.10082 | 0.513179 |
| Non-recurrent GNO sequence | Plastic-work violation pred-norm. | 1.5*IQR | 0.756917 | 1.40514 | 2 | 20260518=0; 20260519=1.96062 | 1.02874 | 0.623756 | 1.02105 | 0.162055 | 0 | 1.96062 |
| Static DeepONet sequence | Cyclic disp. rel. L2 | 1.5*IQR | 13.9194 | 20.4374 | 1 | 20260517=25.6778 | 18.5554 | 3.61666 | 16.4497 | 1.62951 | 16.2929 | 25.6778 |
| Static DeepONet sequence | History-increment rel. L2 | 1.5*IQR | 0.998409 | 1.00139 | 2 | 20260518=1.00177; 20260521=0.998089 | 0.999903 | 0.00118665 | 0.999859 | 0.000745654 | 0.998089 | 1.00177 |
| Static DeepONet sequence | Eqp increment rel. L2 | 1.5*IQR | -12.2365 | 29.277 | 1 | 20260517=159.944 | 37.279 | 61.4707 | 7.56829 | 10.3784 | 1.84186 | 159.944 |
| Static DeepONet sequence | Plastic-work inc. rel. L2 | 1.5*IQR | -179.82 | 344.798 | 1 | 20260518=544.644 | 162.943 | 197.93 | 98.7176 | 131.155 | 6.37562 | 544.644 |
| Static DeepONet sequence | Plastic-work violation abs. | 1.5*IQR | -0.000456058 | 0.000760097 | 1 | 20260518=0.00112414 | 0.000329903 | 0.000414957 | 0.000221333 | 0.000304039 | 0 | 0.00112414 |
| Static DeepONet sequence | Plastic-work violation target-norm. | 1.5*IQR | -221.752 | 369.587 | 1 | 20260518=546.6 | 160.411 | 201.767 | 107.62 | 147.835 | 0 | 546.6 |