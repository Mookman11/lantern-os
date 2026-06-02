<#
.SYNOPSIS
PowerShell-native Lantern help-now launcher.

.DESCRIPTION
Use this from Windows PowerShell when cmd.exe syntax such as `cd /d` fails.
It enters the repo, pulls master with fast-forward only, runs focused checks,
reports env names as set/unset only, then opens the desktop app when available.
It prints the optional Discord adapter command without printing secrets.

Boundaries:
- no reset, clean, force, or destructive git action;
- no secrets printed;
- no tunnels, agents, hidden sensing, or public writes;
- Discord remains opt-in through the existing wrapper.
#>

[CmdletBinding()]
param(
    [string]$RepoRoot = "C:\tmp\hff-lantern-recovery",
    [switch]$SkipPull,
    [switch]$SkipTests,
    [switch]$OpenDiscord
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Show-EnvState {
    param([string]$Name)
    if ([string]::IsNullOrEmpty([Environment]::GetEnvironmentVariable($Name, "Process"))) {
        Write-Host "$Name=unset"
    }
    else {
        Write-Host "$Name=set"
    }
}

Write-Host "=== Lantern PowerShell help now ==="
Write-Host "Repo: $RepoRoot"

if (-not (Test-Path -LiteralPath $RepoRoot)) {
    throw "Repo path not found: $RepoRoot"
}

Set-Location -LiteralPath $RepoRoot

Write-Host ""
Write-Host "=== repo ==="
git status --short
git log -1 --oneline

if (-not $SkipPull) {
    Write-Host ""
    Write-Host "=== pull master safely ==="
    git pull --ff-only origin master
}

if (-not $SkipTests) {
    Write-Host ""
    Write-Host "=== focused tests ==="
    python -m unittest tests.test_echo_human_loop_triangle -v
    python -m unittest tests.test_lantern_doctrine_spine -v
}

Write-Host ""
Write-Host "=== env names only ==="
Show-EnvState "LANTERN_LLM_PROVIDER"
Show-EnvState "LANTERN_OPENAI_BASE_URL"
Show-EnvState "LANTERN_OPENAI_MODEL"
Show-EnvState "OPENAI_API_KEY"
Show-EnvState "ANTHROPIC_API_KEY"

$desktop = Join-Path $RepoRoot "apps\lantern-desktop\lantern_desktop.py"
$localChat = Join-Path $RepoRoot "scripts\start_lantern_local_chat.bat"
$discord = Join-Path $RepoRoot "scripts\start_lantern.bat"

Write-Host ""
Write-Host "=== open Lantern surface ==="
if (Test-Path -LiteralPath $desktop) {
    Write-Host "Starting desktop app: $desktop"
    Start-Process -FilePath "python" -ArgumentList @($desktop) -WorkingDirectory $RepoRoot
}
elseif (Test-Path -LiteralPath $localChat) {
    Write-Host "Desktop app not found; opening local chat shell: $localChat"
    & $localChat
}
else {
    throw "No Lantern desktop or local chat launcher found."
}

Write-Host ""
Write-Host "=== optional Discord adapter ==="
if ($OpenDiscord) {
    if (-not (Test-Path -LiteralPath $discord)) {
        throw "Discord launcher not found: $discord"
    }
    Write-Host "Starting Discord adapter through existing safe wrapper."
    & $discord
}
else {
    Write-Host "After the local app is visible, run:"
    Write-Host "  .\scripts\start_lantern.bat"
}

Write-Host ""
Write-Host "DONE: Lantern help-now path completed."
