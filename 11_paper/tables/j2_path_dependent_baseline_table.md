# J2 Path-Dependent Baseline Table

Data root: `05_data_pipeline\processed\j2_complex_geometry_shared_path_fem2d`
Train load paths: `monotonic`
Evaluation: cyclic path, 50 epochs, 10 seeds

| Model | Seeds | Cyclic disp. rel. L2 | Cyclic history rel. L2 | History-increment rel. L2 | QP history rel. L2 | QP history-inc. rel. L2 | Eqp increment rel. L2 | Plastic-work inc. rel. L2 | Reversal hist-inc. rel. L2 | Reversal yield-flag MAE | Yield-surface RMS | Plastic-work violation abs. | Plastic-work violation target-norm. | Plastic-work violation pred-norm. | FEM residual rel. RMS | FEM energy rel. err. |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| HistoryGNO thermo-aware | 10 | 1.0340 +/- 0.4259 | 1.0895 +/- 0.0730 | 1.0153 +/- 0.0021 |  |  | 2.0019 +/- 0.3693 | 3.8762 +/- 0.5770 | 1.0206 +/- 0.0041 | 0.6970 +/- 0.0428 | 0.5705 +/- 0.0402 | 0.0393 +/- 0.0294 | 3.2706 +/- 2.4507 | 0.8543 +/- 0.7153 |  |  |
| HistoryGNO data-only | 10 | 0.8854 +/- 0.0384 | 1.2493 +/- 0.1299 | 1.0211 +/- 0.0040 |  |  | 2.2964 +/- 0.5268 | 6.5916 +/- 1.0891 | 1.0264 +/- 0.0040 | 0.6972 +/- 0.0243 | 0.5899 +/- 0.0362 | 0.0432 +/- 0.0351 | 3.5923 +/- 2.9225 | 0.5120 +/- 0.4134 |  |  |
| Non-recurrent GNO sequence | 10 | 1.0124 +/- 0.4212 | 0.8394 +/- 0.0214 | 1.0004 +/- 0.0005 |  |  | 0.9999 +/- 0.0008 | 1.0000 +/- 0.0001 | 1.0018 +/- 0.0024 | 0.7008 +/- 0.0130 | 0.4126 +/- 0.2868 | 0.0000 +/- 0.0000 | 0.0005 +/- 0.0010 | 455.8454 +/- 1364.0826 |  |  |
| Static FNO sequence | 10 | 0.7267 +/- 0.0325 | 0.8152 +/- 0.0139 | 1.0003 +/- 0.0002 |  |  | 1.0001 +/- 0.0005 | 1.0001 +/- 0.0002 | 1.0011 +/- 0.0011 | 0.6876 +/- 0.0199 | 0.1978 +/- 0.1515 | 0.0000 +/- 0.0000 | 0.0005 +/- 0.0005 | 3.4821 +/- 7.5776 |  |  |
| Static DeepONet sequence | 10 | 0.7214 +/- 0.0463 | 0.8244 +/- 0.0111 | 1.0004 +/- 0.0004 |  |  | 1.0000 +/- 0.0008 | 1.0001 +/- 0.0002 | 1.0020 +/- 0.0020 | 0.6993 +/- 0.0090 | 0.2083 +/- 0.1897 | 0.0000 +/- 0.0000 | 0.0008 +/- 0.0011 | 3.8639 +/- 7.5058 |  |  |
