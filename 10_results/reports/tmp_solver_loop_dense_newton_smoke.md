# J2 Path-Dependent Baseline Table

Data root: `05_data_pipeline\processed\level6_benchmark_matrix_smoke\multi_hole_6x5`
Train load paths: `monotonic`
Primary table: cyclic path, 1 epochs, 1 seeds
Evaluated paths stored in JSON: `monotonic, cyclic`

| Model | Seeds | Cyclic disp. rel. L2 | Cyclic history rel. L2 | History-increment rel. L2 | QP history rel. L2 | QP history-inc. rel. L2 | QP eqp rel. L2 | QP plastic-work rel. L2 | QP von-Mises rel. L2 | QP reversal scalar-inc. rel. L2 | QP reversal eqp-inc. rel. L2 | QP reversal work-inc. rel. L2 | QP reversal yield MAE | QP inactive false plasticity | True-J2 consistency rel. RMS | True-J2 active consistency rel. RMS | True-J2 negative dgamma | True-J2 active QP frac. | Eqp increment rel. L2 | Plastic-work inc. rel. L2 | Reversal hist-inc. rel. L2 | Reversal yield-flag MAE | Yield-surface RMS | Plastic-work violation abs. | Plastic-work violation target-norm. | Plastic-work violation pred-norm. | HANO strain rel. L2 | HANO stress rel. L2 | FEM residual rel. RMS | FEM energy rel. err. | FEM tangent-solver rel. RMS |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| True differentiable J2 QP-HistoryGNO | 1 | 172.6947 +/- 0.0000 | 1.1872 +/- 0.0000 | 1.0022 +/- 0.0000 | 1.7775 +/- 0.0000 | 1.0033 +/- 0.0000 | 30.6054 +/- 0.0000 | 42.9989 +/- 0.0000 | 1.6212 +/- 0.0000 | 1.0002 +/- 0.0000 | 16.4769 +/- 0.0000 | 27.6908 +/- 0.0000 | 0.4904 +/- 0.0000 | 0.5005 +/- 0.0000 | 0.0000 +/- 0.0000 | 0.0000 +/- 0.0000 | 0.0000 +/- 0.0000 | 1.0000 +/- 0.0000 | 33.3148 +/- 0.0000 | 52.8125 +/- 0.0000 | 1.0015 +/- 0.0000 | 0.5588 +/- 0.0000 | 0.0000 +/- 0.0000 | 0.0000 +/- 0.0000 | 0.0000 +/- 0.0000 | 0.0000 +/- 0.0000 |  |  | 377.5380 +/- 0.0000 | 266917.2500 +/- 0.0000 | 2.0431 +/- 0.0000 |
