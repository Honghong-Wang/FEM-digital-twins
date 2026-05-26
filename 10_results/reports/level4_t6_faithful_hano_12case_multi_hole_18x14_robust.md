# J2 Path-Dependent Baseline Robust Statistics

Each row reports both mean/std and robust median/IQR statistics on the cyclic primary test path.
All evaluated paths are stored in JSON: `monotonic, cyclic`.

| Model | Metric | Mean | Std | Median | Q1 | Q3 | IQR | Min | Max | N |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Faithful HANO strain-stress spectral-window NO | Cyclic disp. rel. L2 | 183.565 | 67.248 | 169.053 | 149.175 | 178.132 | 28.957 | 111.455 | 310.012 | 5 |
| Faithful HANO strain-stress spectral-window NO | Cyclic history rel. L2 | 1.7388 | 0.576428 | 1.82659 | 1.36428 | 1.89366 | 0.529384 | 0.944299 | 2.66517 | 5 |
| Faithful HANO strain-stress spectral-window NO | History-increment rel. L2 | 1.00738 | 0.00557085 | 1.00566 | 1.00563 | 1.01017 | 0.00454009 | 0.999309 | 1.01611 | 5 |
| Faithful HANO strain-stress spectral-window NO | Eqp increment rel. L2 | 142.331 | 96.0434 | 94.7347 | 82.9402 | 211.47 | 128.53 | 29.2834 | 293.225 | 5 |
| Faithful HANO strain-stress spectral-window NO | Plastic-work inc. rel. L2 | 138.692 | 122.971 | 102.035 | 26.2648 | 188.073 | 161.808 | 23.8989 | 353.191 | 5 |
| Faithful HANO strain-stress spectral-window NO | Reversal hist-inc. rel. L2 | 1.02707 | 0.013636 | 1.02394 | 1.02389 | 1.03533 | 0.0114391 | 1.0056 | 1.04658 | 5 |
| Faithful HANO strain-stress spectral-window NO | Reversal yield-flag MAE | 0.512488 | 0.028156 | 0.53243 | 0.485663 | 0.535259 | 0.0495961 | 0.471363 | 0.537723 | 5 |
| Faithful HANO strain-stress spectral-window NO | Yield-surface RMS | 0.319509 | 0.260581 | 0.242173 | 0.188223 | 0.373274 | 0.185051 | 0.00872749 | 0.785149 | 5 |
| Faithful HANO strain-stress spectral-window NO | Plastic-work violation abs. | 0.0107954 | 0.0122642 | 0.00419992 | 0 | 0.0186338 | 0.0186338 | 0 | 0.0311431 | 5 |
| Faithful HANO strain-stress spectral-window NO | Plastic-work violation target-norm. | 487.899 | 554.283 | 189.816 | 0 | 842.159 | 842.159 | 0 | 1407.52 | 5 |
| Faithful HANO strain-stress spectral-window NO | Plastic-work violation pred-norm. | 9.39115 | 11.6466 | 7.46973 | 0 | 7.83062 | 7.83062 | 0 | 31.6554 | 5 |
| Faithful HANO strain-stress spectral-window NO | HANO strain rel. L2 | 75.1178 | 41.9307 | 61.7229 | 56.9574 | 110.612 | 53.6541 | 13.928 | 132.369 | 5 |
| Faithful HANO strain-stress spectral-window NO | HANO stress rel. L2 | 11.8735 | 3.81352 | 10.5208 | 9.22942 | 12.0486 | 2.81922 | 8.46634 | 19.1022 | 5 |
| Faithful HANO strain-stress spectral-window NO | FEM residual rel. RMS | 1342.51 | 700.683 | 1489.89 | 856.89 | 1545.66 | 688.771 | 373.989 | 2446.11 | 5 |
| Faithful HANO strain-stress spectral-window NO | FEM energy rel. err. | 1.76298e+06 | 1.84549e+06 | 1.27627e+06 | 578389 | 1.57665e+06 | 998263 | 81351 | 5.30226e+06 | 5 |