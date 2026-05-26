# J2 Path-Dependent Baseline Table

Data root: `05_data_pipeline\processed\level4_formal_complex_j2_t6_8step_qp_9case\notch_14x11`
Train load paths: `monotonic, unload_reload`
Evaluation: cyclic path, 50 epochs, 5 seeds

| Model | Seeds | Cyclic disp. rel. L2 | Cyclic history rel. L2 | History-increment rel. L2 | QP history rel. L2 | QP history-inc. rel. L2 | Eqp increment rel. L2 | Plastic-work inc. rel. L2 | Reversal hist-inc. rel. L2 | Reversal yield-flag MAE | Yield-surface RMS | Plastic-work violation abs. | Plastic-work violation target-norm. | Plastic-work violation pred-norm. | FEM residual rel. RMS | FEM energy rel. err. |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| QP-thermo-hard HistoryGNO | 5 | 56.8803 +/- 20.3258 | 1.4285 +/- 0.0018 | 1.0000 +/- 0.0001 | 2.2994 +/- 0.0028 | 1.0001 +/- 0.0001 | 7.2660 +/- 3.6194 | 7.6318 +/- 4.1384 | 0.9999 +/- 0.0003 | 0.7307 +/- 0.0002 | 0.0000 +/- 0.0000 | 0.0000 +/- 0.0000 | 0.0000 +/- 0.0000 | 0.0000 +/- 0.0000 | 72.1164 +/- 59.3445 | 4535.4390 +/- 5455.8318 |
