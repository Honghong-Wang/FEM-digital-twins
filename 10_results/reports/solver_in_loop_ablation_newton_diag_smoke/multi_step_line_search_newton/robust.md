# J2 Path-Dependent Baseline Robust Statistics

Each row reports both mean/std and robust median/IQR statistics on the cyclic primary test path.
All evaluated paths are stored in JSON: `monotonic, cyclic, nonproportional`.

| Model | Metric | Mean | Std | Median | Q1 | Q3 | IQR | Min | Max | N |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| True differentiable J2 QP-HistoryGNO | Cyclic disp. rel. L2 | 809.976 | 0 | 809.976 | 809.976 | 809.976 | 0 | 809.976 | 809.976 | 1 |
| True differentiable J2 QP-HistoryGNO | Cyclic history rel. L2 | 1.17644 | 0 | 1.17644 | 1.17644 | 1.17644 | 0 | 1.17644 | 1.17644 | 1 |
| True differentiable J2 QP-HistoryGNO | History-increment rel. L2 | 1.00062 | 0 | 1.00062 | 1.00062 | 1.00062 | 0 | 1.00062 | 1.00062 | 1 |
| True differentiable J2 QP-HistoryGNO | QP history rel. L2 | 1.76502 | 0 | 1.76502 | 1.76502 | 1.76502 | 0 | 1.76502 | 1.76502 | 1 |
| True differentiable J2 QP-HistoryGNO | QP history-inc. rel. L2 | 1.00095 | 0 | 1.00095 | 1.00095 | 1.00095 | 0 | 1.00095 | 1.00095 | 1 |
| True differentiable J2 QP-HistoryGNO | QP eqp rel. L2 | 9.92279 | 0 | 9.92279 | 9.92279 | 9.92279 | 0 | 9.92279 | 9.92279 | 1 |
| True differentiable J2 QP-HistoryGNO | QP plastic-work rel. L2 | 11.0403 | 0 | 11.0403 | 11.0403 | 11.0403 | 0 | 11.0403 | 11.0403 | 1 |
| True differentiable J2 QP-HistoryGNO | QP von-Mises rel. L2 | 1.08533 | 0 | 1.08533 | 1.08533 | 1.08533 | 0 | 1.08533 | 1.08533 | 1 |
| True differentiable J2 QP-HistoryGNO | QP reversal scalar-inc. rel. L2 | 1.00003 | 0 | 1.00003 | 1.00003 | 1.00003 | 0 | 1.00003 | 1.00003 | 1 |
| True differentiable J2 QP-HistoryGNO | QP reversal eqp-inc. rel. L2 | 6.7514 | 0 | 6.7514 | 6.7514 | 6.7514 | 0 | 6.7514 | 6.7514 | 1 |
| True differentiable J2 QP-HistoryGNO | QP reversal work-inc. rel. L2 | 7.95728 | 0 | 7.95728 | 7.95728 | 7.95728 | 0 | 7.95728 | 7.95728 | 1 |
| True differentiable J2 QP-HistoryGNO | QP reversal yield MAE | 0.490385 | 0 | 0.490385 | 0.490385 | 0.490385 | 0 | 0.490385 | 0.490385 | 1 |
| True differentiable J2 QP-HistoryGNO | QP inactive false plasticity | 0.50006 | 0 | 0.50006 | 0.50006 | 0.50006 | 0 | 0.50006 | 0.50006 | 1 |
| True differentiable J2 QP-HistoryGNO | True-J2 consistency rel. RMS | 3.27462e-07 | 0 | 3.27462e-07 | 3.27462e-07 | 3.27462e-07 | 0 | 3.27462e-07 | 3.27462e-07 | 1 |
| True differentiable J2 QP-HistoryGNO | True-J2 active consistency rel. RMS | 3.27462e-07 | 0 | 3.27462e-07 | 3.27462e-07 | 3.27462e-07 | 0 | 3.27462e-07 | 3.27462e-07 | 1 |
| True differentiable J2 QP-HistoryGNO | True-J2 negative dgamma | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| True differentiable J2 QP-HistoryGNO | True-J2 active QP frac. | 1 | 0 | 1 | 1 | 1 | 0 | 1 | 1 | 1 |
| True differentiable J2 QP-HistoryGNO | Eqp increment rel. L2 | 13.1764 | 0 | 13.1764 | 13.1764 | 13.1764 | 0 | 13.1764 | 13.1764 | 1 |
| True differentiable J2 QP-HistoryGNO | Plastic-work inc. rel. L2 | 15.2633 | 0 | 15.2633 | 15.2633 | 15.2633 | 0 | 15.2633 | 15.2633 | 1 |
| True differentiable J2 QP-HistoryGNO | Reversal hist-inc. rel. L2 | 1.00048 | 0 | 1.00048 | 1.00048 | 1.00048 | 0 | 1.00048 | 1.00048 | 1 |
| True differentiable J2 QP-HistoryGNO | Reversal yield-flag MAE | 0.558824 | 0 | 0.558824 | 0.558824 | 0.558824 | 0 | 0.558824 | 0.558824 | 1 |
| True differentiable J2 QP-HistoryGNO | Yield-surface RMS | 2.11708e-07 | 0 | 2.11708e-07 | 2.11708e-07 | 2.11708e-07 | 0 | 2.11708e-07 | 2.11708e-07 | 1 |
| True differentiable J2 QP-HistoryGNO | Plastic-work violation abs. | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| True differentiable J2 QP-HistoryGNO | Plastic-work violation target-norm. | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| True differentiable J2 QP-HistoryGNO | Plastic-work violation pred-norm. | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| True differentiable J2 QP-HistoryGNO | FEM residual rel. RMS | 36.5367 | 0 | 36.5367 | 36.5367 | 36.5367 | 0 | 36.5367 | 36.5367 | 1 |
| True differentiable J2 QP-HistoryGNO | FEM energy rel. err. | 3377.26 | 0 | 3377.26 | 3377.26 | 3377.26 | 0 | 3377.26 | 3377.26 | 1 |
| True differentiable J2 QP-HistoryGNO | FEM tangent-solver rel. RMS | 1081.69 | 0 | 1081.69 | 1081.69 | 1081.69 | 0 | 1081.69 | 1081.69 | 1 |
| True differentiable J2 QP-HistoryGNO | Newton initial residual rel. RMS | 32.2741 | 0 | 32.2741 | 32.2741 | 32.2741 | 0 | 32.2741 | 32.2741 | 1 |
| True differentiable J2 QP-HistoryGNO | Newton final residual rel. RMS | 1.0035e-08 | 0 | 1.0035e-08 | 1.0035e-08 | 1.0035e-08 | 0 | 1.0035e-08 | 1.0035e-08 | 1 |
| True differentiable J2 QP-HistoryGNO | Newton residual ratio | 2.61785e-10 | 0 | 2.61785e-10 | 2.61785e-10 | 2.61785e-10 | 0 | 2.61785e-10 | 2.61785e-10 | 1 |
| True differentiable J2 QP-HistoryGNO | Newton residual decrease frac. | 1 | 0 | 1 | 1 | 1 | 0 | 1 | 1 | 1 |
| True differentiable J2 QP-HistoryGNO | Newton step decrease frac. | 0.997791 | 0 | 0.997791 | 0.997791 | 0.997791 | 0 | 0.997791 | 0.997791 | 1 |
| True differentiable J2 QP-HistoryGNO | Newton correction rel. norm | 15.5599 | 0 | 15.5599 | 15.5599 | 15.5599 | 0 | 15.5599 | 15.5599 | 1 |
| True differentiable J2 QP-HistoryGNO | Newton accepted damping | 1 | 0 | 1 | 1 | 1 | 0 | 1 | 1 | 1 |
| True differentiable J2 QP-HistoryGNO | Newton convergence rate | 1 | 0 | 1 | 1 | 1 | 0 | 1 | 1 | 1 |
| True differentiable J2 QP-HistoryGNO | Newton failure rate | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |