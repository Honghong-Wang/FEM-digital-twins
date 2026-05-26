# J2 Path-Dependent Baseline Table

Data root: `05_data_pipeline\processed\level4_formal_complex_j2_t6_8step_qp_9case\multi_hole_20x15`
Train load paths: `monotonic`
Evaluation: cyclic path, 1 epochs, 1 seeds

| Model | Seeds | Cyclic disp. rel. L2 | Cyclic history rel. L2 | History-increment rel. L2 | QP history rel. L2 | QP history-inc. rel. L2 | Eqp increment rel. L2 | Plastic-work inc. rel. L2 | Reversal hist-inc. rel. L2 | Reversal yield-flag MAE | Yield-surface RMS | Plastic-work violation abs. | Plastic-work violation target-norm. | Plastic-work violation pred-norm. | FEM residual rel. RMS | FEM energy rel. err. |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| QP-thermo-hard HistoryGNO | 1 | 1228.9926 +/- 0.0000 | 1.6748 +/- 0.0000 | 1.0017 +/- 0.0000 | 2.5675 +/- 0.0000 | 1.0036 +/- 0.0000 | 77.0724 +/- 0.0000 | 129.7828 +/- 0.0000 | 1.0016 +/- 0.0000 | 0.7658 +/- 0.0000 | 0.0000 +/- 0.0000 | 0.0000 +/- 0.0000 | 0.0000 +/- 0.0000 | 0.0000 +/- 0.0000 | 336.0186 +/- 0.0000 | 40555.0977 +/- 0.0000 |
