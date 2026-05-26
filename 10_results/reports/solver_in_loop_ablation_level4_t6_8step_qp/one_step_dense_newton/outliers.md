# J2 Path-Dependent Baseline Outlier Diagnostics

Outliers are detected on cyclic-primary metrics using a 1.5 IQR rule when IQR is nonzero, otherwise a 3 sigma rule is used.
All evaluated paths are stored in JSON: `monotonic, unload_reload, cyclic, nonproportional`.

| Model | Metric | Rule | Lower | Upper | Outlier count | Outlier seeds | Mean | Std | Median | IQR | Min | Max |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| True differentiable J2 QP-HistoryGNO | Cyclic history rel. L2 | 1.5*IQR | 1.12339 | 1.2058 | 1 | 20260518=1.09448 | 1.1545 | 0.0311033 | 1.17089 | 0.0206048 | 1.09448 | 1.17794 |
| True differentiable J2 QP-HistoryGNO | History-increment rel. L2 | 1.5*IQR | 1.00171 | 1.02682 | 2 | 20260518=1.28514; 20260521=1.00024 | 1.06531 | 0.110057 | 1.01267 | 0.00627744 | 1.00024 | 1.28514 |
| True differentiable J2 QP-HistoryGNO | QP history rel. L2 | 1.5*IQR | 1.89535 | 1.9844 | 1 | 20260518=1.85695 | 1.92769 | 0.0364977 | 1.94659 | 0.022262 | 1.85695 | 1.95515 |
| True differentiable J2 QP-HistoryGNO | QP history-inc. rel. L2 | 1.5*IQR | 0.97665 | 1.17754 | 1 | 20260518=1.87498 | 1.22186 | 0.328285 | 1.0789 | 0.0502232 | 1.00122 | 1.87498 |
| True differentiable J2 QP-HistoryGNO | QP von-Mises rel. L2 | 1.5*IQR | 0.829156 | 0.940481 | 1 | 20260521=0.941565 | 0.885085 | 0.0362032 | 0.883672 | 0.0278313 | 0.830551 | 0.941565 |
| True differentiable J2 QP-HistoryGNO | QP reversal scalar-inc. rel. L2 | 1.5*IQR | 0.902146 | 1.18489 | 1 | 20260518=1.70343 | 1.16295 | 0.271632 | 1.0243 | 0.0706851 | 1.00001 | 1.70343 |
| True differentiable J2 QP-HistoryGNO | QP reversal yield MAE | 1.5*IQR | 0.111635 | 0.136792 | 1 | 20260518=0.226415 | 0.14434 | 0.0411145 | 0.125786 | 0.00628931 | 0.121069 | 0.226415 |
| True differentiable J2 QP-HistoryGNO | QP inactive false plasticity | 1.5*IQR | 0.482348 | 0.508932 | 1 | 20260518=0.464176 | 0.490665 | 0.0135065 | 0.497905 | 0.00664586 | 0.464176 | 0.499964 |
| True differentiable J2 QP-HistoryGNO | True-J2 consistency rel. RMS | 1.5*IQR | -0.00971446 | 0.0457741 | 1 | 20260518=0.128887 | 0.0369428 | 0.0466927 | 0.0191351 | 0.0138721 | 0.000631693 | 0.128887 |
| True differentiable J2 QP-HistoryGNO | True-J2 active consistency rel. RMS | 1.5*IQR | 5.69375e-08 | 1.38061e-07 | 1 | 20260518=1.39754e-07 | 1.00032e-07 | 2.4983e-08 | 1.0173e-07 | 2.02809e-08 | 6.36785e-08 | 1.39754e-07 |
| True differentiable J2 QP-HistoryGNO | True-J2 active QP frac. | 1.5*IQR | 0.94688 | 1.02552 | 1 | 20260518=0.864538 | 0.965801 | 0.0512567 | 0.992244 | 0.0196609 | 0.864538 | 0.99982 |
| True differentiable J2 QP-HistoryGNO | Eqp increment rel. L2 | 1.5*IQR | 6.18465 | 9.62038 | 2 | 20260517=4.43767; 20260518=10.245 | 7.72802 | 1.88528 | 8.15244 | 0.858932 | 4.43767 | 10.245 |
| True differentiable J2 QP-HistoryGNO | Plastic-work inc. rel. L2 | 1.5*IQR | 6.87562 | 10.0839 | 2 | 20260517=4.56308; 20260518=11.0129 | 8.27825 | 2.09843 | 8.85573 | 0.80208 | 4.56308 | 11.0129 |
| True differentiable J2 QP-HistoryGNO | Reversal hist-inc. rel. L2 | 1.5*IQR | 0.918845 | 1.15611 | 1 | 20260518=1.79839 | 1.17701 | 0.311597 | 1.01185 | 0.059316 | 0.999872 | 1.79839 |
| True differentiable J2 QP-HistoryGNO | Yield-surface RMS | 1.5*IQR | -0.00124037 | 0.0113355 | 1 | 20260518=0.0371182 | 0.0102862 | 0.01357 | 0.00400526 | 0.00314398 | 0.000212379 | 0.0371182 |
| True differentiable J2 QP-HistoryGNO | Plastic-work violation abs. | 1.5*IQR | -1.06036e-07 | 1.76726e-07 | 1 | 20260518=1.53981e-06 | 3.25474e-07 | 6.07722e-07 | 1.68721e-08 | 7.06906e-08 | 0 | 1.53981e-06 |
| True differentiable J2 QP-HistoryGNO | Plastic-work violation target-norm. | 1.5*IQR | -0.00395822 | 0.00659704 | 1 | 20260518=0.0574797 | 0.0121497 | 0.0226857 | 0.000629819 | 0.00263881 | 0 | 0.0574797 |
| True differentiable J2 QP-HistoryGNO | Plastic-work violation pred-norm. | 1.5*IQR | -0.000432691 | 0.000721152 | 1 | 20260518=0.00514111 | 0.00110129 | 0.00202267 | 7.68536e-05 | 0.000288461 | 0 | 0.00514111 |
| True differentiable J2 QP-HistoryGNO | FEM residual rel. RMS | 1.5*IQR | 37.985 | 42.0718 | 2 | 20260517=14.7741; 20260521=54.7251 | 37.8799 | 12.8938 | 39.8435 | 1.02171 | 14.7741 | 54.7251 |
| True differentiable J2 QP-HistoryGNO | Newton initial residual rel. RMS | 1.5*IQR | 32.0879 | 40.8073 | 2 | 20260517=14.0457; 20260521=52.2883 | 35.178 | 12.224 | 36.661 | 2.17984 | 14.0457 | 52.2883 |
| True differentiable J2 QP-HistoryGNO | Newton residual ratio | 1.5*IQR | -4.28278e-06 | 8.76344e-05 | 1 | 20260517=0.000148531 | 5.72973e-05 | 4.67232e-05 | 3.17873e-05 | 2.29793e-05 | 2.28169e-05 | 0.000148531 |
| True differentiable J2 QP-HistoryGNO | Newton residual decrease frac. | 1.5*IQR | 0.999912 | 1 | 1 | 20260517=0.999851 | 0.999943 | 4.67215e-05 | 0.999968 | 2.30074e-05 | 0.999851 | 0.999977 |
| True differentiable J2 QP-HistoryGNO | Newton step decrease frac. | 1.5*IQR | 0.999912 | 1 | 1 | 20260517=0.999851 | 0.999943 | 4.67215e-05 | 0.999968 | 2.30074e-05 | 0.999851 | 0.999977 |