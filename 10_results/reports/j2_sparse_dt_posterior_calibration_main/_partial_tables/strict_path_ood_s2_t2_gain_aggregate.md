# Posterior calibration gain aggregate by protocol and sparse sensor setting

This table promotes material/history posterior calibration from appendix diagnostics to the main evidence chain.

| Protocol | Sparse config | Target | Metric | Direction | Gain mean | Gain std | Gain median | Gain IQR | Improved paths | Paths | Eval paths |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| strict_path_ood | s2_t2 | field | coverage_95 | higher | 0.902148 | 0.0293966 | 0.91071 | 0.014876 | 5 | 5 | cyclic,nonproportional,pre_stress,random_amplitude,unload_reload |
| strict_path_ood | s2_t2 | field | crps | lower | -1.76834 | 0.897295 | -1.88014 | 0.60894 | 0 | 5 | cyclic,nonproportional,pre_stress,random_amplitude,unload_reload |
| strict_path_ood | s2_t2 | field | ece | lower | 0.60918 | 0.0169155 | 0.619487 | 0.02167 | 5 | 5 | cyclic,nonproportional,pre_stress,random_amplitude,unload_reload |
| strict_path_ood | s2_t2 | field | nll | lower | 50855.6 | 26828.9 | 57601.6 | 30750.8 | 5 | 5 | cyclic,nonproportional,pre_stress,random_amplitude,unload_reload |
| strict_path_ood | s2_t2 | history | coverage_95 | higher | 0.806187 | 0.02825 | 0.797867 | 0.038136 | 5 | 5 | cyclic,nonproportional,pre_stress,random_amplitude,unload_reload |
| strict_path_ood | s2_t2 | history | ece | lower | 0.617808 | 0.0249921 | 0.620999 | 0.008967 | 5 | 5 | cyclic,nonproportional,pre_stress,random_amplitude,unload_reload |
| strict_path_ood | s2_t2 | history | nll | lower | 2.32898e+06 | 771030 | 2.53563e+06 | 308280 | 5 | 5 | cyclic,nonproportional,pre_stress,random_amplitude,unload_reload |
| strict_path_ood | s2_t2 | material_parameter | coverage_95 | higher | 0.831667 | 0.0361562 | 0.833333 | 0.041666 | 5 | 5 | cyclic,nonproportional,pre_stress,random_amplitude,unload_reload |
| strict_path_ood | s2_t2 | material_parameter | ece | lower | 0.51975 | 0.0318827 | 0.527083 | 0.02625 | 5 | 5 | cyclic,nonproportional,pre_stress,random_amplitude,unload_reload |
| strict_path_ood | s2_t2 | material_parameter | nll | lower | 67869.1 | 53394.9 | 51706.5 | 68020.5 | 5 | 5 | cyclic,nonproportional,pre_stress,random_amplitude,unload_reload |
