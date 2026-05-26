# J2 Path-Dependent Baseline Robust Statistics

Each row reports both mean/std and robust median/IQR statistics on the cyclic primary test path.
All evaluated paths are stored in JSON: `monotonic, unload_reload, cyclic, nonproportional`.

| Model | Metric | Mean | Std | Median | Q1 | Q3 | IQR | Min | Max | N |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| True differentiable J2 QP-HistoryGNO | Cyclic disp. rel. L2 | 69.0266 | 38.2186 | 57.7992 | 38.3417 | 84.1498 | 45.8081 | 29.2792 | 135.563 | 5 |
| True differentiable J2 QP-HistoryGNO | Cyclic history rel. L2 | 1.15468 | 0.0305284 | 1.17089 | 1.15411 | 1.1749 | 0.0207866 | 1.09585 | 1.17764 | 5 |
| True differentiable J2 QP-HistoryGNO | History-increment rel. L2 | 1.0637 | 0.107737 | 1.01267 | 1.01046 | 1.0174 | 0.00694025 | 0.99912 | 1.27884 | 5 |
| True differentiable J2 QP-HistoryGNO | QP history rel. L2 | 1.92811 | 0.0354669 | 1.94659 | 1.92853 | 1.95101 | 0.0224794 | 1.85952 | 1.95493 | 5 |
| True differentiable J2 QP-HistoryGNO | QP history-inc. rel. L2 | 1.21873 | 0.322198 | 1.0789 | 1.05198 | 1.1033 | 0.0513134 | 1.00002 | 1.85947 | 5 |
| True differentiable J2 QP-HistoryGNO | QP eqp rel. L2 | 6.14333 | 1.69797 | 6.52217 | 5.27162 | 7.40022 | 2.1286 | 3.34881 | 8.17383 | 5 |
| True differentiable J2 QP-HistoryGNO | QP plastic-work rel. L2 | 6.5408 | 1.94881 | 6.86371 | 5.51459 | 8.20927 | 2.69467 | 3.35799 | 8.75844 | 5 |
| True differentiable J2 QP-HistoryGNO | QP von-Mises rel. L2 | 0.885544 | 0.036218 | 0.8857 | 0.870911 | 0.899002 | 0.0280913 | 0.830541 | 0.941563 | 5 |
| True differentiable J2 QP-HistoryGNO | QP reversal scalar-inc. rel. L2 | 1.16199 | 0.269715 | 1.0243 | 1.00817 | 1.07886 | 0.0706851 | 1.00001 | 1.69861 | 5 |
| True differentiable J2 QP-HistoryGNO | QP reversal eqp-inc. rel. L2 | 2.75256 | 0.754049 | 2.74909 | 2.46516 | 3.42377 | 0.95861 | 1.50469 | 3.62011 | 5 |
| True differentiable J2 QP-HistoryGNO | QP reversal work-inc. rel. L2 | 2.92803 | 0.849971 | 2.94459 | 2.57224 | 3.72885 | 1.1566 | 1.52728 | 3.86717 | 5 |
| True differentiable J2 QP-HistoryGNO | QP reversal yield MAE | 0.143711 | 0.039859 | 0.125786 | 0.121069 | 0.127358 | 0.00628931 | 0.121069 | 0.22327 | 5 |
| True differentiable J2 QP-HistoryGNO | QP inactive false plasticity | 0.490785 | 0.013245 | 0.497905 | 0.492254 | 0.498963 | 0.00670835 | 0.46484 | 0.499964 | 5 |
| True differentiable J2 QP-HistoryGNO | True-J2 consistency rel. RMS | 0.0366722 | 0.0461472 | 0.0191417 | 0.0110723 | 0.0249902 | 0.0139179 | 0.000649168 | 0.127507 | 5 |
| True differentiable J2 QP-HistoryGNO | True-J2 active consistency rel. RMS | 1.00523e-07 | 2.51594e-08 | 1.0545e-07 | 8.44902e-08 | 1.05581e-07 | 2.10907e-08 | 6.58667e-08 | 1.41229e-07 | 5 |
| True differentiable J2 QP-HistoryGNO | True-J2 negative dgamma | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 5 |
| True differentiable J2 QP-HistoryGNO | True-J2 active QP frac. | 0.966198 | 0.0502992 | 0.992244 | 0.97619 | 0.996032 | 0.0198413 | 0.866883 | 0.999639 | 5 |
| True differentiable J2 QP-HistoryGNO | Eqp increment rel. L2 | 7.73718 | 1.8958 | 8.15246 | 7.47366 | 8.34173 | 0.868067 | 4.43697 | 10.2811 | 5 |
| True differentiable J2 QP-HistoryGNO | Plastic-work inc. rel. L2 | 8.28963 | 2.11125 | 8.85574 | 8.07946 | 8.8922 | 0.812742 | 4.56231 | 11.0584 | 5 |
| True differentiable J2 QP-HistoryGNO | Reversal hist-inc. rel. L2 | 1.17501 | 0.307603 | 1.01185 | 1.00782 | 1.06713 | 0.0593159 | 0.999872 | 1.78837 | 5 |
| True differentiable J2 QP-HistoryGNO | Reversal yield-flag MAE | 0.45695 | 0.00204072 | 0.455988 | 0.455507 | 0.458874 | 0.00336704 | 0.454545 | 0.459836 | 5 |
| True differentiable J2 QP-HistoryGNO | Yield-surface RMS | 0.0102346 | 0.0134582 | 0.00402314 | 0.00347015 | 0.00662077 | 0.00315062 | 0.000218256 | 0.0368407 | 5 |
| True differentiable J2 QP-HistoryGNO | Plastic-work violation abs. | 3.16652e-07 | 5.90303e-07 | 1.67287e-08 | 0 | 7.0403e-08 | 7.0403e-08 | 0 | 1.49613e-06 | 5 |
| True differentiable J2 QP-HistoryGNO | Plastic-work violation target-norm. | 0.0118203 | 0.0220355 | 0.000624469 | 0 | 0.00262808 | 0.00262808 | 0 | 0.055849 | 5 |
| True differentiable J2 QP-HistoryGNO | Plastic-work violation pred-norm. | 0.00106767 | 0.0019566 | 7.61941e-05 | 0 | 0.000286936 | 0.000286936 | 0 | 0.00497524 | 5 |
| True differentiable J2 QP-HistoryGNO | FEM residual rel. RMS | 37.8912 | 12.8964 | 39.8254 | 39.5902 | 40.5399 | 0.949734 | 14.7727 | 54.7279 | 5 |
| True differentiable J2 QP-HistoryGNO | FEM energy rel. err. | 1161.82 | 666.632 | 1394.64 | 559.554 | 1749.95 | 1190.39 | 205.35 | 1899.61 | 5 |
| True differentiable J2 QP-HistoryGNO | FEM tangent-solver rel. RMS | 6.691 | 4.42382 | 4.03955 | 3.99966 | 6.2136 | 2.21394 | 3.83862 | 15.3636 | 5 |