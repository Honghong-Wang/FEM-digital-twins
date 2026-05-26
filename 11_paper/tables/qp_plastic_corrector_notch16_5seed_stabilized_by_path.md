# J2 Path-Dependent Baseline Pathwise Table

Data root: `05_data_pipeline\processed\level4_formal_complex_j2_t6_8step_qp_9case\notch_16x12`
Train load paths: `monotonic, cyclic`
Evaluated paths: `monotonic, cyclic`
Protocol: 50 epochs, 5 seeds

| Model | Load path | Seeds | Disp. rel. L2 | History rel. L2 | History-increment rel. L2 | QP history rel. L2 | QP history-inc. rel. L2 | QP eqp rel. L2 | QP plastic-work rel. L2 | QP von-Mises rel. L2 | Eqp increment rel. L2 | Plastic-work inc. rel. L2 | Reversal hist-inc. rel. L2 | Reversal yield-flag MAE | Yield-surface RMS | Plastic-work violation abs. | Plastic-work violation target-norm. | Plastic-work violation pred-norm. | HANO strain rel. L2 | HANO stress rel. L2 | FEM residual rel. RMS | FEM energy rel. err. |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| QP plastic-memory corrector HistoryGNO | monotonic | 5 | 100.3015 +/- 51.8846 | 1.7955 +/- 0.6822 | 0.9989 +/- 0.0024 | 2.5281 +/- 1.2742 | 0.9995 +/- 0.0019 | 2.6086 +/- 2.0249 | 2.5938 +/- 2.0146 | 1.1773 +/- 0.0079 | 2.7470 +/- 2.2456 | 2.7399 +/- 2.2474 | 0.0000 +/- 0.0000 | 0.0000 +/- 0.0000 | 0.0001 +/- 0.0001 | 0.0000 +/- 0.0000 | 0.0000 +/- 0.0000 | 0.0000 +/- 0.0000 |  |  | 101.6927 +/- 50.2264 | 83.6405 +/- 89.8184 |
| QP plastic-memory corrector HistoryGNO | cyclic | 5 | 94.2642 +/- 48.6529 | 1.5760 +/- 0.5051 | 0.9996 +/- 0.0006 | 2.2135 +/- 1.0204 | 0.9997 +/- 0.0005 | 1.2266 +/- 0.3855 | 1.2113 +/- 0.3629 | 1.1876 +/- 0.0088 | 1.2898 +/- 0.4796 | 1.2727 +/- 0.4561 | 1.0022 +/- 0.0042 | 0.5341 +/- 0.3128 | 0.0001 +/- 0.0001 | 0.0000 +/- 0.0000 | 0.0000 +/- 0.0000 | 0.0000 +/- 0.0000 |  |  | 105.8701 +/- 52.3500 | 6747.6192 +/- 5476.2130 |