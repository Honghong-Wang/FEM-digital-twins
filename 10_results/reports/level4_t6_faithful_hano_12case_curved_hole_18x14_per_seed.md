# J2 Path-Dependent Baseline Per-Seed Appendix

Per-seed cyclic-primary metrics for diagnosing stochastic training stability and outliers.
All evaluated paths are stored in JSON: `monotonic, cyclic`.

| Model | Seed | Train final loss | Cyclic disp. rel. L2 | Cyclic history rel. L2 | History-increment rel. L2 | Eqp increment rel. L2 | Plastic-work inc. rel. L2 | Reversal hist-inc. rel. L2 | Reversal yield-flag MAE | Yield-surface RMS | Plastic-work violation abs. | Plastic-work violation target-norm. | Plastic-work violation pred-norm. | HANO strain rel. L2 | HANO stress rel. L2 | FEM residual rel. RMS | FEM energy rel. err. |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Faithful HANO strain-stress spectral-window NO | 20260517 | 23552.7 | 212.772 | 1.41948 | 1.00536 | 39.5875 | 86.6363 | 1.00907 | 0.452447 | 0.24171 | 0 | 0 | 0 | 15.3915 | 14.4544 | 578.979 | 48636.7 |
| Faithful HANO strain-stress spectral-window NO | 20260518 | 16640.1 | 211.991 | 3.11863 | 1.01222 | 109.397 | 22.5844 | 1.00356 | 0.449629 | 0.260955 | 0.0033545 | 249.449 | 10.9003 | 129.152 | 11.6917 | 2806.02 | 1.02997e+06 |
| Faithful HANO strain-stress spectral-window NO | 20260519 | 26687.5 | 139.037 | 2.33003 | 1.01658 | 333.703 | 236.797 | 1.01658 | 0.542631 | 0.79949 | 0.0244559 | 1818.6 | 7.66974 | 76.6819 | 27.5216 | 1668.03 | 492794 |
| Faithful HANO strain-stress spectral-window NO | 20260520 | 70251.1 | 405.365 | 1.85316 | 1.00511 | 267.315 | 26.1896 | 1.01377 | 0.445498 | 0.00648663 | 0.0175854 | 1307.69 | 49.3561 | 112.855 | 17.6516 | 3425.03 | 2.22746e+06 |
| Faithful HANO strain-stress spectral-window NO | 20260521 | 11958.1 | 171.967 | 1.10773 | 0.999805 | 133.388 | 232.298 | 1.01247 | 0.524759 | 0.278547 | 0.00254782 | 189.462 | 0.814488 | 86.8654 | 16.6093 | 2508.92 | 1.54591e+06 |