# J2 Path-Dependent Baseline Table

Data root: `05_data_pipeline\processed\level4_formal_complex_j2_t6_8step\multi_hole_14x11`
Train load paths: `monotonic`
Evaluation: cyclic path, 50 epochs, 5 seeds

| Model | Seeds | Cyclic disp. rel. L2 | Cyclic history rel. L2 | History-increment rel. L2 | Eqp increment rel. L2 | Plastic-work inc. rel. L2 | Reversal hist-inc. rel. L2 | Reversal yield-flag MAE | Yield-surface RMS | Plastic-work violation abs. | Plastic-work violation target-norm. | Plastic-work violation pred-norm. | FEM residual rel. RMS | FEM energy rel. err. |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Thermo-hard HistoryGNO | 5 | 151.4017 +/- 77.9615 | 1.1773 +/- 0.0067 | 1.0115 +/- 0.0214 | 20.0561 +/- 5.7472 | 26.0592 +/- 9.0132 | 1.0041 +/- 0.0072 | 0.4563 +/- 0.0006 | 0.0001 +/- 0.0002 | 0.0000 +/- 0.0000 | 0.0000 +/- 0.0000 | 0.0000 +/- 0.0000 | 209.6849 +/- 69.9212 | 13883.7313 +/- 7383.4875 |
| Thermo-projected neural CDE | 5 | 400.6478 +/- 218.3618 | 0.9868 +/- 0.0149 | 1.0325 +/- 0.0650 | 1.0000 +/- 0.0000 | 1.0000 +/- 0.0000 | 1.0736 +/- 0.1470 | 0.5418 +/- 0.0043 | 0.0012 +/- 0.0023 | 0.0000 +/- 0.0000 | 0.0000 +/- 0.0000 | 0.0000 +/- 0.0000 | 1197.3263 +/- 524.4367 | 411835.2250 +/- 355216.5656 |
