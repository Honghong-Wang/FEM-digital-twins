# Posterior calibration gain aggregate by protocol and sparse sensor setting

This table promotes material/history posterior calibration from appendix diagnostics to the main evidence chain.

| Protocol | Sparse config | Target | Metric | Direction | Gain mean | Gain std | Gain median | Gain IQR | Improved paths | Paths | Eval paths |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| family_upper_bound | s6_t3 | field | coverage_95 | higher | 0.911637 | 0.0293023 | 0.919775 | 0.0139733 | 6 | 6 | cyclic,monotonic,nonproportional,pre_stress,random_amplitude,unload_reload |
| family_upper_bound | s6_t3 | field | crps | lower | -0.0293827 | 0.0284598 | -0.0253935 | 0.0425096 | 1 | 6 | cyclic,monotonic,nonproportional,pre_stress,random_amplitude,unload_reload |
| family_upper_bound | s6_t3 | field | ece | lower | 0.679857 | 0.00921735 | 0.683063 | 0.00312675 | 6 | 6 | cyclic,monotonic,nonproportional,pre_stress,random_amplitude,unload_reload |
| family_upper_bound | s6_t3 | field | nll | lower | 262729 | 19170.2 | 256015 | 26278.5 | 6 | 6 | cyclic,monotonic,nonproportional,pre_stress,random_amplitude,unload_reload |
| family_upper_bound | s6_t3 | history | coverage_95 | higher | 0.78662 | 0.0183082 | 0.782999 | 0.0158133 | 6 | 6 | cyclic,monotonic,nonproportional,pre_stress,random_amplitude,unload_reload |
| family_upper_bound | s6_t3 | history | ece | lower | 0.618939 | 0.00804331 | 0.617648 | 0.005634 | 6 | 6 | cyclic,monotonic,nonproportional,pre_stress,random_amplitude,unload_reload |
| family_upper_bound | s6_t3 | history | nll | lower | 857591 | 274826 | 782772 | 310178 | 6 | 6 | cyclic,monotonic,nonproportional,pre_stress,random_amplitude,unload_reload |
| family_upper_bound | s6_t3 | material_parameter | coverage_95 | higher | 0.955556 | 0.018002 | 0.960417 | 0.021875 | 6 | 6 | cyclic,monotonic,nonproportional,pre_stress,random_amplitude,unload_reload |
| family_upper_bound | s6_t3 | material_parameter | ece | lower | 0.634132 | 0.0180699 | 0.634479 | 0.0270835 | 6 | 6 | cyclic,monotonic,nonproportional,pre_stress,random_amplitude,unload_reload |
| family_upper_bound | s6_t3 | material_parameter | nll | lower | 26532.7 | 19141.2 | 20017.4 | 8223.22 | 6 | 6 | cyclic,monotonic,nonproportional,pre_stress,random_amplitude,unload_reload |
