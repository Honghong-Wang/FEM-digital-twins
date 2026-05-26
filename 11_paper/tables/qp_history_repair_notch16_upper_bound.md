# J2 Path-Dependent Baseline Table

Data root: `05_data_pipeline\processed\level4_formal_complex_j2_t6_8step_qp_9case\notch_16x12`
Train load paths: `monotonic, cyclic`
Primary table: cyclic path, 50 epochs, 5 seeds
Evaluated paths stored in JSON: `monotonic, cyclic`

| Model | Seeds | Cyclic disp. rel. L2 | Cyclic history rel. L2 | History-increment rel. L2 | QP history rel. L2 | QP history-inc. rel. L2 | QP eqp rel. L2 | QP plastic-work rel. L2 | QP von-Mises rel. L2 | Eqp increment rel. L2 | Plastic-work inc. rel. L2 | Reversal hist-inc. rel. L2 | Reversal yield-flag MAE | Yield-surface RMS | Plastic-work violation abs. | Plastic-work violation target-norm. | Plastic-work violation pred-norm. | HANO strain rel. L2 | HANO stress rel. L2 | FEM residual rel. RMS | FEM energy rel. err. |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| QP-aware thermo-hard HistoryGNO | 5 | 96.2133 +/- 46.5057 | 0.9979 +/- 0.0034 | 1.0000 +/- 0.0001 | 0.9955 +/- 0.0073 | 1.0001 +/- 0.0001 | 1.0000 +/- 0.0000 | 1.0000 +/- 0.0000 | 0.8947 +/- 0.1761 | 1.0000 +/- 0.0000 | 1.0000 +/- 0.0000 | 0.9999 +/- 0.0001 | 0.1362 +/- 0.0000 | 0.0000 +/- 0.0000 | 0.0000 +/- 0.0000 | 0.0000 +/- 0.0000 | 0.0000 +/- 0.0000 |  |  | 82.2053 +/- 26.1598 | 3062.9384 +/- 1980.5496 |
