# J2 Path-Dependent Baseline Per-Seed Appendix

Per-seed cyclic-primary metrics for diagnosing stochastic training stability and outliers.
All evaluated paths are stored in JSON: `monotonic, unload_reload, cyclic, nonproportional`.

| Model | Seed | Train final loss | Cyclic disp. rel. L2 | Cyclic history rel. L2 | History-increment rel. L2 | QP history rel. L2 | QP history-inc. rel. L2 | QP eqp rel. L2 | QP plastic-work rel. L2 | QP von-Mises rel. L2 | QP reversal scalar-inc. rel. L2 | QP reversal eqp-inc. rel. L2 | QP reversal work-inc. rel. L2 | QP reversal yield MAE | QP inactive false plasticity | Eqp increment rel. L2 | Plastic-work inc. rel. L2 | Reversal hist-inc. rel. L2 | Reversal yield-flag MAE | Yield-surface RMS | Plastic-work violation abs. | Plastic-work violation target-norm. | Plastic-work violation pred-norm. | FEM residual rel. RMS | FEM energy rel. err. |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Dual-head reversal-active QP-HistoryGNO | 20260517 | 2.30396e+07 | 3075.74 | 1.83882 | 0.999054 | 2.82021 | 0.999282 | 0.984821 | 0.985837 | 1.18024 | 1.00616 | 0.992534 | 0.993228 | 0.555591 | 0.414346 | 0.982235 | 0.983242 | 1.00613 | 0.741643 | 2.13457e-05 | 0 | 0 | 0 | 792.997 | 760396 |