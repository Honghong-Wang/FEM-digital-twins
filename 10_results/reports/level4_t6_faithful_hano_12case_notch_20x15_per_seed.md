# J2 Path-Dependent Baseline Per-Seed Appendix

Per-seed cyclic-primary metrics for diagnosing stochastic training stability and outliers.
All evaluated paths are stored in JSON: `monotonic, cyclic`.

| Model | Seed | Train final loss | Cyclic disp. rel. L2 | Cyclic history rel. L2 | History-increment rel. L2 | Eqp increment rel. L2 | Plastic-work inc. rel. L2 | Reversal hist-inc. rel. L2 | Reversal yield-flag MAE | Yield-surface RMS | Plastic-work violation abs. | Plastic-work violation target-norm. | Plastic-work violation pred-norm. | HANO strain rel. L2 | HANO stress rel. L2 | FEM residual rel. RMS | FEM energy rel. err. |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Faithful HANO strain-stress spectral-window NO | 20260517 | 20096 | 91.9105 | 1.66399 | 1.0021 | 57.5616 | 16.2589 | 1.00047 | 0.283276 | 0.521778 | 0.000791708 | 64.095 | 3.89255 | 10.1167 | 20.2868 | 578.941 | 94166.5 |
| Faithful HANO strain-stress spectral-window NO | 20260518 | 9755.56 | 268.312 | 3.94766 | 1.01207 | 135.083 | 4.97879 | 1.00703 | 0.210154 | 0.376644 | 0.00305761 | 247.537 | 48.2646 | 160.616 | 14.6655 | 5996.21 | 7.37067e+06 |
| Faithful HANO strain-stress spectral-window NO | 20260519 | 12993.8 | 374.407 | 4.22781 | 1.01959 | 207.895 | 78.4656 | 1.00242 | 0.773179 | 0.857851 | 0.0056573 | 458.003 | 5.81919 | 72.5096 | 20.1604 | 1183.22 | 446188 |
| Faithful HANO strain-stress spectral-window NO | 20260520 | 54655.9 | 412.827 | 2.05169 | 1.00387 | 135.977 | 2.59496 | 1.00101 | 0.171896 | 0.00583995 | 0.00322697 | 261.248 | 98.7976 | 40.1331 | 14.7619 | 1275.48 | 441711 |
| Faithful HANO strain-stress spectral-window NO | 20260521 | 11194.4 | 178.103 | 1.4487 | 1.00612 | 53.6613 | 41.1145 | 1.01402 | 0.623687 | 0.277818 | 0.00038887 | 31.4821 | 0.761353 | 38.0573 | 13.0002 | 1446.07 | 727058 |