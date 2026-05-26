# J2 Path-Dependent Baseline Table

Data root: `<project-root>\05_data_pipeline\processed\j2_complex_geometry_shared_path_fem2d`
Train load paths: `monotonic`
Evaluation: cyclic path, 1 epochs, 1 seeds

| Model | Seeds | Cyclic disp. rel. L2 | Cyclic history rel. L2 | History-increment rel. L2 | Eqp increment rel. L2 | Plastic-work inc. rel. L2 | Reversal hist-inc. rel. L2 | Reversal yield-flag MAE | Yield-surface RMS | Plastic-work violation |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| HistoryGNO thermo-aware | 1 | 6.4401 +/- 0.0000 | 6.2629 +/- 0.0000 | 1.5243 +/- 0.0000 | 17.9437 +/- 0.0000 | 39.4974 +/- 0.0000 | 1.4016 +/- 0.0000 | 0.5710 +/- 0.0000 | 0.5211 +/- 0.0000 | 7.7029 +/- 0.0000 |
| HistoryGNO data-only | 1 | 6.4027 +/- 0.0000 | 6.5282 +/- 0.0000 | 1.5683 +/- 0.0000 | 18.7090 +/- 0.0000 | 42.1080 +/- 0.0000 | 1.4368 +/- 0.0000 | 0.5946 +/- 0.0000 | 0.5493 +/- 0.0000 | 7.8282 +/- 0.0000 |
| Non-recurrent GNO sequence | 1 | 21.2716 +/- 0.0000 | 2.0248 +/- 0.0000 | 1.0000 +/- 0.0000 | 1.0016 +/- 0.0000 | 0.9783 +/- 0.0000 | 0.9997 +/- 0.0000 | 0.0499 +/- 0.0000 | 0.0006 +/- 0.0000 | 0.0000 +/- 0.0000 |
| Static FNO sequence | 1 | 1.6312 +/- 0.0000 | 15.7924 +/- 0.0000 | 0.9995 +/- 0.0000 | 0.9493 +/- 0.0000 | 0.9755 +/- 0.0000 | 0.9982 +/- 0.0000 | 0.3672 +/- 0.0000 | 0.3438 +/- 0.0000 | 52.9254 +/- 0.0000 |
| Static DeepONet sequence | 1 | 3.8218 +/- 0.0000 | 3.8701 +/- 0.0000 | 1.0001 +/- 0.0000 | 1.0221 +/- 0.0000 | 1.0002 +/- 0.0000 | 1.0000 +/- 0.0000 | 0.9499 +/- 0.0000 | 0.9933 +/- 0.0000 | 0.7899 +/- 0.0000 |

