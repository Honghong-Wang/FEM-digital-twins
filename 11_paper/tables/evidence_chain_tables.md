# Evidence Chain Tables

These tables summarize the current paper-scale evidence for the three-layer paper mainline:

```text
L1: surrogate -> operator + FEM evidence
L2: static operator -> stateful path-dependent operator
L3: path-OOD + thermodynamic consistency
```

## L1: PCGNO FEM Evidence Repair

The original paper preset trained PCGNO with Gaussian NLL as the data term. The repair run uses
MSE-first mean-operator fitting while keeping the probabilistic head through calibration loss.
Both rows use 50 epochs and 5 seeds on the same FEM data splits.

| PCGNO training mode | Test relative L2 | Test FEM residual rel. | Test boundary rel. | Test energy rel. | OOD material relative L2 | OOD loading relative L2 |
|---|---:|---:|---:|---:|---:|---:|
| NLL-first paper preset | 0.4513 | 1.3650 | 0.0417 | 0.2986 | 0.6046 | 0.4073 |
| MSE-first repair | 0.0571 | 0.3088 | 0.0435 | 0.0158 | 0.3639 | 0.1951 |

Source artifacts:

```text
10_results/reports/fem2d_operator_evidence_paper.json
10_results/reports/pcgno_fem_evidence_repair_mse_5seeds.json
10_results/reports/fem2d_final_fair_baseline_results.json
11_paper/tables/fem2d_final_fair_baseline_table.md
```

Interpretation:

```text
The main PCGNO FEM-evidence failure mode was not the operator backbone itself.
It was the coupling between mean fitting and NLL/variance learning.
MSE-first training recovers competitive mean prediction and much lower FEM residual/energy error.
```

## L1b: Final Fair FEM Baseline Table

All rows below use the same split, seed set, epoch count, and metrics. PCGNO uses the MSE-first
setting selected by the FEM-evidence repair.

| Model | Seeds | Test rel. L2 | Test FEM residual rel. | Test energy rel. | OOD material rel. L2 | OOD loading rel. L2 |
|---|---:|---:|---:|---:|---:|---:|
| PINN | 5 | 0.5882 +/- 0.0513 | 1.9949 +/- 0.1579 | 2.0182 +/- 0.0980 | 1.8266 +/- 0.3619 | 0.5664 +/- 0.0216 |
| DeepONet | 5 | 0.4636 +/- 0.0327 | 3.8092 +/- 0.2622 | 3.0713 +/- 0.6266 | 1.6157 +/- 0.2428 | 0.3803 +/- 0.0171 |
| FNO | 5 | 0.6941 +/- 0.0345 | 1.8879 +/- 0.1530 | 2.8804 +/- 0.4112 | 2.1413 +/- 0.2001 | 0.5586 +/- 0.0793 |
| MeshGNO | 5 | 0.6290 +/- 0.0096 | 1.7263 +/- 0.1478 | 2.5625 +/- 0.4315 | 1.4817 +/- 0.5372 | 0.5933 +/- 0.0109 |
| Mesh2MeshGNO | 5 | 0.6129 +/- 0.0977 | 2.0459 +/- 0.5902 | 3.6614 +/- 1.0139 | 1.5010 +/- 0.3024 | 0.5806 +/- 0.0670 |
| PCGNO | 5 | 0.5424 +/- 0.0254 | 2.5878 +/- 0.2099 | 2.8508 +/- 0.0834 | 1.5538 +/- 0.5721 | 0.5794 +/- 0.0683 |

Interpretation:

```text
The fair table is mixed rather than one-sided: DeepONet has the best test/OOD-loading relative L2,
MeshGNO has the lowest FEM residual and competitive OOD-material error, and PCGNO is stable but
not dominant in this final baseline setting. This should be written honestly and used to motivate
the stateful/path-dependent contribution rather than overclaiming static FEM superiority.
```

## L2: Cyclic Path-OOD Failure Mode

All rows are 50-epoch HistoryGraphOperator experiments on the same J2 FEM path family. The strict
path-OOD row trains on monotonic paths only. Curriculum and upper-bound rows are diagnostic rows,
not replacements for the strict path-OOD main result.

| Cyclic test metric | Strict path-OOD | Unload curriculum | Cyclic-seen upper bound |
|---|---:|---:|---:|
| Training paths | monotonic | monotonic + unload_reload | monotonic + unload_reload + cyclic |
| Strict path-OOD? | yes | no | no |
| Displacement relative L2 | 0.9795 | 1.1386 | 0.9331 |
| History relative L2 | 1.2678 | 1.0427 | 0.9196 |
| History-increment relative L2 | 1.0202 | 1.0227 | 0.9971 |
| Eq. plastic strain increment relative L2 | 3.5222 | 2.3937 | 2.2702 |
| Yield-flag MAE | 0.5747 | 0.5576 | 0.5084 |
| Total path loss | 2.5728 | 16.6730 | 8.3227 |

