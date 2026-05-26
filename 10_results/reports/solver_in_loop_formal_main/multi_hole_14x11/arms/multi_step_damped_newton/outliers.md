# J2 Path-Dependent Baseline Outlier Diagnostics

Outliers are detected on cyclic-primary metrics using a 1.5 IQR rule when IQR is nonzero, otherwise a 3 sigma rule is used.
All evaluated paths are stored in JSON: `monotonic, unload_reload, cyclic, nonproportional`.

| Model | Metric | Rule | Lower | Upper | Outlier count | Outlier seeds | Mean | Std | Median | IQR | Min | Max |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| True differentiable J2 QP-HistoryGNO | QP history rel. L2 | 1.5*IQR | 1.18352 | 2.03387 | 1 | 20260520=0.995269 | 1.52939 | 0.284904 | 1.6309 | 0.212589 | 0.995269 | 1.80341 |
| True differentiable J2 QP-HistoryGNO | QP history-inc. rel. L2 | 1.5*IQR | 1.3307 | 1.95315 | 2 | 20260520=0.999971; 20260521=1.99256 | 1.59832 | 0.329553 | 1.71525 | 0.155612 | 0.999971 | 1.99256 |
| True differentiable J2 QP-HistoryGNO | QP reversal scalar-inc. rel. L2 | 1.5*IQR | 1.45235 | 1.56116 | 2 | 20260520=1; 20260521=1.9502 | 1.49465 | 0.301027 | 1.50953 | 0.0272011 | 1 | 1.9502 |
| True differentiable J2 QP-HistoryGNO | QP reversal eqp-inc. rel. L2 | 1.5*IQR | 0.848181 | 1.25303 | 1 | 20260517=1.38035 | 1.09694 | 0.149926 | 1.04879 | 0.101213 | 0.954343 | 1.38035 |
| True differentiable J2 QP-HistoryGNO | QP reversal work-inc. rel. L2 | 1.5*IQR | 0.872335 | 1.21277 | 1 | 20260517=1.38815 | 1.09661 | 0.152714 | 1.05647 | 0.0851098 | 0.953308 | 1.38815 |
| True differentiable J2 QP-HistoryGNO | QP inactive false plasticity | 1.5*IQR | 0.172259 | 0.572589 | 1 | 20260520=0 | 0.313667 | 0.162761 | 0.37355 | 0.100083 | 0 | 0.449935 |
| True differentiable J2 QP-HistoryGNO | True-J2 consistency rel. RMS | 1.5*IQR | -0.0285017 | 0.478012 | 1 | 20260520=0.88397 | 0.348769 | 0.275406 | 0.285156 | 0.126628 | 0.125209 | 0.88397 |
| True differentiable J2 QP-HistoryGNO | True-J2 active consistency rel. RMS | 1.5*IQR | 1.96528e-08 | 7.72109e-08 | 1 | 20260520=0 | 3.96995e-08 | 2.06334e-08 | 4.5846e-08 | 1.43895e-08 | 0 | 5.57875e-08 |
| True differentiable J2 QP-HistoryGNO | Reversal hist-inc. rel. L2 | 1.5*IQR | 1.09967 | 2.165 | 1 | 20260520=1.00002 | 1.55694 | 0.324254 | 1.55234 | 0.266333 | 1.00002 | 1.96766 |
| True differentiable J2 QP-HistoryGNO | FEM residual rel. RMS | 1.5*IQR | -0.277349 | 24.6644 | 1 | 20260518=24.9 | 12.234 | 7.7407 | 10.4435 | 6.23543 | 1.43976 | 24.9 |
| True differentiable J2 QP-HistoryGNO | Newton initial residual rel. RMS | 1.5*IQR | -0.01331 | 23.9433 | 1 | 20260518=24.2035 | 11.8601 | 7.52953 | 9.72868 | 5.98916 | 1.43846 | 24.2035 |
| True differentiable J2 QP-HistoryGNO | Newton final residual rel. RMS | 1.5*IQR | -0.00166339 | 2.99293 | 1 | 20260518=3.02544 | 1.48252 | 0.941194 | 1.21609 | 0.748648 | 0.179807 | 3.02544 |
| True differentiable J2 QP-HistoryGNO | Newton correction rel. norm | 1.5*IQR | -0.260337 | 3.11322 | 1 | 20260517=3.55889 | 1.54243 | 1.16246 | 1.24836 | 0.84339 | 0.0520002 | 3.55889 |