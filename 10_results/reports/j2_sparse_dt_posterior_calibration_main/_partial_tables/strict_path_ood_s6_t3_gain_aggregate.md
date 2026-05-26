# Posterior calibration gain aggregate by protocol and sparse sensor setting

This table promotes material/history posterior calibration from appendix diagnostics to the main evidence chain.

| Protocol | Sparse config | Target | Metric | Direction | Gain mean | Gain std | Gain median | Gain IQR | Improved paths | Paths | Eval paths |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| strict_path_ood | s6_t3 | field | coverage_95 | higher | 0.916302 | 0.0187807 | 0.909115 | 0.028679 | 5 | 5 | cyclic,nonproportional,pre_stress,random_amplitude,unload_reload |
| strict_path_ood | s6_t3 | field | crps | lower | -0.574932 | 0.627952 | -0.240552 | 1.06719 | 0 | 5 | cyclic,nonproportional,pre_stress,random_amplitude,unload_reload |
| strict_path_ood | s6_t3 | field | ece | lower | 0.635501 | 0.0321956 | 0.634715 | 0.04167 | 5 | 5 | cyclic,nonproportional,pre_stress,random_amplitude,unload_reload |
| strict_path_ood | s6_t3 | field | nll | lower | 54574.2 | 29319 | 61596.3 | 32193.9 | 5 | 5 | cyclic,nonproportional,pre_stress,random_amplitude,unload_reload |
| strict_path_ood | s6_t3 | history | coverage_95 | higher | 0.799148 | 0.0214486 | 0.794919 | 0.012861 | 5 | 5 | cyclic,nonproportional,pre_stress,random_amplitude,unload_reload |
| strict_path_ood | s6_t3 | history | ece | lower | 0.627748 | 0.0195506 | 0.636963 | 0.015583 | 5 | 5 | cyclic,nonproportional,pre_stress,random_amplitude,unload_reload |
| strict_path_ood | s6_t3 | history | nll | lower | 2.38518e+06 | 761803 | 2.5934e+06 | 115500 | 5 | 5 | cyclic,nonproportional,pre_stress,random_amplitude,unload_reload |
| strict_path_ood | s6_t3 | material_parameter | coverage_95 | higher | 0.895833 | 0.0244738 | 0.9 | 0.041667 | 5 | 5 | cyclic,nonproportional,pre_stress,random_amplitude,unload_reload |
| strict_path_ood | s6_t3 | material_parameter | ece | lower | 0.566458 | 0.0545164 | 0.591875 | 0.093542 | 5 | 5 | cyclic,nonproportional,pre_stress,random_amplitude,unload_reload |
| strict_path_ood | s6_t3 | material_parameter | nll | lower | 143851 | 87679.7 | 141553 | 123828 | 5 | 5 | cyclic,nonproportional,pre_stress,random_amplitude,unload_reload |
