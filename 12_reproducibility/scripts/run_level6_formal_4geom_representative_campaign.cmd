@echo off
set ROOT=%~dp0..\..
cd /d "%ROOT%"
if not defined PYTHON_EXE set "PYTHON_EXE=python"
if not exist "10_results\logs" mkdir "10_results\logs"
echo START %DATE% %TIME%>>"10_results\logs\level6_formal_4geom_representative.out.log"
"%PYTHON_EXE%" 12_reproducibility\scripts\run_level6_formal_main_table.py --matrix representative --stages data,summary,table --mesh-kinds multi_hole,notch,curved_hole,random_holes --mesh-sizes 14x11 --data-root 05_data_pipeline\processed\level6_complex_j2_benchmark_formal_3geom --report-root 10_results\reports\level6_complex_j2_benchmark_formal_3geom --workers 8 --samples-per-shard 8 --seeds 20260517,20260518,20260519,20260520,20260521 --epochs 50 --batch-size 4 --eval-batch-size 4 --device cuda --fem-training-solver-mode linearized >>"10_results\logs\level6_formal_4geom_representative.out.log" 2>>"10_results\logs\level6_formal_4geom_representative.err.log"
echo EXIT %ERRORLEVEL% %DATE% %TIME%>>"10_results\logs\level6_formal_4geom_representative.out.log"
