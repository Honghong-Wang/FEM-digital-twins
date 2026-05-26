# J2 Path-Dependent Baseline Table

Data root: `05_data_pipeline\processed\level4_formal_complex_j2_t6_8step_qp_9case\notch_20x15`
Train load paths: `monotonic, unload_reload, cyclic, nonproportional`
Evaluation: cyclic path, 50 epochs, 5 seeds

| Model | Seeds | Cyclic disp. rel. L2 | Cyclic history rel. L2 | History-increment rel. L2 | QP history rel. L2 | QP history-inc. rel. L2 | Eqp increment rel. L2 | Plastic-work inc. rel. L2 | Reversal hist-inc. rel. L2 | Reversal yield-flag MAE | Yield-surface RMS | Plastic-work violation abs. | Plastic-work violation target-norm. | Plastic-work violation pred-norm. | FEM residual rel. RMS | FEM energy rel. err. |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| QP-thermo-hard HistoryGNO | 5 | 52.4938 +/- 24.4338 | 1.8634 +/- 0.0330 | 0.9999 +/- 0.0007 | 2.8102 +/- 0.0446 | 1.0008 +/- 0.0008 | 7.4764 +/- 2.3950 | 7.7675 +/- 2.6513 | 0.9972 +/- 0.0034 | 0.8215 +/- 0.0099 | 0.0000 +/- 0.0000 | 0.0000 +/- 0.0000 | 0.0000 +/- 0.0000 | 0.0000 +/- 0.0000 | 108.1374 +/- 70.7077 | 3977.0489 +/- 3795.8592 |
