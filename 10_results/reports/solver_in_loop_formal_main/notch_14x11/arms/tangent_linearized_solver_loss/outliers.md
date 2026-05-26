# J2 Path-Dependent Baseline Outlier Diagnostics

Outliers are detected on cyclic-primary metrics using a 1.5 IQR rule when IQR is nonzero, otherwise a 3 sigma rule is used.
All evaluated paths are stored in JSON: `monotonic, unload_reload, cyclic, nonproportional`.

| Model | Metric | Rule | Lower | Upper | Outlier count | Outlier seeds | Mean | Std | Median | IQR | Min | Max |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| True differentiable J2 QP-HistoryGNO | History-increment rel. L2 | 1.5*IQR | 0.936468 | 1.10887 | 1 | 20260517=1.11041 | 1.03632 | 0.040544 | 1.02584 | 0.0431005 | 1.00001 | 1.11041 |
| True differentiable J2 QP-HistoryGNO | QP eqp rel. L2 | 1.5*IQR | -0.012435 | 2.68739 | 1 | 20260518=2.70465 | 1.59859 | 0.623866 | 1.61334 | 0.674957 | 1 | 2.70465 |
| True differentiable J2 QP-HistoryGNO | QP plastic-work rel. L2 | 1.5*IQR | 0.0506548 | 2.58224 | 1 | 20260518=2.61275 | 1.56331 | 0.590061 | 1.57089 | 0.632897 | 1 | 2.61275 |
| True differentiable J2 QP-HistoryGNO | QP von-Mises rel. L2 | 1.5*IQR | 0.73074 | 0.804885 | 2 | 20260518=0.839404; 20260519=0.564608 | 0.740445 | 0.0925974 | 0.762586 | 0.0185362 | 0.564608 | 0.839404 |
| True differentiable J2 QP-HistoryGNO | Reversal hist-inc. rel. L2 | 1.5*IQR | 0.961722 | 1.06399 | 1 | 20260517=1.13491 | 1.0338 | 0.0514088 | 1.0084 | 0.0255681 | 0.999997 | 1.13491 |