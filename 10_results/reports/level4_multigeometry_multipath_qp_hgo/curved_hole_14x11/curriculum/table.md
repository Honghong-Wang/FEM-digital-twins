# J2 Path-Dependent Baseline Table

Data root: `05_data_pipeline\processed\level4_formal_complex_j2_t6_8step_qp_9case\curved_hole_14x11`
Train load paths: `monotonic, unload_reload`
Evaluation: cyclic path, 50 epochs, 5 seeds

| Model | Seeds | Cyclic disp. rel. L2 | Cyclic history rel. L2 | History-increment rel. L2 | QP history rel. L2 | QP history-inc. rel. L2 | Eqp increment rel. L2 | Plastic-work inc. rel. L2 | Reversal hist-inc. rel. L2 | Reversal yield-flag MAE | Yield-surface RMS | Plastic-work violation abs. | Plastic-work violation target-norm. | Plastic-work violation pred-norm. | FEM residual rel. RMS | FEM energy rel. err. |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| QP-thermo-hard HistoryGNO | 5 | 63.9489 +/- 15.6025 | 1.0701 +/- 0.0093 | 0.9987 +/- 0.0019 | 1.7585 +/- 0.0132 | 0.9993 +/- 0.0014 | 4.1773 +/- 1.1016 | 4.3943 +/- 1.2485 | 1.0016 +/- 0.0022 | 0.4106 +/- 0.0016 | 0.0000 +/- 0.0000 | 0.0000 +/- 0.0000 | 0.0000 +/- 0.0000 | 0.0000 +/- 0.0000 | 123.1268 +/- 91.9342 | 7508.3774 +/- 9799.5863 |
