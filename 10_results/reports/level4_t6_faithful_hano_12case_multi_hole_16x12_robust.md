# J2 Path-Dependent Baseline Robust Statistics

Each row reports both mean/std and robust median/IQR statistics on the cyclic primary test path.
All evaluated paths are stored in JSON: `monotonic, cyclic`.

| Model | Metric | Mean | Std | Median | Q1 | Q3 | IQR | Min | Max | N |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Faithful HANO strain-stress spectral-window NO | Cyclic disp. rel. L2 | 163.449 | 58.1426 | 136.812 | 132.735 | 165.738 | 33.003 | 108.128 | 273.831 | 5 |
| Faithful HANO strain-stress spectral-window NO | Cyclic history rel. L2 | 1.65029 | 0.538879 | 1.76689 | 1.22085 | 1.8993 | 0.678449 | 0.910886 | 2.45354 | 5 |
| Faithful HANO strain-stress spectral-window NO | History-increment rel. L2 | 1.00912 | 0.00496705 | 1.00928 | 1.00489 | 1.01182 | 0.00692773 | 1.00284 | 1.01678 | 5 |
| Faithful HANO strain-stress spectral-window NO | Eqp increment rel. L2 | 107.324 | 41.4021 | 112.116 | 66.8049 | 117.489 | 50.6843 | 63.2009 | 177.007 | 5 |
| Faithful HANO strain-stress spectral-window NO | Plastic-work inc. rel. L2 | 73.6309 | 57.1911 | 64.5269 | 21.8974 | 98.6638 | 76.7664 | 13.0244 | 170.042 | 5 |
| Faithful HANO strain-stress spectral-window NO | Reversal hist-inc. rel. L2 | 1.02931 | 0.0219561 | 1.02637 | 1.01083 | 1.03512 | 0.0242914 | 1.00626 | 1.06798 | 5 |
| Faithful HANO strain-stress spectral-window NO | Reversal yield-flag MAE | 0.527631 | 0.0915797 | 0.549255 | 0.460069 | 0.600433 | 0.140363 | 0.389217 | 0.639181 | 5 |
| Faithful HANO strain-stress spectral-window NO | Yield-surface RMS | 0.520428 | 0.279253 | 0.524557 | 0.469836 | 0.77767 | 0.307834 | 0.0284208 | 0.801656 | 5 |
| Faithful HANO strain-stress spectral-window NO | Plastic-work violation abs. | 0.00562401 | 0.00405627 | 0.00666235 | 0.00156313 | 0.00675458 | 0.00519145 | 0.00101886 | 0.0121211 | 5 |
| Faithful HANO strain-stress spectral-window NO | Plastic-work violation target-norm. | 248.807 | 179.45 | 294.743 | 69.1531 | 298.823 | 229.67 | 45.0745 | 536.239 | 5 |
| Faithful HANO strain-stress spectral-window NO | Plastic-work violation pred-norm. | 8.03854 | 8.48925 | 3.14626 | 1.06541 | 13.2277 | 12.1622 | 0.455021 | 22.2983 | 5 |
| Faithful HANO strain-stress spectral-window NO | HANO strain rel. L2 | 58.259 | 46.0502 | 37.3194 | 32.9034 | 71.6676 | 38.7641 | 8.36524 | 141.039 | 5 |
| Faithful HANO strain-stress spectral-window NO | HANO stress rel. L2 | 17.9363 | 4.72623 | 19.9597 | 14.4253 | 21.7432 | 7.31791 | 10.5284 | 23.0251 | 5 |
| Faithful HANO strain-stress spectral-window NO | FEM residual rel. RMS | 1187.73 | 1232.29 | 688.139 | 624.02 | 716.324 | 92.304 | 277.967 | 3632.19 | 5 |
| Faithful HANO strain-stress spectral-window NO | FEM energy rel. err. | 1.49765e+06 | 2.42944e+06 | 324477 | 321010 | 425533 | 104523 | 66511.8 | 6.35073e+06 | 5 |