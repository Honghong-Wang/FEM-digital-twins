# J2 Path-Dependent Baseline Robust Statistics

Each row reports both mean/std and robust median/IQR statistics on the cyclic primary test path.
All evaluated paths are stored in JSON: `monotonic, cyclic, nonproportional`.

| Model | Metric | Mean | Std | Median | Q1 | Q3 | IQR | Min | Max | N |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| True differentiable J2 QP-HistoryGNO | Cyclic disp. rel. L2 | 893.221 | 0 | 893.221 | 893.221 | 893.221 | 0 | 893.221 | 893.221 | 1 |
| True differentiable J2 QP-HistoryGNO | Cyclic history rel. L2 | 1.18068 | 0 | 1.18068 | 1.18068 | 1.18068 | 0 | 1.18068 | 1.18068 | 1 |
| True differentiable J2 QP-HistoryGNO | History-increment rel. L2 | 1.00105 | 0 | 1.00105 | 1.00105 | 1.00105 | 0 | 1.00105 | 1.00105 | 1 |
| True differentiable J2 QP-HistoryGNO | QP history rel. L2 | 1.76989 | 0 | 1.76989 | 1.76989 | 1.76989 | 0 | 1.76989 | 1.76989 | 1 |
| True differentiable J2 QP-HistoryGNO | QP history-inc. rel. L2 | 1.00161 | 0 | 1.00161 | 1.00161 | 1.00161 | 0 | 1.00161 | 1.00161 | 1 |
| True differentiable J2 QP-HistoryGNO | QP eqp rel. L2 | 19.4295 | 0 | 19.4295 | 19.4295 | 19.4295 | 0 | 19.4295 | 19.4295 | 1 |
| True differentiable J2 QP-HistoryGNO | QP plastic-work rel. L2 | 23.6327 | 0 | 23.6327 | 23.6327 | 23.6327 | 0 | 23.6327 | 23.6327 | 1 |
| True differentiable J2 QP-HistoryGNO | QP von-Mises rel. L2 | 1.32838 | 0 | 1.32838 | 1.32838 | 1.32838 | 0 | 1.32838 | 1.32838 | 1 |
| True differentiable J2 QP-HistoryGNO | QP reversal scalar-inc. rel. L2 | 1.00007 | 0 | 1.00007 | 1.00007 | 1.00007 | 0 | 1.00007 | 1.00007 | 1 |
| True differentiable J2 QP-HistoryGNO | QP reversal eqp-inc. rel. L2 | 9.52535 | 0 | 9.52535 | 9.52535 | 9.52535 | 0 | 9.52535 | 9.52535 | 1 |
| True differentiable J2 QP-HistoryGNO | QP reversal work-inc. rel. L2 | 13.0899 | 0 | 13.0899 | 13.0899 | 13.0899 | 0 | 13.0899 | 13.0899 | 1 |
| True differentiable J2 QP-HistoryGNO | QP reversal yield MAE | 0.490385 | 0 | 0.490385 | 0.490385 | 0.490385 | 0 | 0.490385 | 0.490385 | 1 |
| True differentiable J2 QP-HistoryGNO | QP inactive false plasticity | 0.500211 | 0 | 0.500211 | 0.500211 | 0.500211 | 0 | 0.500211 | 0.500211 | 1 |
| True differentiable J2 QP-HistoryGNO | True-J2 consistency rel. RMS | 5.91426e-07 | 0 | 5.91426e-07 | 5.91426e-07 | 5.91426e-07 | 0 | 5.91426e-07 | 5.91426e-07 | 1 |
| True differentiable J2 QP-HistoryGNO | True-J2 active consistency rel. RMS | 5.91426e-07 | 0 | 5.91426e-07 | 5.91426e-07 | 5.91426e-07 | 0 | 5.91426e-07 | 5.91426e-07 | 1 |
| True differentiable J2 QP-HistoryGNO | True-J2 negative dgamma | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| True differentiable J2 QP-HistoryGNO | True-J2 active QP frac. | 1 | 0 | 1 | 1 | 1 | 0 | 1 | 1 | 1 |
| True differentiable J2 QP-HistoryGNO | Eqp increment rel. L2 | 20.194 | 0 | 20.194 | 20.194 | 20.194 | 0 | 20.194 | 20.194 | 1 |
| True differentiable J2 QP-HistoryGNO | Plastic-work inc. rel. L2 | 26.5076 | 0 | 26.5076 | 26.5076 | 26.5076 | 0 | 26.5076 | 26.5076 | 1 |
| True differentiable J2 QP-HistoryGNO | Reversal hist-inc. rel. L2 | 1.00071 | 0 | 1.00071 | 1.00071 | 1.00071 | 0 | 1.00071 | 1.00071 | 1 |
| True differentiable J2 QP-HistoryGNO | Reversal yield-flag MAE | 0.558824 | 0 | 0.558824 | 0.558824 | 0.558824 | 0 | 0.558824 | 0.558824 | 1 |
| True differentiable J2 QP-HistoryGNO | Yield-surface RMS | 3.05247e-07 | 0 | 3.05247e-07 | 3.05247e-07 | 3.05247e-07 | 0 | 3.05247e-07 | 3.05247e-07 | 1 |
| True differentiable J2 QP-HistoryGNO | Plastic-work violation abs. | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| True differentiable J2 QP-HistoryGNO | Plastic-work violation target-norm. | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| True differentiable J2 QP-HistoryGNO | Plastic-work violation pred-norm. | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| True differentiable J2 QP-HistoryGNO | FEM residual rel. RMS | 178.778 | 0 | 178.778 | 178.778 | 178.778 | 0 | 178.778 | 178.778 | 1 |
| True differentiable J2 QP-HistoryGNO | FEM energy rel. err. | 68014.3 | 0 | 68014.3 | 68014.3 | 68014.3 | 0 | 68014.3 | 68014.3 | 1 |
| True differentiable J2 QP-HistoryGNO | FEM tangent-solver rel. RMS | 3.17884 | 0 | 3.17884 | 3.17884 | 3.17884 | 0 | 3.17884 | 3.17884 | 1 |