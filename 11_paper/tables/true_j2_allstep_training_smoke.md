# J2 Path-Dependent Baseline Table

Data root: `05_data_pipeline\processed\level4_formal_complex_j2_t6_8step_qp_9case\notch_16x12`
Train load paths: `monotonic`
Primary table: cyclic path, 1 epochs, 1 seeds
Evaluated paths stored in JSON: `monotonic, cyclic`

| Model | Seeds | Cyclic disp. rel. L2 | Cyclic history rel. L2 | History-increment rel. L2 | QP history rel. L2 | QP history-inc. rel. L2 | QP eqp rel. L2 | QP plastic-work rel. L2 | QP von-Mises rel. L2 | QP reversal scalar-inc. rel. L2 | QP reversal eqp-inc. rel. L2 | QP reversal work-inc. rel. L2 | QP reversal yield MAE | QP inactive false plasticity | True-J2 consistency rel. RMS | True-J2 active consistency rel. RMS | True-J2 negative dgamma | True-J2 active QP frac. | Eqp increment rel. L2 | Plastic-work inc. rel. L2 | Reversal hist-inc. rel. L2 | Reversal yield-flag MAE | Yield-surface RMS | Plastic-work violation abs. | Plastic-work violation target-norm. | Plastic-work violation pred-norm. | HANO strain rel. L2 | HANO stress rel. L2 | FEM residual rel. RMS | FEM energy rel. err. |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| True differentiable J2 QP-HistoryGNO | 1 | 298.5912 +/- 0.0000 | 2.2350 +/- 0.0000 | 1.0193 +/- 0.0000 | 3.4365 +/- 0.0000 | 1.0840 +/- 0.0000 | 125.9845 +/- 0.0000 | 261.2411 +/- 0.0000 | 2.8587 +/- 0.0000 | 1.0036 +/- 0.0000 | 68.9724 +/- 0.0000 | 152.6754 +/- 0.0000 | 0.5806 +/- 0.0000 | 0.4985 +/- 0.0000 | 0.0563 +/- 0.0000 | 0.0000 +/- 0.0000 | 0.0000 +/- 0.0000 | 0.9899 +/- 0.0000 | 175.9751 +/- 0.0000 | 348.5417 +/- 0.0000 | 1.0189 +/- 0.0000 | 0.8613 +/- 0.0000 | 0.0104 +/- 0.0000 | 0.0000 +/- 0.0000 | 3.0481 +/- 0.0000 | 0.0087 +/- 0.0000 |  |  | 812.8113 +/- 0.0000 | 353010.0938 +/- 0.0000 |
