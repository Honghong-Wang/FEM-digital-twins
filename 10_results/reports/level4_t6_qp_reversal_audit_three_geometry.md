# T6 QP-State and FEM Audit Across Three Geometries

All rows use strict monotonic-to-cyclic training/testing, 50 epochs, five seeds, T=8, T6 elements, quadrature-point plastic strain/history, and matrix-free FEM residual/energy audit. The 'reversal_final' policy audits cyclic turning points plus the final step; the 'all' policy applies the FEM loss on every rollout step during training and reports all-step audit metrics at test time. QP history columns are populated only for the QP-level HistoryGNO that explicitly predicts quadrature-point material states.

| Geometry | Model | Audit policy | Seeds | Displacement rel. L2 | History rel. L2 | QP history rel. L2 | QP history-inc. rel. L2 | Reversal hist-inc. rel. L2 | Reversal yield-flag MAE | Yield-surface RMS | Plastic-work violation target-norm. | FEM residual rel. RMS | FEM energy rel. err. |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| multi_hole | Thermo-hard HistoryGNO | reversal_final | 5 | 150.7 +/- 76.99 | 1.176 +/- 0.007134 |  |  | 1.026 +/- 0.04743 | 0.4565 +/- 0.0007703 | 0.0002104 +/- 0.0002702 | 0 +/- 0 | 138.8 +/- 52.01 | 1.681e+04 +/- 9329 |
| multi_hole | TINN-style | reversal_final | 5 | 400.8 +/- 218.2 | 0.9868 +/- 0.01489 |  |  | 1.074 +/- 0.147 | 0.5418 +/- 0.004332 | 0.001184 +/- 0.002261 | 0 +/- 0 | 812.2 +/- 368.9 | 5.082e+05 +/- 4.38e+05 |
| multi_hole | QP-thermo-hard HistoryGNO | reversal_final | 5 | 81.54 +/- 11.73 | 1.12 +/- 0.09639 | 1.874 +/- 0.129 | 1.054 +/- 0.1093 | 1.001 +/- 0.001134 | 0.4624 +/- 0.01149 | 0.02454 +/- 0.04904 | 0 +/- 0 | 81.32 +/- 54.84 | 5841 +/- 7397 |
| multi_hole | QP-thermo-hard HistoryGNO | all | 5 | 79.5 +/- 14.01 | 1.144 +/- 0.05015 | 1.905 +/- 0.07096 | 1.009 +/- 0.01868 | 1.008 +/- 0.01469 | 0.4584 +/- 0.003747 | 0.00178 +/- 0.003522 | 0 +/- 0 | 80.1 +/- 62.4 | 5080 +/- 7299 |
| notch | Thermo-hard HistoryGNO | reversal_final | 5 | 203.6 +/- 96.19 | 1.342 +/- 0.005118 |  |  | 1.005 +/- 0.006366 | 0.7167 +/- 0.0006443 | 9.301e-05 +/- 0.0001837 | 3.104e-08 +/- 6.209e-08 | 167 +/- 53.36 | 1.989e+04 +/- 8181 |
| notch | TINN-style | reversal_final | 5 | 564.4 +/- 309.4 | 0.9752 +/- 0.03925 |  |  | 0.9703 +/- 0.05938 | 0.2972 +/- 0.02848 | 0.00114 +/- 0.002277 | 0 +/- 0 | 926.8 +/- 414.1 | 5.315e+05 +/- 4.575e+05 |
| notch | QP-thermo-hard HistoryGNO | reversal_final | 5 | 105.8 +/- 27.22 | 1.334 +/- 0.005289 | 2.152 +/- 0.008477 | 1 +/- 0.0001299 | 0.9991 +/- 0.0007639 | 0.7164 +/- 0.000396 | 1.535e-05 +/- 1.081e-05 | 0 +/- 0 | 97.04 +/- 67.47 | 6745 +/- 8743 |
| notch | QP-thermo-hard HistoryGNO | all | 5 | 109.9 +/- 21.83 | 1.336 +/- 0.004893 | 2.156 +/- 0.007349 | 1 +/- 0.0001218 | 0.9994 +/- 0.0007372 | 0.7166 +/- 0.0004066 | 9.824e-06 +/- 1.036e-05 | 0 +/- 0 | 87.49 +/- 61.37 | 4705 +/- 6222 |
| curved_hole | Thermo-hard HistoryGNO | reversal_final | 5 | 152.6 +/- 81.93 | 1.123 +/- 0.007163 |  |  | 1.185 +/- 0.3129 | 0.4296 +/- 0.003232 | 0.0005596 +/- 0.000589 | 4.84e-09 +/- 9.679e-09 | 166.9 +/- 45.87 | 1.099e+04 +/- 5080 |
| curved_hole | TINN-style | reversal_final | 5 | 413 +/- 230 | 0.9821 +/- 0.02538 |  |  | 1.049 +/- 0.09729 | 0.5681 +/- 0.00223 | 0.001142 +/- 0.00228 | 0 +/- 0 | 908.1 +/- 405 | 3.164e+05 +/- 2.684e+05 |
| curved_hole | QP-thermo-hard HistoryGNO | reversal_final | 5 | 85.77 +/- 12.6 | 1.108 +/- 0.02084 | 1.784 +/- 0.02847 | 1.001 +/- 0.001473 | 1.006 +/- 0.00773 | 0.4336 +/- 0.003749 | 2.163e-05 +/- 2.271e-05 | 0 +/- 0 | 88.11 +/- 57.11 | 3352 +/- 4057 |
| curved_hole | QP-thermo-hard HistoryGNO | all | 5 | 85.32 +/- 12.48 | 1.11 +/- 0.0197 | 1.787 +/- 0.02696 | 1.001 +/- 0.00131 | 1.005 +/- 0.007275 | 0.4333 +/- 0.003537 | 2.023e-05 +/- 2.165e-05 | 0 +/- 0 | 82.29 +/- 56.83 | 2456 +/- 3162 |

## Sources

- multi_hole: `05_data_pipeline\processed\level4_formal_complex_j2_t6_8step_qp`, epochs=50, models=hgo_thermo_hard,tinn, seeds=5, train=monotonic, eval=monotonic,cyclic
- multi_hole: `05_data_pipeline\processed\level4_formal_complex_j2_t6_8step_qp`, epochs=50, models=hgo_qp_thermo_hard, seeds=5, train=monotonic, eval=monotonic,cyclic
- notch: `05_data_pipeline\processed\level4_formal_complex_j2_t6_8step_qp_notch`, epochs=50, models=hgo_thermo_hard,tinn, seeds=5, train=monotonic, eval=monotonic,cyclic
- notch: `05_data_pipeline\processed\level4_formal_complex_j2_t6_8step_qp_notch`, epochs=50, models=hgo_qp_thermo_hard, seeds=5, train=monotonic, eval=monotonic,cyclic
- curved_hole: `05_data_pipeline\processed\level4_formal_complex_j2_t6_8step_qp_curved_hole`, epochs=50, models=hgo_thermo_hard,tinn, seeds=5, train=monotonic, eval=monotonic,cyclic
- curved_hole: `05_data_pipeline\processed\level4_formal_complex_j2_t6_8step_qp_curved_hole`, epochs=50, models=hgo_qp_thermo_hard, seeds=5, train=monotonic, eval=monotonic,cyclic
