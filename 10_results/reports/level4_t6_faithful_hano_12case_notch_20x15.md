# J2 Path-Dependent Baseline Table

Data root: `05_data_pipeline\processed\level4_formal_complex_j2_t6_8step_qp_9case\notch_20x15`
Train load paths: `monotonic`
Primary table: cyclic path, 50 epochs, 5 seeds
Evaluated paths stored in JSON: `monotonic, cyclic`

| Model | Seeds | Cyclic disp. rel. L2 | Cyclic history rel. L2 | History-increment rel. L2 | QP history rel. L2 | QP history-inc. rel. L2 | QP eqp rel. L2 | QP plastic-work rel. L2 | QP von-Mises rel. L2 | QP reversal scalar-inc. rel. L2 | QP reversal eqp-inc. rel. L2 | QP reversal work-inc. rel. L2 | QP reversal yield MAE | QP inactive false plasticity | True-J2 consistency rel. RMS | True-J2 active consistency rel. RMS | True-J2 negative dgamma | True-J2 active QP frac. | Eqp increment rel. L2 | Plastic-work inc. rel. L2 | Reversal hist-inc. rel. L2 | Reversal yield-flag MAE | Yield-surface RMS | Plastic-work violation abs. | Plastic-work violation target-norm. | Plastic-work violation pred-norm. | HANO strain rel. L2 | HANO stress rel. L2 | FEM residual rel. RMS | FEM energy rel. err. |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Faithful HANO strain-stress spectral-window NO | 5 | 265.1116 +/- 119.4525 | 2.6680 +/- 1.1786 | 1.0088 +/- 0.0064 |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 118.0354 +/- 57.4252 | 28.6826 +/- 28.3890 | 1.0050 +/- 0.0051 | 0.4124 +/- 0.2409 | 0.4080 +/- 0.2811 | 0.0026 +/- 0.0019 | 212.4731 +/- 154.0566 | 31.5070 +/- 37.8855 | 64.2865 +/- 52.0628 | 16.5750 +/- 3.0445 | 2095.9836 +/- 1971.8975 | 1815958.4656 +/- 2784597.4756 |
