@echo off
set ROOT=%~dp0..\..
cd /d "%ROOT%"
if not exist "10_results\logs" mkdir "10_results\logs"

set WAIT_LOG=10_results\logs\level6_mesh_transfer_after_4geom_queue.out.log
set WAIT_ERR=10_results\logs\level6_mesh_transfer_after_4geom_queue.err.log
set UPSTREAM_LOG=10_results\logs\level6_formal_4geom_representative.out.log

echo QUEUE_START %DATE% %TIME%>>"%WAIT_LOG%"

:wait_for_4geom
if not exist "%UPSTREAM_LOG%" (
  echo WAITING_NO_4GEOM_LOG %DATE% %TIME%>>"%WAIT_LOG%"
  ping -n 601 127.0.0.1 >nul
  goto wait_for_4geom
)

findstr /C:"EXIT" "%UPSTREAM_LOG%" >nul 2>>"%WAIT_ERR%"
if errorlevel 1 (
  echo WAITING_FOR_4GEOM_EXIT %DATE% %TIME%>>"%WAIT_LOG%"
  ping -n 601 127.0.0.1 >nul
  goto wait_for_4geom
)

echo UPSTREAM_DONE_STARTING_MESH_TRANSFER %DATE% %TIME%>>"%WAIT_LOG%"
call "12_reproducibility\scripts\run_level6_mesh_transfer_4geom_data_campaign.cmd" >>"%WAIT_LOG%" 2>>"%WAIT_ERR%"
echo QUEUE_EXIT %ERRORLEVEL% %DATE% %TIME%>>"%WAIT_LOG%"
