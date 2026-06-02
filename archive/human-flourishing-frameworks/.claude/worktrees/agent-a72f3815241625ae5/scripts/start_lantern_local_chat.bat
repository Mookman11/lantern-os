@echo off
setlocal

rem Lantern Local Chat Shell batch launcher.
rem Refreshes a read-only repo-state snapshot and opens the static local shell.
rem No GPT calls, no agents, no tunnels, no sensors, no public writes.

set "SCRIPT_DIR=%~dp0"
set "REPO_ROOT=%SCRIPT_DIR%.."

cd /d "%REPO_ROOT%" || exit /b 1

python "%SCRIPT_DIR%start_lantern_local_chat.py" --batch-state
set "EXIT_CODE=%ERRORLEVEL%"
exit /b %EXIT_CODE%
