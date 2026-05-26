# J2 Path-Dependent Baseline Table

Data root: `05_data_pipeline\processed\level4_formal_complex_j2_t6_8step_qp_9case\notch_18x14`
Train load paths: `monotonic`
Evaluation: cyclic path, 50 epochs, 5 seeds

| Model | Seeds | Cyclic disp. rel. L2 | Cyclic history rel. L2 | History-increment rel. L2 | QP history rel. L2 | QP history-inc. rel. L2 | Eqp increment rel. L2 | Plastic-work inc. rel. L2 | Reversal hist-inc. rel. L2 | Reversal yield-flag MAE | Yield-surface RMS | Plastic-work violation abs. | Plastic-work violation target-norm. | Plastic-work violation pred-norm. | FEM residual rel. RMS | FEM energy rel. err. |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| QP-thermo-hard HistoryGNO | 5 | 69.1983 +/- 31.3753 | 1.4566 +/- 0.1625 | 1.0089 +/- 0.0176 | 2.3521 +/- 0.1697 | 1.0365 +/- 0.0728 | 8.6425 +/- 4.0298 | 8.8916 +/- 4.3491 | 1.0000 +/- 0.0001 | 0.7279 +/- 0.0701 | 0.0297 +/- 0.0594 | 0.0000 +/- 0.0000 | 0.0000 +/- 0.0000 | 0.0000 +/- 0.0000 | 78.4521 +/- 42.0566 | 3866.3129 +/- 4536.4600 |
