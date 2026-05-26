# J2 Path-Dependent Baseline Table

Data root: `05_data_pipeline\processed\level4_formal_complex_j2_t6_8step_qp_9case\notch_16x12`
Train load paths: `monotonic, cyclic`
Primary table: cyclic path, 50 epochs, 5 seeds
Evaluated paths stored in JSON: `monotonic, cyclic`

| Model | Seeds | Cyclic disp. rel. L2 | Cyclic history rel. L2 | History-increment rel. L2 | QP history rel. L2 | QP history-inc. rel. L2 | QP eqp rel. L2 | QP plastic-work rel. L2 | QP von-Mises rel. L2 | Eqp increment rel. L2 | Plastic-work inc. rel. L2 | Reversal hist-inc. rel. L2 | Reversal yield-flag MAE | Yield-surface RMS | Plastic-work violation abs. | Plastic-work violation target-norm. | Plastic-work violation pred-norm. | HANO strain rel. L2 | HANO stress rel. L2 | FEM residual rel. RMS | FEM energy rel. err. |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| True differentiable J2 QP-HistoryGNO | 5 | 94.4280 +/- 36.4997 | 2.1780 +/- 0.0575 | 1.0409 +/- 0.0765 | 3.3608 +/- 0.0657 | 1.1293 +/- 0.2358 | 15.8083 +/- 4.2160 | 16.7228 +/- 4.7347 | 1.3762 +/- 0.0644 | 19.1663 +/- 5.8284 | 21.1079 +/- 7.0627 | 1.0748 +/- 0.1457 | 0.8365 +/- 0.0537 | 0.0055 +/- 0.0077 | 0.0000 +/- 0.0000 | 0.0006 +/- 0.0007 | 0.0000 +/- 0.0000 |  |  | 68.2413 +/- 36.3153 | 2598.7625 +/- 2471.2533 |
