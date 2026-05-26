# J2 Path-Dependent Baseline Outlier Diagnostics

Outliers are detected on cyclic-path metrics using a 1.5 IQR rule when IQR is nonzero, otherwise a 3 sigma rule is used.

| Model | Metric | Rule | Lower | Upper | Outlier count | Outlier seeds | Mean | Std | Median | IQR | Min | Max |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Thermo-hard HistoryGNO | Cyclic disp. rel. L2 | 1.5*IQR | 25.2324 | 93.8122 | 1 | 20260518=100.413 | 60.3654 | 23.7701 | 54.1663 | 17.1449 | 28.2028 | 100.413 |
| Thermo-hard HistoryGNO | Yield-surface RMS | 1.5*IQR | 0.00171479 | 0.00315572 | 1 | 20260519=0.00168347 | 0.00237398 | 0.000432137 | 0.0023239 | 0.000360233 | 0.00168347 | 0.00299204 |
| HistoryGNO data-only | Yield-surface RMS | 1.5*IQR | 0.376389 | 0.485512 | 2 | 20260519=0.576262; 20260520=0.336298 | 0.439026 | 0.0777512 | 0.42067 | 0.0272808 | 0.336298 | 0.576262 |
| HANO-window recent-history NO | Eqp increment rel. L2 | 1.5*IQR | 1365.69 | 1766.93 | 2 | 20260517=354.93; 20260521=2228.43 | 1458.12 | 608.673 | 1574.63 | 100.309 | 354.93 | 2228.43 |
| HANO-window recent-history NO | Yield-surface RMS | 1.5*IQR | -1.17106 | 2.05632 | 1 | 20260517=2.08457 | 0.67196 | 0.765673 | 0.353254 | 0.806844 | 0.0367155 | 2.08457 |
| HANO-window recent-history NO | Plastic-work violation pred-norm. | 1.5*IQR | -0.993224 | 1.65537 | 1 | 20260519=1.79313 | 0.532325 | 0.675201 | 0.206345 | 0.662149 | 0 | 1.79313 |
| INCDE Euler neural CDE | Cyclic disp. rel. L2 | 1.5*IQR | 100.387 | 190.642 | 1 | 20260517=333.577 | 180.246 | 77.8372 | 155.618 | 22.5636 | 121.007 | 333.577 |
| INCDE Euler neural CDE | Cyclic history rel. L2 | 1.5*IQR | 1.09505 | 1.12386 | 1 | 20260520=1.14079 | 1.11538 | 0.0131439 | 1.11245 | 0.00720346 | 1.10473 | 1.14079 |
| INCDE Euler neural CDE | History-increment rel. L2 | 1.5*IQR | 0.969984 | 1.00242 | 1 | 20260518=1.01077 | 0.99015 | 0.0112161 | 0.989206 | 0.00810838 | 0.978369 | 1.01077 |
| Thermo-projected neural CDE | Cyclic disp. rel. L2 | 1.5*IQR | 100.636 | 190.492 | 1 | 20260517=333.95 | 180.663 | 77.7064 | 155.342 | 22.4642 | 122.895 | 333.95 |
| Thermo-projected neural CDE | Cyclic history rel. L2 | 1.5*IQR | 0.985457 | 0.996123 | 1 | 20260519=0.965316 | 0.986591 | 0.0108816 | 0.990056 | 0.00266641 | 0.965316 | 0.996003 |
| Thermo-projected neural CDE | History-increment rel. L2 | 1.5*IQR | 0.997548 | 1.00111 | 1 | 20260519=1.07534 | 1.01421 | 0.0305761 | 0.999265 | 0.000890613 | 0.997762 | 1.07534 |
| Thermo-projected neural CDE | Yield-surface RMS | 1.5*IQR | -0.000488737 | 0.000821486 | 1 | 20260519=0.00663308 | 0.0013996 | 0.00261967 | 3.20885e-05 | 0.000327556 | 8.16907e-08 | 0.00663308 |
| Non-recurrent GNO sequence | Plastic-work inc. rel. L2 | 1.5*IQR | -66.7997 | 158.669 | 1 | 20260521=304.37 | 89.5627 | 110.363 | 50.5567 | 56.3672 | 1.01689 | 304.37 |
| Non-recurrent GNO sequence | Plastic-work violation abs. | 1.5*IQR | -0.000254255 | 0.000423758 | 1 | 20260521=0.000625495 | 0.000159018 | 0.000242299 | 8.92723e-08 | 0.000169503 | 0 | 0.000625495 |
| Non-recurrent GNO sequence | Plastic-work violation target-norm. | 1.5*IQR | -123.628 | 206.047 | 1 | 20260521=304.139 | 77.3201 | 117.814 | 0.0434075 | 82.4186 | 0 | 304.139 |
| Static DeepONet sequence | Cyclic disp. rel. L2 | 1.5*IQR | 5.60359 | 8.01861 | 2 | 20260517=8.74672; 20260518=5.16805 | 6.85133 | 1.15141 | 6.71965 | 0.603755 | 5.16805 | 8.74672 |
| Static DeepONet sequence | History-increment rel. L2 | 1.5*IQR | 0.998265 | 1.00154 | 1 | 20260518=1.0016 | 1 | 0.000972997 | 0.999954 | 0.000819147 | 0.998648 | 1.0016 |
| Static DeepONet sequence | Eqp increment rel. L2 | 1.5*IQR | -5.34512 | 15.2171 | 1 | 20260517=39.7819 | 11.16 | 14.4871 | 5.15591 | 5.14057 | 0.990356 | 39.7819 |
| Static DeepONet sequence | Yield-surface RMS | 1.5*IQR | 0.169309 | 0.262601 | 1 | 20260520=0.282033 | 0.225653 | 0.0305385 | 0.220204 | 0.0233231 | 0.194117 | 0.282033 |
| Static DeepONet sequence | Plastic-work violation pred-norm. | 1.5*IQR | 0.996707 | 1.00549 | 2 | 20260519=0; 20260521=1.10796 | 0.822031 | 0.413109 | 1 | 0.00219548 | 0 | 1.10796 |