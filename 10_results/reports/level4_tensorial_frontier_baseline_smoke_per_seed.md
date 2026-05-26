# J2 Path-Dependent Baseline Per-Seed Appendix

Per-seed cyclic-path metrics for diagnosing stochastic training stability and outliers.

| Model | Seed | Train final loss | Cyclic disp. rel. L2 | Cyclic history rel. L2 | History-increment rel. L2 | Eqp increment rel. L2 | Plastic-work inc. rel. L2 | Reversal hist-inc. rel. L2 | Reversal yield-flag MAE | Yield-surface RMS | Plastic-work violation abs. | Plastic-work violation target-norm. | Plastic-work violation pred-norm. |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Thermo-hard HistoryGNO | 20260517 | 216.825 | 2.67156 | 1.03978 | 1.00007 | 0.93037 | 0.968545 | 1.00332 | 0.951613 | 4.42289e-07 | 0 | 0 | 0 |
| HANO-style history-aware NO | 20260517 | 879.695 | 2.8113 | 4.98488 | 1.34003 | 14.0889 | 29.2423 | 1.25962 | 0.573134 | 0.540701 | 2.2422 | 185.93 | 6.31915 |
| INCDE-style controlled recurrent operator | 20260517 | 381233 | 290.972 | 4.45589 | 1.03286 | 4.97545 | 2.02409 | 1.02761 | 0.349958 | 0.402116 | 0.344288 | 28.4897 | 13.4656 |
| TINN-style hard-thermo operator | 20260517 | 381218 | 290.972 | 1.04521 | 1.00118 | 0.946025 | 1.01887 | 1.0078 | 0.951613 | 0 | 0 | 0 | 0 |