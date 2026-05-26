# J2 Path-Dependent Baseline Per-Seed Appendix

Per-seed cyclic-primary metrics for diagnosing stochastic training stability and outliers.
All evaluated paths are stored in JSON: `monotonic, cyclic`.

| Model | Seed | Train final loss | Cyclic disp. rel. L2 | Cyclic history rel. L2 | History-increment rel. L2 | Eqp increment rel. L2 | Plastic-work inc. rel. L2 | Reversal hist-inc. rel. L2 | Reversal yield-flag MAE | Yield-surface RMS | Plastic-work violation abs. | Plastic-work violation target-norm. | Plastic-work violation pred-norm. | HANO strain rel. L2 | HANO stress rel. L2 | FEM residual rel. RMS | FEM energy rel. err. |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Faithful HANO strain-stress spectral-window NO | 20260517 | 4728.83 | 227.472 | 1.26839 | 1.01123 | 42.918 | 19.7198 | 1.00599 | 0.539586 | 1.15046 | 0.000350253 | 36.374 | 1.80936 | 10.4872 | 25.4741 | 515.023 | 112345 |
| Faithful HANO strain-stress spectral-window NO | 20260518 | 5987.26 | 1099.77 | 2.66643 | 1.01052 | 104.765 | 5.48713 | 1.00836 | 0.564923 | 0.694965 | 0.00162307 | 168.557 | 28.994 | 176.709 | 18.0156 | 4411.82 | 6.14654e+06 |
| Faithful HANO strain-stress spectral-window NO | 20260519 | 8075.09 | 541.33 | 3.37373 | 1.01421 | 185.053 | 88.3404 | 1.00971 | 0.433205 | 0.87167 | 0.00337542 | 350.539 | 3.95004 | 93.8881 | 24.0012 | 1181.1 | 601497 |
| Faithful HANO strain-stress spectral-window NO | 20260520 | 39498.3 | 625.32 | 1.949 | 1.00186 | 101.871 | 2.29268 | 1.00711 | 0.576035 | 0.0134902 | 0.00164409 | 170.74 | 67.7516 | 44.6058 | 17.4738 | 1333.02 | 695966 |
| Faithful HANO strain-stress spectral-window NO | 20260521 | 10798.6 | 579.002 | 0.913657 | 1.00002 | 54.358 | 50.2742 | 1.02624 | 0.470581 | 0.843423 | 0.000235653 | 24.4727 | 0.482989 | 50.4007 | 11.7787 | 1253.1 | 920665 |