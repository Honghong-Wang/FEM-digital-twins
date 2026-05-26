# J2 Path-Dependent Baseline Outlier Diagnostics

Outliers are detected on cyclic-primary metrics using a 1.5 IQR rule when IQR is nonzero, otherwise a 3 sigma rule is used.
All evaluated paths are stored in JSON: `monotonic, cyclic`.

| Model | Metric | Rule | Lower | Upper | Outlier count | Outlier seeds | Mean | Std | Median | IQR | Min | Max |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Faithful HANO strain-stress spectral-window NO | Cyclic disp. rel. L2 | 1.5*IQR | 169.102 | 395.367 | 2 | 20260520=446.272; 20260521=160.519 | 285.986 | 93.6032 | 258.671 | 56.5663 | 160.519 | 446.272 |
| Faithful HANO strain-stress spectral-window NO | Cyclic history rel. L2 | 1.5*IQR | 0.732165 | 2.54814 | 1 | 20260518=2.61925 | 1.75079 | 0.479333 | 1.59693 | 0.453995 | 1.25746 | 2.61925 |
| Faithful HANO strain-stress spectral-window NO | Plastic-work violation pred-norm. | 1.5*IQR | -9.04336 | 15.3204 | 1 | 20260520=76.5135 | 17.514 | 29.6031 | 4.77942 | 6.09093 | 0 | 76.5135 |
| Faithful HANO strain-stress spectral-window NO | HANO strain rel. L2 | 1.5*IQR | 39.7418 | 71.6788 | 2 | 20260517=14.7618; 20260518=134.6 | 62.5497 | 39.2742 | 51.9661 | 7.98425 | 14.7618 | 134.6 |
| Faithful HANO strain-stress spectral-window NO | FEM residual rel. RMS | 1.5*IQR | 70.3575 | 2828.56 | 1 | 20260518=4758.59 | 1927.39 | 1472.2 | 1418.75 | 689.55 | 560.697 | 4758.59 |
| Faithful HANO strain-stress spectral-window NO | FEM energy rel. err. | 1.5*IQR | -1.79414e+06 | 4.16727e+06 | 1 | 20260518=6.30827e+06 | 1.94205e+06 | 2.26792e+06 | 917574 | 1.49035e+06 | 111279 | 6.30827e+06 |