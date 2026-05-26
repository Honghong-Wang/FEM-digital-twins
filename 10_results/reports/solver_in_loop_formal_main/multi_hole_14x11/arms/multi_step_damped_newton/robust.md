# J2 Path-Dependent Baseline Robust Statistics

Each row reports both mean/std and robust median/IQR statistics on the cyclic primary test path.
All evaluated paths are stored in JSON: `monotonic, unload_reload, cyclic, nonproportional`.

| Model | Metric | Mean | Std | Median | Q1 | Q3 | IQR | Min | Max | N |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| True differentiable J2 QP-HistoryGNO | Cyclic disp. rel. L2 | 66.7209 | 27.7261 | 69.3514 | 56.4983 | 81.1017 | 24.6034 | 21.4792 | 105.174 | 5 |
| True differentiable J2 QP-HistoryGNO | Cyclic history rel. L2 | 1.0331 | 0.034137 | 1.02942 | 1.00216 | 1.04419 | 0.0420256 | 0.997656 | 1.09206 | 5 |
| True differentiable J2 QP-HistoryGNO | History-increment rel. L2 | 1.21422 | 0.126181 | 1.22454 | 1.16797 | 1.33003 | 0.162058 | 0.999984 | 1.34859 | 5 |
| True differentiable J2 QP-HistoryGNO | QP history rel. L2 | 1.52939 | 0.284904 | 1.6309 | 1.5024 | 1.71499 | 0.212589 | 0.995269 | 1.80341 | 5 |
| True differentiable J2 QP-HistoryGNO | QP history-inc. rel. L2 | 1.59832 | 0.329553 | 1.71525 | 1.56412 | 1.71973 | 0.155612 | 0.999971 | 1.99256 | 5 |
| True differentiable J2 QP-HistoryGNO | QP eqp rel. L2 | 1.70386 | 0.619673 | 1.36515 | 1.27216 | 2.30543 | 1.03327 | 1 | 2.57655 | 5 |
| True differentiable J2 QP-HistoryGNO | QP plastic-work rel. L2 | 1.70171 | 0.622905 | 1.35265 | 1.27274 | 2.28837 | 1.01563 | 1 | 2.59481 | 5 |
| True differentiable J2 QP-HistoryGNO | QP von-Mises rel. L2 | 0.757848 | 0.0630237 | 0.740489 | 0.722065 | 0.783965 | 0.0619002 | 0.67854 | 0.864179 | 5 |
| True differentiable J2 QP-HistoryGNO | QP reversal scalar-inc. rel. L2 | 1.49465 | 0.301027 | 1.50953 | 1.49315 | 1.52035 | 0.0272011 | 1 | 1.9502 | 5 |
| True differentiable J2 QP-HistoryGNO | QP reversal eqp-inc. rel. L2 | 1.09694 | 0.149926 | 1.04879 | 1 | 1.10121 | 0.101213 | 0.954343 | 1.38035 | 5 |
| True differentiable J2 QP-HistoryGNO | QP reversal work-inc. rel. L2 | 1.09661 | 0.152714 | 1.05647 | 1 | 1.08511 | 0.0851098 | 0.953308 | 1.38815 | 5 |
| True differentiable J2 QP-HistoryGNO | QP reversal yield MAE | 0.466038 | 0.24323 | 0.43239 | 0.278302 | 0.558176 | 0.279874 | 0.18239 | 0.878931 | 5 |
| True differentiable J2 QP-HistoryGNO | QP inactive false plasticity | 0.313667 | 0.162761 | 0.37355 | 0.322383 | 0.422466 | 0.100083 | 0 | 0.449935 | 5 |
| True differentiable J2 QP-HistoryGNO | True-J2 consistency rel. RMS | 0.348769 | 0.275406 | 0.285156 | 0.161441 | 0.288069 | 0.126628 | 0.125209 | 0.88397 | 5 |
| True differentiable J2 QP-HistoryGNO | True-J2 active consistency rel. RMS | 3.96995e-08 | 2.06334e-08 | 4.5846e-08 | 4.12371e-08 | 5.56266e-08 | 1.43895e-08 | 0 | 5.57875e-08 | 5 |
| True differentiable J2 QP-HistoryGNO | True-J2 negative dgamma | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 5 |
| True differentiable J2 QP-HistoryGNO | True-J2 active QP frac. | 0.506674 | 0.287755 | 0.572691 | 0.416306 | 0.728716 | 0.31241 | 0 | 0.815657 | 5 |
| True differentiable J2 QP-HistoryGNO | Eqp increment rel. L2 | 2.11037 | 0.890901 | 1.91844 | 1.41222 | 2.78616 | 1.37394 | 1 | 3.43501 | 5 |
| True differentiable J2 QP-HistoryGNO | Plastic-work inc. rel. L2 | 2.10106 | 0.891366 | 1.87603 | 1.40359 | 2.81636 | 1.41277 | 1 | 3.40933 | 5 |
| True differentiable J2 QP-HistoryGNO | Reversal hist-inc. rel. L2 | 1.55694 | 0.324254 | 1.55234 | 1.49917 | 1.7655 | 0.266333 | 1.00002 | 1.96766 | 5 |
| True differentiable J2 QP-HistoryGNO | Reversal yield-flag MAE | 0.505628 | 0.0579356 | 0.532948 | 0.463684 | 0.544012 | 0.0803271 | 0.414622 | 0.572872 | 5 |
| True differentiable J2 QP-HistoryGNO | Yield-surface RMS | 0.0332709 | 0.0186129 | 0.0441518 | 0.0262918 | 0.0442893 | 0.0179975 | 0 | 0.0516216 | 5 |
| True differentiable J2 QP-HistoryGNO | Plastic-work violation abs. | 3.91884e-08 | 4.76749e-08 | 4.56478e-09 | 2.83446e-09 | 6.93712e-08 | 6.65368e-08 | 0 | 1.19172e-07 | 5 |
| True differentiable J2 QP-HistoryGNO | Plastic-work violation target-norm. | 0.00146287 | 0.00177966 | 0.000170399 | 0.000105808 | 0.00258957 | 0.00248376 | 0 | 0.00444857 | 5 |
| True differentiable J2 QP-HistoryGNO | Plastic-work violation pred-norm. | 0.000575214 | 0.00064473 | 9.06836e-05 | 6.08816e-05 | 0.00129388 | 0.001233 | 0 | 0.00143063 | 5 |
| True differentiable J2 QP-HistoryGNO | FEM residual rel. RMS | 12.234 | 7.7407 | 10.4435 | 9.07579 | 15.3112 | 6.23543 | 1.43976 | 24.9 | 5 |
| True differentiable J2 QP-HistoryGNO | FEM energy rel. err. | 91.9955 | 63.9005 | 68.7963 | 59.9829 | 150.609 | 90.6263 | 2.51069 | 178.078 | 5 |
| True differentiable J2 QP-HistoryGNO | FEM tangent-solver rel. RMS | 127.101 | 54.864 | 134.146 | 98.7787 | 159.301 | 60.5221 | 40.7017 | 202.579 | 5 |
| True differentiable J2 QP-HistoryGNO | Newton initial residual rel. RMS | 11.8601 | 7.52953 | 9.72868 | 8.97043 | 14.9596 | 5.98916 | 1.43846 | 24.2035 | 5 |
| True differentiable J2 QP-HistoryGNO | Newton final residual rel. RMS | 1.48252 | 0.941194 | 1.21609 | 1.12131 | 1.86996 | 0.748648 | 0.179807 | 3.02544 | 5 |
| True differentiable J2 QP-HistoryGNO | Newton residual ratio | 0.125 | 1.41992e-07 | 0.125 | 0.125 | 0.125001 | 2.83122e-07 | 0.125 | 0.125001 | 5 |
| True differentiable J2 QP-HistoryGNO | Newton residual decrease frac. | 0.875 | 1.47935e-07 | 0.875 | 0.874999 | 0.875 | 2.98023e-07 | 0.874999 | 0.875 | 5 |
| True differentiable J2 QP-HistoryGNO | Newton step decrease frac. | 0.499999 | 1.96243e-07 | 0.499999 | 0.499999 | 0.5 | 3.8743e-07 | 0.499999 | 0.5 | 5 |
| True differentiable J2 QP-HistoryGNO | Newton step 1 residual ratio | 0.500001 | 1.83133e-07 | 0.500001 | 0.5 | 0.500001 | 2.98023e-07 | 0.5 | 0.500001 | 5 |
| True differentiable J2 QP-HistoryGNO | Newton step 2 residual ratio | 0.250001 | 1.8216e-07 | 0.250001 | 0.25 | 0.250001 | 3.57628e-07 | 0.25 | 0.250001 | 5 |
| True differentiable J2 QP-HistoryGNO | Newton step 3 residual ratio | 0.125 | 1.41992e-07 | 0.125 | 0.125 | 0.125001 | 2.83122e-07 | 0.125 | 0.125001 | 5 |
| True differentiable J2 QP-HistoryGNO | Newton step 1 decrease frac. | 0.499999 | 1.73161e-07 | 0.499999 | 0.499999 | 0.5 | 2.98023e-07 | 0.499999 | 0.5 | 5 |
| True differentiable J2 QP-HistoryGNO | Newton step 2 decrease frac. | 0.749999 | 1.90735e-07 | 0.749999 | 0.749999 | 0.75 | 3.57628e-07 | 0.749999 | 0.75 | 5 |
| True differentiable J2 QP-HistoryGNO | Newton step 3 decrease frac. | 0.875 | 1.47935e-07 | 0.875 | 0.874999 | 0.875 | 2.98023e-07 | 0.874999 | 0.875 | 5 |
| True differentiable J2 QP-HistoryGNO | Newton correction rel. norm | 1.54243 | 1.16246 | 1.24836 | 1.00475 | 1.84814 | 0.84339 | 0.0520002 | 3.55889 | 5 |
| True differentiable J2 QP-HistoryGNO | Newton accepted damping | 0.5 | 0 | 0.5 | 0.5 | 0.5 | 0 | 0.5 | 0.5 | 5 |
| True differentiable J2 QP-HistoryGNO | Newton convergence rate | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 5 |
| True differentiable J2 QP-HistoryGNO | Newton failure rate | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 5 |