Note: total path loss is kept as an experiment diagnostic because repair runs use additional
history-increment terms. Cross-column interpretation should rely primarily on the explicit field
and history metrics above.

Source artifacts:

```text
10_results/reports/j2_path_operator_evidence_paper.json
10_results/reports/j2_path_operator_repair_unload_curriculum.json
10_results/reports/j2_path_operator_repair_cyclic_seen.json
```

Interpretation:

```text
Cyclic degradation is mainly a load-path distribution gap.
History-aware loss terms help, but exposing the operator to unload/reload improves cyclic history error more.
The cyclic-seen row is an upper-bound diagnostic showing the architecture can represent cyclic memory when the path family is present.
```

## L2a: J2 Path-Dependent Baseline Table

This table compares recurrent and static sequence baselines on the same shared-geometry complex
J2 path-OOD split. All rows train on monotonic loading and are evaluated on the cyclic path with
50 epochs and 10 seeds. The static rows receive the same per-step coordinates, parameters, forcing,
and load-step fraction, but do not recurrently propagate `history_t -> history_{t+1}`.

| Model | Seeds | Cyclic disp. rel. L2 | Cyclic history rel. L2 | History-increment rel. L2 | Eqp increment rel. L2 | Plastic-work inc. rel. L2 | Reversal hist-inc. rel. L2 | Reversal yield-flag MAE | Yield-surface RMS | Plastic-work violation abs. | Plastic-work violation target-norm. | Plastic-work violation pred-norm. |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| HistoryGNO thermo-aware | 10 | 1.0340 +/- 0.4259 | 1.0895 +/- 0.0730 | 1.0153 +/- 0.0021 | 2.0019 +/- 0.3693 | 3.8762 +/- 0.5770 | 1.0206 +/- 0.0041 | 0.6970 +/- 0.0428 | 0.5705 +/- 0.0402 | 0.0393 +/- 0.0294 | 3.2706 +/- 2.4507 | 0.8543 +/- 0.7153 |
| HistoryGNO data-only | 10 | 0.8854 +/- 0.0384 | 1.2493 +/- 0.1299 | 1.0211 +/- 0.0040 | 2.2964 +/- 0.5268 | 6.5916 +/- 1.0891 | 1.0264 +/- 0.0040 | 0.6972 +/- 0.0243 | 0.5899 +/- 0.0362 | 0.0432 +/- 0.0351 | 3.5923 +/- 2.9225 | 0.5120 +/- 0.4134 |
| Non-recurrent GNO sequence | 10 | 1.0124 +/- 0.4212 | 0.8394 +/- 0.0214 | 1.0004 +/- 0.0005 | 0.9999 +/- 0.0008 | 1.0000 +/- 0.0001 | 1.0018 +/- 0.0024 | 0.7008 +/- 0.0130 | 0.4126 +/- 0.2868 | 0.0000 +/- 0.0000 | 0.0005 +/- 0.0010 | 455.8454 +/- 1364.0826 |
| Static FNO sequence | 10 | 0.7267 +/- 0.0325 | 0.8152 +/- 0.0139 | 1.0003 +/- 0.0002 | 1.0001 +/- 0.0005 | 1.0001 +/- 0.0002 | 1.0011 +/- 0.0011 | 0.6876 +/- 0.0199 | 0.1978 +/- 0.1515 | 0.0000 +/- 0.0000 | 0.0005 +/- 0.0005 | 3.4821 +/- 7.5776 |
| Static DeepONet sequence | 10 | 0.7214 +/- 0.0463 | 0.8244 +/- 0.0111 | 1.0004 +/- 0.0004 | 1.0000 +/- 0.0008 | 1.0001 +/- 0.0002 | 1.0020 +/- 0.0020 | 0.6993 +/- 0.0090 | 0.2083 +/- 0.1897 | 0.0000 +/- 0.0000 | 0.0008 +/- 0.0011 | 3.8639 +/- 7.5058 |

Source artifacts:

```text
10_results/reports/j2_path_dependent_baseline_table.json
11_paper/tables/j2_path_dependent_baseline_table.csv
11_paper/tables/j2_path_dependent_baseline_table.md
11_paper/tables/j2_path_dependent_baseline_table_robust_stats.csv
11_paper/tables/j2_path_dependent_baseline_table_robust_stats.md
11_paper/tables/j2_path_dependent_baseline_table_per_seed.csv
11_paper/tables/j2_path_dependent_baseline_table_per_seed.md
11_paper/tables/j2_path_dependent_baseline_table_outliers.csv
11_paper/tables/j2_path_dependent_baseline_table_outliers.md
```

