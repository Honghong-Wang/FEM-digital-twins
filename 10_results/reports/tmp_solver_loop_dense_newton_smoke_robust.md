# J2 Path-Dependent Baseline Robust Statistics

Each row reports both mean/std and robust median/IQR statistics on the cyclic primary test path.
All evaluated paths are stored in JSON: `monotonic, cyclic`.

| Model | Metric | Mean | Std | Median | Q1 | Q3 | IQR | Min | Max | N |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| True differentiable J2 QP-HistoryGNO | Cyclic disp. rel. L2 | 172.695 | 0 | 172.695 | 172.695 | 172.695 | 0 | 172.695 | 172.695 | 1 |
| True differentiable J2 QP-HistoryGNO | Cyclic history rel. L2 | 1.18724 | 0 | 1.18724 | 1.18724 | 1.18724 | 0 | 1.18724 | 1.18724 | 1 |
| True differentiable J2 QP-HistoryGNO | History-increment rel. L2 | 1.00217 | 0 | 1.00217 | 1.00217 | 1.00217 | 0 | 1.00217 | 1.00217 | 1 |
| True differentiable J2 QP-HistoryGNO | QP history rel. L2 | 1.77747 | 0 | 1.77747 | 1.77747 | 1.77747 | 0 | 1.77747 | 1.77747 | 1 |
| True differentiable J2 QP-HistoryGNO | QP history-inc. rel. L2 | 1.00332 | 0 | 1.00332 | 1.00332 | 1.00332 | 0 | 1.00332 | 1.00332 | 1 |
| True differentiable J2 QP-HistoryGNO | QP eqp rel. L2 | 30.6054 | 0 | 30.6054 | 30.6054 | 30.6054 | 0 | 30.6054 | 30.6054 | 1 |
| True differentiable J2 QP-HistoryGNO | QP plastic-work rel. L2 | 42.9989 | 0 | 42.9989 | 42.9989 | 42.9989 | 0 | 42.9989 | 42.9989 | 1 |
| True differentiable J2 QP-HistoryGNO | QP von-Mises rel. L2 | 1.62121 | 0 | 1.62121 | 1.62121 | 1.62121 | 0 | 1.62121 | 1.62121 | 1 |
| True differentiable J2 QP-HistoryGNO | QP reversal scalar-inc. rel. L2 | 1.00019 | 0 | 1.00019 | 1.00019 | 1.00019 | 0 | 1.00019 | 1.00019 | 1 |
| True differentiable J2 QP-HistoryGNO | QP reversal eqp-inc. rel. L2 | 16.4769 | 0 | 16.4769 | 16.4769 | 16.4769 | 0 | 16.4769 | 16.4769 | 1 |
| True differentiable J2 QP-HistoryGNO | QP reversal work-inc. rel. L2 | 27.6908 | 0 | 27.6908 | 27.6908 | 27.6908 | 0 | 27.6908 | 27.6908 | 1 |
| True differentiable J2 QP-HistoryGNO | QP reversal yield MAE | 0.490385 | 0 | 0.490385 | 0.490385 | 0.490385 | 0 | 0.490385 | 0.490385 | 1 |
| True differentiable J2 QP-HistoryGNO | QP inactive false plasticity | 0.500524 | 0 | 0.500524 | 0.500524 | 0.500524 | 0 | 0.500524 | 0.500524 | 1 |
| True differentiable J2 QP-HistoryGNO | True-J2 consistency rel. RMS | 8.62744e-07 | 0 | 8.62744e-07 | 8.62744e-07 | 8.62744e-07 | 0 | 8.62744e-07 | 8.62744e-07 | 1 |
| True differentiable J2 QP-HistoryGNO | True-J2 active consistency rel. RMS | 8.62744e-07 | 0 | 8.62744e-07 | 8.62744e-07 | 8.62744e-07 | 0 | 8.62744e-07 | 8.62744e-07 | 1 |
| True differentiable J2 QP-HistoryGNO | True-J2 negative dgamma | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| True differentiable J2 QP-HistoryGNO | True-J2 active QP frac. | 1 | 0 | 1 | 1 | 1 | 0 | 1 | 1 | 1 |
| True differentiable J2 QP-HistoryGNO | Eqp increment rel. L2 | 33.3148 | 0 | 33.3148 | 33.3148 | 33.3148 | 0 | 33.3148 | 33.3148 | 1 |
| True differentiable J2 QP-HistoryGNO | Plastic-work inc. rel. L2 | 52.8125 | 0 | 52.8125 | 52.8125 | 52.8125 | 0 | 52.8125 | 52.8125 | 1 |
| True differentiable J2 QP-HistoryGNO | Reversal hist-inc. rel. L2 | 1.00148 | 0 | 1.00148 | 1.00148 | 1.00148 | 0 | 1.00148 | 1.00148 | 1 |
| True differentiable J2 QP-HistoryGNO | Reversal yield-flag MAE | 0.558824 | 0 | 0.558824 | 0.558824 | 0.558824 | 0 | 0.558824 | 0.558824 | 1 |
| True differentiable J2 QP-HistoryGNO | Yield-surface RMS | 4.44146e-07 | 0 | 4.44146e-07 | 4.44146e-07 | 4.44146e-07 | 0 | 4.44146e-07 | 4.44146e-07 | 1 |
| True differentiable J2 QP-HistoryGNO | Plastic-work violation abs. | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| True differentiable J2 QP-HistoryGNO | Plastic-work violation target-norm. | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| True differentiable J2 QP-HistoryGNO | Plastic-work violation pred-norm. | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| True differentiable J2 QP-HistoryGNO | FEM residual rel. RMS | 377.538 | 0 | 377.538 | 377.538 | 377.538 | 0 | 377.538 | 377.538 | 1 |
| True differentiable J2 QP-HistoryGNO | FEM energy rel. err. | 266917 | 0 | 266917 | 266917 | 266917 | 0 | 266917 | 266917 | 1 |
| True differentiable J2 QP-HistoryGNO | FEM tangent-solver rel. RMS | 2.04306 | 0 | 2.04306 | 2.04306 | 2.04306 | 0 | 2.04306 | 2.04306 | 1 |