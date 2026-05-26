@echo off
set ROOT=%~dp0..\..
cd /d "%ROOT%"
if not defined PYTHON_EXE set "PYTHON_EXE=python"
if not exist "10_results\logs" mkdir "10_results\logs"
echo START %DATE% %TIME%>>"10_results\logs\j2_sparse_dt_posterior_calibration_main.out.log"
"%PYTHON_EXE%" 12_reproducibility\scripts\run_j2_sparse_dt_posterior_calibration_main_suite.py --protocols strict_path_ood,reversal_curriculum,family_upper_bound --sparse-configs s2_t2:2:2:0.001,s4_t2:4:2:0.001,s6_t3:6:3:0.001 --epochs 50 --seeds 20260517,20260518,20260519,20260520,20260521 --train-samples 32 --eval-samples 8 --num-posterior-chains 8 --inversion-steps 120 --device cuda --paper-csv-out 11_paper\tables\j2_sparse_dt_posterior_calibration_main_table.csv --paper-md-out 11_paper\tables\j2_sparse_dt_posterior_calibration_main_table.md --compact-csv-out 11_paper\tables\j2_sparse_dt_posterior_calibration_compact_main.csv --compact-md-out 11_paper\tables\j2_sparse_dt_posterior_calibration_compact_main.md --gain-csv-out 11_paper\tables\j2_sparse_dt_posterior_calibration_gain_table.csv --gain-md-out 11_paper\tables\j2_sparse_dt_posterior_calibration_gain_table.md --gain-aggregate-csv-out 11_paper\tables\j2_sparse_dt_posterior_calibration_gain_aggregate.csv --gain-aggregate-md-out 11_paper\tables\j2_sparse_dt_posterior_calibration_gain_aggregate.md >>"10_results\logs\j2_sparse_dt_posterior_calibration_main.out.log" 2>>"10_results\logs\j2_sparse_dt_posterior_calibration_main.err.log"
echo EXIT %ERRORLEVEL% %DATE% %TIME%>>"10_results\logs\j2_sparse_dt_posterior_calibration_main.out.log"
