# Posterior calibration gain aggregate by protocol and sparse sensor setting

This table promotes material/history posterior calibration from appendix diagnostics to the main evidence chain.

| Protocol | Sparse config | Target | Metric | Direction | Gain mean | Gain std | Gain median | Gain IQR | Improved paths | Paths | Eval paths |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| family_upper_bound | s2_t2 | field | coverage_95 | higher | 0.849051 | 0.0371023 | 0.848047 | 0.0331713 | 6 | 6 | cyclic,monotonic,nonproportional,pre_stress,random_amplitude,unload_reload |
| family_upper_bound | s2_t2 | field | crps | lower | -0.0608668 | 0.109069 | -0.0162375 | 0.0226426 | 0 | 6 | cyclic,monotonic,nonproportional,pre_stress,random_amplitude,unload_reload |
| family_upper_bound | s2_t2 | field | ece | lower | 0.637075 | 0.0165327 | 0.631646 | 0.0159968 | 6 | 6 | cyclic,monotonic,nonproportional,pre_stress,random_amplitude,unload_reload |
| family_upper_bound | s2_t2 | field | nll | lower | 222790 | 21705.1 | 219122 | 37000.2 | 6 | 6 | cyclic,monotonic,nonproportional,pre_stress,random_amplitude,unload_reload |
| family_upper_bound | s2_t2 | history | coverage_95 | higher | 0.790521 | 0.0267974 | 0.78827 | 0.0402955 | 6 | 6 | cyclic,monotonic,nonproportional,pre_stress,random_amplitude,unload_reload |
| family_upper_bound | s2_t2 | history | ece | lower | 0.62039 | 0.00734029 | 0.620834 | 0.0115715 | 6 | 6 | cyclic,monotonic,nonproportional,pre_stress,random_amplitude,unload_reload |
| family_upper_bound | s2_t2 | history | nll | lower | 880527 | 189879 | 876266 | 178513 | 6 | 6 | cyclic,monotonic,nonproportional,pre_stress,random_amplitude,unload_reload |
| family_upper_bound | s2_t2 | material_parameter | coverage_95 | higher | 0.9375 | 0.0476531 | 0.952084 | 0.077083 | 6 | 6 | cyclic,monotonic,nonproportional,pre_stress,random_amplitude,unload_reload |
| family_upper_bound | s2_t2 | material_parameter | ece | lower | 0.607222 | 0.0282248 | 0.609584 | 0.0266663 | 6 | 6 | cyclic,monotonic,nonproportional,pre_stress,random_amplitude,unload_reload |
| family_upper_bound | s2_t2 | material_parameter | nll | lower | 122945 | 225376 | 26859.6 | 30725 | 6 | 6 | cyclic,monotonic,nonproportional,pre_stress,random_amplitude,unload_reload |
