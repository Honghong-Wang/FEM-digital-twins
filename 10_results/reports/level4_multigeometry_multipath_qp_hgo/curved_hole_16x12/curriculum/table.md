# J2 Path-Dependent Baseline Table

Data root: `05_data_pipeline\processed\level4_formal_complex_j2_t6_8step_qp_9case\curved_hole_16x12`
Train load paths: `monotonic, unload_reload`
Evaluation: cyclic path, 50 epochs, 5 seeds

| Model | Seeds | Cyclic disp. rel. L2 | Cyclic history rel. L2 | History-increment rel. L2 | QP history rel. L2 | QP history-inc. rel. L2 | Eqp increment rel. L2 | Plastic-work inc. rel. L2 | Reversal hist-inc. rel. L2 | Reversal yield-flag MAE | Yield-surface RMS | Plastic-work violation abs. | Plastic-work violation target-norm. | Plastic-work violation pred-norm. | FEM residual rel. RMS | FEM energy rel. err. |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| QP-thermo-hard HistoryGNO | 5 | 173.6054 +/- 21.4259 | 0.9738 +/- 0.1256 | 1.0264 +/- 0.0527 | 1.7769 +/- 0.1556 | 1.0594 +/- 0.1187 | 5.8903 +/- 1.0268 | 6.1277 +/- 1.0833 | 1.0000 +/- 0.0001 | 0.4440 +/- 0.0249 | 0.0663 +/- 0.0835 | 0.0000 +/- 0.0000 | 0.0000 +/- 0.0000 | 0.0000 +/- 0.0000 | 162.0390 +/- 144.5739 | 17832.8723 +/- 27607.9539 |
