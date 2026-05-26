@echo off
setlocal EnableExtensions

set ROOT=%~dp0..\..
cd /d "%ROOT%"

if not defined PYTHON_EXE set "PYTHON_EXE=python"
set "PY=%PYTHON_EXE%"
set SUITE=12_reproducibility\scripts\run_j2_sparse_dt_posterior_calibration_main_suite.py
set STATUS=12_reproducibility\scripts\check_j2_sparse_dt_posterior_calibration_main_status.py
set AUDIT=12_reproducibility\scripts\audit_j2_sparse_dt_posterior_calibration_formal.py
set LOGDIR=10_results\logs
set PARTIAL=10_results\reports\j2_sparse_dt_posterior_calibration_main\_partial_tables

if not exist "%LOGDIR%" mkdir "%LOGDIR%"
if not exist "%PARTIAL%" mkdir "%PARTIAL%"

echo FORMAL_RESUME_START %DATE% %TIME%>>"%LOGDIR%\j2_sparse_dt_posterior_calibration_formal_resume.out.log"

call :RUN strict_path_ood s2_t2:2:2:0.001 strict_path_ood_s2_t2
if errorlevel 1 exit /b %ERRORLEVEL%
call :RUN strict_path_ood s4_t2:4:2:0.001 strict_path_ood_s4_t2
if errorlevel 1 exit /b %ERRORLEVEL%
call :RUN strict_path_ood s6_t3:6:3:0.001 strict_path_ood_s6_t3
if errorlevel 1 exit /b %ERRORLEVEL%

call :RUN reversal_curriculum s2_t2:2:2:0.001 reversal_curriculum_s2_t2
if errorlevel 1 exit /b %ERRORLEVEL%
call :RUN reversal_curriculum s4_t2:4:2:0.001 reversal_curriculum_s4_t2
if errorlevel 1 exit /b %ERRORLEVEL%
call :RUN reversal_curriculum s6_t3:6:3:0.001 reversal_curriculum_s6_t3
if errorlevel 1 exit /b %ERRORLEVEL%

call :RUN family_upper_bound s2_t2:2:2:0.001 family_upper_bound_s2_t2
if errorlevel 1 exit /b %ERRORLEVEL%
call :RUN family_upper_bound s4_t2:4:2:0.001 family_upper_bound_s4_t2
if errorlevel 1 exit /b %ERRORLEVEL%
call :RUN family_upper_bound s6_t3:6:3:0.001 family_upper_bound_s6_t3
if errorlevel 1 exit /b %ERRORLEVEL%

echo AGGREGATE_FULL_FORMAL %DATE% %TIME%>>"%LOGDIR%\j2_sparse_dt_posterior_calibration_formal_resume.out.log"
%PY% "%SUITE%" ^
  --aggregate-only ^
  --protocols strict_path_ood,reversal_curriculum,family_upper_bound ^
  --sparse-configs s2_t2:2:2:0.001,s4_t2:4:2:0.001,s6_t3:6:3:0.001 ^
  --epochs 50 ^
  --seeds 20260517,20260518,20260519,20260520,20260521 ^
  --train-samples 32 ^
  --eval-samples 8 ^
  --num-posterior-chains 8 ^
  --inversion-steps 120 ^
  --device cuda ^
  --paper-csv-out 11_paper\tables\j2_sparse_dt_posterior_calibration_main_table.csv ^
  --paper-md-out 11_paper\tables\j2_sparse_dt_posterior_calibration_main_table.md ^
  --compact-csv-out 11_paper\tables\j2_sparse_dt_posterior_calibration_compact_main.csv ^
  --compact-md-out 11_paper\tables\j2_sparse_dt_posterior_calibration_compact_main.md ^
  --gain-csv-out 11_paper\tables\j2_sparse_dt_posterior_calibration_gain_table.csv ^
  --gain-md-out 11_paper\tables\j2_sparse_dt_posterior_calibration_gain_table.md ^
  --gain-aggregate-csv-out 11_paper\tables\j2_sparse_dt_posterior_calibration_gain_aggregate.csv ^
  --gain-aggregate-md-out 11_paper\tables\j2_sparse_dt_posterior_calibration_gain_aggregate.md ^
  >>"%LOGDIR%\j2_sparse_dt_posterior_calibration_formal_resume.out.log" 2>>"%LOGDIR%\j2_sparse_dt_posterior_calibration_formal_resume.err.log"
if errorlevel 1 exit /b %ERRORLEVEL%

%PY% "%STATUS%" >>"%LOGDIR%\j2_sparse_dt_posterior_calibration_formal_resume.out.log" 2>>"%LOGDIR%\j2_sparse_dt_posterior_calibration_formal_resume.err.log"
%PY% "%AUDIT%" >>"%LOGDIR%\j2_sparse_dt_posterior_calibration_formal_resume.out.log" 2>>"%LOGDIR%\j2_sparse_dt_posterior_calibration_formal_resume.err.log"

echo FORMAL_RESUME_EXIT %ERRORLEVEL% %DATE% %TIME%>>"%LOGDIR%\j2_sparse_dt_posterior_calibration_formal_resume.out.log"
exit /b %ERRORLEVEL%

:RUN
set PROTOCOL=%~1
set SPARSE=%~2
set TAG=%~3
echo CONDITION_START %PROTOCOL% %SPARSE% %DATE% %TIME%>>"%LOGDIR%\j2_sparse_dt_posterior_calibration_formal_resume.out.log"
%PY% "%SUITE%" ^
  --protocols %PROTOCOL% ^
  --sparse-configs %SPARSE% ^
  --epochs 50 ^
  --seeds 20260517,20260518,20260519,20260520,20260521 ^
  --train-samples 32 ^
  --eval-samples 8 ^
  --num-posterior-chains 8 ^
  --inversion-steps 120 ^
  --device cuda ^
  --paper-csv-out "%PARTIAL%\%TAG%_main_table.csv" ^
  --paper-md-out "%PARTIAL%\%TAG%_main_table.md" ^
  --compact-csv-out "%PARTIAL%\%TAG%_compact_main.csv" ^
  --compact-md-out "%PARTIAL%\%TAG%_compact_main.md" ^
  --gain-csv-out "%PARTIAL%\%TAG%_gain_table.csv" ^
  --gain-md-out "%PARTIAL%\%TAG%_gain_table.md" ^
  --gain-aggregate-csv-out "%PARTIAL%\%TAG%_gain_aggregate.csv" ^
  --gain-aggregate-md-out "%PARTIAL%\%TAG%_gain_aggregate.md" ^
  >>"%LOGDIR%\j2_sparse_dt_posterior_calibration_formal_resume.out.log" 2>>"%LOGDIR%\j2_sparse_dt_posterior_calibration_formal_resume.err.log"
if errorlevel 1 exit /b %ERRORLEVEL%
%PY% "%STATUS%" >>"%LOGDIR%\j2_sparse_dt_posterior_calibration_formal_resume.out.log" 2>>"%LOGDIR%\j2_sparse_dt_posterior_calibration_formal_resume.err.log"
echo CONDITION_DONE %PROTOCOL% %SPARSE% %DATE% %TIME%>>"%LOGDIR%\j2_sparse_dt_posterior_calibration_formal_resume.out.log"
exit /b 0
