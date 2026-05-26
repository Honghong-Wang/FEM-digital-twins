# J2 Path-Dependent Baseline Outlier Diagnostics

Outliers are detected on cyclic-primary metrics using a 1.5 IQR rule when IQR is nonzero, otherwise a 3 sigma rule is used.
All evaluated paths are stored in JSON: `monotonic, cyclic`.

| Model | Metric | Rule | Lower | Upper | Outlier count | Outlier seeds | Mean | Std | Median | IQR | Min | Max |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Faithful HANO strain-stress spectral-window NO | Cyclic disp. rel. L2 | 1.5*IQR | 83.2302 | 215.242 | 1 | 20260520=273.831 | 163.449 | 58.1426 | 136.812 | 33.003 | 108.128 | 273.831 |
| Faithful HANO strain-stress spectral-window NO | HANO strain rel. L2 | 1.5*IQR | -25.2427 | 129.814 | 1 | 20260518=141.039 | 58.259 | 46.0502 | 37.3194 | 38.7641 | 8.36524 | 141.039 |
| Faithful HANO strain-stress spectral-window NO | FEM residual rel. RMS | 1.5*IQR | 485.564 | 854.78 | 2 | 20260517=277.967; 20260518=3632.19 | 1187.73 | 1232.29 | 688.139 | 92.304 | 277.967 | 3632.19 |
| Faithful HANO strain-stress spectral-window NO | FEM energy rel. err. | 1.5*IQR | 164226 | 582318 | 2 | 20260517=66511.8; 20260518=6.35073e+06 | 1.49765e+06 | 2.42944e+06 | 324477 | 104523 | 66511.8 | 6.35073e+06 |