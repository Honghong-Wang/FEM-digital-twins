# J2 Path-Dependent Baseline Table

Data root: `05_data_pipeline\processed\level4_formal_complex_j2_t6_8step_qp_notch`
Train load paths: `monotonic`
Evaluation: cyclic path, 50 epochs, 5 seeds

| Model | Seeds | Cyclic disp. rel. L2 | Cyclic history rel. L2 | History-increment rel. L2 | Eqp increment rel. L2 | Plastic-work inc. rel. L2 | Reversal hist-inc. rel. L2 | Reversal yield-flag MAE | Yield-surface RMS | Plastic-work violation abs. | Plastic-work violation target-norm. | Plastic-work violation pred-norm. | FEM residual rel. RMS | FEM energy rel. err. |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Thermo-hard HistoryGNO | 5 | 203.5652 +/- 96.1860 | 1.3423 +/- 0.0051 | 1.0090 +/- 0.0152 | 25.7029 +/- 4.2513 | 32.5663 +/- 7.2795 | 1.0052 +/- 0.0064 | 0.7167 +/- 0.0006 | 0.0001 +/- 0.0002 | 0.0000 +/- 0.0000 | 0.0000 +/- 0.0000 | 0.0000 +/- 0.0000 | 167.0235 +/- 53.3558 | 19887.8443 +/- 8181.2198 |
| Thermo-projected neural CDE | 5 | 564.4248 +/- 309.4469 | 0.9752 +/- 0.0392 | 1.0016 +/- 0.0032 | 1.0000 +/- 0.0000 | 1.0000 +/- 0.0000 | 0.9703 +/- 0.0594 | 0.2972 +/- 0.0285 | 0.0011 +/- 0.0023 | 0.0000 +/- 0.0000 | 0.0000 +/- 0.0000 | 0.0000 +/- 0.0000 | 926.8170 +/- 414.1118 | 531457.2719 +/- 457512.8841 |
