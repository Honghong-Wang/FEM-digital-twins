@echo off
set ROOT=%~dp0..\..
cd /d "%ROOT%"
if not defined PYTHON_EXE set "PYTHON_EXE=python"
if not exist "10_results\logs" mkdir "10_results\logs"
echo START %DATE% %TIME%>>"10_results\logs\level6_mesh_transfer_4geom_data.out.log"
"%PYTHON_EXE%" 12_reproducibility\scripts\run_level6_formal_main_table.py --matrix full --stages data,summary --mesh-kinds multi_hole,notch,curved_hole,random_holes --mesh-sizes 14x11,18x14,22x17 --train-samples 64 --eval-samples 20 --load-steps 12 --max-newton-steps 24 --data-root 05_data_pipeline\processed\level6_complex_j2_benchmark_mesh_transfer_4geom --report-root 10_results\reports\level6_complex_j2_benchmark_mesh_transfer_4geom --workers 8 --samples-per-shard 8 >>"10_results\logs\level6_mesh_transfer_4geom_data.out.log" 2>>"10_results\logs\level6_mesh_transfer_4geom_data.err.log"
echo EXIT %ERRORLEVEL% %DATE% %TIME%>>"10_results\logs\level6_mesh_transfer_4geom_data.out.log"
