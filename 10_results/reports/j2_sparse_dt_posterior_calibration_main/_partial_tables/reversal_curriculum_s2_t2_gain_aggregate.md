# Posterior calibration gain aggregate by protocol and sparse sensor setting

This table promotes material/history posterior calibration from appendix diagnostics to the main evidence chain.

| Protocol | Sparse config | Target | Metric | Direction | Gain mean | Gain std | Gain median | Gain IQR | Improved paths | Paths | Eval paths |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| reversal_curriculum | s2_t2 | field | coverage_95 | higher | 0.899324 | 0.0304252 | 0.899479 | 0.0243412 | 4 | 4 | cyclic,nonproportional,pre_stress,random_amplitude |
| reversal_curriculum | s2_t2 | field | crps | lower | -0.395527 | 0.443741 | -0.379246 | 0.746136 | 0 | 4 | cyclic,nonproportional,pre_stress,random_amplitude |
| reversal_curriculum | s2_t2 | field | ece | lower | 0.652567 | 0.0162303 | 0.65803 | 0.0167217 | 4 | 4 | cyclic,nonproportional,pre_stress,random_amplitude |
| reversal_curriculum | s2_t2 | field | nll | lower | 82851.6 | 37016.6 | 95544 | 23148.5 | 4 | 4 | cyclic,nonproportional,pre_stress,random_amplitude |
| reversal_curriculum | s2_t2 | history | coverage_95 | higher | 0.835773 | 0.0211629 | 0.833128 | 0.032721 | 4 | 4 | cyclic,nonproportional,pre_stress,random_amplitude |
| reversal_curriculum | s2_t2 | history | ece | lower | 0.634268 | 0.00769209 | 0.632753 | 0.0110042 | 4 | 4 | cyclic,nonproportional,pre_stress,random_amplitude |
| reversal_curriculum | s2_t2 | history | nll | lower | 397193 | 224833 | 384122 | 352083 | 4 | 4 | cyclic,nonproportional,pre_stress,random_amplitude |
| reversal_curriculum | s2_t2 | material_parameter | coverage_95 | higher | 0.89375 | 0.0756528 | 0.897917 | 0.095833 | 4 | 4 | cyclic,nonproportional,pre_stress,random_amplitude |
| reversal_curriculum | s2_t2 | material_parameter | ece | lower | 0.609063 | 0.035837 | 0.596667 | 0.0265625 | 4 | 4 | cyclic,nonproportional,pre_stress,random_amplitude |
| reversal_curriculum | s2_t2 | material_parameter | nll | lower | 431363 | 731656 | 96687.7 | 425304 | 4 | 4 | cyclic,nonproportional,pre_stress,random_amplitude |
