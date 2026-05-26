@echo off
set ROOT=%~dp0..\..
cd /d "%ROOT%"
if not defined PYTHON_EXE set "PYTHON_EXE=python"
if not exist "10_results\logs" mkdir "10_results\logs"
echo START %DATE% %TIME%>>"10_results\logs\solver_in_loop_ablation_level4_t6.out.log"
"%PYTHON_EXE%" 12_reproducibility\scripts\run_solver_in_loop_ablation.py --data-root 05_data_pipeline\processed\level4_formal_complex_j2_t6_8step_qp --out-root 10_results\reports\solver_in_loop_ablation_level4_t6_8step_qp --models hgo_qp_true_j2 --train-load-paths monotonic --eval-load-paths monotonic,unload_reload,cyclic,nonproportional --seeds 20260517,20260518,20260519,20260520,20260521 --epochs 50 --batch-size 1 --eval-batch-size 1 --device cuda --table-csv-out 11_paper\tables\solver_in_loop_ablation_level4_t6_table.csv --table-md-out 11_paper\tables\solver_in_loop_ablation_level4_t6_table.md --reduction-csv-out 11_paper\tables\solver_in_loop_ablation_level4_t6_reduction.csv --reduction-md-out 11_paper\tables\solver_in_loop_ablation_level4_t6_reduction.md >>"10_results\logs\solver_in_loop_ablation_level4_t6.out.log" 2>>"10_results\logs\solver_in_loop_ablation_level4_t6.err.log"
echo EXIT %ERRORLEVEL% %DATE% %TIME%>>"10_results\logs\solver_in_loop_ablation_level4_t6.out.log"
