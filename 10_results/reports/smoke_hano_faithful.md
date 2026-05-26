# J2 Path-Dependent Baseline Table

Data root: `05_data_pipeline\processed\level4_formal_complex_j2_t6_8step_qp_9case\multi_hole_14x11`
Train load paths: `monotonic`
Evaluation: cyclic path, 1 epochs, 1 seeds

| Model | Seeds | Cyclic disp. rel. L2 | Cyclic history rel. L2 | History-increment rel. L2 | QP history rel. L2 | QP history-inc. rel. L2 | Eqp increment rel. L2 | Plastic-work inc. rel. L2 | Reversal hist-inc. rel. L2 | Reversal yield-flag MAE | Yield-surface RMS | Plastic-work violation abs. | Plastic-work violation target-norm. | Plastic-work violation pred-norm. | FEM residual rel. RMS | FEM energy rel. err. |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Faithful HANO strain-stress window NO | 1 | 5071.0088 +/- 0.0000 | 7.7325 +/- 0.0000 | 2.5537 +/- 0.0000 |  |  | 188.7820 +/- 0.0000 | 34391.1719 +/- 0.0000 | 4.6796 +/- 0.0000 | 0.5077 +/- 0.0000 | 0.3832 +/- 0.0000 | 0.0000 +/- 0.0000 | 0.0000 +/- 0.0000 | 0.0000 +/- 0.0000 |  |  |
| HANO-style window NO | 1 | 17487.8203 +/- 0.0000 | 7.9240 +/- 0.0000 | 1.6544 +/- 0.0000 |  |  | 402.1375 +/- 0.0000 | 18988.4199 +/- 0.0000 | 2.7584 +/- 0.0000 | 0.5247 +/- 0.0000 | 0.1196 +/- 0.0000 | 0.0000 +/- 0.0000 | 0.0000 +/- 0.0000 | 0.0000 +/- 0.0000 |  |  |
