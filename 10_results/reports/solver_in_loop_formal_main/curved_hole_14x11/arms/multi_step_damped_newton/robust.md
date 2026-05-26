# J2 Path-Dependent Baseline Robust Statistics

Each row reports both mean/std and robust median/IQR statistics on the cyclic primary test path.
All evaluated paths are stored in JSON: `monotonic, unload_reload, cyclic, nonproportional`.

| Model | Metric | Mean | Std | Median | Q1 | Q3 | IQR | Min | Max | N |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| True differentiable J2 QP-HistoryGNO | Cyclic disp. rel. L2 | 93.1504 | 55.2477 | 79.8322 | 52.744 | 86.3001 | 33.5561 | 47.379 | 199.497 | 5 |
| True differentiable J2 QP-HistoryGNO | Cyclic history rel. L2 | 1.00415 | 0.0270889 | 0.989945 | 0.979685 | 1.02714 | 0.0474579 | 0.978682 | 1.04528 | 5 |
| True differentiable J2 QP-HistoryGNO | History-increment rel. L2 | 1.18948 | 0.0780118 | 1.21726 | 1.17407 | 1.22966 | 0.0555899 | 1.04826 | 1.27815 | 5 |
| True differentiable J2 QP-HistoryGNO | QP history rel. L2 | 1.4261 | 0.269087 | 1.55599 | 1.18839 | 1.6762 | 0.487809 | 1.02633 | 1.68358 | 5 |
| True differentiable J2 QP-HistoryGNO | QP history-inc. rel. L2 | 1.53626 | 0.240206 | 1.66759 | 1.45104 | 1.67877 | 0.227727 | 1.10588 | 1.77803 | 5 |
| True differentiable J2 QP-HistoryGNO | QP eqp rel. L2 | 2.70309 | 1.70179 | 1.82866 | 1.20749 | 4.37364 | 3.16615 | 0.998121 | 5.10753 | 5 |
| True differentiable J2 QP-HistoryGNO | QP plastic-work rel. L2 | 2.84425 | 1.87051 | 1.84752 | 1.2141 | 4.61628 | 3.40218 | 0.998183 | 5.54519 | 5 |
| True differentiable J2 QP-HistoryGNO | QP von-Mises rel. L2 | 0.713172 | 0.0801493 | 0.721081 | 0.656677 | 0.785494 | 0.128817 | 0.593245 | 0.809362 | 5 |
| True differentiable J2 QP-HistoryGNO | QP reversal scalar-inc. rel. L2 | 1.42445 | 0.220445 | 1.54158 | 1.26955 | 1.60147 | 0.331918 | 1.06826 | 1.64138 | 5 |
| True differentiable J2 QP-HistoryGNO | QP reversal eqp-inc. rel. L2 | 1.45881 | 0.530217 | 1.12298 | 1.09128 | 1.67178 | 0.580501 | 0.999687 | 2.40835 | 5 |
| True differentiable J2 QP-HistoryGNO | QP reversal work-inc. rel. L2 | 1.51564 | 0.60486 | 1.1285 | 1.09946 | 1.74529 | 0.645834 | 0.999696 | 2.60525 | 5 |
| True differentiable J2 QP-HistoryGNO | QP reversal yield MAE | 0.508727 | 0.28753 | 0.453505 | 0.223176 | 0.753934 | 0.530758 | 0.193133 | 0.919886 | 5 |
| True differentiable J2 QP-HistoryGNO | QP inactive false plasticity | 0.32028 | 0.150203 | 0.39493 | 0.214224 | 0.456259 | 0.242036 | 0.0782233 | 0.457764 | 5 |
| True differentiable J2 QP-HistoryGNO | True-J2 consistency rel. RMS | 0.297011 | 0.185502 | 0.199352 | 0.130142 | 0.48665 | 0.356509 | 0.115475 | 0.553437 | 5 |
| True differentiable J2 QP-HistoryGNO | True-J2 active consistency rel. RMS | 4.85624e-08 | 2.32573e-08 | 3.98941e-08 | 3.84466e-08 | 6.79015e-08 | 2.94549e-08 | 1.54758e-08 | 8.10942e-08 | 5 |
| True differentiable J2 QP-HistoryGNO | True-J2 negative dgamma | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 5 |
| True differentiable J2 QP-HistoryGNO | True-J2 active QP frac. | 0.499332 | 0.331097 | 0.607947 | 0.194093 | 0.825246 | 0.631153 | 0.0293601 | 0.840014 | 5 |
| True differentiable J2 QP-HistoryGNO | Eqp increment rel. L2 | 3.52269 | 2.43545 | 2.30806 | 1.59334 | 5.3441 | 3.75075 | 1.00065 | 7.36731 | 5 |
| True differentiable J2 QP-HistoryGNO | Plastic-work inc. rel. L2 | 3.76266 | 2.77141 | 2.32899 | 1.593 | 5.57574 | 3.98274 | 1.00054 | 8.31503 | 5 |
| True differentiable J2 QP-HistoryGNO | Reversal hist-inc. rel. L2 | 1.42429 | 0.216821 | 1.51934 | 1.3359 | 1.53507 | 0.199168 | 1.05011 | 1.68105 | 5 |
| True differentiable J2 QP-HistoryGNO | Reversal yield-flag MAE | 0.51158 | 0.0463821 | 0.503516 | 0.480544 | 0.552274 | 0.07173 | 0.447257 | 0.574308 | 5 |
| True differentiable J2 QP-HistoryGNO | Yield-surface RMS | 0.0316251 | 0.0154328 | 0.0368266 | 0.030784 | 0.0380019 | 0.00721793 | 0.00318285 | 0.04933 | 5 |
| True differentiable J2 QP-HistoryGNO | Plastic-work violation abs. | 5.89609e-08 | 9.08387e-08 | 9.03205e-09 | 7.66662e-09 | 3.94828e-08 | 3.18162e-08 | 0 | 2.38623e-07 | 5 |
| True differentiable J2 QP-HistoryGNO | Plastic-work violation target-norm. | 0.00291849 | 0.0044964 | 0.000447075 | 0.000379488 | 0.00195435 | 0.00157486 | 0 | 0.0118115 | 5 |
| True differentiable J2 QP-HistoryGNO | Plastic-work violation pred-norm. | 0.000555543 | 0.00077093 | 0.00023043 | 0.000192914 | 0.000268076 | 7.51621e-05 | 0 | 0.00208629 | 5 |
| True differentiable J2 QP-HistoryGNO | FEM residual rel. RMS | 17.5709 | 11.2568 | 16.1745 | 7.91393 | 30.0024 | 22.0884 | 3.04567 | 30.7182 | 5 |
| True differentiable J2 QP-HistoryGNO | FEM energy rel. err. | 328.901 | 380.228 | 222.902 | 67.0491 | 268.352 | 201.303 | 19.8244 | 1066.38 | 5 |
| True differentiable J2 QP-HistoryGNO | FEM tangent-solver rel. RMS | 181.476 | 111.333 | 141.926 | 110.084 | 163.488 | 53.4046 | 93.167 | 398.714 | 5 |
| True differentiable J2 QP-HistoryGNO | Newton initial residual rel. RMS | 16.3971 | 10.5311 | 14.9623 | 7.19475 | 27.6093 | 20.4146 | 3.03478 | 29.1844 | 5 |
| True differentiable J2 QP-HistoryGNO | Newton final residual rel. RMS | 2.04964 | 1.31639 | 1.87029 | 0.899347 | 3.45117 | 2.55182 | 0.37935 | 3.64806 | 5 |
| True differentiable J2 QP-HistoryGNO | Newton residual ratio | 0.125 | 1.40546e-07 | 0.125 | 0.125 | 0.125 | 1.19209e-07 | 0.125 | 0.125001 | 5 |
| True differentiable J2 QP-HistoryGNO | Newton residual decrease frac. | 0.875 | 1.61703e-07 | 0.875 | 0.875 | 0.875 | 1.19209e-07 | 0.874999 | 0.875 | 5 |
| True differentiable J2 QP-HistoryGNO | Newton step decrease frac. | 0.499999 | 1.89988e-07 | 0.5 | 0.499999 | 0.5 | 1.78814e-07 | 0.499999 | 0.5 | 5 |
| True differentiable J2 QP-HistoryGNO | Newton step 1 residual ratio | 0.500001 | 2.00895e-07 | 0.500001 | 0.5 | 0.500001 | 1.19209e-07 | 0.5 | 0.500001 | 5 |
| True differentiable J2 QP-HistoryGNO | Newton step 2 residual ratio | 0.250001 | 1.97146e-07 | 0.25 | 0.25 | 0.250001 | 1.49012e-07 | 0.25 | 0.250001 | 5 |
| True differentiable J2 QP-HistoryGNO | Newton step 3 residual ratio | 0.125 | 1.40546e-07 | 0.125 | 0.125 | 0.125 | 1.19209e-07 | 0.125 | 0.125001 | 5 |
| True differentiable J2 QP-HistoryGNO | Newton step 1 decrease frac. | 0.499999 | 2.0596e-07 | 0.499999 | 0.499999 | 0.5 | 1.49012e-07 | 0.499999 | 0.5 | 5 |
| True differentiable J2 QP-HistoryGNO | Newton step 2 decrease frac. | 0.749999 | 2.05095e-07 | 0.75 | 0.749999 | 0.75 | 1.19209e-07 | 0.749999 | 0.75 | 5 |
| True differentiable J2 QP-HistoryGNO | Newton step 3 decrease frac. | 0.875 | 1.61703e-07 | 0.875 | 0.875 | 0.875 | 1.19209e-07 | 0.874999 | 0.875 | 5 |
| True differentiable J2 QP-HistoryGNO | Newton correction rel. norm | 1.69271 | 1.19258 | 1.11647 | 0.627628 | 2.77935 | 2.15172 | 0.50202 | 3.43808 | 5 |
| True differentiable J2 QP-HistoryGNO | Newton accepted damping | 0.5 | 0 | 0.5 | 0.5 | 0.5 | 0 | 0.5 | 0.5 | 5 |
| True differentiable J2 QP-HistoryGNO | Newton convergence rate | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 5 |
| True differentiable J2 QP-HistoryGNO | Newton failure rate | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 5 |