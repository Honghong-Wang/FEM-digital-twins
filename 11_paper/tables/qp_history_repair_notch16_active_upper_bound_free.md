# J2 Path-Dependent Baseline Table

Data root: `05_data_pipeline\processed\level4_formal_complex_j2_t6_8step_qp_9case\notch_16x12`
Train load paths: `monotonic, cyclic`
Primary table: cyclic path, 50 epochs, 5 seeds
Evaluated paths stored in JSON: `monotonic, cyclic`

| Model | Seeds | Cyclic disp. rel. L2 | Cyclic history rel. L2 | History-increment rel. L2 | QP history rel. L2 | QP history-inc. rel. L2 | QP eqp rel. L2 | QP plastic-work rel. L2 | QP von-Mises rel. L2 | Eqp increment rel. L2 | Plastic-work inc. rel. L2 | Reversal hist-inc. rel. L2 | Reversal yield-flag MAE | Yield-surface RMS | Plastic-work violation abs. | Plastic-work violation target-norm. | Plastic-work violation pred-norm. | HANO strain rel. L2 | HANO stress rel. L2 | FEM residual rel. RMS | FEM energy rel. err. |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| QP-aware active-zone thermo-hard HistoryGNO | 5 | 74.0720 +/- 41.4085 | 0.9931 +/- 0.0034 | 1.0001 +/- 0.0001 | 0.9857 +/- 0.0070 | 1.0002 +/- 0.0001 | 1.0000 +/- 0.0000 | 1.0000 +/- 0.0000 | 0.6645 +/- 0.1666 | 1.0000 +/- 0.0000 | 1.0000 +/- 0.0000 | 0.9998 +/- 0.0001 | 0.1362 +/- 0.0000 | 0.0000 +/- 0.0000 | 0.0000 +/- 0.0000 | 0.0000 +/- 0.0000 | 0.0000 +/- 0.0000 |  |  | 99.2952 +/- 45.4624 | 5782.6670 +/- 4981.3987 |
