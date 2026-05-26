@echo off
setlocal

set "ROOT=%~dp0..\.."
set "OUT=%ROOT%\10_results\logs\level6_solver_in_loop_direct_cmd.out.log"
set "ERR=%ROOT%\10_results\logs\level6_solver_in_loop_direct_cmd.err.log"

cd /d "%ROOT%"
if not defined PYTHON_EXE set "PYTHON_EXE=python"
if not exist "%ROOT%\10_results\logs" mkdir "%ROOT%\10_results\logs"

echo LEVEL6_SOLVER_CMD_START %DATE% %TIME% > "%OUT%"
echo LEVEL6_SOLVER_CMD_START %DATE% %TIME% > "%ERR%"
echo LEVEL6_SOLVER_CMD_BEFORE_PY %DATE% %TIME% >> "%OUT%"

"%PYTHON_EXE%" "12_reproducibility\scripts\run_solver_in_loop_formal_main_suite.py" --matrix-root "05_data_pipeline\processed\level4_formal_complex_j2_t6_8step_qp_9case" --case-names "multi_hole_14x11,notch_14x11,curved_hole_14x11" --models "hgo_qp_true_j2" --train-load-paths "monotonic" --eval-load-paths "monotonic,unload_reload,cyclic,nonproportional" --seeds "20260517,20260518,20260519,20260520,20260521" --epochs 50 --batch-size 1 --eval-batch-size 1 --device "cuda" --step-policy "all" --no-skip-existing --main-csv-out "11_paper\tables\solver_in_loop_formal_main_table.csv" --main-md-out "11_paper\tables\solver_in_loop_formal_main_table.md" --case-csv-out "11_paper\tables\solver_in_loop_formal_main_case_rows.csv" --case-md-out "11_paper\tables\solver_in_loop_formal_main_case_rows.md" --case-aggregate-csv-out "11_paper\tables\solver_in_loop_formal_main_case_aggregate.csv" --case-aggregate-md-out "11_paper\tables\solver_in_loop_formal_main_case_aggregate.md" --reduction-csv-out "11_paper\tables\solver_in_loop_formal_main_reduction.csv" --reduction-md-out "11_paper\tables\solver_in_loop_formal_main_reduction.md" --reduction-aggregate-csv-out "11_paper\tables\solver_in_loop_formal_main_reduction_aggregate.csv" --reduction-aggregate-md-out "11_paper\tables\solver_in_loop_formal_main_reduction_aggregate.md" >> "%OUT%" 2>> "%ERR%"

set "EXITCODE=%ERRORLEVEL%"
echo LEVEL6_SOLVER_CMD_EXIT %EXITCODE% %DATE% %TIME% >> "%OUT%"
echo LEVEL6_SOLVER_CMD_EXIT %EXITCODE% %DATE% %TIME% >> "%ERR%"
exit /b %EXITCODE%
