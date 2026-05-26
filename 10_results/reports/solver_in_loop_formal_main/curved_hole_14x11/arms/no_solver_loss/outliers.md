# J2 Path-Dependent Baseline Outlier Diagnostics

Outliers are detected on cyclic-primary metrics using a 1.5 IQR rule when IQR is nonzero, otherwise a 3 sigma rule is used.
All evaluated paths are stored in JSON: `monotonic, unload_reload, cyclic, nonproportional`.

| Model | Metric | Rule | Lower | Upper | Outlier count | Outlier seeds | Mean | Std | Median | IQR | Min | Max |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| True differentiable J2 QP-HistoryGNO | Cyclic disp. rel. L2 | 1.5*IQR | 85.0397 | 145.908 | 2 | 20260517=193.875; 20260520=37.5827 | 114.382 | 49.7177 | 109.504 | 15.2171 | 37.5827 | 193.875 |
| True differentiable J2 QP-HistoryGNO | History-increment rel. L2 | 1.5*IQR | 1.08813 | 1.46963 | 1 | 20260520=0.998179 | 1.2478 | 0.137577 | 1.27719 | 0.0953748 | 0.998179 | 1.40586 |
| True differentiable J2 QP-HistoryGNO | QP history rel. L2 | 1.5*IQR | 1.44691 | 1.74272 | 1 | 20260520=0.99531 | 1.4794 | 0.244576 | 1.5654 | 0.0739543 | 0.99531 | 1.64665 |
| True differentiable J2 QP-HistoryGNO | QP history-inc. rel. L2 | 1.5*IQR | 1.64796 | 1.81098 | 2 | 20260519=1.89461; 20260520=1.02092 | 1.61979 | 0.3066 | 1.72449 | 0.0407542 | 1.02092 | 1.89461 |
| True differentiable J2 QP-HistoryGNO | QP von-Mises rel. L2 | 1.5*IQR | 0.651879 | 0.831236 | 1 | 20260520=0.58522 | 0.71791 | 0.0697937 | 0.738479 | 0.0448393 | 0.58522 | 0.782736 |
| True differentiable J2 QP-HistoryGNO | QP reversal scalar-inc. rel. L2 | 1.5*IQR | 1.38857 | 1.73508 | 2 | 20260519=2.03209; 20260520=1.03469 | 1.55095 | 0.316919 | 1.56431 | 0.0866261 | 1.03469 | 2.03209 |
| True differentiable J2 QP-HistoryGNO | QP reversal yield MAE | 1.5*IQR | -0.0987124 | 0.874106 | 1 | 20260520=0.949928 | 0.446066 | 0.271757 | 0.297568 | 0.243205 | 0.207439 | 0.949928 |
| True differentiable J2 QP-HistoryGNO | QP inactive false plasticity | 1.5*IQR | 0.332186 | 0.505186 | 1 | 20260520=0.0295656 | 0.341981 | 0.157471 | 0.398707 | 0.0432501 | 0.0295656 | 0.444261 |
| True differentiable J2 QP-HistoryGNO | True-J2 consistency rel. RMS | 1.5*IQR | -0.0637058 | 0.511263 | 1 | 20260520=0.591504 | 0.280277 | 0.164836 | 0.217422 | 0.143742 | 0.144903 | 0.591504 |
| True differentiable J2 QP-HistoryGNO | True-J2 active consistency rel. RMS | 1.5*IQR | 1.09658e-08 | 9.07948e-08 | 1 | 20260520=0 | 4.59225e-08 | 2.49929e-08 | 5.62513e-08 | 1.99573e-08 | 0 | 7.16005e-08 |
| True differentiable J2 QP-HistoryGNO | True-J2 active QP frac. | 1.5*IQR | 0.357243 | 1.03657 | 1 | 20260520=0.00281294 | 0.566631 | 0.291707 | 0.636955 | 0.169831 | 0.00281294 | 0.799578 |
| True differentiable J2 QP-HistoryGNO | Yield-surface RMS | 1.5*IQR | 0.025829 | 0.0444798 | 2 | 20260519=0.0519864; 20260520=0.00484378 | 0.0325614 | 0.0153595 | 0.0356681 | 0.00466269 | 0.00484378 | 0.0519864 |
| True differentiable J2 QP-HistoryGNO | Plastic-work violation abs. | 1.5*IQR | -2.60086e-08 | 5.89757e-08 | 1 | 20260521=1.18123e-07 | 3.40452e-08 | 4.31113e-08 | 1.91363e-08 | 2.12461e-08 | 0 | 1.18123e-07 |
| True differentiable J2 QP-HistoryGNO | Plastic-work violation target-norm. | 1.5*IQR | -0.00128739 | 0.00291922 | 1 | 20260521=0.00584693 | 0.0016852 | 0.00213395 | 0.00094722 | 0.00105165 | 0 | 0.00584693 |
| True differentiable J2 QP-HistoryGNO | Plastic-work violation pred-norm. | 1.5*IQR | -0.000512265 | 0.000964215 | 1 | 20260521=0.00124981 | 0.000397902 | 0.000452427 | 0.000287751 | 0.00036912 | 0 | 0.00124981 |
| True differentiable J2 QP-HistoryGNO | FEM tangent-solver rel. RMS | 1.5*IQR | 103.835 | 359.584 | 2 | 20260517=365.369; 20260520=75.5389 | 223.606 | 94.1212 | 213.705 | 63.9371 | 75.5389 | 365.369 |
| True differentiable J2 QP-HistoryGNO | Newton initial residual rel. RMS | 1.5*IQR | 7.72499 | 30.6937 | 1 | 20260520=4.6098 | 17.0084 | 6.71352 | 18.41 | 5.74218 | 4.6098 | 23.6033 |
| True differentiable J2 QP-HistoryGNO | Newton final residual rel. RMS | 1.5*IQR | -5.1105e-05 | 0.000479409 | 1 | 20260517=0.000635904 | 0.000283111 | 0.000186775 | 0.000241136 | 0.000132629 | 0.000110211 | 0.000635904 |
| True differentiable J2 QP-HistoryGNO | Newton correction rel. norm | 1.5*IQR | -0.116927 | 2.97109 | 1 | 20260517=4.01243 | 1.74086 | 1.21767 | 1.37009 | 0.772003 | 0.467598 | 4.01243 |