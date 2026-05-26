@echo off
set ROOT=%~dp0..\..
cd /d "%ROOT%"
if not defined PYTHON_EXE set "PYTHON_EXE=python"
if not exist "10_results\logs" mkdir "10_results\logs"
echo START %DATE% %TIME%>>"10_results\logs\level6_frontier_baseline_4geom.out.log"
"%PYTHON_EXE%" 12_reproducibility\scripts\run_level6_frontier_baseline_suite.py --data-root 05_data_pipeline\processed\level6_complex_j2_benchmark_formal_3geom --cases multi_hole_14x11,notch_14x11,curved_hole_14x11,random_holes_14x11 --out-root 10_results\reports\level6_frontier_baseline_4geom --paper-table-stem 11_paper\tables\level6_frontier_baseline_4geom_table --epochs 50 --seeds 20260517,20260518,20260519,20260520,20260521 --batch-size 4 --eval-batch-size 4 --device cuda >>"10_results\logs\level6_frontier_baseline_4geom.out.log" 2>>"10_results\logs\level6_frontier_baseline_4geom.err.log"
echo EXIT %ERRORLEVEL% %DATE% %TIME%>>"10_results\logs\level6_frontier_baseline_4geom.out.log"
