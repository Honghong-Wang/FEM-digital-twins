# J2 Path-Dependent Baseline Robust Statistics

Each row reports both mean/std and robust median/IQR statistics on the cyclic primary test path.
All evaluated paths are stored in JSON: `monotonic, unload_reload, cyclic, nonproportional`.

| Model | Metric | Mean | Std | Median | Q1 | Q3 | IQR | Min | Max | N |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| True differentiable J2 QP-HistoryGNO | Cyclic disp. rel. L2 | 69.0275 | 38.2175 | 57.7986 | 38.3408 | 84.1499 | 45.8091 | 29.2851 | 135.563 | 5 |
| True differentiable J2 QP-HistoryGNO | Cyclic history rel. L2 | 1.15443 | 0.0311665 | 1.17089 | 1.15411 | 1.1749 | 0.0207868 | 1.09431 | 1.17794 | 5 |
| True differentiable J2 QP-HistoryGNO | History-increment rel. L2 | 1.06336 | 0.106484 | 1.01267 | 1.01046 | 1.0174 | 0.00694025 | 1.00024 | 1.27603 | 5 |
| True differentiable J2 QP-HistoryGNO | QP history rel. L2 | 1.92863 | 0.0345991 | 1.94659 | 1.92853 | 1.95101 | 0.0224794 | 1.86185 | 1.95515 | 5 |
| True differentiable J2 QP-HistoryGNO | QP history-inc. rel. L2 | 1.21717 | 0.318444 | 1.0789 | 1.05198 | 1.1033 | 0.0513134 | 1.00122 | 1.85044 | 5 |
| True differentiable J2 QP-HistoryGNO | QP eqp rel. L2 | 6.16425 | 1.71374 | 6.52221 | 5.27175 | 7.50479 | 2.23304 | 3.34898 | 8.17351 | 5 |
| True differentiable J2 QP-HistoryGNO | QP plastic-work rel. L2 | 6.56368 | 1.96866 | 6.86375 | 5.51479 | 8.32366 | 2.80887 | 3.35818 | 8.75803 | 5 |
| True differentiable J2 QP-HistoryGNO | QP von-Mises rel. L2 | 0.885837 | 0.0362205 | 0.887167 | 0.870914 | 0.899 | 0.0280861 | 0.830547 | 0.941559 | 5 |
| True differentiable J2 QP-HistoryGNO | QP reversal scalar-inc. rel. L2 | 1.16102 | 0.267792 | 1.0243 | 1.00817 | 1.07886 | 0.0706851 | 1.00001 | 1.69378 | 5 |
| True differentiable J2 QP-HistoryGNO | QP reversal eqp-inc. rel. L2 | 2.77116 | 0.771199 | 2.74888 | 2.4656 | 3.51662 | 1.05102 | 1.50477 | 3.61994 | 5 |
| True differentiable J2 QP-HistoryGNO | QP reversal work-inc. rel. L2 | 2.95373 | 0.875209 | 2.94434 | 2.57279 | 3.85721 | 1.28442 | 1.52737 | 3.86695 | 5 |
| True differentiable J2 QP-HistoryGNO | QP reversal yield MAE | 0.142453 | 0.0373486 | 0.125786 | 0.121069 | 0.127358 | 0.00628931 | 0.121069 | 0.216981 | 5 |
| True differentiable J2 QP-HistoryGNO | QP inactive false plasticity | 0.490984 | 0.0128561 | 0.497905 | 0.492254 | 0.498963 | 0.00670838 | 0.465833 | 0.499964 | 5 |
| True differentiable J2 QP-HistoryGNO | True-J2 consistency rel. RMS | 0.037044 | 0.0468942 | 0.0191294 | 0.0110509 | 0.0250121 | 0.0139612 | 0.000634643 | 0.129393 | 5 |
| True differentiable J2 QP-HistoryGNO | True-J2 active consistency rel. RMS | 1.02622e-07 | 2.88468e-08 | 1.00255e-07 | 8.90813e-08 | 1.06727e-07 | 1.76457e-08 | 6.44472e-08 | 1.52598e-07 | 5 |
| True differentiable J2 QP-HistoryGNO | True-J2 negative dgamma | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 5 |
| True differentiable J2 QP-HistoryGNO | True-J2 active QP frac. | 0.966667 | 0.0494688 | 0.992244 | 0.97619 | 0.996032 | 0.0198413 | 0.869048 | 0.99982 | 5 |
| True differentiable J2 QP-HistoryGNO | Eqp increment rel. L2 | 7.76002 | 1.92641 | 8.15219 | 7.47393 | 8.34184 | 0.867919 | 4.43745 | 10.3947 | 5 |
| True differentiable J2 QP-HistoryGNO | Plastic-work inc. rel. L2 | 8.31258 | 2.14123 | 8.85537 | 8.07987 | 8.89238 | 0.812512 | 4.56285 | 11.1725 | 5 |
| True differentiable J2 QP-HistoryGNO | Reversal hist-inc. rel. L2 | 1.17723 | 0.312032 | 1.01185 | 1.00782 | 1.06713 | 0.0593163 | 0.999872 | 1.79948 | 5 |
| True differentiable J2 QP-HistoryGNO | Reversal yield-flag MAE | 0.456566 | 0.00159239 | 0.455988 | 0.455507 | 0.457912 | 0.00240499 | 0.454545 | 0.458874 | 5 |
| True differentiable J2 QP-HistoryGNO | Yield-surface RMS | 0.0103429 | 0.0136724 | 0.00403641 | 0.00346603 | 0.00661661 | 0.00315059 | 0.000213372 | 0.0373821 | 5 |
| True differentiable J2 QP-HistoryGNO | Plastic-work violation abs. | 3.942e-07 | 7.45113e-07 | 1.66536e-08 | 0 | 7.0829e-08 | 7.0829e-08 | 0 | 1.88352e-06 | 5 |
| True differentiable J2 QP-HistoryGNO | Plastic-work violation target-norm. | 0.0147151 | 0.0278144 | 0.000621665 | 0 | 0.00264398 | 0.00264398 | 0 | 0.0703101 | 5 |
| True differentiable J2 QP-HistoryGNO | Plastic-work violation pred-norm. | 0.0013103 | 0.00244064 | 7.58479e-05 | 0 | 0.000288667 | 0.000288667 | 0 | 0.00618701 | 5 |
| True differentiable J2 QP-HistoryGNO | FEM residual rel. RMS | 38.0569 | 12.9208 | 40.4128 | 39.8296 | 40.5473 | 0.717747 | 14.7731 | 54.7215 | 5 |
| True differentiable J2 QP-HistoryGNO | FEM energy rel. err. | 1166.29 | 662.732 | 1394.46 | 581.674 | 1750.14 | 1168.46 | 205.392 | 1899.8 | 5 |
| True differentiable J2 QP-HistoryGNO | FEM tangent-solver rel. RMS | 6.7434 | 4.55683 | 4.03982 | 3.99934 | 6.14146 | 2.14212 | 3.83847 | 15.6979 | 5 |