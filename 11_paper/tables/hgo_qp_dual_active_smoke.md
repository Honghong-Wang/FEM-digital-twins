# J2 Path-Dependent Baseline Table

Data root: `05_data_pipeline\processed\level4_formal_complex_j2_t6_8step_qp_9case\notch_16x12`
Train load paths: `monotonic, cyclic`
Primary table: cyclic path, 1 epochs, 1 seeds
Evaluated paths stored in JSON: `monotonic, cyclic`

| Model | Seeds | Cyclic disp. rel. L2 | Cyclic history rel. L2 | History-increment rel. L2 | QP history rel. L2 | QP history-inc. rel. L2 | QP eqp rel. L2 | QP plastic-work rel. L2 | QP von-Mises rel. L2 | QP reversal scalar-inc. rel. L2 | QP reversal eqp-inc. rel. L2 | QP reversal work-inc. rel. L2 | QP reversal yield MAE | QP inactive false plasticity | Eqp increment rel. L2 | Plastic-work inc. rel. L2 | Reversal hist-inc. rel. L2 | Reversal yield-flag MAE | Yield-surface RMS | Plastic-work violation abs. | Plastic-work violation target-norm. | Plastic-work violation pred-norm. | HANO strain rel. L2 | HANO stress rel. L2 | FEM residual rel. RMS | FEM energy rel. err. |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Dual-head active-QP HistoryGNO | 1 | 606.8928 +/- 0.0000 | 1.0048 +/- 0.0000 | 1.0000 +/- 0.0000 | 1.0103 +/- 0.0000 | 1.0000 +/- 0.0000 | 0.9900 +/- 0.0000 | 0.9907 +/- 0.0000 | 1.1797 +/- 0.0000 | 1.0000 +/- 0.0000 | 0.9955 +/- 0.0000 | 0.9960 +/- 0.0000 | 0.4123 +/- 0.0000 | 0.0000 +/- 0.0000 | 0.9885 +/- 0.0000 | 0.9893 +/- 0.0000 | 1.0000 +/- 0.0000 | 0.1362 +/- 0.0000 | 0.0000 +/- 0.0000 | 0.0000 +/- 0.0000 | 0.0000 +/- 0.0000 | 0.0000 +/- 0.0000 |  |  | 1105.3585 +/- 0.0000 | 402637.0312 +/- 0.0000 |
