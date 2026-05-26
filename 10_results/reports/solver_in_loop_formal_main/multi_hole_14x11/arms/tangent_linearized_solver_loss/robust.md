# J2 Path-Dependent Baseline Robust Statistics

Each row reports both mean/std and robust median/IQR statistics on the cyclic primary test path.
All evaluated paths are stored in JSON: `monotonic, unload_reload, cyclic, nonproportional`.

| Model | Metric | Mean | Std | Median | Q1 | Q3 | IQR | Min | Max | N |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| True differentiable J2 QP-HistoryGNO | Cyclic disp. rel. L2 | 56.1233 | 25.5955 | 48.0976 | 34.0872 | 77.2867 | 43.1994 | 27.12 | 94.0252 | 5 |
| True differentiable J2 QP-HistoryGNO | Cyclic history rel. L2 | 1.04656 | 0.0459232 | 1.04063 | 1.00638 | 1.06316 | 0.0567763 | 0.997356 | 1.12529 | 5 |
| True differentiable J2 QP-HistoryGNO | History-increment rel. L2 | 1.21169 | 0.121627 | 1.24613 | 1.16358 | 1.31455 | 0.150967 | 0.999906 | 1.3343 | 5 |
| True differentiable J2 QP-HistoryGNO | QP history rel. L2 | 1.53729 | 0.299327 | 1.63817 | 1.48077 | 1.69689 | 0.216118 | 0.994671 | 1.87597 | 5 |
| True differentiable J2 QP-HistoryGNO | QP history-inc. rel. L2 | 1.60816 | 0.335741 | 1.73021 | 1.5239 | 1.82707 | 0.303172 | 0.999831 | 1.95977 | 5 |
| True differentiable J2 QP-HistoryGNO | QP eqp rel. L2 | 1.86699 | 0.985304 | 1.47138 | 1.21499 | 1.90562 | 0.690636 | 1 | 3.74298 | 5 |
| True differentiable J2 QP-HistoryGNO | QP plastic-work rel. L2 | 1.88754 | 1.03743 | 1.4549 | 1.21251 | 1.89513 | 0.682617 | 1 | 3.87517 | 5 |
| True differentiable J2 QP-HistoryGNO | QP von-Mises rel. L2 | 0.759066 | 0.063681 | 0.740262 | 0.717489 | 0.818099 | 0.10061 | 0.673983 | 0.845496 | 5 |
| True differentiable J2 QP-HistoryGNO | QP reversal scalar-inc. rel. L2 | 1.53767 | 0.302182 | 1.64466 | 1.4315 | 1.78794 | 0.356442 | 1 | 1.82425 | 5 |
| True differentiable J2 QP-HistoryGNO | QP reversal eqp-inc. rel. L2 | 1.2993 | 0.530078 | 1 | 0.967066 | 1.23094 | 0.263875 | 0.958104 | 2.34039 | 5 |
| True differentiable J2 QP-HistoryGNO | QP reversal work-inc. rel. L2 | 1.30843 | 0.559008 | 1 | 0.966363 | 1.20401 | 0.237645 | 0.959786 | 2.41199 | 5 |
| True differentiable J2 QP-HistoryGNO | QP reversal yield MAE | 0.525157 | 0.215674 | 0.422956 | 0.393082 | 0.65566 | 0.262579 | 0.275157 | 0.878931 | 5 |
| True differentiable J2 QP-HistoryGNO | QP inactive false plasticity | 0.311896 | 0.164416 | 0.376098 | 0.307417 | 0.406789 | 0.0993721 | 0 | 0.469176 | 5 |
| True differentiable J2 QP-HistoryGNO | True-J2 consistency rel. RMS | 0.352311 | 0.273511 | 0.277405 | 0.187204 | 0.319134 | 0.13193 | 0.0998333 | 0.877978 | 5 |
| True differentiable J2 QP-HistoryGNO | True-J2 active consistency rel. RMS | 4.29479e-08 | 2.49029e-08 | 5.05207e-08 | 3.71702e-08 | 5.09006e-08 | 1.37304e-08 | 0 | 7.61483e-08 | 5 |
| True differentiable J2 QP-HistoryGNO | True-J2 negative dgamma | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 5 |
| True differentiable J2 QP-HistoryGNO | True-J2 active QP frac. | 0.497294 | 0.298455 | 0.586039 | 0.36057 | 0.663059 | 0.302489 | 0 | 0.876804 | 5 |
| True differentiable J2 QP-HistoryGNO | Eqp increment rel. L2 | 2.37523 | 1.37714 | 2.16404 | 1.37004 | 2.41045 | 1.04041 | 1 | 4.93161 | 5 |
| True differentiable J2 QP-HistoryGNO | Plastic-work inc. rel. L2 | 2.41325 | 1.49177 | 2.1108 | 1.35742 | 2.37025 | 1.01283 | 1 | 5.22776 | 5 |
| True differentiable J2 QP-HistoryGNO | Reversal hist-inc. rel. L2 | 1.67341 | 0.451645 | 1.6078 | 1.44136 | 2.0229 | 0.581544 | 1.00009 | 2.29491 | 5 |
| True differentiable J2 QP-HistoryGNO | Reversal yield-flag MAE | 0.527658 | 0.046714 | 0.532468 | 0.493026 | 0.544012 | 0.050986 | 0.466089 | 0.602694 | 5 |
| True differentiable J2 QP-HistoryGNO | Yield-surface RMS | 0.0336942 | 0.0179147 | 0.04325 | 0.0307161 | 0.0463733 | 0.0156572 | 0 | 0.0481315 | 5 |
| True differentiable J2 QP-HistoryGNO | Plastic-work violation abs. | 4.29881e-08 | 3.46262e-08 | 6.67933e-08 | 1.40724e-09 | 7.17729e-08 | 7.03657e-08 | 0 | 7.49672e-08 | 5 |
| True differentiable J2 QP-HistoryGNO | Plastic-work violation target-norm. | 0.00160471 | 0.00129256 | 0.00249333 | 5.25311e-05 | 0.00267922 | 0.00262669 | 0 | 0.00279846 | 5 |
| True differentiable J2 QP-HistoryGNO | Plastic-work violation pred-norm. | 0.00057773 | 0.000507088 | 0.000525494 | 5.04324e-05 | 0.00112879 | 0.00107836 | 0 | 0.00118393 | 5 |
| True differentiable J2 QP-HistoryGNO | FEM residual rel. RMS | 12.8537 | 8.56018 | 10.1326 | 9.40779 | 17.7437 | 8.33592 | 0.796099 | 26.1881 | 5 |
| True differentiable J2 QP-HistoryGNO | FEM energy rel. err. | 157.812 | 180.03 | 84.9322 | 57.0014 | 122.117 | 65.1158 | 14.1268 | 510.884 | 5 |
| True differentiable J2 QP-HistoryGNO | FEM tangent-solver rel. RMS | 3.33039 | 1.62511 | 3.40337 | 2.38831 | 5.03124 | 2.64293 | 0.784578 | 5.04447 | 5 |