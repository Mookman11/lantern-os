@echo off
setlocal

REM Visible one-click launcher for Lantern Chat on Windows.
REM Safe behavior:
REM - runs from this repo folder;
REM - tries a fast-forward-only update only through the watchdog;
REM - starts the visible Tkinter desktop app;
REM - does not reset, clean, force, deploy, tunnel, or start agents.

set "REPO_ROOT=%~dp0"
set "WATCHDOG=%REPO_ROOT%scripts\watch_lantern_chat.ps1"

if not exist "%WATCHDOG%" (
  echo Lantern watchdog not found: %WATCHDOG%
  echo Run: git pull --ff-only origin master
  pause
  exit /b 1
)

echo Starting Lantern Chat from:
echo   %REPO_ROOT%
echo.

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%WATCHDOG%" -Once
set "EXIT_CODE=%ERRORLEVEL%"

if not "%EXIT_CODE%"=="0" (
  echo.
  echo Lantern Chat launcher failed with exit code %EXIT_CODE%.
  echo Keep this window open and share the text above for repair.
  pause
)

endlocal & exit /b %EXIT_CODE%
