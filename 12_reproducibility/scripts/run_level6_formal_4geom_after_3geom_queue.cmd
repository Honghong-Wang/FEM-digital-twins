@echo off
set ROOT=%~dp0..\..
cd /d "%ROOT%"
if not exist "10_results\logs" mkdir "10_results\logs"

set WAIT_LOG=10_results\logs\level6_formal_4geom_after_3geom_queue.out.log
set WAIT_ERR=10_results\logs\level6_formal_4geom_after_3geom_queue.err.log
set UPSTREAM_LOG=10_results\logs\level6_formal_3geom_campaign.out.log

echo QUEUE_START %DATE% %TIME%>>"%WAIT_LOG%"

:wait_for_3geom
if not exist "%UPSTREAM_LOG%" (
  echo WAITING_NO_UPSTREAM_LOG %DATE% %TIME%>>"%WAIT_LOG%"
  ping -n 601 127.0.0.1 >nul
  goto wait_for_3geom
)

findstr /C:"EXIT" "%UPSTREAM_LOG%" >nul 2>>"%WAIT_ERR%"
if errorlevel 1 (
  echo WAITING_FOR_3GEOM_EXIT %DATE% %TIME%>>"%WAIT_LOG%"
  ping -n 601 127.0.0.1 >nul
  goto wait_for_3geom
)

echo UPSTREAM_DONE_STARTING_4GEOM %DATE% %TIME%>>"%WAIT_LOG%"
call "12_reproducibility\scripts\run_level6_formal_4geom_representative_campaign.cmd" >>"%WAIT_LOG%" 2>>"%WAIT_ERR%"
echo QUEUE_EXIT %ERRORLEVEL% %DATE% %TIME%>>"%WAIT_LOG%"
