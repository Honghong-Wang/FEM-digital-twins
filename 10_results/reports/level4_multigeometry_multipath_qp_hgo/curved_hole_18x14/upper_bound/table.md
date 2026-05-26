# J2 Path-Dependent Baseline Table

Data root: `05_data_pipeline\processed\level4_formal_complex_j2_t6_8step_qp_9case\curved_hole_18x14`
Train load paths: `monotonic, unload_reload, cyclic, nonproportional`
Evaluation: cyclic path, 50 epochs, 5 seeds

| Model | Seeds | Cyclic disp. rel. L2 | Cyclic history rel. L2 | History-increment rel. L2 | QP history rel. L2 | QP history-inc. rel. L2 | Eqp increment rel. L2 | Plastic-work inc. rel. L2 | Reversal hist-inc. rel. L2 | Reversal yield-flag MAE | Yield-surface RMS | Plastic-work violation abs. | Plastic-work violation target-norm. | Plastic-work violation pred-norm. | FEM residual rel. RMS | FEM energy rel. err. |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| QP-thermo-hard HistoryGNO | 5 | 14.3718 +/- 4.4272 | 1.3607 +/- 0.0170 | 0.9997 +/- 0.0008 | 2.0713 +/- 0.0214 | 1.0000 +/- 0.0003 | 7.6534 +/- 1.6721 | 8.5368 +/- 2.0805 | 1.0020 +/- 0.0040 | 0.5552 +/- 0.0001 | 0.0000 +/- 0.0000 | 0.0000 +/- 0.0000 | 0.0000 +/- 0.0000 | 0.0000 +/- 0.0000 | 52.1584 +/- 30.1753 | 605.6471 +/- 553.0246 |
