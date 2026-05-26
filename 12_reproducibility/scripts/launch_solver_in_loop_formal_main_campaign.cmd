@echo off
set SCRIPT=%~dp0run_solver_in_loop_formal_main_campaign.cmd
start "solver_in_loop_formal_main" /min "%ComSpec%" /c ""%SCRIPT%""
