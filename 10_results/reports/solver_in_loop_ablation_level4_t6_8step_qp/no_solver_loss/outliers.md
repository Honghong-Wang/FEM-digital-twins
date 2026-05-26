# J2 Path-Dependent Baseline Outlier Diagnostics

Outliers are detected on cyclic-primary metrics using a 1.5 IQR rule when IQR is nonzero, otherwise a 3 sigma rule is used.
All evaluated paths are stored in JSON: `monotonic, unload_reload, cyclic, nonproportional`.

| Model | Metric | Rule | Lower | Upper | Outlier count | Outlier seeds | Mean | Std | Median | IQR | Min | Max |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| True differentiable J2 QP-HistoryGNO | Cyclic history rel. L2 | 1.5*IQR | 1.12293 | 1.20608 | 1 | 20260518=1.09431 | 1.15443 | 0.0311665 | 1.17089 | 0.0207868 | 1.09431 | 1.17794 |
| True differentiable J2 QP-HistoryGNO | History-increment rel. L2 | 1.5*IQR | 1.00005 | 1.02781 | 1 | 20260518=1.27603 | 1.06336 | 0.106484 | 1.01267 | 0.00694025 | 1.00024 | 1.27603 |
| True differentiable J2 QP-HistoryGNO | QP history rel. L2 | 1.5*IQR | 1.89481 | 1.98473 | 1 | 20260518=1.86185 | 1.92863 | 0.0345991 | 1.94659 | 0.0224794 | 1.86185 | 1.95515 |
| True differentiable J2 QP-HistoryGNO | QP history-inc. rel. L2 | 1.5*IQR | 0.975014 | 1.18027 | 1 | 20260518=1.85044 | 1.21717 | 0.318444 | 1.0789 | 0.0513134 | 1.00122 | 1.85044 |
| True differentiable J2 QP-HistoryGNO | QP von-Mises rel. L2 | 1.5*IQR | 0.828785 | 0.941129 | 1 | 20260521=0.941559 | 0.885837 | 0.0362205 | 0.887167 | 0.0280861 | 0.830547 | 0.941559 |
| True differentiable J2 QP-HistoryGNO | QP reversal scalar-inc. rel. L2 | 1.5*IQR | 0.902146 | 1.18489 | 1 | 20260518=1.69378 | 1.16102 | 0.267792 | 1.0243 | 0.0706851 | 1.00001 | 1.69378 |
| True differentiable J2 QP-HistoryGNO | QP reversal yield MAE | 1.5*IQR | 0.111635 | 0.136792 | 1 | 20260518=0.216981 | 0.142453 | 0.0373486 | 0.125786 | 0.00628931 | 0.121069 | 0.216981 |
| True differentiable J2 QP-HistoryGNO | QP inactive false plasticity | 1.5*IQR | 0.482192 | 0.509025 | 1 | 20260518=0.465833 | 0.490984 | 0.0128561 | 0.497905 | 0.00670838 | 0.465833 | 0.499964 |
| True differentiable J2 QP-HistoryGNO | True-J2 consistency rel. RMS | 1.5*IQR | -0.00989099 | 0.0459539 | 1 | 20260518=0.129393 | 0.037044 | 0.0468942 | 0.0191294 | 0.0139612 | 0.000634643 | 0.129393 |
| True differentiable J2 QP-HistoryGNO | True-J2 active consistency rel. RMS | 1.5*IQR | 6.26127e-08 | 1.33196e-07 | 1 | 20260518=1.52598e-07 | 1.02622e-07 | 2.88468e-08 | 1.00255e-07 | 1.76457e-08 | 6.44472e-08 | 1.52598e-07 |
| True differentiable J2 QP-HistoryGNO | True-J2 active QP frac. | 1.5*IQR | 0.946428 | 1.02579 | 1 | 20260518=0.869048 | 0.966667 | 0.0494688 | 0.992244 | 0.0198413 | 0.869048 | 0.99982 |
| True differentiable J2 QP-HistoryGNO | Eqp increment rel. L2 | 1.5*IQR | 6.17205 | 9.64372 | 2 | 20260517=4.43745; 20260518=10.3947 | 7.76002 | 1.92641 | 8.15219 | 0.867919 | 4.43745 | 10.3947 |
| True differentiable J2 QP-HistoryGNO | Plastic-work inc. rel. L2 | 1.5*IQR | 6.8611 | 10.1112 | 2 | 20260517=4.56285; 20260518=11.1725 | 8.31258 | 2.14123 | 8.85537 | 0.812512 | 4.56285 | 11.1725 |
| True differentiable J2 QP-HistoryGNO | Reversal hist-inc. rel. L2 | 1.5*IQR | 0.918844 | 1.15611 | 1 | 20260518=1.79948 | 1.17723 | 0.312032 | 1.01185 | 0.0593163 | 0.999872 | 1.79948 |
| True differentiable J2 QP-HistoryGNO | Yield-surface RMS | 1.5*IQR | -0.00125985 | 0.0113425 | 1 | 20260518=0.0373821 | 0.0103429 | 0.0136724 | 0.00403641 | 0.00315059 | 0.000213372 | 0.0373821 |
| True differentiable J2 QP-HistoryGNO | Plastic-work violation abs. | 1.5*IQR | -1.06243e-07 | 1.77072e-07 | 1 | 20260518=1.88352e-06 | 3.942e-07 | 7.45113e-07 | 1.66536e-08 | 7.0829e-08 | 0 | 1.88352e-06 |
| True differentiable J2 QP-HistoryGNO | Plastic-work violation target-norm. | 1.5*IQR | -0.00396597 | 0.00660996 | 1 | 20260518=0.0703101 | 0.0147151 | 0.0278144 | 0.000621665 | 0.00264398 | 0 | 0.0703101 |
| True differentiable J2 QP-HistoryGNO | Plastic-work violation pred-norm. | 1.5*IQR | -0.000433 | 0.000721667 | 1 | 20260518=0.00618701 | 0.0013103 | 0.00244064 | 7.58479e-05 | 0.000288667 | 0 | 0.00618701 |
| True differentiable J2 QP-HistoryGNO | FEM residual rel. RMS | 1.5*IQR | 38.7529 | 41.6239 | 2 | 20260517=14.7731; 20260521=54.7215 | 38.0569 | 12.9208 | 40.4128 | 0.717747 | 14.7731 | 54.7215 |
| True differentiable J2 QP-HistoryGNO | FEM tangent-solver rel. RMS | 1.5*IQR | 0.786156 | 9.35465 | 1 | 20260518=15.6979 | 6.7434 | 4.55683 | 4.03982 | 2.14212 | 3.83847 | 15.6979 |