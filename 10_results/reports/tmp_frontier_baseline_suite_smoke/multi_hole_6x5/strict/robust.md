# J2 Path-Dependent Baseline Robust Statistics

Each row reports both mean/std and robust median/IQR statistics on the cyclic primary test path.
All evaluated paths are stored in JSON: `monotonic, cyclic`.

| Model | Metric | Mean | Std | Median | Q1 | Q3 | IQR | Min | Max | N |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Faithful HANO strain-stress spectral-window NO | Cyclic disp. rel. L2 | 2366.08 | 0 | 2366.08 | 2366.08 | 2366.08 | 0 | 2366.08 | 2366.08 | 1 |
| Faithful HANO strain-stress spectral-window NO | Cyclic history rel. L2 | 3.54078 | 0 | 3.54078 | 3.54078 | 3.54078 | 0 | 3.54078 | 3.54078 | 1 |
| Faithful HANO strain-stress spectral-window NO | History-increment rel. L2 | 1.29567 | 0 | 1.29567 | 1.29567 | 1.29567 | 0 | 1.29567 | 1.29567 | 1 |
| Faithful HANO strain-stress spectral-window NO | Eqp increment rel. L2 | 287.748 | 0 | 287.748 | 287.748 | 287.748 | 0 | 287.748 | 287.748 | 1 |
| Faithful HANO strain-stress spectral-window NO | Plastic-work inc. rel. L2 | 8131.12 | 0 | 8131.12 | 8131.12 | 8131.12 | 0 | 8131.12 | 8131.12 | 1 |
| Faithful HANO strain-stress spectral-window NO | Reversal hist-inc. rel. L2 | 1.19813 | 0 | 1.19813 | 1.19813 | 1.19813 | 0 | 1.19813 | 1.19813 | 1 |
| Faithful HANO strain-stress spectral-window NO | Reversal yield-flag MAE | 0.448232 | 0 | 0.448232 | 0.448232 | 0.448232 | 0 | 0.448232 | 0.448232 | 1 |
| Faithful HANO strain-stress spectral-window NO | Yield-surface RMS | 0.0511347 | 0 | 0.0511347 | 0.0511347 | 0.0511347 | 0 | 0.0511347 | 0.0511347 | 1 |
| Faithful HANO strain-stress spectral-window NO | Plastic-work violation abs. | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| Faithful HANO strain-stress spectral-window NO | Plastic-work violation target-norm. | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| Faithful HANO strain-stress spectral-window NO | Plastic-work violation pred-norm. | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| Faithful HANO strain-stress spectral-window NO | HANO strain rel. L2 | 54.7561 | 0 | 54.7561 | 54.7561 | 54.7561 | 0 | 54.7561 | 54.7561 | 1 |
| Faithful HANO strain-stress spectral-window NO | HANO stress rel. L2 | 2.35422 | 0 | 2.35422 | 2.35422 | 2.35422 | 0 | 2.35422 | 2.35422 | 1 |
| Faithful HANO strain-stress spectral-window NO | FEM residual rel. RMS | 242.557 | 0 | 242.557 | 242.557 | 242.557 | 0 | 242.557 | 242.557 | 1 |
| Faithful HANO strain-stress spectral-window NO | FEM energy rel. err. | 186376 | 0 | 186376 | 186376 | 186376 | 0 | 186376 | 186376 | 1 |
| Faithful HANO strain-stress spectral-window NO | FEM tangent-solver rel. RMS | 242.557 | 0 | 242.557 | 242.557 | 242.557 | 0 | 242.557 | 242.557 | 1 |
| INCDE-style Euler neural CDE | Cyclic disp. rel. L2 | 4301.85 | 0 | 4301.85 | 4301.85 | 4301.85 | 0 | 4301.85 | 4301.85 | 1 |
| INCDE-style Euler neural CDE | Cyclic history rel. L2 | 17.3827 | 0 | 17.3827 | 17.3827 | 17.3827 | 0 | 17.3827 | 17.3827 | 1 |
| INCDE-style Euler neural CDE | History-increment rel. L2 | 6.40908 | 0 | 6.40908 | 6.40908 | 6.40908 | 0 | 6.40908 | 6.40908 | 1 |
| INCDE-style Euler neural CDE | Eqp increment rel. L2 | 2118.6 | 0 | 2118.6 | 2118.6 | 2118.6 | 0 | 2118.6 | 2118.6 | 1 |
| INCDE-style Euler neural CDE | Plastic-work inc. rel. L2 | 62787.1 | 0 | 62787.1 | 62787.1 | 62787.1 | 0 | 62787.1 | 62787.1 | 1 |
| INCDE-style Euler neural CDE | Reversal hist-inc. rel. L2 | 5.38382 | 0 | 5.38382 | 5.38382 | 5.38382 | 0 | 5.38382 | 5.38382 | 1 |
| INCDE-style Euler neural CDE | Reversal yield-flag MAE | 0.548601 | 0 | 0.548601 | 0.548601 | 0.548601 | 0 | 0.548601 | 0.548601 | 1 |
| INCDE-style Euler neural CDE | Yield-surface RMS | 0.850425 | 0 | 0.850425 | 0.850425 | 0.850425 | 0 | 0.850425 | 0.850425 | 1 |
| INCDE-style Euler neural CDE | Plastic-work violation abs. | 0.940961 | 0 | 0.940961 | 0.940961 | 0.940961 | 0 | 0.940961 | 0.940961 | 1 |
| INCDE-style Euler neural CDE | Plastic-work violation target-norm. | 14524.1 | 0 | 14524.1 | 14524.1 | 14524.1 | 0 | 14524.1 | 14524.1 | 1 |
| INCDE-style Euler neural CDE | Plastic-work violation pred-norm. | 0.231321 | 0 | 0.231321 | 0.231321 | 0.231321 | 0 | 0.231321 | 0.231321 | 1 |
| INCDE-style Euler neural CDE | FEM residual rel. RMS | 121.009 | 0 | 121.009 | 121.009 | 121.009 | 0 | 121.009 | 121.009 | 1 |
| INCDE-style Euler neural CDE | FEM energy rel. err. | 3.3283e+06 | 0 | 3.3283e+06 | 3.3283e+06 | 3.3283e+06 | 0 | 3.3283e+06 | 3.3283e+06 | 1 |
| INCDE-style Euler neural CDE | FEM tangent-solver rel. RMS | 121.009 | 0 | 121.009 | 121.009 | 121.009 | 0 | 121.009 | 121.009 | 1 |
| TINN-style thermo-projected neural CDE | Cyclic disp. rel. L2 | 4301.85 | 0 | 4301.85 | 4301.85 | 4301.85 | 0 | 4301.85 | 4301.85 | 1 |
| TINN-style thermo-projected neural CDE | Cyclic history rel. L2 | 1.17405 | 0 | 1.17405 | 1.17405 | 1.17405 | 0 | 1.17405 | 1.17405 | 1 |
| TINN-style thermo-projected neural CDE | History-increment rel. L2 | 1.00006 | 0 | 1.00006 | 1.00006 | 1.00006 | 0 | 1.00006 | 1.00006 | 1 |
| TINN-style thermo-projected neural CDE | Eqp increment rel. L2 | 2.10878 | 0 | 2.10878 | 2.10878 | 2.10878 | 0 | 2.10878 | 2.10878 | 1 |
| TINN-style thermo-projected neural CDE | Plastic-work inc. rel. L2 | 2.12048 | 0 | 2.12048 | 2.12048 | 2.12048 | 0 | 2.12048 | 2.12048 | 1 |
| TINN-style thermo-projected neural CDE | Reversal hist-inc. rel. L2 | 1.00003 | 0 | 1.00003 | 1.00003 | 1.00003 | 0 | 1.00003 | 1.00003 | 1 |
| TINN-style thermo-projected neural CDE | Reversal yield-flag MAE | 0.558824 | 0 | 0.558824 | 0.558824 | 0.558824 | 0 | 0.558824 | 0.558824 | 1 |
| TINN-style thermo-projected neural CDE | Yield-surface RMS | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| TINN-style thermo-projected neural CDE | Plastic-work violation abs. | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| TINN-style thermo-projected neural CDE | Plastic-work violation target-norm. | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| TINN-style thermo-projected neural CDE | Plastic-work violation pred-norm. | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| TINN-style thermo-projected neural CDE | FEM residual rel. RMS | 121.007 | 0 | 121.007 | 121.007 | 121.007 | 0 | 121.007 | 121.007 | 1 |
| TINN-style thermo-projected neural CDE | FEM energy rel. err. | 51625.3 | 0 | 51625.3 | 51625.3 | 51625.3 | 0 | 51625.3 | 51625.3 | 1 |
| TINN-style thermo-projected neural CDE | FEM tangent-solver rel. RMS | 121.007 | 0 | 121.007 | 121.007 | 121.007 | 0 | 121.007 | 121.007 | 1 |
| Non-recurrent GNO sequence | Cyclic disp. rel. L2 | 308.379 | 0 | 308.379 | 308.379 | 308.379 | 0 | 308.379 | 308.379 | 1 |
| Non-recurrent GNO sequence | Cyclic history rel. L2 | 4.69941 | 0 | 4.69941 | 4.69941 | 4.69941 | 0 | 4.69941 | 4.69941 | 1 |
| Non-recurrent GNO sequence | History-increment rel. L2 | 0.999325 | 0 | 0.999325 | 0.999325 | 0.999325 | 0 | 0.999325 | 0.999325 | 1 |
| Non-recurrent GNO sequence | Eqp increment rel. L2 | 0.96711 | 0 | 0.96711 | 0.96711 | 0.96711 | 0 | 0.96711 | 0.96711 | 1 |
| Non-recurrent GNO sequence | Plastic-work inc. rel. L2 | 41.3479 | 0 | 41.3479 | 41.3479 | 41.3479 | 0 | 41.3479 | 41.3479 | 1 |
| Non-recurrent GNO sequence | Reversal hist-inc. rel. L2 | 0.999343 | 0 | 0.999343 | 0.999343 | 0.999343 | 0 | 0.999343 | 0.999343 | 1 |
| Non-recurrent GNO sequence | Reversal yield-flag MAE | 0.529957 | 0 | 0.529957 | 0.529957 | 0.529957 | 0 | 0.529957 | 0.529957 | 1 |
| Non-recurrent GNO sequence | Yield-surface RMS | 0.714497 | 0 | 0.714497 | 0.714497 | 0.714497 | 0 | 0.714497 | 0.714497 | 1 |
| Non-recurrent GNO sequence | Plastic-work violation abs. | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| Non-recurrent GNO sequence | Plastic-work violation target-norm. | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| Non-recurrent GNO sequence | Plastic-work violation pred-norm. | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| Non-recurrent GNO sequence | FEM residual rel. RMS | 604.21 | 0 | 604.21 | 604.21 | 604.21 | 0 | 604.21 | 604.21 | 1 |
| Non-recurrent GNO sequence | FEM energy rel. err. | 277253 | 0 | 277253 | 277253 | 277253 | 0 | 277253 | 277253 | 1 |
| Non-recurrent GNO sequence | FEM tangent-solver rel. RMS | 604.21 | 0 | 604.21 | 604.21 | 604.21 | 0 | 604.21 | 604.21 | 1 |
| Static FNO sequence | Cyclic disp. rel. L2 | 429.217 | 0 | 429.217 | 429.217 | 429.217 | 0 | 429.217 | 429.217 | 1 |
| Static FNO sequence | Cyclic history rel. L2 | 6.54639 | 0 | 6.54639 | 6.54639 | 6.54639 | 0 | 6.54639 | 6.54639 | 1 |
| Static FNO sequence | History-increment rel. L2 | 0.999939 | 0 | 0.999939 | 0.999939 | 0.999939 | 0 | 0.999939 | 0.999939 | 1 |
| Static FNO sequence | Eqp increment rel. L2 | 3.5628 | 0 | 3.5628 | 3.5628 | 3.5628 | 0 | 3.5628 | 3.5628 | 1 |
| Static FNO sequence | Plastic-work inc. rel. L2 | 1.17307 | 0 | 1.17307 | 1.17307 | 1.17307 | 0 | 1.17307 | 1.17307 | 1 |
| Static FNO sequence | Reversal hist-inc. rel. L2 | 0.999957 | 0 | 0.999957 | 0.999957 | 0.999957 | 0 | 0.999957 | 0.999957 | 1 |
| Static FNO sequence | Reversal yield-flag MAE | 0.558696 | 0 | 0.558696 | 0.558696 | 0.558696 | 0 | 0.558696 | 0.558696 | 1 |
| Static FNO sequence | Yield-surface RMS | 0.654415 | 0 | 0.654415 | 0.654415 | 0.654415 | 0 | 0.654415 | 0.654415 | 1 |
| Static FNO sequence | Plastic-work violation abs. | 2.86299e-05 | 0 | 2.86299e-05 | 2.86299e-05 | 2.86299e-05 | 0 | 2.86299e-05 | 2.86299e-05 | 1 |
| Static FNO sequence | Plastic-work violation target-norm. | 0.441913 | 0 | 0.441913 | 0.441913 | 0.441913 | 0 | 0.441913 | 0.441913 | 1 |
| Static FNO sequence | Plastic-work violation pred-norm. | 0.598455 | 0 | 0.598455 | 0.598455 | 0.598455 | 0 | 0.598455 | 0.598455 | 1 |
| Static FNO sequence | FEM residual rel. RMS | 17.1742 | 0 | 17.1742 | 17.1742 | 17.1742 | 0 | 17.1742 | 17.1742 | 1 |
| Static FNO sequence | FEM energy rel. err. | 2.29097e+06 | 0 | 2.29097e+06 | 2.29097e+06 | 2.29097e+06 | 0 | 2.29097e+06 | 2.29097e+06 | 1 |
| Static FNO sequence | FEM tangent-solver rel. RMS | 17.1742 | 0 | 17.1742 | 17.1742 | 17.1742 | 0 | 17.1742 | 17.1742 | 1 |
| Static DeepONet sequence | Cyclic disp. rel. L2 | 160.06 | 0 | 160.06 | 160.06 | 160.06 | 0 | 160.06 | 160.06 | 1 |
| Static DeepONet sequence | Cyclic history rel. L2 | 3.31674 | 0 | 3.31674 | 3.31674 | 3.31674 | 0 | 3.31674 | 3.31674 | 1 |
| Static DeepONet sequence | History-increment rel. L2 | 1.00033 | 0 | 1.00033 | 1.00033 | 1.00033 | 0 | 1.00033 | 1.00033 | 1 |
| Static DeepONet sequence | Eqp increment rel. L2 | 0.956932 | 0 | 0.956932 | 0.956932 | 0.956932 | 0 | 0.956932 | 0.956932 | 1 |
| Static DeepONet sequence | Plastic-work inc. rel. L2 | 17.8782 | 0 | 17.8782 | 17.8782 | 17.8782 | 0 | 17.8782 | 17.8782 | 1 |
| Static DeepONet sequence | Reversal hist-inc. rel. L2 | 1.00031 | 0 | 1.00031 | 1.00031 | 1.00031 | 0 | 1.00031 | 1.00031 | 1 |
| Static DeepONet sequence | Reversal yield-flag MAE | 0.49605 | 0 | 0.49605 | 0.49605 | 0.49605 | 0 | 0.49605 | 0.49605 | 1 |
| Static DeepONet sequence | Yield-surface RMS | 0.4094 | 0 | 0.4094 | 0.4094 | 0.4094 | 0 | 0.4094 | 0.4094 | 1 |
| Static DeepONet sequence | Plastic-work violation abs. | 0.00234198 | 0 | 0.00234198 | 0.00234198 | 0.00234198 | 0 | 0.00234198 | 0.00234198 | 1 |
| Static DeepONet sequence | Plastic-work violation target-norm. | 36.1494 | 0 | 36.1494 | 36.1494 | 36.1494 | 0 | 36.1494 | 36.1494 | 1 |
| Static DeepONet sequence | Plastic-work violation pred-norm. | 2.0773 | 0 | 2.0773 | 2.0773 | 2.0773 | 0 | 2.0773 | 2.0773 | 1 |
| Static DeepONet sequence | FEM residual rel. RMS | 19820.1 | 0 | 19820.1 | 19820.1 | 19820.1 | 0 | 19820.1 | 19820.1 | 1 |
| Static DeepONet sequence | FEM energy rel. err. | 1.73192e+08 | 0 | 1.73192e+08 | 1.73192e+08 | 1.73192e+08 | 0 | 1.73192e+08 | 1.73192e+08 | 1 |
| Static DeepONet sequence | FEM tangent-solver rel. RMS | 19820.1 | 0 | 19820.1 | 19820.1 | 19820.1 | 0 | 19820.1 | 19820.1 | 1 |