# Current posterior calibration table audit

- source_summary: `<project-root>\10_results\reports\j2_sparse_dt_assimilation_5seed_calibrated_2sample_summary.json`
- seed_json_count: 5
- seed_csv_count: 5
- seeds: [20260517, 20260518, 20260519, 20260520, 20260521]
- epochs: 50
- train_samples: 32
- eval_samples: 2
- mesh_kind: multi_hole
- grid_shape: [8, 6]
- load_steps: 8
- train_load_paths: ['monotonic', 'unload_reload', 'cyclic']
- eval_load_paths: ['cyclic', 'nonproportional', 'random_amplitude', 'pre_stress']
- max_absdiff_seed_recompute_vs_summary: 3.469e-18
- failed_stat_checks: 0
- current_table_rows: 4
- current_table_evidence_tiers: ['expedited_5seed_2sample_current_main; full_9condition_formal_running']
- current_table_source_summaries: ['<project-root>\\10_results\\reports\\j2_sparse_dt_assimilation_5seed_calibrated_2sample_summary.json']
- formal_9condition_summary_count: 0

## Verdict
The current posterior calibration table is traceable to completed seed-level result files and matches the source summary within numerical tolerance.
The full 9-condition formal posterior calibration table has not been obtained yet: no formal condition summary.json files are present.
