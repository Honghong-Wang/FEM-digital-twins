# J2 Path-Dependent Baseline Table

Data root: `05_data_pipeline\processed\level4_formal_complex_j2_t6_8step_qp_9case\multi_hole_16x12`
Train load paths: `monotonic, unload_reload, cyclic, nonproportional`
Evaluation: cyclic path, 50 epochs, 5 seeds

| Model | Seeds | Cyclic disp. rel. L2 | Cyclic history rel. L2 | History-increment rel. L2 | QP history rel. L2 | QP history-inc. rel. L2 | Eqp increment rel. L2 | Plastic-work inc. rel. L2 | Reversal hist-inc. rel. L2 | Reversal yield-flag MAE | Yield-surface RMS | Plastic-work violation abs. | Plastic-work violation target-norm. | Plastic-work violation pred-norm. | FEM residual rel. RMS | FEM energy rel. err. |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| QP-thermo-hard HistoryGNO | 5 | 14.9071 +/- 5.4469 | 0.8762 +/- 0.0686 | 1.0166 +/- 0.0249 | 1.5498 +/- 0.1092 | 1.0435 +/- 0.0542 | 4.5182 +/- 0.3179 | 4.9271 +/- 0.3210 | 1.0396 +/- 0.0557 | 0.3995 +/- 0.0400 | 0.0139 +/- 0.0202 | 0.0000 +/- 0.0000 | 0.0000 +/- 0.0000 | 0.0000 +/- 0.0000 | 38.9359 +/- 6.1395 | 1035.4238 +/- 331.4397 |
