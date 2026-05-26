# J2 Path-Dependent Baseline Outlier Diagnostics

Outliers are detected on cyclic-primary metrics using a 1.5 IQR rule when IQR is nonzero, otherwise a 3 sigma rule is used.
All evaluated paths are stored in JSON: `monotonic, cyclic`.

| Model | Metric | Rule | Lower | Upper | Outlier count | Outlier seeds | Mean | Std | Median | IQR | Min | Max |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Faithful HANO strain-stress spectral-window NO | Cyclic disp. rel. L2 | 1.5*IQR | 110.759 | 273.98 | 1 | 20260520=405.365 | 228.227 | 92.7368 | 211.991 | 40.8052 | 139.037 | 405.365 |
| Faithful HANO strain-stress spectral-window NO | Yield-surface RMS | 1.5*IQR | 0.186455 | 0.333803 | 2 | 20260519=0.79949; 20260520=0.00648663 | 0.317438 | 0.260577 | 0.260955 | 0.0368371 | 0.00648663 | 0.79949 |
| Faithful HANO strain-stress spectral-window NO | Plastic-work violation pred-norm. | 1.5*IQR | -14.3142 | 26.0289 | 1 | 20260520=49.3561 | 13.7481 | 18.2717 | 7.66974 | 10.0858 | 0 | 49.3561 |
| Faithful HANO strain-stress spectral-window NO | HANO strain rel. L2 | 1.5*IQR | 22.4216 | 167.116 | 1 | 20260517=15.3915 | 84.1893 | 39.0899 | 86.8654 | 36.1735 | 15.3915 | 129.152 |
| Faithful HANO strain-stress spectral-window NO | HANO stress rel. L2 | 1.5*IQR | 9.65859 | 22.4475 | 1 | 20260519=27.5216 | 17.5857 | 5.37075 | 16.6093 | 3.19722 | 11.6917 | 27.5216 |