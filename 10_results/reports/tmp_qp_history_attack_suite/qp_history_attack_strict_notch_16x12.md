# J2 Path-Dependent Baseline Table

Data root: `05_data_pipeline\processed\level4_formal_complex_j2_t6_8step_qp_9case\notch_16x12`
Train load paths: `monotonic`
Primary table: cyclic path, 1 epochs, 1 seeds
Evaluated paths stored in JSON: `monotonic, unload_reload, cyclic, nonproportional`

| Model | Seeds | Cyclic disp. rel. L2 | Cyclic history rel. L2 | History-increment rel. L2 | QP history rel. L2 | QP history-inc. rel. L2 | QP eqp rel. L2 | QP plastic-work rel. L2 | QP von-Mises rel. L2 | QP reversal scalar-inc. rel. L2 | QP reversal eqp-inc. rel. L2 | QP reversal work-inc. rel. L2 | QP reversal yield MAE | QP inactive false plasticity | True-J2 consistency rel. RMS | True-J2 active consistency rel. RMS | True-J2 negative dgamma | True-J2 active QP frac. | Eqp increment rel. L2 | Plastic-work inc. rel. L2 | Reversal hist-inc. rel. L2 | Reversal yield-flag MAE | Yield-surface RMS | Plastic-work violation abs. | Plastic-work violation target-norm. | Plastic-work violation pred-norm. | HANO strain rel. L2 | HANO stress rel. L2 | FEM residual rel. RMS | FEM energy rel. err. |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Dual-head reversal-active QP-HistoryGNO | 1 | 3075.7383 +/- 0.0000 | 1.8388 +/- 0.0000 | 0.9991 +/- 0.0000 | 2.8202 +/- 0.0000 | 0.9993 +/- 0.0000 | 0.9848 +/- 0.0000 | 0.9858 +/- 0.0000 | 1.1802 +/- 0.0000 | 1.0062 +/- 0.0000 | 0.9925 +/- 0.0000 | 0.9932 +/- 0.0000 | 0.5556 +/- 0.0000 | 0.4143 +/- 0.0000 |  |  |  |  | 0.9822 +/- 0.0000 | 0.9832 +/- 0.0000 | 1.0061 +/- 0.0000 | 0.7416 +/- 0.0000 | 0.0000 +/- 0.0000 | 0.0000 +/- 0.0000 | 0.0000 +/- 0.0000 | 0.0000 +/- 0.0000 |  |  | 792.9966 +/- 0.0000 | 760396.0000 +/- 0.0000 |
