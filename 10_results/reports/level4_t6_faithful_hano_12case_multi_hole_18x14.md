# J2 Path-Dependent Baseline Table

Data root: `05_data_pipeline\processed\level4_formal_complex_j2_t6_8step_qp_9case\multi_hole_18x14`
Train load paths: `monotonic`
Primary table: cyclic path, 50 epochs, 5 seeds
Evaluated paths stored in JSON: `monotonic, cyclic`

| Model | Seeds | Cyclic disp. rel. L2 | Cyclic history rel. L2 | History-increment rel. L2 | QP history rel. L2 | QP history-inc. rel. L2 | QP eqp rel. L2 | QP plastic-work rel. L2 | QP von-Mises rel. L2 | QP reversal scalar-inc. rel. L2 | QP reversal eqp-inc. rel. L2 | QP reversal work-inc. rel. L2 | QP reversal yield MAE | QP inactive false plasticity | True-J2 consistency rel. RMS | True-J2 active consistency rel. RMS | True-J2 negative dgamma | True-J2 active QP frac. | Eqp increment rel. L2 | Plastic-work inc. rel. L2 | Reversal hist-inc. rel. L2 | Reversal yield-flag MAE | Yield-surface RMS | Plastic-work violation abs. | Plastic-work violation target-norm. | Plastic-work violation pred-norm. | HANO strain rel. L2 | HANO stress rel. L2 | FEM residual rel. RMS | FEM energy rel. err. |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Faithful HANO strain-stress spectral-window NO | 5 | 183.5654 +/- 67.2480 | 1.7388 +/- 0.5764 | 1.0074 +/- 0.0056 |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 142.3307 +/- 96.0434 | 138.6923 +/- 122.9709 | 1.0271 +/- 0.0136 | 0.5125 +/- 0.0282 | 0.3195 +/- 0.2606 | 0.0108 +/- 0.0123 | 487.8990 +/- 554.2826 | 9.3912 +/- 11.6466 | 75.1178 +/- 41.9307 | 11.8735 +/- 3.8135 | 1342.5085 +/- 700.6833 | 1762983.4953 +/- 1845492.0148 |
