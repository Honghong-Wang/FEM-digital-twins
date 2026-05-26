# J2 Path-Dependent Baseline Outlier Diagnostics

Outliers are detected on cyclic-primary metrics using a 1.5 IQR rule when IQR is nonzero, otherwise a 3 sigma rule is used.
All evaluated paths are stored in JSON: `monotonic, unload_reload, cyclic, nonproportional`.

| Model | Metric | Rule | Lower | Upper | Outlier count | Outlier seeds | Mean | Std | Median | IQR | Min | Max |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| True differentiable J2 QP-HistoryGNO | Cyclic history rel. L2 | 1.5*IQR | 0.767491 | 1.37819 | 1 | 20260518=1.41464 | 1.13728 | 0.153116 | 1.13126 | 0.152674 | 0.994807 | 1.41464 |
| True differentiable J2 QP-HistoryGNO | QP eqp rel. L2 | 1.5*IQR | 0.275661 | 2.20723 | 1 | 20260518=2.82315 | 1.51448 | 0.678907 | 1.26634 | 0.482893 | 1 | 2.82315 |
| True differentiable J2 QP-HistoryGNO | QP plastic-work rel. L2 | 1.5*IQR | 0.33709 | 2.10485 | 1 | 20260518=2.72744 | 1.48217 | 0.644242 | 1.24147 | 0.44194 | 1 | 2.72744 |
| True differentiable J2 QP-HistoryGNO | QP von-Mises rel. L2 | 1.5*IQR | 0.684647 | 0.789364 | 2 | 20260518=0.844016; 20260519=0.595722 | 0.732482 | 0.0797354 | 0.748662 | 0.0261793 | 0.595722 | 0.844016 |
| True differentiable J2 QP-HistoryGNO | QP reversal scalar-inc. rel. L2 | 1.5*IQR | 0.989221 | 1.01796 | 2 | 20260517=0.919866; 20260521=1.15609 | 1.01663 | 0.0767514 | 1 | 0.00718594 | 0.919866 | 1.15609 |
| True differentiable J2 QP-HistoryGNO | QP reversal eqp-inc. rel. L2 | 1.5*IQR | 0.883682 | 1.19386 | 1 | 20260518=1.2798 | 1.07429 | 0.10668 | 1.01411 | 0.077545 | 1 | 1.2798 |
| True differentiable J2 QP-HistoryGNO | QP reversal work-inc. rel. L2 | 1.5*IQR | 0.895764 | 1.17373 | 1 | 20260518=1.25726 | 1.06745 | 0.0983576 | 1.01053 | 0.0694907 | 1 | 1.25726 |
| True differentiable J2 QP-HistoryGNO | Plastic-work violation pred-norm. | 1.5*IQR | -3.67788e-05 | 6.1298e-05 | 1 | 20260521=7.32773e-05 | 2.22195e-05 | 2.71262e-05 | 1.3301e-05 | 2.45192e-05 | 0 | 7.32773e-05 |
| True differentiable J2 QP-HistoryGNO | Newton correction rel. norm | 1.5*IQR | -5.48673 | 10.1039 | 1 | 20260518=13.219 | 3.91736 | 4.87792 | 1.64001 | 3.89766 | 0.110625 | 13.219 |