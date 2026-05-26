# J2 Path-Dependent Baseline Robust Statistics

Each row reports both mean/std and robust median/IQR statistics on the cyclic primary test path.
All evaluated paths are stored in JSON: `monotonic, cyclic`.

| Model | Metric | Mean | Std | Median | Q1 | Q3 | IQR | Min | Max | N |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Faithful HANO strain-stress spectral-window NO | Cyclic disp. rel. L2 | 148.893 | 55.3238 | 127.045 | 110.074 | 162.228 | 52.1542 | 95.0297 | 250.087 | 5 |
| Faithful HANO strain-stress spectral-window NO | Cyclic history rel. L2 | 2.04784 | 0.838469 | 2.09195 | 1.27804 | 2.85817 | 1.58013 | 0.942414 | 3.06863 | 5 |
| Faithful HANO strain-stress spectral-window NO | History-increment rel. L2 | 1.00982 | 0.00464699 | 1.00765 | 1.00689 | 1.01472 | 0.00783372 | 1.00398 | 1.01587 | 5 |
| Faithful HANO strain-stress spectral-window NO | Eqp increment rel. L2 | 161.079 | 74.1798 | 158.908 | 127.666 | 173.618 | 45.9524 | 58.6506 | 286.551 | 5 |
| Faithful HANO strain-stress spectral-window NO | Plastic-work inc. rel. L2 | 71.8154 | 62.3044 | 41.9325 | 16.171 | 138.899 | 122.728 | 7.7243 | 154.351 | 5 |
| Faithful HANO strain-stress spectral-window NO | Reversal hist-inc. rel. L2 | 1.02866 | 0.0190132 | 1.02217 | 1.01766 | 1.02284 | 0.0051837 | 1.01442 | 1.06618 | 5 |
| Faithful HANO strain-stress spectral-window NO | Reversal yield-flag MAE | 0.515533 | 0.0447988 | 0.540601 | 0.475866 | 0.552304 | 0.0764385 | 0.448613 | 0.56028 | 5 |
| Faithful HANO strain-stress spectral-window NO | Yield-surface RMS | 0.38692 | 0.280211 | 0.329447 | 0.270536 | 0.453244 | 0.182708 | 0.0131581 | 0.868216 | 5 |
| Faithful HANO strain-stress spectral-window NO | Plastic-work violation abs. | 0.00789357 | 0.00645541 | 0.00745199 | 0.00326818 | 0.0081028 | 0.00483462 | 0.000970177 | 0.0196747 | 5 |
| Faithful HANO strain-stress spectral-window NO | Plastic-work violation target-norm. | 543.173 | 444.21 | 512.787 | 224.89 | 557.57 | 332.68 | 66.7599 | 1353.86 | 5 |
| Faithful HANO strain-stress spectral-window NO | Plastic-work violation pred-norm. | 21.8816 | 24.0245 | 8.75043 | 1.61478 | 33.7549 | 32.1401 | 1.57904 | 63.709 | 5 |
| Faithful HANO strain-stress spectral-window NO | HANO strain rel. L2 | 83.2328 | 41.4988 | 81.712 | 79.0982 | 96.1326 | 17.0344 | 14.8084 | 144.413 | 5 |
| Faithful HANO strain-stress spectral-window NO | HANO stress rel. L2 | 16.1585 | 4.49538 | 14.4133 | 12.3676 | 18.4791 | 6.11147 | 11.7218 | 23.8107 | 5 |
| Faithful HANO strain-stress spectral-window NO | FEM residual rel. RMS | 1372.62 | 598.072 | 1578.49 | 1026.34 | 1683.24 | 656.901 | 417.125 | 2157.92 | 5 |
| Faithful HANO strain-stress spectral-window NO | FEM energy rel. err. | 1.4381e+06 | 887629 | 1.75201e+06 | 710658 | 2.25497e+06 | 1.54431e+06 | 104386 | 2.3685e+06 | 5 |