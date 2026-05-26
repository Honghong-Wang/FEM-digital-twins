# J2 Path-Dependent Baseline Table

Data root: `05_data_pipeline\processed\level6_benchmark_matrix_smoke\multi_hole_6x5`
Train load paths: `monotonic`
Primary table: cyclic path, 1 epochs, 1 seeds
Evaluated paths stored in JSON: `monotonic, cyclic, nonproportional`

| Model | Seeds | Cyclic disp. rel. L2 | Cyclic history rel. L2 | History-increment rel. L2 | QP history rel. L2 | QP history-inc. rel. L2 | QP eqp rel. L2 | QP plastic-work rel. L2 | QP von-Mises rel. L2 | QP reversal scalar-inc. rel. L2 | QP reversal eqp-inc. rel. L2 | QP reversal work-inc. rel. L2 | QP reversal yield MAE | QP inactive false plasticity | True-J2 consistency rel. RMS | True-J2 active consistency rel. RMS | True-J2 negative dgamma | True-J2 active QP frac. | Eqp increment rel. L2 | Plastic-work inc. rel. L2 | Reversal hist-inc. rel. L2 | Reversal yield-flag MAE | Yield-surface RMS | Plastic-work violation abs. | Plastic-work violation target-norm. | Plastic-work violation pred-norm. | HANO strain rel. L2 | HANO stress rel. L2 | FEM residual rel. RMS | FEM energy rel. err. |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| True differentiable J2 QP-HistoryGNO | 1 | 893.2210 +/- 0.0000 | 1.1807 +/- 0.0000 | 1.0011 +/- 0.0000 | 1.7699 +/- 0.0000 | 1.0016 +/- 0.0000 | 19.4295 +/- 0.0000 | 23.6327 +/- 0.0000 | 1.3284 +/- 0.0000 | 1.0001 +/- 0.0000 | 9.5254 +/- 0.0000 | 13.0899 +/- 0.0000 | 0.4904 +/- 0.0000 | 0.5002 +/- 0.0000 | 0.0000 +/- 0.0000 | 0.0000 +/- 0.0000 | 0.0000 +/- 0.0000 | 1.0000 +/- 0.0000 | 20.1940 +/- 0.0000 | 26.5077 +/- 0.0000 | 1.0007 +/- 0.0000 | 0.5588 +/- 0.0000 | 0.0000 +/- 0.0000 | 0.0000 +/- 0.0000 | 0.0000 +/- 0.0000 | 0.0000 +/- 0.0000 |  |  | 178.7783 +/- 0.0000 | 17071.4785 +/- 0.0000 |
