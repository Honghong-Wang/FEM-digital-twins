# J2 Path-Dependent Baseline Robust Statistics

Each row reports both mean/std and robust median/IQR statistics on the cyclic primary test path.
All evaluated paths are stored in JSON: `monotonic, cyclic, nonproportional`.

| Model | Metric | Mean | Std | Median | Q1 | Q3 | IQR | Min | Max | N |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| True differentiable J2 QP-HistoryGNO | Cyclic disp. rel. L2 | 809.977 | 0 | 809.977 | 809.977 | 809.977 | 0 | 809.977 | 809.977 | 1 |
| True differentiable J2 QP-HistoryGNO | Cyclic history rel. L2 | 1.17644 | 0 | 1.17644 | 1.17644 | 1.17644 | 0 | 1.17644 | 1.17644 | 1 |
| True differentiable J2 QP-HistoryGNO | History-increment rel. L2 | 1.00062 | 0 | 1.00062 | 1.00062 | 1.00062 | 0 | 1.00062 | 1.00062 | 1 |
| True differentiable J2 QP-HistoryGNO | QP history rel. L2 | 1.76502 | 0 | 1.76502 | 1.76502 | 1.76502 | 0 | 1.76502 | 1.76502 | 1 |
| True differentiable J2 QP-HistoryGNO | QP history-inc. rel. L2 | 1.00095 | 0 | 1.00095 | 1.00095 | 1.00095 | 0 | 1.00095 | 1.00095 | 1 |
| True differentiable J2 QP-HistoryGNO | QP eqp rel. L2 | 9.92292 | 0 | 9.92292 | 9.92292 | 9.92292 | 0 | 9.92292 | 9.92292 | 1 |
| True differentiable J2 QP-HistoryGNO | QP plastic-work rel. L2 | 11.0405 | 0 | 11.0405 | 11.0405 | 11.0405 | 0 | 11.0405 | 11.0405 | 1 |
| True differentiable J2 QP-HistoryGNO | QP von-Mises rel. L2 | 1.08533 | 0 | 1.08533 | 1.08533 | 1.08533 | 0 | 1.08533 | 1.08533 | 1 |
| True differentiable J2 QP-HistoryGNO | QP reversal scalar-inc. rel. L2 | 1.00003 | 0 | 1.00003 | 1.00003 | 1.00003 | 0 | 1.00003 | 1.00003 | 1 |
| True differentiable J2 QP-HistoryGNO | QP reversal eqp-inc. rel. L2 | 6.75144 | 0 | 6.75144 | 6.75144 | 6.75144 | 0 | 6.75144 | 6.75144 | 1 |
| True differentiable J2 QP-HistoryGNO | QP reversal work-inc. rel. L2 | 7.95737 | 0 | 7.95737 | 7.95737 | 7.95737 | 0 | 7.95737 | 7.95737 | 1 |
| True differentiable J2 QP-HistoryGNO | QP reversal yield MAE | 0.490385 | 0 | 0.490385 | 0.490385 | 0.490385 | 0 | 0.490385 | 0.490385 | 1 |
| True differentiable J2 QP-HistoryGNO | QP inactive false plasticity | 0.50006 | 0 | 0.50006 | 0.50006 | 0.50006 | 0 | 0.50006 | 0.50006 | 1 |
| True differentiable J2 QP-HistoryGNO | True-J2 consistency rel. RMS | 3.33376e-07 | 0 | 3.33376e-07 | 3.33376e-07 | 3.33376e-07 | 0 | 3.33376e-07 | 3.33376e-07 | 1 |
| True differentiable J2 QP-HistoryGNO | True-J2 active consistency rel. RMS | 3.33376e-07 | 0 | 3.33376e-07 | 3.33376e-07 | 3.33376e-07 | 0 | 3.33376e-07 | 3.33376e-07 | 1 |
| True differentiable J2 QP-HistoryGNO | True-J2 negative dgamma | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| True differentiable J2 QP-HistoryGNO | True-J2 active QP frac. | 1 | 0 | 1 | 1 | 1 | 0 | 1 | 1 | 1 |
| True differentiable J2 QP-HistoryGNO | Eqp increment rel. L2 | 13.1766 | 0 | 13.1766 | 13.1766 | 13.1766 | 0 | 13.1766 | 13.1766 | 1 |
| True differentiable J2 QP-HistoryGNO | Plastic-work inc. rel. L2 | 15.2636 | 0 | 15.2636 | 15.2636 | 15.2636 | 0 | 15.2636 | 15.2636 | 1 |
| True differentiable J2 QP-HistoryGNO | Reversal hist-inc. rel. L2 | 1.00048 | 0 | 1.00048 | 1.00048 | 1.00048 | 0 | 1.00048 | 1.00048 | 1 |
| True differentiable J2 QP-HistoryGNO | Reversal yield-flag MAE | 0.558824 | 0 | 0.558824 | 0.558824 | 0.558824 | 0 | 0.558824 | 0.558824 | 1 |
| True differentiable J2 QP-HistoryGNO | Yield-surface RMS | 2.22359e-07 | 0 | 2.22359e-07 | 2.22359e-07 | 2.22359e-07 | 0 | 2.22359e-07 | 2.22359e-07 | 1 |
| True differentiable J2 QP-HistoryGNO | Plastic-work violation abs. | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| True differentiable J2 QP-HistoryGNO | Plastic-work violation target-norm. | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| True differentiable J2 QP-HistoryGNO | Plastic-work violation pred-norm. | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| True differentiable J2 QP-HistoryGNO | FEM residual rel. RMS | 36.5368 | 0 | 36.5368 | 36.5368 | 36.5368 | 0 | 36.5368 | 36.5368 | 1 |
| True differentiable J2 QP-HistoryGNO | FEM energy rel. err. | 3377.07 | 0 | 3377.07 | 3377.07 | 3377.07 | 0 | 3377.07 | 3377.07 | 1 |
| True differentiable J2 QP-HistoryGNO | FEM tangent-solver rel. RMS | 1081.65 | 0 | 1081.65 | 1081.65 | 1081.65 | 0 | 1081.65 | 1081.65 | 1 |
| True differentiable J2 QP-HistoryGNO | Newton initial residual rel. RMS | 32.2741 | 0 | 32.2741 | 32.2741 | 32.2741 | 0 | 32.2741 | 32.2741 | 1 |
| True differentiable J2 QP-HistoryGNO | Newton final residual rel. RMS | 0.000687393 | 0 | 0.000687393 | 0.000687393 | 0.000687393 | 0 | 0.000687393 | 0.000687393 | 1 |
| True differentiable J2 QP-HistoryGNO | Newton residual ratio | 2.31372e-05 | 0 | 2.31372e-05 | 2.31372e-05 | 2.31372e-05 | 0 | 2.31372e-05 | 2.31372e-05 | 1 |
| True differentiable J2 QP-HistoryGNO | Newton residual decrease frac. | 0.999977 | 0 | 0.999977 | 0.999977 | 0.999977 | 0 | 0.999977 | 0.999977 | 1 |
| True differentiable J2 QP-HistoryGNO | Newton step decrease frac. | 0.999977 | 0 | 0.999977 | 0.999977 | 0.999977 | 0 | 0.999977 | 0.999977 | 1 |
| True differentiable J2 QP-HistoryGNO | Newton correction rel. norm | 15.5136 | 0 | 15.5136 | 15.5136 | 15.5136 | 0 | 15.5136 | 15.5136 | 1 |
| True differentiable J2 QP-HistoryGNO | Newton accepted damping | 1 | 0 | 1 | 1 | 1 | 0 | 1 | 1 | 1 |
| True differentiable J2 QP-HistoryGNO | Newton convergence rate | 1 | 0 | 1 | 1 | 1 | 0 | 1 | 1 | 1 |
| True differentiable J2 QP-HistoryGNO | Newton failure rate | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |