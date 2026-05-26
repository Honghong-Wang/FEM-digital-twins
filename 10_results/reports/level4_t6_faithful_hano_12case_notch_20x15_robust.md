# J2 Path-Dependent Baseline Robust Statistics

Each row reports both mean/std and robust median/IQR statistics on the cyclic primary test path.
All evaluated paths are stored in JSON: `monotonic, cyclic`.

| Model | Metric | Mean | Std | Median | Q1 | Q3 | IQR | Min | Max | N |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Faithful HANO strain-stress spectral-window NO | Cyclic disp. rel. L2 | 265.112 | 119.453 | 268.312 | 178.103 | 374.407 | 196.304 | 91.9105 | 412.827 | 5 |
| Faithful HANO strain-stress spectral-window NO | Cyclic history rel. L2 | 2.66797 | 1.17857 | 2.05169 | 1.66399 | 3.94766 | 2.28366 | 1.4487 | 4.22781 | 5 |
| Faithful HANO strain-stress spectral-window NO | History-increment rel. L2 | 1.00875 | 0.00637889 | 1.00612 | 1.00387 | 1.01207 | 0.00820661 | 1.0021 | 1.01959 | 5 |
| Faithful HANO strain-stress spectral-window NO | Eqp increment rel. L2 | 118.035 | 57.4252 | 135.083 | 57.5616 | 135.977 | 78.4152 | 53.6613 | 207.895 | 5 |
| Faithful HANO strain-stress spectral-window NO | Plastic-work inc. rel. L2 | 28.6826 | 28.389 | 16.2589 | 4.97879 | 41.1145 | 36.1357 | 2.59496 | 78.4656 | 5 |
| Faithful HANO strain-stress spectral-window NO | Reversal hist-inc. rel. L2 | 1.00499 | 0.00507021 | 1.00242 | 1.00101 | 1.00703 | 0.00601947 | 1.00047 | 1.01402 | 5 |
| Faithful HANO strain-stress spectral-window NO | Reversal yield-flag MAE | 0.412438 | 0.240924 | 0.283276 | 0.210154 | 0.623687 | 0.413533 | 0.171896 | 0.773179 | 5 |
| Faithful HANO strain-stress spectral-window NO | Yield-surface RMS | 0.407986 | 0.28106 | 0.376644 | 0.277818 | 0.521778 | 0.24396 | 0.00583995 | 0.857851 | 5 |
| Faithful HANO strain-stress spectral-window NO | Plastic-work violation abs. | 0.00262449 | 0.00190292 | 0.00305761 | 0.000791708 | 0.00322697 | 0.00243526 | 0.00038887 | 0.0056573 | 5 |
| Faithful HANO strain-stress spectral-window NO | Plastic-work violation target-norm. | 212.473 | 154.057 | 247.537 | 64.095 | 261.248 | 197.153 | 31.4821 | 458.003 | 5 |
| Faithful HANO strain-stress spectral-window NO | Plastic-work violation pred-norm. | 31.507 | 37.8855 | 5.81919 | 3.89255 | 48.2646 | 44.372 | 0.761353 | 98.7976 | 5 |
| Faithful HANO strain-stress spectral-window NO | HANO strain rel. L2 | 64.2865 | 52.0628 | 40.1331 | 38.0573 | 72.5096 | 34.4523 | 10.1167 | 160.616 | 5 |
| Faithful HANO strain-stress spectral-window NO | HANO stress rel. L2 | 16.575 | 3.04451 | 14.7619 | 14.6655 | 20.1604 | 5.49488 | 13.0002 | 20.2868 | 5 |
| Faithful HANO strain-stress spectral-window NO | FEM residual rel. RMS | 2095.98 | 1971.9 | 1275.48 | 1183.22 | 1446.07 | 262.848 | 578.941 | 5996.21 | 5 |
| Faithful HANO strain-stress spectral-window NO | FEM energy rel. err. | 1.81596e+06 | 2.7846e+06 | 446188 | 441711 | 727058 | 285347 | 94166.5 | 7.37067e+06 | 5 |