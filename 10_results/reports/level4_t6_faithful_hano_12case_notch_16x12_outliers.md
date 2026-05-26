# J2 Path-Dependent Baseline Outlier Diagnostics

Outliers are detected on cyclic-primary metrics using a 1.5 IQR rule when IQR is nonzero, otherwise a 3 sigma rule is used.
All evaluated paths are stored in JSON: `monotonic, cyclic`.

| Model | Metric | Rule | Lower | Upper | Outlier count | Outlier seeds | Mean | Std | Median | IQR | Min | Max |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Faithful HANO strain-stress spectral-window NO | Cyclic history rel. L2 | 1.5*IQR | 1.04386 | 3.49935 | 1 | 20260518=4.66618 | 2.66047 | 1.03942 | 2.30559 | 0.613872 | 1.78737 | 4.66618 |
| Faithful HANO strain-stress spectral-window NO | Yield-surface RMS | 1.5*IQR | 0.0593784 | 0.281632 | 2 | 20260519=0.698354; 20260520=0.00349914 | 0.24233 | 0.237599 | 0.168787 | 0.0555634 | 0.00349914 | 0.698354 |
| Faithful HANO strain-stress spectral-window NO | Plastic-work violation pred-norm. | 1.5*IQR | -38.2321 | 69.314 | 1 | 20260520=137.684 | 34.5798 | 52.611 | 4.13316 | 26.8865 | 0.000249096 | 137.684 |
| Faithful HANO strain-stress spectral-window NO | HANO strain rel. L2 | 1.5*IQR | -0.0801964 | 122.56 | 1 | 20260518=280.505 | 94.4432 | 94.8987 | 51.5893 | 30.6601 | 17.6416 | 280.505 |
| Faithful HANO strain-stress spectral-window NO | FEM residual rel. RMS | 1.5*IQR | 359.638 | 2355.53 | 1 | 20260518=11320.5 | 3235.23 | 4055.69 | 1471.33 | 498.974 | 669.167 | 11320.5 |
| Faithful HANO strain-stress spectral-window NO | FEM energy rel. err. | 1.5*IQR | 4583.59 | 1.44178e+06 | 1 | 20260518=3.17676e+07 | 6.84694e+06 | 1.24633e+07 | 869765 | 359298 | 151011 | 3.17676e+07 |