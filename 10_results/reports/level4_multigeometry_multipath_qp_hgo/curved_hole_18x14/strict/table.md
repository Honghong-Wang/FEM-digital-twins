# J2 Path-Dependent Baseline Table

Data root: `05_data_pipeline\processed\level4_formal_complex_j2_t6_8step_qp_9case\curved_hole_18x14`
Train load paths: `monotonic`
Evaluation: cyclic path, 50 epochs, 5 seeds

| Model | Seeds | Cyclic disp. rel. L2 | Cyclic history rel. L2 | History-increment rel. L2 | QP history rel. L2 | QP history-inc. rel. L2 | Eqp increment rel. L2 | Plastic-work inc. rel. L2 | Reversal hist-inc. rel. L2 | Reversal yield-flag MAE | Yield-surface RMS | Plastic-work violation abs. | Plastic-work violation target-norm. | Plastic-work violation pred-norm. | FEM residual rel. RMS | FEM energy rel. err. |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| QP-thermo-hard HistoryGNO | 5 | 56.6054 +/- 22.3807 | 1.2893 +/- 0.1594 | 1.0001 +/- 0.0001 | 2.0032 +/- 0.1570 | 1.0002 +/- 0.0001 | 6.8914 +/- 1.9286 | 7.5916 +/- 2.2594 | 1.0000 +/- 0.0001 | 0.5479 +/- 0.0147 | 0.0332 +/- 0.0663 | 0.0000 +/- 0.0000 | 0.0000 +/- 0.0000 | 0.0000 +/- 0.0000 | 99.5030 +/- 76.9245 | 2383.3509 +/- 3071.3327 |
