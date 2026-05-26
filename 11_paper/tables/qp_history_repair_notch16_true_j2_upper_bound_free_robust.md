# J2 Path-Dependent Baseline Robust Statistics

Each row reports both mean/std and robust median/IQR statistics on the cyclic primary test path.
All evaluated paths are stored in JSON: `monotonic, cyclic`.

| Model | Metric | Mean | Std | Median | Q1 | Q3 | IQR | Min | Max | N |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| True differentiable J2 QP-HistoryGNO | Cyclic disp. rel. L2 | 94.428 | 36.4997 | 97.7333 | 57.3511 | 105.33 | 47.9786 | 56.3898 | 155.336 | 5 |
| True differentiable J2 QP-HistoryGNO | Cyclic history rel. L2 | 2.178 | 0.0574871 | 2.20847 | 2.20054 | 2.20879 | 0.00824666 | 2.0632 | 2.209 | 5 |
| True differentiable J2 QP-HistoryGNO | History-increment rel. L2 | 1.04091 | 0.0765149 | 1.00044 | 1.00025 | 1.00995 | 0.00970078 | 1.00015 | 1.19375 | 5 |
| True differentiable J2 QP-HistoryGNO | QP history rel. L2 | 3.36077 | 0.0656767 | 3.39503 | 3.38771 | 3.39577 | 0.00805879 | 3.22956 | 3.3958 | 5 |
| True differentiable J2 QP-HistoryGNO | QP history-inc. rel. L2 | 1.12927 | 0.235815 | 1.00212 | 1.00055 | 1.04361 | 0.0430624 | 1.00032 | 1.59974 | 5 |
| True differentiable J2 QP-HistoryGNO | QP eqp rel. L2 | 15.8083 | 4.21597 | 16.9982 | 16.3228 | 17.8886 | 1.56586 | 7.76358 | 20.0681 | 5 |
| True differentiable J2 QP-HistoryGNO | QP plastic-work rel. L2 | 16.7228 | 4.73469 | 17.64 | 17.5798 | 18.9128 | 1.33295 | 7.74585 | 21.7357 | 5 |
| True differentiable J2 QP-HistoryGNO | QP von-Mises rel. L2 | 1.37624 | 0.0644002 | 1.4063 | 1.37808 | 1.41092 | 0.0328333 | 1.25236 | 1.43353 | 5 |
| True differentiable J2 QP-HistoryGNO | Eqp increment rel. L2 | 19.1663 | 5.82841 | 20.2298 | 16.3371 | 23.7952 | 7.45805 | 9.51303 | 25.9563 | 5 |
| True differentiable J2 QP-HistoryGNO | Plastic-work inc. rel. L2 | 21.1079 | 7.06269 | 22.2901 | 17.29 | 26.2596 | 8.96957 | 9.75705 | 29.9426 | 5 |
| True differentiable J2 QP-HistoryGNO | Reversal hist-inc. rel. L2 | 1.07478 | 0.145721 | 1.00031 | 1.00024 | 1.00704 | 0.00679815 | 1.00015 | 1.36618 | 5 |
| True differentiable J2 QP-HistoryGNO | Reversal yield-flag MAE | 0.836456 | 0.053674 | 0.863834 | 0.861656 | 0.863834 | 0.00217867 | 0.729121 | 0.863834 | 5 |
| True differentiable J2 QP-HistoryGNO | Yield-surface RMS | 0.00546669 | 0.0076646 | 0.000445942 | 8.96724e-08 | 0.00706046 | 0.00706037 | 8.76757e-08 | 0.0198269 | 5 |
| True differentiable J2 QP-HistoryGNO | Plastic-work violation abs. | 5.19127e-09 | 6.83826e-09 | 0 | 0 | 8.99764e-09 | 8.99764e-09 | 0 | 1.69587e-08 | 5 |
| True differentiable J2 QP-HistoryGNO | Plastic-work violation target-norm. | 0.000556745 | 0.000733378 | 0 | 0 | 0.000964964 | 0.000964964 | 0 | 0.00181876 | 5 |
| True differentiable J2 QP-HistoryGNO | Plastic-work violation pred-norm. | 4.03841e-05 | 4.95022e-05 | 0 | 0 | 9.77407e-05 | 9.77407e-05 | 0 | 0.00010418 | 5 |
| True differentiable J2 QP-HistoryGNO | FEM residual rel. RMS | 68.2413 | 36.3153 | 61.7455 | 42.0735 | 83.8922 | 41.8186 | 24.4151 | 129.08 | 5 |
| True differentiable J2 QP-HistoryGNO | FEM energy rel. err. | 2598.76 | 2471.25 | 1078.93 | 921.184 | 3794.47 | 2873.28 | 284.635 | 6914.6 | 5 |