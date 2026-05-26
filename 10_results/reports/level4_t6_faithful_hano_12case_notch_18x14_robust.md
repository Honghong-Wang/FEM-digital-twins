# J2 Path-Dependent Baseline Robust Statistics

Each row reports both mean/std and robust median/IQR statistics on the cyclic primary test path.
All evaluated paths are stored in JSON: `monotonic, cyclic`.

| Model | Metric | Mean | Std | Median | Q1 | Q3 | IQR | Min | Max | N |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Faithful HANO strain-stress spectral-window NO | Cyclic disp. rel. L2 | 285.986 | 93.6032 | 258.671 | 253.952 | 310.518 | 56.5663 | 160.519 | 446.272 | 5 |
| Faithful HANO strain-stress spectral-window NO | Cyclic history rel. L2 | 1.75079 | 0.479333 | 1.59693 | 1.41316 | 1.86715 | 0.453995 | 1.25746 | 2.61925 | 5 |
| Faithful HANO strain-stress spectral-window NO | History-increment rel. L2 | 1.00331 | 0.00257205 | 1.00276 | 1.00159 | 1.00434 | 0.00274646 | 1.00019 | 1.00767 | 5 |
| Faithful HANO strain-stress spectral-window NO | Eqp increment rel. L2 | 211.339 | 167.414 | 90.2038 | 87.2219 | 397.116 | 309.895 | 49.0137 | 433.14 | 5 |
| Faithful HANO strain-stress spectral-window NO | Plastic-work inc. rel. L2 | 137.773 | 136.514 | 58.9935 | 19.4118 | 231.863 | 212.451 | 17.8298 | 360.765 | 5 |
| Faithful HANO strain-stress spectral-window NO | Reversal hist-inc. rel. L2 | 1.00344 | 0.00295824 | 1.00281 | 1.00045 | 1.00589 | 0.00543964 | 1.0003 | 1.00775 | 5 |
| Faithful HANO strain-stress spectral-window NO | Reversal yield-flag MAE | 0.40354 | 0.18888 | 0.258738 | 0.250106 | 0.622316 | 0.37221 | 0.239739 | 0.646801 | 5 |
| Faithful HANO strain-stress spectral-window NO | Yield-surface RMS | 0.273092 | 0.240958 | 0.157157 | 0.124988 | 0.395583 | 0.270595 | 0.00481965 | 0.682913 | 5 |
| Faithful HANO strain-stress spectral-window NO | Plastic-work violation abs. | 0.00760999 | 0.00884149 | 0.00155557 | 7.68723e-05 | 0.0154814 | 0.0154045 | 0 | 0.0209361 | 5 |
| Faithful HANO strain-stress spectral-window NO | Plastic-work violation target-norm. | 545.242 | 633.477 | 111.453 | 5.50776 | 1109.22 | 1103.71 | 0 | 1500.03 | 5 |
| Faithful HANO strain-stress spectral-window NO | Plastic-work violation pred-norm. | 17.514 | 29.6031 | 4.77942 | 0.0930367 | 6.18397 | 6.09093 | 0 | 76.5135 | 5 |
| Faithful HANO strain-stress spectral-window NO | HANO strain rel. L2 | 62.5497 | 39.2742 | 51.9661 | 51.7182 | 59.7025 | 7.98425 | 14.7618 | 134.6 | 5 |
| Faithful HANO strain-stress spectral-window NO | HANO stress rel. L2 | 12.1 | 3.03015 | 12.4787 | 9.65839 | 13.3064 | 3.64803 | 8.17036 | 16.8861 | 5 |
| Faithful HANO strain-stress spectral-window NO | FEM residual rel. RMS | 1927.39 | 1472.2 | 1418.75 | 1104.68 | 1794.23 | 689.55 | 560.697 | 4758.59 | 5 |
| Faithful HANO strain-stress spectral-window NO | FEM energy rel. err. | 1.94205e+06 | 2.26792e+06 | 917574 | 441385 | 1.93174e+06 | 1.49035e+06 | 111279 | 6.30827e+06 | 5 |