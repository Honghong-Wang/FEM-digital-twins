# J2 Path-Dependent Baseline Table

Data root: `05_data_pipeline\processed\level4_formal_complex_j2_t6_8step_qp_9case\multi_hole_20x15`
Train load paths: `monotonic`
Evaluation: cyclic path, 1 epochs, 1 seeds

| Model | Seeds | Cyclic disp. rel. L2 | Cyclic history rel. L2 | History-increment rel. L2 | QP history rel. L2 | QP history-inc. rel. L2 | Eqp increment rel. L2 | Plastic-work inc. rel. L2 | Reversal hist-inc. rel. L2 | Reversal yield-flag MAE | Yield-surface RMS | Plastic-work violation abs. | Plastic-work violation target-norm. | Plastic-work violation pred-norm. | FEM residual rel. RMS | FEM energy rel. err. |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| QP-thermo-hard HistoryGNO | 1 | 1882.2649 +/- 0.0000 | 1.6712 +/- 0.0000 | 1.0014 +/- 0.0000 | 2.5628 +/- 0.0000 | 1.0028 +/- 0.0000 | 66.0142 +/- 0.0000 | 104.4540 +/- 0.0000 | 1.0012 +/- 0.0000 | 0.7658 +/- 0.0000 | 0.0000 +/- 0.0000 | 0.0000 +/- 0.0000 | 0.0000 +/- 0.0000 | 0.0000 +/- 0.0000 | 454.8113 +/- 0.0000 | 114608.9766 +/- 0.0000 |
