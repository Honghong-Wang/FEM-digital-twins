# J2 Path-Dependent Baseline Table

Data root: `<project-root>\05_data_pipeline\processed\j2_complex_geometry_shared_path_fem2d`
Train load paths: `monotonic`
Evaluation: cyclic path, 1 epochs, 1 seeds

| Model | Seeds | Cyclic disp. rel. L2 | Cyclic history rel. L2 | History-increment rel. L2 | Eqp increment rel. L2 | Plastic-work inc. rel. L2 | Reversal hist-inc. rel. L2 | Reversal yield-flag MAE | Yield-surface RMS | Plastic-work violation abs. | Plastic-work violation target-norm. | Plastic-work violation pred-norm. |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Non-recurrent GNO sequence | 1 | 21.2716 +/- 0.0000 | 2.0248 +/- 0.0000 | 1.0000 +/- 0.0000 | 1.0016 +/- 0.0000 | 0.9783 +/- 0.0000 | 0.9997 +/- 0.0000 | 0.0499 +/- 0.0000 | 0.0006 +/- 0.0000 | 0.0000 +/- 0.0000 | 0.0000 +/- 0.0000 | 0.0000 +/- 0.0000 |

