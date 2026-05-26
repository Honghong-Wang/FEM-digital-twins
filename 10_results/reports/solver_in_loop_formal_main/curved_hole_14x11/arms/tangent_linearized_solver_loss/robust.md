# J2 Path-Dependent Baseline Robust Statistics

Each row reports both mean/std and robust median/IQR statistics on the cyclic primary test path.
All evaluated paths are stored in JSON: `monotonic, unload_reload, cyclic, nonproportional`.

| Model | Metric | Mean | Std | Median | Q1 | Q3 | IQR | Min | Max | N |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| True differentiable J2 QP-HistoryGNO | Cyclic disp. rel. L2 | 80.4647 | 28.4636 | 73.2846 | 65.8984 | 82.3551 | 16.4567 | 48.0461 | 132.739 | 5 |
| True differentiable J2 QP-HistoryGNO | Cyclic history rel. L2 | 0.994161 | 0.0281712 | 0.9878 | 0.984375 | 1.01293 | 0.0285506 | 0.951161 | 1.03454 | 5 |
| True differentiable J2 QP-HistoryGNO | History-increment rel. L2 | 1.25103 | 0.13029 | 1.19541 | 1.1704 | 1.3872 | 0.216799 | 1.08264 | 1.41951 | 5 |
| True differentiable J2 QP-HistoryGNO | QP history rel. L2 | 1.41212 | 0.25851 | 1.37901 | 1.22915 | 1.6856 | 0.456457 | 1.04942 | 1.71743 | 5 |
| True differentiable J2 QP-HistoryGNO | QP history-inc. rel. L2 | 1.59537 | 0.258555 | 1.5981 | 1.48319 | 1.85221 | 0.369023 | 1.1718 | 1.87157 | 5 |
| True differentiable J2 QP-HistoryGNO | QP eqp rel. L2 | 2.05846 | 1.1299 | 1.34718 | 1.11045 | 3.16472 | 2.05427 | 0.992956 | 3.67697 | 5 |
| True differentiable J2 QP-HistoryGNO | QP plastic-work rel. L2 | 2.08779 | 1.16451 | 1.35654 | 1.10732 | 3.21859 | 2.11127 | 0.993162 | 3.76332 | 5 |
| True differentiable J2 QP-HistoryGNO | QP von-Mises rel. L2 | 0.698744 | 0.0735656 | 0.67143 | 0.641368 | 0.778208 | 0.13684 | 0.609997 | 0.792716 | 5 |
| True differentiable J2 QP-HistoryGNO | QP reversal scalar-inc. rel. L2 | 1.53082 | 0.247571 | 1.49902 | 1.45925 | 1.67332 | 0.214069 | 1.13759 | 1.88492 | 5 |
| True differentiable J2 QP-HistoryGNO | QP reversal eqp-inc. rel. L2 | 1.19054 | 0.147213 | 1.26029 | 1.03679 | 1.28313 | 0.246337 | 0.997498 | 1.37498 | 5 |
| True differentiable J2 QP-HistoryGNO | QP reversal work-inc. rel. L2 | 1.20422 | 0.162471 | 1.26181 | 1.03424 | 1.30812 | 0.273883 | 0.997583 | 1.41935 | 5 |
| True differentiable J2 QP-HistoryGNO | QP reversal yield MAE | 0.524177 | 0.299461 | 0.69814 | 0.170243 | 0.723891 | 0.553648 | 0.158798 | 0.869814 | 5 |
| True differentiable J2 QP-HistoryGNO | QP inactive false plasticity | 0.318541 | 0.139237 | 0.307763 | 0.237185 | 0.462576 | 0.225391 | 0.108055 | 0.477128 | 5 |
| True differentiable J2 QP-HistoryGNO | True-J2 consistency rel. RMS | 0.284302 | 0.173389 | 0.290555 | 0.104177 | 0.398458 | 0.294281 | 0.0871999 | 0.541118 | 5 |
| True differentiable J2 QP-HistoryGNO | True-J2 active consistency rel. RMS | 3.87582e-08 | 1.49145e-08 | 4.19591e-08 | 2.94145e-08 | 5.30026e-08 | 2.35881e-08 | 1.49723e-08 | 5.44425e-08 | 5 |
| True differentiable J2 QP-HistoryGNO | True-J2 negative dgamma | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 5 |
| True differentiable J2 QP-HistoryGNO | True-J2 active QP frac. | 0.48488 | 0.338167 | 0.3641 | 0.238045 | 0.858298 | 0.620253 | 0.0595992 | 0.90436 | 5 |
| True differentiable J2 QP-HistoryGNO | Eqp increment rel. L2 | 2.44118 | 1.25239 | 1.92328 | 1.43708 | 3.69123 | 2.25415 | 1.00133 | 4.15297 | 5 |
| True differentiable J2 QP-HistoryGNO | Plastic-work inc. rel. L2 | 2.49299 | 1.32357 | 1.92105 | 1.42828 | 3.75916 | 2.33088 | 1.00093 | 4.35552 | 5 |
| True differentiable J2 QP-HistoryGNO | Reversal hist-inc. rel. L2 | 1.57185 | 0.327474 | 1.46369 | 1.45581 | 1.79694 | 0.341131 | 1.09163 | 2.05119 | 5 |
| True differentiable J2 QP-HistoryGNO | Reversal yield-flag MAE | 0.496203 | 0.0564005 | 0.528364 | 0.436474 | 0.546179 | 0.109705 | 0.419597 | 0.550399 | 5 |
| True differentiable J2 QP-HistoryGNO | Yield-surface RMS | 0.0294777 | 0.0152393 | 0.0295249 | 0.0255561 | 0.040404 | 0.0148479 | 0.00357367 | 0.0483297 | 5 |
| True differentiable J2 QP-HistoryGNO | Plastic-work violation abs. | 3.10566e-08 | 3.59714e-08 | 2.01021e-08 | 7.61958e-10 | 3.6768e-08 | 3.6006e-08 | 0 | 9.7651e-08 | 5 |
| True differentiable J2 QP-HistoryGNO | Plastic-work violation target-norm. | 0.00153726 | 0.00178054 | 0.000995027 | 3.77159e-05 | 0.00181997 | 0.00178225 | 0 | 0.0048336 | 5 |
| True differentiable J2 QP-HistoryGNO | Plastic-work violation pred-norm. | 0.000500566 | 0.000521945 | 0.000219488 | 3.32173e-05 | 0.000994381 | 0.000961163 | 0 | 0.00125574 | 5 |
| True differentiable J2 QP-HistoryGNO | FEM residual rel. RMS | 12.7909 | 7.37246 | 8.80574 | 8.70153 | 20.6795 | 11.978 | 3.47871 | 22.289 | 5 |
| True differentiable J2 QP-HistoryGNO | FEM energy rel. err. | 141.41 | 119.933 | 65.1323 | 35.9181 | 282.561 | 246.643 | 30.9077 | 292.533 | 5 |
| True differentiable J2 QP-HistoryGNO | FEM tangent-solver rel. RMS | 4.09977 | 2.05901 | 3.34784 | 2.69673 | 6.2056 | 3.50886 | 1.45712 | 6.79155 | 5 |