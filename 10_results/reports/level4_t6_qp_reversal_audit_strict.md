# J2 Path-Dependent Baseline Table

Data root: `05_data_pipeline\processed\level4_formal_complex_j2_t6_8step_qp`
Train load paths: `monotonic`
Evaluation: cyclic path, 50 epochs, 5 seeds

| Model | Seeds | Cyclic disp. rel. L2 | Cyclic history rel. L2 | History-increment rel. L2 | Eqp increment rel. L2 | Plastic-work inc. rel. L2 | Reversal hist-inc. rel. L2 | Reversal yield-flag MAE | Yield-surface RMS | Plastic-work violation abs. | Plastic-work violation target-norm. | Plastic-work violation pred-norm. | FEM residual rel. RMS | FEM energy rel. err. |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Thermo-hard HistoryGNO | 5 | 150.6879 +/- 76.9912 | 1.1764 +/- 0.0071 | 1.0176 +/- 0.0220 | 20.2897 +/- 5.3243 | 26.4338 +/- 8.3667 | 1.0256 +/- 0.0474 | 0.4565 +/- 0.0008 | 0.0002 +/- 0.0003 | 0.0000 +/- 0.0000 | 0.0000 +/- 0.0000 | 0.0000 +/- 0.0000 | 138.8322 +/- 52.0064 | 16809.3213 +/- 9329.4612 |
| Thermo-projected neural CDE | 5 | 400.7928 +/- 218.2051 | 0.9868 +/- 0.0149 | 1.0325 +/- 0.0650 | 1.0000 +/- 0.0000 | 1.0000 +/- 0.0000 | 1.0736 +/- 0.1470 | 0.5418 +/- 0.0043 | 0.0012 +/- 0.0023 | 0.0000 +/- 0.0000 | 0.0000 +/- 0.0000 | 0.0000 +/- 0.0000 | 812.1843 +/- 368.9296 | 508240.9688 +/- 437991.7931 |
