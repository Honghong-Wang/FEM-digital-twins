# J2 Path-Dependent Baseline Outlier Diagnostics

Outliers are detected on cyclic-primary metrics using a 1.5 IQR rule when IQR is nonzero, otherwise a 3 sigma rule is used.
All evaluated paths are stored in JSON: `monotonic, cyclic`.

| Model | Metric | Rule | Lower | Upper | Outlier count | Outlier seeds | Mean | Std | Median | IQR | Min | Max |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Faithful HANO strain-stress spectral-window NO | Cyclic disp. rel. L2 | 1.5*IQR | 91.2225 | 350.34 | 2 | 20260517=50.8347; 20260518=399.227 | 219.265 | 112.312 | 204.699 | 64.7795 | 50.8347 | 399.227 |
| Faithful HANO strain-stress spectral-window NO | Eqp increment rel. L2 | 1.5*IQR | -12.3297 | 106.996 | 1 | 20260519=109.599 | 57.2902 | 30.4881 | 60.3736 | 29.8314 | 21.8122 | 109.599 |
| Faithful HANO strain-stress spectral-window NO | HANO strain rel. L2 | 1.5*IQR | -4.89508 | 89.9496 | 1 | 20260518=168.96 | 60.564 | 55.9163 | 37.3725 | 23.7112 | 11.433 | 168.96 |
| Faithful HANO strain-stress spectral-window NO | FEM residual rel. RMS | 1.5*IQR | 256.18 | 1171.45 | 1 | 20260518=4790.36 | 1444.2 | 1679.95 | 649.718 | 228.818 | 353.302 | 4790.36 |
| Faithful HANO strain-stress spectral-window NO | FEM energy rel. err. | 1.5*IQR | 57673.2 | 539445 | 1 | 20260518=9.15615e+06 | 2.01204e+06 | 3.57329e+06 | 242033 | 120443 | 64906.9 | 9.15615e+06 |