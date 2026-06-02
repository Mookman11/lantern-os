@echo off
setlocal

REM One-command Windows launcher for cmd.exe users.
REM This wrapper invokes the PowerShell launcher with a process-local execution policy bypass.
REM It does not print, save, or commit the Discord token.

set "SCRIPT_DIR=%~dp0"
set "PS_SCRIPT=%SCRIPT_DIR%start_lantern.ps1"

if not exist "%PS_SCRIPT%" (
  echo Lantern PowerShell launcher not found: %PS_SCRIPT%
  exit /b 1
)

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%PS_SCRIPT%" %*
set "EXIT_CODE=%ERRORLEVEL%"

endlocal & exit /b %EXIT_CODE%
