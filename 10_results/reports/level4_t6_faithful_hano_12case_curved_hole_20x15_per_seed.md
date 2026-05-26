# J2 Path-Dependent Baseline Per-Seed Appendix

Per-seed cyclic-primary metrics for diagnosing stochastic training stability and outliers.
All evaluated paths are stored in JSON: `monotonic, cyclic`.

| Model | Seed | Train final loss | Cyclic disp. rel. L2 | Cyclic history rel. L2 | History-increment rel. L2 | Eqp increment rel. L2 | Plastic-work inc. rel. L2 | Reversal hist-inc. rel. L2 | Reversal yield-flag MAE | Yield-surface RMS | Plastic-work violation abs. | Plastic-work violation target-norm. | Plastic-work violation pred-norm. | HANO strain rel. L2 | HANO stress rel. L2 | FEM residual rel. RMS | FEM energy rel. err. |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Faithful HANO strain-stress spectral-window NO | 20260517 | 4065.49 | 95.0297 | 1.27804 | 1.00689 | 58.6506 | 41.9325 | 1.02284 | 0.540601 | 0.453244 | 0.000970177 | 66.7599 | 1.57904 | 14.8084 | 18.4791 | 417.125 | 104386 |
| Faithful HANO strain-stress spectral-window NO | 20260518 | 22625.9 | 110.074 | 3.06863 | 1.01587 | 173.618 | 16.171 | 1.01766 | 0.552304 | 0.329447 | 0.0081028 | 557.57 | 33.7549 | 144.413 | 12.3676 | 2157.92 | 2.25497e+06 |
| Faithful HANO strain-stress spectral-window NO | 20260519 | 14524.6 | 162.228 | 2.85817 | 1.01472 | 286.551 | 154.351 | 1.02217 | 0.448613 | 0.868216 | 0.0196747 | 1353.86 | 8.75043 | 96.1326 | 23.8107 | 1026.34 | 710658 |
| Faithful HANO strain-stress spectral-window NO | 20260520 | 66795.3 | 250.087 | 2.09195 | 1.00398 | 158.908 | 7.7243 | 1.01442 | 0.56028 | 0.0131581 | 0.00745199 | 512.787 | 63.709 | 81.712 | 14.4133 | 1578.49 | 1.75201e+06 |
| Faithful HANO strain-stress spectral-window NO | 20260521 | 16547.6 | 127.045 | 0.942414 | 1.00765 | 127.666 | 138.899 | 1.06618 | 0.475866 | 0.270536 | 0.00326818 | 224.89 | 1.61478 | 79.0982 | 11.7218 | 1683.24 | 2.3685e+06 |