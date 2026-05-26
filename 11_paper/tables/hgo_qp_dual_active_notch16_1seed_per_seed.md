# J2 Path-Dependent Baseline Per-Seed Appendix

Per-seed cyclic-primary metrics for diagnosing stochastic training stability and outliers.
All evaluated paths are stored in JSON: `monotonic, cyclic`.

| Model | Seed | Train final loss | Cyclic disp. rel. L2 | Cyclic history rel. L2 | History-increment rel. L2 | QP history rel. L2 | QP history-inc. rel. L2 | QP eqp rel. L2 | QP plastic-work rel. L2 | QP von-Mises rel. L2 | QP reversal scalar-inc. rel. L2 | QP reversal eqp-inc. rel. L2 | QP reversal work-inc. rel. L2 | QP reversal yield MAE | QP inactive false plasticity | Eqp increment rel. L2 | Plastic-work inc. rel. L2 | Reversal hist-inc. rel. L2 | Reversal yield-flag MAE | Yield-surface RMS | Plastic-work violation abs. | Plastic-work violation target-norm. | Plastic-work violation pred-norm. | FEM residual rel. RMS | FEM energy rel. err. |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Dual-head active-QP HistoryGNO | 20260517 | 1837.61 | 93.4997 | 1.7822 | 0.999504 | 2.73049 | 0.999574 | 1.656 | 1.61102 | 1.19827 | 1.00215 | 1.14894 | 1.12553 | 0.551728 | 0.400779 | 1.83901 | 1.78896 | 1.00216 | 0.720243 | 0.000398591 | 0 | 0 | 0 | 79.8267 | 4118.44 |