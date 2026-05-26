# J2 Path-Dependent Baseline Outlier Diagnostics

Outliers are detected on cyclic-primary metrics using a 1.5 IQR rule when IQR is nonzero, otherwise a 3 sigma rule is used.
All evaluated paths are stored in JSON: `monotonic, unload_reload, cyclic, nonproportional`.

| Model | Metric | Rule | Lower | Upper | Outlier count | Outlier seeds | Mean | Std | Median | IQR | Min | Max |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| True differentiable J2 QP-HistoryGNO | Cyclic history rel. L2 | 1.5*IQR | 0.940951 | 1.06891 | 1 | 20260518=0.935196 | 0.997292 | 0.0334177 | 1.01941 | 0.0319886 | 0.935196 | 1.022 |
| True differentiable J2 QP-HistoryGNO | History-increment rel. L2 | 1.5*IQR | 1.1114 | 1.37007 | 1 | 20260519=1.49683 | 1.2667 | 0.121979 | 1.21008 | 0.0646672 | 1.14509 | 1.49683 |
| True differentiable J2 QP-HistoryGNO | QP reversal scalar-inc. rel. L2 | 1.5*IQR | 1.30026 | 1.59303 | 2 | 20260519=2.12271; 20260520=1.12197 | 1.5121 | 0.329943 | 1.42251 | 0.0731921 | 1.12197 | 2.12271 |
| True differentiable J2 QP-HistoryGNO | Reversal hist-inc. rel. L2 | 1.5*IQR | 1.28451 | 1.66347 | 2 | 20260519=2.52582; 20260520=1.19716 | 1.6312 | 0.461303 | 1.48506 | 0.0947403 | 1.19716 | 2.52582 |
| True differentiable J2 QP-HistoryGNO | Plastic-work violation abs. | 1.5*IQR | -5.16213e-08 | 8.89868e-08 | 1 | 20260521=3.31204e-07 | 7.6025e-08 | 1.28255e-07 | 1.15554e-08 | 3.5152e-08 | 0 | 3.31204e-07 |
| True differentiable J2 QP-HistoryGNO | Plastic-work violation target-norm. | 1.5*IQR | -0.00255519 | 0.00440473 | 1 | 20260521=0.0163942 | 0.00376314 | 0.00634846 | 0.000571977 | 0.00173998 | 0 | 0.0163942 |
| True differentiable J2 QP-HistoryGNO | Plastic-work violation pred-norm. | 1.5*IQR | -0.000260435 | 0.000519754 | 1 | 20260521=0.00297143 | 0.000676183 | 0.00115052 | 0.000150168 | 0.000195047 | 0 | 0.00297143 |
| True differentiable J2 QP-HistoryGNO | FEM energy rel. err. | 1.5*IQR | -156.064 | 592.114 | 1 | 20260517=880.396 | 329.306 | 293.2 | 287.322 | 187.045 | 42.7595 | 880.396 |
| True differentiable J2 QP-HistoryGNO | Newton correction rel. norm | 1.5*IQR | -0.483549 | 3.2334 | 1 | 20260517=4.0552 | 1.76777 | 1.19477 | 1.15294 | 0.929238 | 0.880861 | 4.0552 |