# J2 Path-Dependent Baseline Table

Data root: `05_data_pipeline\processed\level4_formal_complex_j2_t6_8step_qp_9case\multi_hole_18x14`
Train load paths: `monotonic`
Primary table: cyclic path, 50 epochs, 5 seeds
Evaluated paths stored in JSON: `monotonic, cyclic, nonproportional`

| Model | Seeds | Cyclic disp. rel. L2 | Cyclic history rel. L2 | History-increment rel. L2 | QP history rel. L2 | QP history-inc. rel. L2 | Eqp increment rel. L2 | Plastic-work inc. rel. L2 | Reversal hist-inc. rel. L2 | Reversal yield-flag MAE | Yield-surface RMS | Plastic-work violation abs. | Plastic-work violation target-norm. | Plastic-work violation pred-norm. | HANO strain rel. L2 | HANO stress rel. L2 | FEM residual rel. RMS | FEM energy rel. err. |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| QP-thermo-hard HistoryGNO | 5 | 76.0234 +/- 34.7837 | 1.0711 +/- 0.1233 | 0.9996 +/- 0.0011 | 1.7966 +/- 0.1535 | 0.9998 +/- 0.0010 | 4.4811 +/- 1.1239 | 4.7858 +/- 1.2510 | 1.0000 +/- 0.0003 | 0.4669 +/- 0.0102 | 0.0334 +/- 0.0668 | 0.0000 +/- 0.0000 | 0.0000 +/- 0.0000 | 0.0000 +/- 0.0000 |  |  | 61.5074 +/- 50.8689 | 5773.6369 +/- 8295.0429 |
| Faithful HANO strain-stress spectral-window NO | 5 | 183.5656 +/- 67.2480 | 1.7388 +/- 0.5764 | 1.0074 +/- 0.0056 |  |  | 142.3307 +/- 96.0434 | 138.6923 +/- 122.9709 | 1.0271 +/- 0.0136 | 0.5125 +/- 0.0282 | 0.3195 +/- 0.2606 | 0.0108 +/- 0.0123 | 487.8991 +/- 554.2826 | 9.3912 +/- 11.6466 | 75.1160 +/- 41.9306 | 11.8735 +/- 3.8135 | 700.2654 +/- 309.1091 | 612648.4277 +/- 650730.0508 |
| HANO-style window NO | 5 | 172.3619 +/- 16.4208 | 1.2688 +/- 0.4682 | 1.0043 +/- 0.0045 |  |  | 179.2533 +/- 109.5397 | 148.6188 +/- 56.9797 | 1.0241 +/- 0.0190 | 0.5240 +/- 0.0133 | 0.1249 +/- 0.0999 | 0.0159 +/- 0.0144 | 716.8290 +/- 650.2678 | 6.2042 +/- 6.0191 |  |  | 333.8762 +/- 184.3054 | 100249.1746 +/- 112056.4347 |
| INCDE-style Euler neural CDE | 5 | 197.4466 +/- 71.8527 | 0.7745 +/- 0.0068 | 1.0102 +/- 0.0041 |  |  | 13.4501 +/- 9.8380 | 181.9491 +/- 122.6433 | 1.0517 +/- 0.0152 | 0.5013 +/- 0.0019 | 0.1263 +/- 0.0420 | 0.0000 +/- 0.0000 | 0.0000 +/- 0.0000 | 0.0000 +/- 0.0000 |  |  | 213.5406 +/- 89.3815 | 43161.7881 +/- 29779.4598 |
| TINN-style thermo-projected neural CDE | 5 | 197.4083 +/- 71.7982 | 0.9999 +/- 0.0000 | 1.0000 +/- 0.0000 |  |  | 1.0000 +/- 0.0000 | 1.0000 +/- 0.0000 | 1.0000 +/- 0.0000 | 0.5383 +/- 0.0000 | 0.0000 +/- 0.0000 | 0.0000 +/- 0.0000 | 0.0000 +/- 0.0000 | 0.0000 +/- 0.0000 |  |  | 213.5589 +/- 89.3508 | 43158.4254 +/- 29775.4335 |
