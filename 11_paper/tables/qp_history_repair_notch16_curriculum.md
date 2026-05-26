# J2 Path-Dependent Baseline Table

Data root: `05_data_pipeline\processed\level4_formal_complex_j2_t6_8step_qp_9case\notch_16x12`
Train load paths: `monotonic, unload_reload`
Primary table: cyclic path, 50 epochs, 5 seeds
Evaluated paths stored in JSON: `monotonic, cyclic`

| Model | Seeds | Cyclic disp. rel. L2 | Cyclic history rel. L2 | History-increment rel. L2 | QP history rel. L2 | QP history-inc. rel. L2 | QP eqp rel. L2 | QP plastic-work rel. L2 | QP von-Mises rel. L2 | Eqp increment rel. L2 | Plastic-work inc. rel. L2 | Reversal hist-inc. rel. L2 | Reversal yield-flag MAE | Yield-surface RMS | Plastic-work violation abs. | Plastic-work violation target-norm. | Plastic-work violation pred-norm. | HANO strain rel. L2 | HANO stress rel. L2 | FEM residual rel. RMS | FEM energy rel. err. |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| QP-aware thermo-hard HistoryGNO | 5 | 85.3670 +/- 18.9961 | 1.2811 +/- 0.4674 | 1.0785 +/- 0.1574 | 1.5729 +/- 0.9262 | 1.1311 +/- 0.2623 | 2.4123 +/- 2.8190 | 2.3925 +/- 2.7807 | 0.9212 +/- 0.2410 | 2.0881 +/- 2.1761 | 2.0902 +/- 2.1804 | 0.9991 +/- 0.0016 | 0.2822 +/- 0.2904 | 0.0003 +/- 0.0005 | 0.0000 +/- 0.0000 | 0.0000 +/- 0.0000 | 0.0000 +/- 0.0000 |  |  | 156.7148 +/- 90.0304 | 12045.9499 +/- 11187.5701 |
