# J2 Path-Dependent Baseline Per-Seed Appendix

Per-seed cyclic-primary metrics for diagnosing stochastic training stability and outliers.
All evaluated paths are stored in JSON: `monotonic, cyclic`.

| Model | Seed | Train final loss | Cyclic disp. rel. L2 | Cyclic history rel. L2 | History-increment rel. L2 | Eqp increment rel. L2 | Plastic-work inc. rel. L2 | Reversal hist-inc. rel. L2 | Reversal yield-flag MAE | Yield-surface RMS | Plastic-work violation abs. | Plastic-work violation target-norm. | Plastic-work violation pred-norm. | HANO strain rel. L2 | HANO stress rel. L2 | FEM residual rel. RMS | FEM energy rel. err. |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Faithful HANO strain-stress spectral-window NO | 20260517 | 5583.51 | 50.8347 | 1.3517 | 1.0083 | 21.8122 | 17.4435 | 1.00792 | 0.532178 | 0.433509 | 0.000282952 | 10.5624 | 0.594165 | 11.433 | 13.9163 | 353.302 | 64906.9 |
| Faithful HANO strain-stress spectral-window NO | 20260518 | 5626.58 | 399.227 | 2.88287 | 1.01319 | 60.3736 | 4.11704 | 1.00546 | 0.539328 | 0.327621 | 0.00270552 | 100.995 | 23.1026 | 168.96 | 11.0688 | 4790.36 | 9.15615e+06 |
| Faithful HANO strain-stress spectral-window NO | 20260519 | 5313.34 | 253.171 | 2.75658 | 1.01789 | 109.599 | 49.7978 | 1.00843 | 0.464271 | 0.8448 | 0.00636245 | 237.504 | 4.73565 | 54.3828 | 16.813 | 649.718 | 238337 |
| Faithful HANO strain-stress spectral-window NO | 20260520 | 23431.4 | 204.699 | 1.79439 | 1.00408 | 62.2489 | 2.0353 | 1.01221 | 0.543766 | 0.00853603 | 0.00299661 | 111.861 | 51.3697 | 37.3725 | 11.0025 | 828.225 | 358780 |
| Faithful HANO strain-stress spectral-window NO | 20260521 | 5188.51 | 188.392 | 0.914994 | 0.997124 | 32.4175 | 39.8634 | 1.01561 | 0.484663 | 0.124847 | 0.000221615 | 8.27269 | 0.205724 | 30.6717 | 10.3118 | 599.407 | 242033 |