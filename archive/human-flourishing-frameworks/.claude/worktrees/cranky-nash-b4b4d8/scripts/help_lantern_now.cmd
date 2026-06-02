@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
set "REPO_ROOT=%SCRIPT_DIR%.."
set "LOCAL_CHAT=%SCRIPT_DIR%start_lantern_local_chat.bat"

echo === Lantern help now ===
cd /d "%REPO_ROOT%" || exit /b 1

echo === repo ===
git status --short
git log -1 --oneline

echo === pull master safely ===
git pull --ff-only origin master
if errorlevel 1 exit /b 1

echo === focused tests ===
python -m unittest tests.test_echo_human_loop_triangle -v
if errorlevel 1 exit /b 1
python -m unittest tests.test_lantern_doctrine_spine -v
if errorlevel 1 exit /b 1

echo === env names only ===
if defined LANTERN_LLM_PROVIDER (echo LANTERN_LLM_PROVIDER=set) else echo LANTERN_LLM_PROVIDER=unset
if defined LANTERN_OPENAI_BASE_URL (echo LANTERN_OPENAI_BASE_URL=set) else echo LANTERN_OPENAI_BASE_URL=unset
if defined LANTERN_OPENAI_MODEL (echo LANTERN_OPENAI_MODEL=set) else echo LANTERN_OPENAI_MODEL=unset
if defined OPENAI_API_KEY (echo OPENAI_API_KEY=set) else echo OPENAI_API_KEY=unset
if defined ANTHROPIC_API_KEY (echo ANTHROPIC_API_KEY=set) else echo ANTHROPIC_API_KEY=unset

echo === open local Lantern app ===
if not exist "%LOCAL_CHAT%" exit /b 1
call "%LOCAL_CHAT%"

echo === optional Discord adapter ===
echo Run scripts\start_lantern.bat after the local app is visible.

endlocal
