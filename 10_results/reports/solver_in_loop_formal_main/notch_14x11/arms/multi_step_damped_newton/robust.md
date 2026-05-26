# J2 Path-Dependent Baseline Robust Statistics

Each row reports both mean/std and robust median/IQR statistics on the cyclic primary test path.
All evaluated paths are stored in JSON: `monotonic, unload_reload, cyclic, nonproportional`.

| Model | Metric | Mean | Std | Median | Q1 | Q3 | IQR | Min | Max | N |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| True differentiable J2 QP-HistoryGNO | Cyclic disp. rel. L2 | 85.4132 | 71.4241 | 46.7461 | 29.3129 | 160.026 | 130.713 | 8.61574 | 182.365 | 5 |
| True differentiable J2 QP-HistoryGNO | Cyclic history rel. L2 | 1.13728 | 0.153116 | 1.13126 | 0.996502 | 1.14918 | 0.152674 | 0.994807 | 1.41464 | 5 |
| True differentiable J2 QP-HistoryGNO | History-increment rel. L2 | 1.05174 | 0.0579472 | 1.01355 | 1.0002 | 1.12236 | 0.122154 | 1.00005 | 1.12256 | 5 |
| True differentiable J2 QP-HistoryGNO | QP history rel. L2 | 1.56873 | 0.505667 | 1.76048 | 0.992759 | 1.81607 | 0.823306 | 0.989301 | 2.28502 | 5 |
| True differentiable J2 QP-HistoryGNO | QP history-inc. rel. L2 | 1.22057 | 0.251271 | 1.05375 | 1.00041 | 1.46824 | 0.467829 | 1.00009 | 1.58034 | 5 |
| True differentiable J2 QP-HistoryGNO | QP eqp rel. L2 | 1.51448 | 0.678907 | 1.26634 | 1 | 1.48289 | 0.482893 | 1 | 2.82315 | 5 |
| True differentiable J2 QP-HistoryGNO | QP plastic-work rel. L2 | 1.48217 | 0.644242 | 1.24147 | 1 | 1.44194 | 0.44194 | 1 | 2.72744 | 5 |
| True differentiable J2 QP-HistoryGNO | QP von-Mises rel. L2 | 0.732482 | 0.0797354 | 0.748662 | 0.723916 | 0.750095 | 0.0261793 | 0.595722 | 0.844016 | 5 |
| True differentiable J2 QP-HistoryGNO | QP reversal scalar-inc. rel. L2 | 1.01663 | 0.0767514 | 1 | 1 | 1.00719 | 0.00718594 | 0.919866 | 1.15609 | 5 |
| True differentiable J2 QP-HistoryGNO | QP reversal eqp-inc. rel. L2 | 1.07429 | 0.10668 | 1.01411 | 1 | 1.07755 | 0.077545 | 1 | 1.2798 | 5 |
| True differentiable J2 QP-HistoryGNO | QP reversal work-inc. rel. L2 | 1.06745 | 0.0983576 | 1.01053 | 1 | 1.06949 | 0.0694907 | 1 | 1.25726 | 5 |
| True differentiable J2 QP-HistoryGNO | QP reversal yield MAE | 0.462319 | 0.0618961 | 0.474638 | 0.42029 | 0.525362 | 0.105072 | 0.365942 | 0.525362 | 5 |
| True differentiable J2 QP-HistoryGNO | QP inactive false plasticity | 0.244578 | 0.205503 | 0.360885 | 0 | 0.365872 | 0.365872 | 0 | 0.496136 | 5 |
| True differentiable J2 QP-HistoryGNO | True-J2 consistency rel. RMS | 0.389529 | 0.291116 | 0.242686 | 0.228614 | 0.663513 | 0.4349 | 0.0187013 | 0.794133 | 5 |
| True differentiable J2 QP-HistoryGNO | True-J2 active consistency rel. RMS | 1.94571e-08 | 1.62439e-08 | 2.68427e-08 | 0 | 3.29199e-08 | 3.29199e-08 | 0 | 3.75228e-08 | 5 |
| True differentiable J2 QP-HistoryGNO | True-J2 negative dgamma | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 5 |
| True differentiable J2 QP-HistoryGNO | True-J2 active QP frac. | 0.404611 | 0.372307 | 0.501195 | 0 | 0.534665 | 0.534665 | 0 | 0.987193 | 5 |
| True differentiable J2 QP-HistoryGNO | Eqp increment rel. L2 | 1.66538 | 0.746546 | 1.46114 | 1 | 1.84923 | 0.84923 | 1 | 3.01656 | 5 |
| True differentiable J2 QP-HistoryGNO | Plastic-work inc. rel. L2 | 1.62914 | 0.714048 | 1.4197 | 1 | 1.79876 | 0.798762 | 1 | 2.92724 | 5 |
| True differentiable J2 QP-HistoryGNO | Reversal hist-inc. rel. L2 | 1.04006 | 0.0438084 | 1.01417 | 1.00005 | 1.08577 | 0.0857202 | 1 | 1.10032 | 5 |
| True differentiable J2 QP-HistoryGNO | Reversal yield-flag MAE | 0.432514 | 0.171304 | 0.384335 | 0.269126 | 0.518215 | 0.249089 | 0.269126 | 0.721767 | 5 |
| True differentiable J2 QP-HistoryGNO | Yield-surface RMS | 0.0179605 | 0.0196229 | 0.00646064 | 0 | 0.0382418 | 0.0382418 | 0 | 0.0450999 | 5 |
| True differentiable J2 QP-HistoryGNO | Plastic-work violation abs. | 5.38551e-10 | 5.30148e-10 | 6.14346e-10 | 0 | 6.40355e-10 | 6.40355e-10 | 0 | 1.43805e-09 | 5 |
| True differentiable J2 QP-HistoryGNO | Plastic-work violation target-norm. | 3.31193e-05 | 3.26026e-05 | 3.77805e-05 | 0 | 3.938e-05 | 3.938e-05 | 0 | 8.8436e-05 | 5 |
| True differentiable J2 QP-HistoryGNO | Plastic-work violation pred-norm. | 2.22195e-05 | 2.71262e-05 | 1.3301e-05 | 0 | 2.45192e-05 | 2.45192e-05 | 0 | 7.32773e-05 | 5 |
| True differentiable J2 QP-HistoryGNO | FEM residual rel. RMS | 8.35489 | 4.65433 | 9.77664 | 3.08769 | 12.9875 | 9.89985 | 2.63316 | 13.2894 | 5 |
| True differentiable J2 QP-HistoryGNO | FEM energy rel. err. | 102.077 | 77.5512 | 126.397 | 21.3961 | 150.428 | 129.032 | 4.5933 | 207.572 | 5 |
| True differentiable J2 QP-HistoryGNO | FEM tangent-solver rel. RMS | 209.992 | 177.454 | 118.459 | 73.9762 | 393.8 | 319.824 | 12.969 | 450.756 | 5 |
| True differentiable J2 QP-HistoryGNO | Newton initial residual rel. RMS | 8.17648 | 4.56469 | 9.56773 | 2.96092 | 12.7557 | 9.79482 | 2.61297 | 12.985 | 5 |
| True differentiable J2 QP-HistoryGNO | Newton final residual rel. RMS | 1.02207 | 0.57059 | 1.19597 | 0.370117 | 1.59447 | 1.22436 | 0.326621 | 1.62314 | 5 |
| True differentiable J2 QP-HistoryGNO | Newton residual ratio | 0.125001 | 3.02314e-07 | 0.125 | 0.125 | 0.125001 | 4.32134e-07 | 0.125 | 0.125001 | 5 |
| True differentiable J2 QP-HistoryGNO | Newton residual decrease frac. | 0.874999 | 3.05325e-07 | 0.875 | 0.874999 | 0.875 | 4.17233e-07 | 0.874999 | 0.875 | 5 |
| True differentiable J2 QP-HistoryGNO | Newton step decrease frac. | 0.499999 | 4.00905e-07 | 0.499999 | 0.499999 | 0.499999 | 5.66244e-07 | 0.499999 | 0.5 | 5 |
| True differentiable J2 QP-HistoryGNO | Newton step 1 residual ratio | 0.500001 | 3.94293e-07 | 0.500001 | 0.500001 | 0.500001 | 6.55651e-07 | 0.5 | 0.500001 | 5 |
| True differentiable J2 QP-HistoryGNO | Newton step 2 residual ratio | 0.250001 | 4.28822e-07 | 0.250001 | 0.250001 | 0.250001 | 7.45058e-07 | 0.25 | 0.250001 | 5 |
| True differentiable J2 QP-HistoryGNO | Newton step 3 residual ratio | 0.125001 | 3.02314e-07 | 0.125 | 0.125 | 0.125001 | 4.32134e-07 | 0.125 | 0.125001 | 5 |
| True differentiable J2 QP-HistoryGNO | Newton step 1 decrease frac. | 0.499999 | 4.09497e-07 | 0.499999 | 0.499999 | 0.499999 | 6.55651e-07 | 0.499999 | 0.5 | 5 |
| True differentiable J2 QP-HistoryGNO | Newton step 2 decrease frac. | 0.749999 | 4.22479e-07 | 0.749999 | 0.749999 | 0.749999 | 7.15256e-07 | 0.749999 | 0.75 | 5 |
| True differentiable J2 QP-HistoryGNO | Newton step 3 decrease frac. | 0.874999 | 3.05325e-07 | 0.875 | 0.874999 | 0.875 | 4.17233e-07 | 0.874999 | 0.875 | 5 |
| True differentiable J2 QP-HistoryGNO | Newton correction rel. norm | 3.91736 | 4.87792 | 1.64001 | 0.359753 | 4.25741 | 3.89766 | 0.110625 | 13.219 | 5 |
| True differentiable J2 QP-HistoryGNO | Newton accepted damping | 0.5 | 0 | 0.5 | 0.5 | 0.5 | 0 | 0.5 | 0.5 | 5 |
| True differentiable J2 QP-HistoryGNO | Newton convergence rate | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 5 |
| True differentiable J2 QP-HistoryGNO | Newton failure rate | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 5 |