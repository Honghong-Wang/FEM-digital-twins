# FEM2D Final Fair Baseline Table

All rows are generated from the same baseline-runner JSON artifact.

Source: `10_results\reports\fem2d_final_fair_baseline_results.json`

| Model | Seeds | Strategy | Test rel. L2 | Test FEM residual rel. | Test boundary rel. | Test energy rel. | OOD material rel. L2 | OOD loading rel. L2 |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| pinn | 5 | data=mse, curriculum=constant | 0.5882 +/- 0.0513 | 1.9949 +/- 0.1579 | 0.5391 +/- 0.0673 | 2.0182 +/- 0.0980 | 1.8266 +/- 0.3619 | 0.5664 +/- 0.0216 |
| deeponet | 5 | data=mse, curriculum=constant | 0.4636 +/- 0.0327 | 3.8092 +/- 0.2622 | 0.1159 +/- 0.0106 | 3.0713 +/- 0.6266 | 1.6157 +/- 0.2428 | 0.3803 +/- 0.0171 |
| fno | 5 | data=mse, curriculum=constant | 0.6941 +/- 0.0345 | 1.8879 +/- 0.1530 | 0.1963 +/- 0.0711 | 2.8804 +/- 0.4112 | 2.1413 +/- 0.2001 | 0.5586 +/- 0.0793 |
| meshgno | 5 | data=mse, curriculum=constant | 0.6290 +/- 0.0096 | 1.7263 +/- 0.1478 | 0.6517 +/- 0.0438 | 2.5625 +/- 0.4315 | 1.4817 +/- 0.5372 | 0.5933 +/- 0.0109 |
| mesh2meshgno | 5 | data=mse, curriculum=constant | 0.6129 +/- 0.0977 | 2.0459 +/- 0.5902 | 0.3758 +/- 0.0443 | 3.6614 +/- 1.0139 | 1.5010 +/- 0.3024 | 0.5806 +/- 0.0670 |
| pcgno | 5 | data=mse, curriculum=constant | 0.5424 +/- 0.0254 | 2.5878 +/- 0.2099 | 0.4678 +/- 0.0413 | 2.8508 +/- 0.0834 | 1.5538 +/- 0.5721 | 0.5794 +/- 0.0683 |
