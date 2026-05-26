# J2 Path-Dependent Baseline Pathwise Table

Data root: `05_data_pipeline\processed\level4_formal_complex_j2_t6_8step_qp_9case\notch_16x12`
Train load paths: `monotonic, cyclic`
Evaluated paths: `monotonic, cyclic`
Protocol: 50 epochs, 5 seeds

| Model | Load path | Seeds | Disp. rel. L2 | History rel. L2 | History-increment rel. L2 | QP history rel. L2 | QP history-inc. rel. L2 | QP eqp rel. L2 | QP plastic-work rel. L2 | QP von-Mises rel. L2 | Eqp increment rel. L2 | Plastic-work inc. rel. L2 | Reversal hist-inc. rel. L2 | Reversal yield-flag MAE | Yield-surface RMS | Plastic-work violation abs. | Plastic-work violation target-norm. | Plastic-work violation pred-norm. | HANO strain rel. L2 | HANO stress rel. L2 | FEM residual rel. RMS | FEM energy rel. err. |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| QP-aware active-zone thermo-hard HistoryGNO | monotonic | 5 | 102.1997 +/- 50.0586 | 1.3523 +/- 0.6341 | 1.0919 +/- 0.1828 | 1.6584 +/- 1.1653 | 1.1657 +/- 0.3296 | 5.4919 +/- 8.9799 | 5.5695 +/- 9.1352 | 0.9433 +/- 0.2243 | 4.1257 +/- 6.2514 | 4.2364 +/- 6.4727 | 0.0000 +/- 0.0000 | 0.0000 +/- 0.0000 | 0.0010 +/- 0.0021 | 0.0000 +/- 0.0000 | 0.0000 +/- 0.0000 | 0.0000 +/- 0.0000 |  |  | 79.7724 +/- 24.8627 | 60.1594 +/- 37.2905 |
| QP-aware active-zone thermo-hard HistoryGNO | cyclic | 5 | 95.8955 +/- 46.8229 | 1.2471 +/- 0.4787 | 1.0269 +/- 0.0537 | 1.5141 +/- 0.9406 | 1.0452 +/- 0.0903 | 2.1699 +/- 2.3422 | 2.1463 +/- 2.2948 | 0.9393 +/- 0.2317 | 1.8099 +/- 1.6198 | 1.8091 +/- 1.6182 | 0.9887 +/- 0.0223 | 0.2860 +/- 0.2887 | 0.0010 +/- 0.0021 | 0.0000 +/- 0.0000 | 0.0000 +/- 0.0000 | 0.0000 +/- 0.0000 |  |  | 83.0567 +/- 25.8953 | 3079.0710 +/- 1980.7672 |