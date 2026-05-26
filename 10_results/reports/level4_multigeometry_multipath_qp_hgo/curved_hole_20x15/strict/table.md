# J2 Path-Dependent Baseline Table

Data root: `05_data_pipeline\processed\level4_formal_complex_j2_t6_8step_qp_9case\curved_hole_20x15`
Train load paths: `monotonic`
Evaluation: cyclic path, 50 epochs, 5 seeds

| Model | Seeds | Cyclic disp. rel. L2 | Cyclic history rel. L2 | History-increment rel. L2 | QP history rel. L2 | QP history-inc. rel. L2 | Eqp increment rel. L2 | Plastic-work inc. rel. L2 | Reversal hist-inc. rel. L2 | Reversal yield-flag MAE | Yield-surface RMS | Plastic-work violation abs. | Plastic-work violation target-norm. | Plastic-work violation pred-norm. | FEM residual rel. RMS | FEM energy rel. err. |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| QP-thermo-hard HistoryGNO | 5 | 49.8719 +/- 22.8537 | 0.9571 +/- 0.1234 | 1.0134 +/- 0.0267 | 1.7057 +/- 0.1456 | 1.0462 +/- 0.0923 | 5.1161 +/- 1.5997 | 5.5332 +/- 1.8217 | 1.0002 +/- 0.0004 | 0.4555 +/- 0.0198 | 0.0590 +/- 0.0759 | 0.0000 +/- 0.0000 | 0.0000 +/- 0.0000 | 0.0000 +/- 0.0000 | 53.7843 +/- 26.3031 | 2307.8691 +/- 1767.4378 |
