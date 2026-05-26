# J2 Path-Dependent Baseline Outlier Diagnostics

Outliers are detected on cyclic-primary metrics using a 1.5 IQR rule when IQR is nonzero, otherwise a 3 sigma rule is used.
All evaluated paths are stored in JSON: `monotonic, unload_reload, cyclic, nonproportional`.

| Model | Metric | Rule | Lower | Upper | Outlier count | Outlier seeds | Mean | Std | Median | IQR | Min | Max |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| True differentiable J2 QP-HistoryGNO | Cyclic history rel. L2 | 1.5*IQR | 1.12293 | 1.20608 | 1 | 20260518=1.09585 | 1.15468 | 0.0305284 | 1.17089 | 0.0207866 | 1.09585 | 1.17764 |
| True differentiable J2 QP-HistoryGNO | History-increment rel. L2 | 1.5*IQR | 1.00005 | 1.02781 | 2 | 20260518=1.27884; 20260521=0.99912 | 1.0637 | 0.107737 | 1.01267 | 0.00694025 | 0.99912 | 1.27884 |
| True differentiable J2 QP-HistoryGNO | QP history rel. L2 | 1.5*IQR | 1.89481 | 1.98473 | 1 | 20260518=1.85952 | 1.92811 | 0.0354669 | 1.94659 | 0.0224794 | 1.85952 | 1.95493 |
| True differentiable J2 QP-HistoryGNO | QP history-inc. rel. L2 | 1.5*IQR | 0.975014 | 1.18027 | 1 | 20260518=1.85947 | 1.21873 | 0.322198 | 1.0789 | 0.0513134 | 1.00002 | 1.85947 |
| True differentiable J2 QP-HistoryGNO | QP von-Mises rel. L2 | 1.5*IQR | 0.828774 | 0.941139 | 1 | 20260521=0.941563 | 0.885544 | 0.036218 | 0.8857 | 0.0280913 | 0.830541 | 0.941563 |
| True differentiable J2 QP-HistoryGNO | QP reversal scalar-inc. rel. L2 | 1.5*IQR | 0.902146 | 1.18489 | 1 | 20260518=1.69861 | 1.16199 | 0.269715 | 1.0243 | 0.0706851 | 1.00001 | 1.69861 |
| True differentiable J2 QP-HistoryGNO | QP reversal yield MAE | 1.5*IQR | 0.111635 | 0.136792 | 1 | 20260518=0.22327 | 0.143711 | 0.039859 | 0.125786 | 0.00628931 | 0.121069 | 0.22327 |
| True differentiable J2 QP-HistoryGNO | QP inactive false plasticity | 1.5*IQR | 0.482192 | 0.509025 | 1 | 20260518=0.46484 | 0.490785 | 0.013245 | 0.497905 | 0.00670835 | 0.46484 | 0.499964 |
| True differentiable J2 QP-HistoryGNO | True-J2 consistency rel. RMS | 1.5*IQR | -0.00980445 | 0.045867 | 1 | 20260518=0.127507 | 0.0366722 | 0.0461472 | 0.0191417 | 0.0139179 | 0.000649168 | 0.127507 |
| True differentiable J2 QP-HistoryGNO | True-J2 active consistency rel. RMS | 1.5*IQR | 5.28541e-08 | 1.37217e-07 | 1 | 20260518=1.41229e-07 | 1.00523e-07 | 2.51594e-08 | 1.0545e-07 | 2.10907e-08 | 6.58667e-08 | 1.41229e-07 |
| True differentiable J2 QP-HistoryGNO | True-J2 active QP frac. | 1.5*IQR | 0.946428 | 1.02579 | 1 | 20260518=0.866883 | 0.966198 | 0.0502992 | 0.992244 | 0.0198413 | 0.866883 | 0.999639 |
| True differentiable J2 QP-HistoryGNO | Eqp increment rel. L2 | 1.5*IQR | 6.17156 | 9.64383 | 2 | 20260517=4.43697; 20260518=10.2811 | 7.73718 | 1.8958 | 8.15246 | 0.868067 | 4.43697 | 10.2811 |
| True differentiable J2 QP-HistoryGNO | Plastic-work inc. rel. L2 | 1.5*IQR | 6.86035 | 10.1113 | 2 | 20260517=4.56231; 20260518=11.0584 | 8.28963 | 2.11125 | 8.85574 | 0.812742 | 4.56231 | 11.0584 |
| True differentiable J2 QP-HistoryGNO | Reversal hist-inc. rel. L2 | 1.5*IQR | 0.918845 | 1.15611 | 1 | 20260518=1.78837 | 1.17501 | 0.307603 | 1.01185 | 0.0593159 | 0.999872 | 1.78837 |
| True differentiable J2 QP-HistoryGNO | Yield-surface RMS | 1.5*IQR | -0.00125578 | 0.0113467 | 1 | 20260518=0.0368407 | 0.0102346 | 0.0134582 | 0.00402314 | 0.00315062 | 0.000218256 | 0.0368407 |
| True differentiable J2 QP-HistoryGNO | Plastic-work violation abs. | 1.5*IQR | -1.05604e-07 | 1.76007e-07 | 1 | 20260518=1.49613e-06 | 3.16652e-07 | 5.90303e-07 | 1.67287e-08 | 7.0403e-08 | 0 | 1.49613e-06 |
| True differentiable J2 QP-HistoryGNO | Plastic-work violation target-norm. | 1.5*IQR | -0.00394212 | 0.0065702 | 1 | 20260518=0.055849 | 0.0118203 | 0.0220355 | 0.000624469 | 0.00262808 | 0 | 0.055849 |
| True differentiable J2 QP-HistoryGNO | Plastic-work violation pred-norm. | 1.5*IQR | -0.000430404 | 0.00071734 | 1 | 20260518=0.00497524 | 0.00106767 | 0.0019566 | 7.61941e-05 | 0.000286936 | 0 | 0.00497524 |
| True differentiable J2 QP-HistoryGNO | FEM residual rel. RMS | 1.5*IQR | 38.1656 | 41.9645 | 2 | 20260517=14.7727; 20260521=54.7279 | 37.8912 | 12.8964 | 39.8254 | 0.949734 | 14.7727 | 54.7279 |
| True differentiable J2 QP-HistoryGNO | FEM tangent-solver rel. RMS | 1.5*IQR | 0.678752 | 9.5345 | 1 | 20260518=15.3636 | 6.691 | 4.42382 | 4.03955 | 2.21394 | 3.83862 | 15.3636 |