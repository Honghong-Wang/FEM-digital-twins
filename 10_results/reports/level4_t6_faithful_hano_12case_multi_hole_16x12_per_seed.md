# J2 Path-Dependent Baseline Per-Seed Appendix

Per-seed cyclic-primary metrics for diagnosing stochastic training stability and outliers.
All evaluated paths are stored in JSON: `monotonic, cyclic`.

| Model | Seed | Train final loss | Cyclic disp. rel. L2 | Cyclic history rel. L2 | History-increment rel. L2 | Eqp increment rel. L2 | Plastic-work inc. rel. L2 | Reversal hist-inc. rel. L2 | Reversal yield-flag MAE | Yield-surface RMS | Plastic-work violation abs. | Plastic-work violation target-norm. | Plastic-work violation pred-norm. | HANO strain rel. L2 | HANO stress rel. L2 | FEM residual rel. RMS | FEM energy rel. err. |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Faithful HANO strain-stress spectral-window NO | 20260517 | 2467.82 | 108.128 | 1.22085 | 1.00928 | 63.2009 | 64.5269 | 1.00626 | 0.549255 | 0.77767 | 0.00156313 | 69.1531 | 1.06541 | 8.36524 | 23.0251 | 277.967 | 66511.8 |
| Faithful HANO strain-stress spectral-window NO | 20260518 | 4388.55 | 136.812 | 1.8993 | 1.01678 | 117.489 | 21.8974 | 1.02637 | 0.600433 | 0.469836 | 0.00666235 | 294.743 | 13.2277 | 141.039 | 19.9597 | 3632.19 | 6.35073e+06 |
| Faithful HANO strain-stress spectral-window NO | 20260519 | 10376.2 | 165.738 | 2.45354 | 1.01182 | 177.007 | 170.042 | 1.03512 | 0.389217 | 0.801656 | 0.0121211 | 536.239 | 3.14626 | 71.6676 | 21.7432 | 624.02 | 321010 |
| Faithful HANO strain-stress spectral-window NO | 20260520 | 28476.8 | 273.831 | 1.76689 | 1.00284 | 112.116 | 13.0244 | 1.01083 | 0.639181 | 0.0284208 | 0.00675458 | 298.823 | 22.2983 | 37.3194 | 14.4253 | 688.139 | 324477 |
| Faithful HANO strain-stress spectral-window NO | 20260521 | 8499.7 | 132.735 | 0.910886 | 1.00489 | 66.8049 | 98.6638 | 1.06798 | 0.460069 | 0.524557 | 0.00101886 | 45.0745 | 0.455021 | 32.9034 | 10.5284 | 716.324 | 425533 |