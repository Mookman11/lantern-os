@echo off
setlocal EnableExtensions

set "BASE=%~1"
if "%BASE%"=="" set "BASE=https://human-flourishing-frameworks.onrender.com"

echo Checking HFF nodes API at %BASE%
echo.

echo == adoption stats ==
curl.exe -fsS "%BASE%/api/adoption/stats" | python -m json.tool
if errorlevel 1 (
  echo FAIL: adoption stats request failed.
  exit /b 1
)

echo.
echo == adoption nodes pass 1 ==
curl.exe -fsS "%BASE%/api/adoption/nodes" | python -m json.tool
if errorlevel 1 (
  echo FAIL: adoption nodes request failed on pass 1.
  exit /b 1
)

echo.
echo Waiting 75 seconds before second poll...
timeout /t 75 /nobreak >nul

echo.
echo == adoption nodes pass 2 ==
curl.exe -fsS "%BASE%/api/adoption/nodes" | python -m json.tool
if errorlevel 1 (
  echo FAIL: adoption nodes request failed on pass 2.
  exit /b 1
)

echo.
echo DONE: Compare last_seen values between pass 1 and pass 2.
echo If both arrays are [], there are no visible registered nodes polling this central service.