Interpretation:

```text
This comparison is deliberately not a one-sided accuracy table. Static FNO/DeepONet-sequence
baselines fit cyclic displacement and snapshot history more strongly on this small shared-geometry
split, but their increment and reversal metrics stay near the no-memory baseline. Thermo-aware
HistoryGNO improves history, eqp increment, plastic-work increment, reversal yield flag, and
yield-surface RMS over data-only HistoryGNO. The predicted-normalized plastic-work violation is
ill-conditioned for static sequence baselines because their predicted plastic-work increments can
approach zero; absolute and target-normalized violations therefore must be reported beside it.
Per-seed and outlier tables show that the huge static-GNO predicted-normalized value is a scaling
pathology rather than a genuinely large absolute violation. The narrow paper claim remains:
recurrent history propagation and thermodynamic losses expose path-memory behavior that static
sequence surrogates do not explicitly model.
```

## L2b: Thermo-Aware Reversal Evidence

These rows repeat the strict / curriculum / upper-bound comparison with thermodynamic consistency
terms enabled. All rows use 50 epochs, the same seed, the same J2 path family, and the same cyclic
test split.

| Cyclic test metric | Strict path-OOD | Unload curriculum | Cyclic-seen upper bound |
|---|---:|---:|---:|
| Training paths | monotonic | monotonic + unload_reload | monotonic + unload_reload + cyclic |
| Strict path-OOD? | yes | no | no |
| Displacement relative L2 | 1.0500 | 1.1388 | 0.9327 |
| History relative L2 | 1.1771 | 1.0417 | 0.9200 |
| History-increment relative L2 | 1.0304 | 1.0227 | 0.9971 |
| Eq. plastic strain increment relative L2 | 3.4598 | 2.3697 | 2.2571 |
| Plastic-work increment relative L2 | 13.2238 | 11.1933 | 7.3771 |
| Yield-flag MAE | 0.5844 | 0.5576 | 0.5089 |
| Reversal history-increment relative L2 | 1.0809 | 1.0686 | 1.0171 |
| Reversal yield-flag MAE | 0.6584 | 0.5975 | 0.4966 |
| Predicted yield-surface relative RMS | 0.5697 | 0.4755 | 0.3908 |
| Plastic-work lower-bound violation | 0.2173 | 0.0000 | 0.0732 |

Source artifacts:

```text
10_results/reports/j2_frontier_thermo_strict.json
10_results/reports/j2_frontier_thermo_unload_curriculum.json
10_results/reports/j2_frontier_thermo_cyclic_seen.json
11_paper/tables/thermo_path_ood_reversal_evidence.csv
```

Interpretation:

```text
Thermo-aware training improves the cyclic memory evidence in the expected diagnostic order:
strict path-OOD remains hard, unload/reload curriculum reduces reversal errors, and cyclic-seen
training gives the upper-bound row. Reversal eqp/plastic-work increment relative errors remain
numerically ill-conditioned because their reversal targets are near zero, so the primary reversal
metrics are reversal history increment and reversal yield flag.
```

## L2c: Failure-Analysis Figure

The failure-analysis figure converts the strict / curriculum / upper-bound rows into a mechanism
view. It compares the structured J2 and shared-hole J2 datasets on cyclic history error, eqp
increment error, reversal yield-flag error, yield-surface consistency, and plastic-work
lower-bound violation.

Source artifacts:

```text
12_reproducibility/scripts/make_path_ood_failure_analysis_figure.py
11_paper/figures/path_ood_failure_analysis.png
11_paper/figures/path_ood_failure_analysis.pdf
11_paper/tables/path_ood_failure_analysis_metrics.csv
```

Interpretation:

```text
The figure should be used as the main failure-analysis visual. It shows that strict monotonic
training remains the stress test, curriculum partially repairs cyclic-history and thermodynamic
metrics, and cyclic-seen training is an architectural upper bound rather than a deployable
path-OOD generalization claim.
```

## L3: Thermo-Aware 5-Seed Path-OOD Evidence

These are the formal 50-epoch, 5-seed cyclic-test statistics for the strict / curriculum /
upper-bound diagnostic rows.

