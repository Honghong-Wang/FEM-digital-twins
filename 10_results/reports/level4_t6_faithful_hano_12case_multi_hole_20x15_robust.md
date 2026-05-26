# J2 Path-Dependent Baseline Robust Statistics

Each row reports both mean/std and robust median/IQR statistics on the cyclic primary test path.
All evaluated paths are stored in JSON: `monotonic, cyclic`.

| Model | Metric | Mean | Std | Median | Q1 | Q3 | IQR | Min | Max | N |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Faithful HANO strain-stress spectral-window NO | Cyclic disp. rel. L2 | 173.43 | 75.3329 | 138.936 | 137.024 | 148.442 | 11.4187 | 119.792 | 322.958 | 5 |
| Faithful HANO strain-stress spectral-window NO | Cyclic history rel. L2 | 1.94382 | 0.604739 | 1.94085 | 1.48317 | 1.98412 | 0.500953 | 1.28223 | 3.02872 | 5 |
| Faithful HANO strain-stress spectral-window NO | History-increment rel. L2 | 1.01472 | 0.0104637 | 1.013 | 1.00427 | 1.02232 | 0.0180577 | 1.00347 | 1.03056 | 5 |
| Faithful HANO strain-stress spectral-window NO | Eqp increment rel. L2 | 540.791 | 321.725 | 330.517 | 323.201 | 899.717 | 576.516 | 191.352 | 959.165 | 5 |
| Faithful HANO strain-stress spectral-window NO | Plastic-work inc. rel. L2 | 544.224 | 409.282 | 335.529 | 158.766 | 1025.51 | 866.744 | 149.313 | 1052 | 5 |
| Faithful HANO strain-stress spectral-window NO | Reversal hist-inc. rel. L2 | 1.01863 | 0.0142858 | 1.00924 | 1.0064 | 1.03355 | 0.0271578 | 1.00559 | 1.03837 | 5 |
| Faithful HANO strain-stress spectral-window NO | Reversal yield-flag MAE | 0.400768 | 0.169947 | 0.278867 | 0.266149 | 0.583197 | 0.317047 | 0.243647 | 0.631982 | 5 |
| Faithful HANO strain-stress spectral-window NO | Yield-surface RMS | 0.267362 | 0.243246 | 0.14567 | 0.0949611 | 0.421723 | 0.326762 | 0.00728717 | 0.667168 | 5 |
| Faithful HANO strain-stress spectral-window NO | Plastic-work violation abs. | 0.0380455 | 0.0395551 | 0.0115792 | 0.00383842 | 0.0840829 | 0.0802444 | 0.0022015 | 0.0885254 | 5 |
| Faithful HANO strain-stress spectral-window NO | Plastic-work violation target-norm. | 3449.04 | 3585.9 | 1049.72 | 347.975 | 7622.6 | 7274.62 | 199.579 | 8025.33 | 5 |
| Faithful HANO strain-stress spectral-window NO | Plastic-work violation pred-norm. | 12.7398 | 17.8713 | 7.01804 | 0.594348 | 7.82368 | 7.22933 | 0.330692 | 47.9323 | 5 |
| Faithful HANO strain-stress spectral-window NO | HANO strain rel. L2 | 60.4592 | 27.6695 | 59.067 | 52.6761 | 84.4778 | 31.8017 | 13.8046 | 92.2702 | 5 |
| Faithful HANO strain-stress spectral-window NO | HANO stress rel. L2 | 12.8641 | 3.97214 | 12.68 | 9.5555 | 15.6342 | 6.07873 | 7.74921 | 18.7013 | 5 |
| Faithful HANO strain-stress spectral-window NO | FEM residual rel. RMS | 1755.9 | 732.309 | 1930.7 | 1308.34 | 2185.92 | 877.57 | 615.853 | 2738.7 | 5 |
| Faithful HANO strain-stress spectral-window NO | FEM energy rel. err. | 1.19115e+06 | 943416 | 1.03782e+06 | 661907 | 1.26664e+06 | 604738 | 88181.6 | 2.90121e+06 | 5 |