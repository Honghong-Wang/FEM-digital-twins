# J2 Path-Dependent Baseline Table

Data root: `05_data_pipeline\processed\level4_formal_complex_j2_t6_8step_qp_9case\curved_hole_20x15`
Train load paths: `monotonic, unload_reload, cyclic, nonproportional`
Evaluation: cyclic path, 50 epochs, 5 seeds

| Model | Seeds | Cyclic disp. rel. L2 | Cyclic history rel. L2 | History-increment rel. L2 | QP history rel. L2 | QP history-inc. rel. L2 | Eqp increment rel. L2 | Plastic-work inc. rel. L2 | Reversal hist-inc. rel. L2 | Reversal yield-flag MAE | Yield-surface RMS | Plastic-work violation abs. | Plastic-work violation target-norm. | Plastic-work violation pred-norm. | FEM residual rel. RMS | FEM energy rel. err. |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| QP-thermo-hard HistoryGNO | 5 | 14.3062 +/- 5.6989 | 1.0571 +/- 0.0003 | 1.0001 +/- 0.0000 | 1.8155 +/- 0.0003 | 1.0002 +/- 0.0000 | 5.8420 +/- 1.3025 | 6.3228 +/- 1.5553 | 1.0001 +/- 0.0000 | 0.4392 +/- 0.0000 | 0.0000 +/- 0.0000 | 0.0000 +/- 0.0000 | 0.0000 +/- 0.0000 | 0.0000 +/- 0.0000 | 36.5676 +/- 17.4761 | 1308.0792 +/- 1085.1827 |
