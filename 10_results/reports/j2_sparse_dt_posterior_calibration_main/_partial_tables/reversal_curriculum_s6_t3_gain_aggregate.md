# Posterior calibration gain aggregate by protocol and sparse sensor setting

This table promotes material/history posterior calibration from appendix diagnostics to the main evidence chain.

| Protocol | Sparse config | Target | Metric | Direction | Gain mean | Gain std | Gain median | Gain IQR | Improved paths | Paths | Eval paths |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| reversal_curriculum | s6_t3 | field | coverage_95 | higher | 0.859351 | 0.0684399 | 0.838086 | 0.0621333 | 4 | 4 | cyclic,nonproportional,pre_stress,random_amplitude |
| reversal_curriculum | s6_t3 | field | crps | lower | -0.0461046 | 0.0590712 | -0.0193743 | 0.0326821 | 0 | 4 | cyclic,nonproportional,pre_stress,random_amplitude |
| reversal_curriculum | s6_t3 | field | ece | lower | 0.647984 | 0.0252535 | 0.658776 | 0.0203473 | 4 | 4 | cyclic,nonproportional,pre_stress,random_amplitude |
| reversal_curriculum | s6_t3 | field | nll | lower | 91052.6 | 47209.2 | 101757 | 34322.6 | 4 | 4 | cyclic,nonproportional,pre_stress,random_amplitude |
| reversal_curriculum | s6_t3 | history | coverage_95 | higher | 0.821406 | 0.0229646 | 0.825538 | 0.0284363 | 4 | 4 | cyclic,nonproportional,pre_stress,random_amplitude |
| reversal_curriculum | s6_t3 | history | ece | lower | 0.621779 | 0.00689719 | 0.621531 | 0.0071865 | 4 | 4 | cyclic,nonproportional,pre_stress,random_amplitude |
| reversal_curriculum | s6_t3 | history | nll | lower | 388621 | 192612 | 388180 | 265050 | 4 | 4 | cyclic,nonproportional,pre_stress,random_amplitude |
| reversal_curriculum | s6_t3 | material_parameter | coverage_95 | higher | 0.895833 | 0.0170102 | 0.895833 | 0.0270833 | 4 | 4 | cyclic,nonproportional,pre_stress,random_amplitude |
| reversal_curriculum | s6_t3 | material_parameter | ece | lower | 0.638073 | 0.0654705 | 0.64 | 0.0676567 | 4 | 4 | cyclic,nonproportional,pre_stress,random_amplitude |
| reversal_curriculum | s6_t3 | material_parameter | nll | lower | 36900.1 | 33052.4 | 31554 | 37124.7 | 4 | 4 | cyclic,nonproportional,pre_stress,random_amplitude |
