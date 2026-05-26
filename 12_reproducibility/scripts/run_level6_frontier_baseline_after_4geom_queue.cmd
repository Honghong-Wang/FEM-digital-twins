@echo off
set ROOT=%~dp0..\..
cd /d "%ROOT%"
if not defined PYTHON_EXE set "PYTHON_EXE=python"
if not exist "10_results\logs" mkdir "10_results\logs"
"%PYTHON_EXE%" 12_reproducibility\scripts\wait_for_log_exit_then_run.py --root "%ROOT%" --upstream-log 10_results\logs\level6_formal_4geom_representative.out.log --command 12_reproducibility\scripts\run_level6_frontier_baseline_4geom_campaign.cmd --out-log 10_results\logs\level6_frontier_baseline_after_4geom_queue.out.log --err-log 10_results\logs\level6_frontier_baseline_after_4geom_queue.err.log --poll-seconds 600