| Cyclic test metric | Strict path-OOD | Unload curriculum | Cyclic-seen upper bound |
|---|---:|---:|---:|
| Displacement relative L2 | 1.0376 +/- 0.1521 | 1.3274 +/- 0.5968 | 0.9965 +/- 0.0968 |
| History relative L2 | 1.1644 +/- 0.1026 | 0.9867 +/- 0.0461 | 0.8584 +/- 0.0378 |
| History-increment relative L2 | 1.0185 +/- 0.0087 | 1.0165 +/- 0.0061 | 0.9918 +/- 0.0063 |
| Eq. plastic strain increment relative L2 | 3.5931 +/- 1.1121 | 2.3066 +/- 0.6022 | 1.6886 +/- 0.4071 |
| Plastic-work increment relative L2 | 11.0740 +/- 1.6219 | 8.5151 +/- 1.2307 | 5.8900 +/- 1.1893 |
| Yield-flag MAE | 0.5551 +/- 0.0207 | 0.5476 +/- 0.0122 | 0.5086 +/- 0.0079 |
| Reversal history-increment relative L2 | 1.0464 +/- 0.0265 | 1.0500 +/- 0.0125 | 1.0034 +/- 0.0054 |
| Reversal yield-flag MAE | 0.6276 +/- 0.0236 | 0.5733 +/- 0.0262 | 0.4975 +/- 0.0185 |
| Predicted yield-surface relative RMS | 0.5291 +/- 0.0371 | 0.4644 +/- 0.0157 | 0.3679 +/- 0.0257 |
| Plastic-work lower-bound violation | 0.7007 +/- 0.6737 | 0.1676 +/- 0.2114 | 0.0352 +/- 0.0563 |

Source artifacts:

```text
10_results/reports/thermo_path_ood_5seed_summary.json
11_paper/tables/thermo_path_ood_5seed_summary.csv
```

Interpretation:

```text
The 5-seed evidence strengthens the main path-OOD claim. Curriculum and upper-bound rows reduce
history error, yield-flag reversal error, yield-surface violation, and plastic-work lower-bound
violation. Reversal history-increment is nearly flat from strict to curriculum and improves only in
the cyclic-seen upper-bound row, so the paper should claim partial curriculum repair, not complete
strict-to-cyclic memory transfer.
```

## L3b: Shared-Geometry Complex J2 Path-OOD Evidence

This table repeats the thermo-aware strict / curriculum / upper-bound study on a harder hole-geometry
J2 FEM dataset. All load paths within a split share the same mesh and parameter samples, so the
comparison isolates path-OOD behavior. Train and test splits use different hole meshes, adding a
mesh-transfer component to the validation.

Dataset:

```text
05_data_pipeline/processed/j2_complex_geometry_shared_path_fem2d
mesh_kind: hole
train coords: (8, 48, 2), train connectivity: (63, 3)
test coords: (3, 48, 2), test connectivity: (62, 3)
load paths: monotonic, unload_reload, cyclic, nonproportional
```

| Cyclic test metric | Strict path-OOD | Unload curriculum | Cyclic-seen upper bound |
|---|---:|---:|---:|
| Displacement relative L2 | 0.9132 +/- 0.0883 | 0.8756 +/- 0.0317 | 0.8704 +/- 0.0930 |
| History relative L2 | 1.0903 +/- 0.0954 | 0.9092 +/- 0.0355 | 0.8021 +/- 0.0500 |
| History-increment relative L2 | 1.0160 +/- 0.0022 | 1.0109 +/- 0.0021 | 1.0008 +/- 0.0020 |
| Eq. plastic strain increment relative L2 | 2.0700 +/- 0.4899 | 1.4737 +/- 0.2270 | 1.1834 +/- 0.2174 |
| Plastic-work increment relative L2 | 3.7015 +/- 0.6555 | 3.0074 +/- 0.3014 | 2.6189 +/- 0.3821 |
| Yield-flag MAE | 0.5412 +/- 0.0120 | 0.5394 +/- 0.0069 | 0.5057 +/- 0.0024 |
| Reversal history-increment relative L2 | 1.0206 +/- 0.0046 | 1.0155 +/- 0.0041 | 0.9958 +/- 0.0026 |
| Reversal yield-flag MAE | 0.6824 +/- 0.0427 | 0.6499 +/- 0.0058 | 0.5608 +/- 0.0059 |
| Predicted yield-surface relative RMS | 0.5578 +/- 0.0324 | 0.5073 +/- 0.0253 | 0.3858 +/- 0.0408 |
| Plastic-work lower-bound violation | 1.0951 +/- 0.9186 | 0.3220 +/- 0.2484 | 0.0870 +/- 0.1686 |

Source artifacts:

```text
10_results/reports/j2_complex_geometry_shared_thermo_path_ood_5seed_summary.json
11_paper/tables/j2_complex_geometry_shared_thermo_path_ood_5seed_summary.csv
11_paper/tables/j2_complex_geometry_shared_thermo_path_ood_5seed_primary_table.md
```

Interpretation:

```text
The complex-geometry table reproduces the same diagnostic ordering under a harder mesh setting.
Unload/reload curriculum improves cyclic history, reversal yield flag, yield-surface consistency,
and plastic-work lower-bound violation. The cyclic-seen row remains the architectural upper bound.
This provides a second validation layer beyond the small structured-grid J2 path benchmark.
```
