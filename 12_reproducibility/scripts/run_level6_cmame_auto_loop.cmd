@echo off
setlocal EnableExtensions

set ROOT=%~dp0..\..
cd /d "%ROOT%"

if not defined PYTHON_EXE set "PYTHON_EXE=python"
set "PY=%PYTHON_EXE%"
set LOGDIR=10_results\logs
set LOG=%LOGDIR%\level6_cmame_auto_loop.out.log
set ERR=%LOGDIR%\level6_cmame_auto_loop.err.log
set EVAL=12_reproducibility\scripts\evaluate_level6_readiness.py
set SOLVER=12_reproducibility\scripts\run_solver_in_loop_formal_main_suite.py

if not exist "%LOGDIR%" mkdir "%LOGDIR%"

echo LEVEL6_CMAME_AUTO_START %DATE% %TIME%>>"%LOG%"

echo STEP 1 EVALUATE_INITIAL %DATE% %TIME%>>"%LOG%"
%PY% "%EVAL%" >>"%LOG%" 2>>"%ERR%"

echo STEP 2 RUN_SOLVER_IN_LOOP_FORMAL_3CASE %DATE% %TIME%>>"%LOG%"
%PY% "%SOLVER%" ^
  --matrix-root 05_data_pipeline\processed\level4_formal_complex_j2_t6_8step_qp_9case ^
  --case-names multi_hole_14x11,notch_14x11,curved_hole_14x11 ^
  --models hgo_qp_true_j2 ^
  --train-load-paths monotonic ^
  --eval-load-paths monotonic,unload_reload,cyclic,nonproportional ^
  --seeds 20260517,20260518,20260519,20260520,20260521 ^
  --epochs 50 ^
  --batch-size 1 ^
  --eval-batch-size 1 ^
  --device cuda ^
  --step-policy all ^
  --main-csv-out 11_paper\tables\solver_in_loop_formal_main_table.csv ^
  --main-md-out 11_paper\tables\solver_in_loop_formal_main_table.md ^
  --case-csv-out 11_paper\tables\solver_in_loop_formal_main_case_rows.csv ^
  --case-md-out 11_paper\tables\solver_in_loop_formal_main_case_rows.md ^
  --case-aggregate-csv-out 11_paper\tables\solver_in_loop_formal_main_case_aggregate.csv ^
  --case-aggregate-md-out 11_paper\tables\solver_in_loop_formal_main_case_aggregate.md ^
  --reduction-csv-out 11_paper\tables\solver_in_loop_formal_main_reduction.csv ^
  --reduction-md-out 11_paper\tables\solver_in_loop_formal_main_reduction.md ^
  --reduction-aggregate-csv-out 11_paper\tables\solver_in_loop_formal_main_reduction_aggregate.csv ^
  --reduction-aggregate-md-out 11_paper\tables\solver_in_loop_formal_main_reduction_aggregate.md ^
  >>"%LOG%" 2>>"%ERR%"
if errorlevel 1 goto FAIL

echo STEP 3 EVALUATE_AFTER_SOLVER %DATE% %TIME%>>"%LOG%"
%PY% "%EVAL%" >>"%LOG%" 2>>"%ERR%"
if errorlevel 1 goto FAIL

echo LEVEL6_CMAME_AUTO_EXIT 0 %DATE% %TIME%>>"%LOG%"
exit /b 0

:FAIL
echo LEVEL6_CMAME_AUTO_EXIT %ERRORLEVEL% %DATE% %TIME%>>"%LOG%"
exit /b %ERRORLEVEL%
