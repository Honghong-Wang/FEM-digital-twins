# J2 Path-Dependent Baseline Table

Data root: `05_data_pipeline\processed\level4_formal_complex_j2_t6_8step_qp_9case\multi_hole_14x11`
Train load paths: `monotonic, unload_reload`
Evaluation: cyclic path, 50 epochs, 5 seeds

| Model | Seeds | Cyclic disp. rel. L2 | Cyclic history rel. L2 | History-increment rel. L2 | QP history rel. L2 | QP history-inc. rel. L2 | Eqp increment rel. L2 | Plastic-work inc. rel. L2 | Reversal hist-inc. rel. L2 | Reversal yield-flag MAE | Yield-surface RMS | Plastic-work violation abs. | Plastic-work violation target-norm. | Plastic-work violation pred-norm. | FEM residual rel. RMS | FEM energy rel. err. |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| QP-thermo-hard HistoryGNO | 5 | 78.2967 +/- 14.5629 | 1.1721 +/- 0.0069 | 0.9995 +/- 0.0008 | 1.9463 +/- 0.0105 | 0.9998 +/- 0.0007 | 3.0048 +/- 0.6866 | 3.0480 +/- 0.7273 | 1.0001 +/- 0.0002 | 0.4563 +/- 0.0005 | 0.0000 +/- 0.0000 | 0.0000 +/- 0.0000 | 0.0000 +/- 0.0000 | 0.0000 +/- 0.0000 | 75.1436 +/- 54.1345 | 4356.6103 +/- 5910.9069 |
