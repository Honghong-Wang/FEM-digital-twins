# J2 Path-Dependent Baseline Table

Data root: `05_data_pipeline\processed\level4_formal_complex_j2_t6_8step_qp_9case\notch_16x12`
Train load paths: `monotonic, cyclic`
Primary table: cyclic path, 1 epochs, 1 seeds
Evaluated paths stored in JSON: `monotonic, cyclic`

| Model | Seeds | Cyclic disp. rel. L2 | Cyclic history rel. L2 | History-increment rel. L2 | QP history rel. L2 | QP history-inc. rel. L2 | QP eqp rel. L2 | QP plastic-work rel. L2 | QP von-Mises rel. L2 | QP reversal scalar-inc. rel. L2 | QP reversal eqp-inc. rel. L2 | QP reversal work-inc. rel. L2 | QP reversal yield MAE | QP inactive false plasticity | True-J2 consistency rel. RMS | True-J2 active consistency rel. RMS | True-J2 negative dgamma | True-J2 active QP frac. | Eqp increment rel. L2 | Plastic-work inc. rel. L2 | Reversal hist-inc. rel. L2 | Reversal yield-flag MAE | Yield-surface RMS | Plastic-work violation abs. | Plastic-work violation target-norm. | Plastic-work violation pred-norm. | HANO strain rel. L2 | HANO stress rel. L2 | FEM residual rel. RMS | FEM energy rel. err. |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| True differentiable J2 QP-HistoryGNO | 1 | 299.1726 +/- 0.0000 | 2.2320 +/- 0.0000 | 1.0133 +/- 0.0000 | 3.4319 +/- 0.0000 | 1.0708 +/- 0.0000 | 113.3159 +/- 0.0000 | 225.2010 +/- 0.0000 | 2.6752 +/- 0.0000 | 1.0097 +/- 0.0000 | 56.7053 +/- 0.0000 | 112.8504 +/- 0.0000 | 0.5877 +/- 0.0000 | 0.4990 +/- 0.0000 | 0.0422 +/- 0.0000 | 0.0000 +/- 0.0000 | 0.0000 +/- 0.0000 | 0.9926 +/- 0.0000 | 156.5968 +/- 0.0000 | 301.5434 +/- 0.0000 | 1.0118 +/- 0.0000 | 0.8606 +/- 0.0000 | 0.0087 +/- 0.0000 | 0.0000 +/- 0.0000 | 2.8962 +/- 0.0000 | 0.0096 +/- 0.0000 |  |  | 784.7782 +/- 0.0000 | 314311.1562 +/- 0.0000 |
