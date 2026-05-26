# J2 Path-Dependent Baseline Table

Data root: `05_data_pipeline\processed\level4_formal_complex_j2_t6_8step_qp_9case\notch_16x12`
Train load paths: `monotonic, cyclic`
Primary table: cyclic path, 50 epochs, 1 seeds
Evaluated paths stored in JSON: `monotonic, cyclic`

| Model | Seeds | Cyclic disp. rel. L2 | Cyclic history rel. L2 | History-increment rel. L2 | QP history rel. L2 | QP history-inc. rel. L2 | QP eqp rel. L2 | QP plastic-work rel. L2 | QP von-Mises rel. L2 | Eqp increment rel. L2 | Plastic-work inc. rel. L2 | Reversal hist-inc. rel. L2 | Reversal yield-flag MAE | Yield-surface RMS | Plastic-work violation abs. | Plastic-work violation target-norm. | Plastic-work violation pred-norm. | HANO strain rel. L2 | HANO stress rel. L2 | FEM residual rel. RMS | FEM energy rel. err. |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| QP plastic-memory corrector HistoryGNO | 1 | 88.3193 +/- 0.0000 | 1.0025 +/- 0.0000 | 1.0000 +/- 0.0000 | 1.0084 +/- 0.0000 | 1.0000 +/- 0.0000 | 1.2793 +/- 0.0000 | 1.2553 +/- 0.0000 | 1.1898 +/- 0.0000 | 1.3489 +/- 0.0000 | 1.3213 +/- 0.0000 | 0.9998 +/- 0.0000 | 0.1382 +/- 0.0000 | 0.0000 +/- 0.0000 | 0.0000 +/- 0.0000 | 0.0000 +/- 0.0000 | 0.0000 +/- 0.0000 |  |  | 86.0548 +/- 0.0000 | 4400.2549 +/- 0.0000 |
