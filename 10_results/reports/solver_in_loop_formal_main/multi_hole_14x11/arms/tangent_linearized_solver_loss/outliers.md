# J2 Path-Dependent Baseline Outlier Diagnostics

Outliers are detected on cyclic-primary metrics using a 1.5 IQR rule when IQR is nonzero, otherwise a 3 sigma rule is used.
All evaluated paths are stored in JSON: `monotonic, unload_reload, cyclic, nonproportional`.

| Model | Metric | Rule | Lower | Upper | Outlier count | Outlier seeds | Mean | Std | Median | IQR | Min | Max |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| True differentiable J2 QP-HistoryGNO | QP history rel. L2 | 1.5*IQR | 1.1566 | 2.02107 | 1 | 20260520=0.994671 | 1.53729 | 0.299327 | 1.63817 | 0.216118 | 0.994671 | 1.87597 |
| True differentiable J2 QP-HistoryGNO | QP history-inc. rel. L2 | 1.5*IQR | 1.06914 | 2.28183 | 1 | 20260520=0.999831 | 1.60816 | 0.335741 | 1.73021 | 0.303172 | 0.999831 | 1.95977 |
| True differentiable J2 QP-HistoryGNO | QP eqp rel. L2 | 1.5*IQR | 0.179033 | 2.94158 | 1 | 20260517=3.74298 | 1.86699 | 0.985304 | 1.47138 | 0.690636 | 1 | 3.74298 |
| True differentiable J2 QP-HistoryGNO | QP plastic-work rel. L2 | 1.5*IQR | 0.188582 | 2.91905 | 1 | 20260517=3.87517 | 1.88754 | 1.03743 | 1.4549 | 0.682617 | 1 | 3.87517 |
| True differentiable J2 QP-HistoryGNO | QP reversal eqp-inc. rel. L2 | 1.5*IQR | 0.571253 | 1.62675 | 1 | 20260517=2.34039 | 1.2993 | 0.530078 | 1 | 0.263875 | 0.958104 | 2.34039 |
| True differentiable J2 QP-HistoryGNO | QP reversal work-inc. rel. L2 | 1.5*IQR | 0.609895 | 1.56048 | 1 | 20260517=2.41199 | 1.30843 | 0.559008 | 1 | 0.237645 | 0.959786 | 2.41199 |
| True differentiable J2 QP-HistoryGNO | QP inactive false plasticity | 1.5*IQR | 0.158358 | 0.555847 | 1 | 20260520=0 | 0.311896 | 0.164416 | 0.376098 | 0.0993721 | 0 | 0.469176 |
| True differentiable J2 QP-HistoryGNO | True-J2 consistency rel. RMS | 1.5*IQR | -0.0106901 | 0.517029 | 1 | 20260520=0.877978 | 0.352311 | 0.273511 | 0.277405 | 0.13193 | 0.0998333 | 0.877978 |
| True differentiable J2 QP-HistoryGNO | True-J2 active consistency rel. RMS | 1.5*IQR | 1.65746e-08 | 7.14962e-08 | 2 | 20260517=7.61483e-08; 20260520=0 | 4.29479e-08 | 2.49029e-08 | 5.05207e-08 | 1.37304e-08 | 0 | 7.61483e-08 |
| True differentiable J2 QP-HistoryGNO | Eqp increment rel. L2 | 1.5*IQR | -0.19058 | 3.97107 | 1 | 20260517=4.93161 | 2.37523 | 1.37714 | 2.16404 | 1.04041 | 1 | 4.93161 |
| True differentiable J2 QP-HistoryGNO | Plastic-work inc. rel. L2 | 1.5*IQR | -0.16183 | 3.8895 | 1 | 20260517=5.22776 | 2.41325 | 1.49177 | 2.1108 | 1.01283 | 1 | 5.22776 |
| True differentiable J2 QP-HistoryGNO | Yield-surface RMS | 1.5*IQR | 0.00723031 | 0.0698591 | 1 | 20260520=0 | 0.0336942 | 0.0179147 | 0.04325 | 0.0156572 | 0 | 0.0481315 |
| True differentiable J2 QP-HistoryGNO | FEM energy rel. err. | 1.5*IQR | -40.6723 | 219.791 | 1 | 20260517=510.884 | 157.812 | 180.03 | 84.9322 | 65.1158 | 14.1268 | 510.884 |