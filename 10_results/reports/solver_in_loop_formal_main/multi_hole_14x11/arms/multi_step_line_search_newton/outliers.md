# J2 Path-Dependent Baseline Outlier Diagnostics

Outliers are detected on cyclic-primary metrics using a 1.5 IQR rule when IQR is nonzero, otherwise a 3 sigma rule is used.
All evaluated paths are stored in JSON: `monotonic, unload_reload, cyclic, nonproportional`.

| Model | Metric | Rule | Lower | Upper | Outlier count | Outlier seeds | Mean | Std | Median | IQR | Min | Max |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| True differentiable J2 QP-HistoryGNO | Cyclic history rel. L2 | 1.5*IQR | 0.998349 | 1.03126 | 2 | 20260517=1.13081; 20260520=0.997866 | 1.0338 | 0.0489667 | 1.01074 | 0.00822783 | 0.997866 | 1.13081 |
| True differentiable J2 QP-HistoryGNO | QP reversal eqp-inc. rel. L2 | 1.5*IQR | 0.798032 | 1.33661 | 1 | 20260517=2.10327 | 1.25137 | 0.429347 | 1.04198 | 0.134645 | 0.976955 | 2.10327 |
| True differentiable J2 QP-HistoryGNO | QP reversal work-inc. rel. L2 | 1.5*IQR | 0.821204 | 1.29799 | 1 | 20260517=2.14991 | 1.25834 | 0.448471 | 1.04719 | 0.119197 | 0.97541 | 2.14991 |
| True differentiable J2 QP-HistoryGNO | True-J2 consistency rel. RMS | 1.5*IQR | -0.155133 | 0.678307 | 1 | 20260520=0.900819 | 0.35606 | 0.288182 | 0.266533 | 0.20836 | 0.0897713 | 0.900819 |
| True differentiable J2 QP-HistoryGNO | True-J2 active consistency rel. RMS | 1.5*IQR | 1.70989e-08 | 7.71202e-08 | 1 | 20260520=0 | 4.24015e-08 | 2.43575e-08 | 4.36031e-08 | 1.50053e-08 | 0 | 7.41851e-08 |
| True differentiable J2 QP-HistoryGNO | Yield-surface RMS | 1.5*IQR | 0.00643597 | 0.0671537 | 1 | 20260520=0 | 0.0315266 | 0.0177177 | 0.0324127 | 0.0151794 | 0 | 0.0516304 |
| True differentiable J2 QP-HistoryGNO | FEM energy rel. err. | 1.5*IQR | -218.151 | 439.22 | 1 | 20260517=508.183 | 159.846 | 185.174 | 51.7578 | 164.343 | 18.2186 | 508.183 |
| True differentiable J2 QP-HistoryGNO | Newton final residual rel. RMS | 1.5*IQR | -1.41499e-09 | 1.31618e-08 | 1 | 20260517=3.14925e-08 | 9.69885e-09 | 1.11239e-08 | 4.60547e-09 | 3.64419e-09 | 6.49457e-10 | 3.14925e-08 |
| True differentiable J2 QP-HistoryGNO | Newton residual ratio | 1.5*IQR | 5.83128e-10 | 8.88315e-10 | 2 | 20260517=2.52877e-09; 20260518=2.30511e-10 | 9.85968e-10 | 7.95158e-10 | 6.99121e-10 | 7.62966e-11 | 2.30511e-10 | 2.52877e-09 |
| True differentiable J2 QP-HistoryGNO | Newton step decrease frac. | 1.5*IQR | 0.993735 | 0.998731 | 1 | 20260520=0.985856 | 0.99443 | 0.00431673 | 0.996776 | 0.00124907 | 0.985856 | 0.99705 |
| True differentiable J2 QP-HistoryGNO | Newton step 3 residual ratio | 1.5*IQR | 5.83128e-10 | 8.88315e-10 | 2 | 20260517=2.52877e-09; 20260518=2.30511e-10 | 9.85968e-10 | 7.95158e-10 | 6.99121e-10 | 7.62966e-11 | 2.30511e-10 | 2.52877e-09 |
| True differentiable J2 QP-HistoryGNO | Newton correction rel. norm | 1.5*IQR | -0.249401 | 2.89472 | 1 | 20260517=3.19544 | 1.38534 | 1.05167 | 1.05175 | 0.78603 | 0.0341963 | 3.19544 |