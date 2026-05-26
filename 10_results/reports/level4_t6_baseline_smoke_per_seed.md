# J2 Path-Dependent Baseline Per-Seed Appendix

Per-seed cyclic-path metrics for diagnosing stochastic training stability and outliers.

| Model | Seed | Train final loss | Cyclic disp. rel. L2 | Cyclic history rel. L2 | History-increment rel. L2 | Eqp increment rel. L2 | Plastic-work inc. rel. L2 | Reversal hist-inc. rel. L2 | Reversal yield-flag MAE | Yield-surface RMS | Plastic-work violation abs. | Plastic-work violation target-norm. | Plastic-work violation pred-norm. |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Thermo-hard HistoryGNO | 20260517 | 73264.3 | 128.953 | 2.9023 | 1.01346 | 788.72 | 1107.69 | 0 | 0 | 4.51535e-07 | 0 | 0 | 0 |
| HANO-window recent-history NO | 20260517 | 5.05653e+08 | 6526.61 | 4.62298 | 2.15838 | 13483.1 | 271643 | 0 | 0 | 0.544162 | 0 | 0 | 0 |
| INCDE Euler neural CDE | 20260517 | 2.06062e+07 | 7912.01 | 4.08796 | 2.01326 | 23015.6 | 195955 | 0 | 0 | 0.414414 | 0.108433 | 52724.3 | 0.269063 |