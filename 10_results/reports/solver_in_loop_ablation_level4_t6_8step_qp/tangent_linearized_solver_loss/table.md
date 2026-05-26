# J2 Path-Dependent Baseline Table

Data root: `05_data_pipeline\processed\level4_formal_complex_j2_t6_8step_qp`
Train load paths: `monotonic`
Primary table: cyclic path, 50 epochs, 5 seeds
Evaluated paths stored in JSON: `monotonic, unload_reload, cyclic, nonproportional`

| Model | Seeds | Cyclic disp. rel. L2 | Cyclic history rel. L2 | History-increment rel. L2 | QP history rel. L2 | QP history-inc. rel. L2 | QP eqp rel. L2 | QP plastic-work rel. L2 | QP von-Mises rel. L2 | QP reversal scalar-inc. rel. L2 | QP reversal eqp-inc. rel. L2 | QP reversal work-inc. rel. L2 | QP reversal yield MAE | QP inactive false plasticity | True-J2 consistency rel. RMS | True-J2 active consistency rel. RMS | True-J2 negative dgamma | True-J2 active QP frac. | Eqp increment rel. L2 | Plastic-work inc. rel. L2 | Reversal hist-inc. rel. L2 | Reversal yield-flag MAE | Yield-surface RMS | Plastic-work violation abs. | Plastic-work violation target-norm. | Plastic-work violation pred-norm. | HANO strain rel. L2 | HANO stress rel. L2 | FEM residual rel. RMS | FEM energy rel. err. | FEM tangent-solver rel. RMS |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| True differentiable J2 QP-HistoryGNO | 5 | 69.0266 +/- 38.2186 | 1.1547 +/- 0.0305 | 1.0637 +/- 0.1077 | 1.9281 +/- 0.0355 | 1.2187 +/- 0.3222 | 6.1433 +/- 1.6980 | 6.5408 +/- 1.9488 | 0.8855 +/- 0.0362 | 1.1620 +/- 0.2697 | 2.7526 +/- 0.7540 | 2.9280 +/- 0.8500 | 0.1437 +/- 0.0399 | 0.4908 +/- 0.0132 | 0.0367 +/- 0.0461 | 0.0000 +/- 0.0000 | 0.0000 +/- 0.0000 | 0.9662 +/- 0.0503 | 7.7372 +/- 1.8958 | 8.2896 +/- 2.1112 | 1.1750 +/- 0.3076 | 0.4570 +/- 0.0020 | 0.0102 +/- 0.0135 | 0.0000 +/- 0.0000 | 0.0118 +/- 0.0220 | 0.0011 +/- 0.0020 |  |  | 37.8912 +/- 12.8964 | 1161.8196 +/- 666.6319 | 6.6910 +/- 4.4238 |
