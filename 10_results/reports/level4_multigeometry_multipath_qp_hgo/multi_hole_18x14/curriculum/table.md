# J2 Path-Dependent Baseline Table

Data root: `05_data_pipeline\processed\level4_formal_complex_j2_t6_8step_qp_9case\multi_hole_18x14`
Train load paths: `monotonic, unload_reload`
Evaluation: cyclic path, 50 epochs, 5 seeds

| Model | Seeds | Cyclic disp. rel. L2 | Cyclic history rel. L2 | History-increment rel. L2 | QP history rel. L2 | QP history-inc. rel. L2 | Eqp increment rel. L2 | Plastic-work inc. rel. L2 | Reversal hist-inc. rel. L2 | Reversal yield-flag MAE | Yield-surface RMS | Plastic-work violation abs. | Plastic-work violation target-norm. | Plastic-work violation pred-norm. | FEM residual rel. RMS | FEM energy rel. err. |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| QP-thermo-hard HistoryGNO | 5 | 74.7645 +/- 34.6728 | 1.0698 +/- 0.1226 | 0.9993 +/- 0.0019 | 1.7946 +/- 0.1526 | 0.9996 +/- 0.0017 | 4.2609 +/- 1.0709 | 4.5223 +/- 1.1972 | 0.9997 +/- 0.0010 | 0.4672 +/- 0.0101 | 0.0331 +/- 0.0662 | 0.0000 +/- 0.0000 | 0.0000 +/- 0.0000 | 0.0000 +/- 0.0000 | 61.9031 +/- 52.0810 | 6085.1692 +/- 8933.3600 |
