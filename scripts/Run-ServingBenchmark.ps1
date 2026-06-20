#!/usr/bin/env pwsh
# Run-ServingBenchmark.ps1
# Phase 2 / issue #730 — daily serving benchmark against the LOCAL Ollama models.
#
# GitHub-hosted CI has no local model, so the host PC accrues the daily Ollama
# runs that satisfy the Definition of Done ("leaderboard has >= 7 daily runs").
# Register this with Windows Task Scheduler to run once a day:
#
#   $action  = New-ScheduledTaskAction -Execute "pwsh.exe" `
#       -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$PWD\scripts\Run-ServingBenchmark.ps1`""
#   $trigger = New-ScheduledTaskTrigger -Daily -At 7:30am
#   Register-ScheduledTask -TaskName "LanternServingBenchmark" -Action $action -Trigger $trigger
#
# Then verify the validation gate passes:  python src\serving_benchmark.py --validate

[CmdletBinding()]
param(
    # provider:model specs to benchmark. Defaults to the local Ollama models.
    [string[]] $Specs = @("ollama:qwen2.5-coder"),
    [ValidateSet("fast", "deep")]
    [string] $Mode = "fast",
    # Fail the script (non-zero exit) if the run regresses the serving contract.
    [switch] $FailOnRegression
)

$ErrorActionPreference = "Stop"
$repoRoot = git rev-parse --show-toplevel
Set-Location $repoRoot

# Only benchmark Ollama models that are actually installed (no fabricated data).
$installed = @()
try {
    $installed = (& ollama list 2>$null | Select-Object -Skip 1 | ForEach-Object {
        ($_ -split '\s+')[0]
    }) | Where-Object { $_ }
} catch {
    Write-Warning "ollama not found on PATH; only non-ollama specs will run."
}

$specJoined = ($Specs | Where-Object {
    $parts = $_ -split ':', 2
    if ($parts[0] -ne 'ollama') { return $true }
    $model = $parts[1]
    $present = $installed -contains $model -or $installed -contains "${model}:latest"
    if (-not $present) { Write-Warning "Skipping ollama:$model (not installed)." }
    return $present
}) -join ','

if (-not $specJoined) {
    Write-Host "No runnable specs. Installed Ollama models: $($installed -join ', ')"
    exit 0
}

Write-Host "Benchmarking [$specJoined] in $Mode mode..."
python src/serving_benchmark.py --providers $specJoined --mode $Mode
$runExit = $LASTEXITCODE

# Refresh the human-readable monitoring report.
python src/serving_benchmark.py --report | Out-Null

Write-Host "`nLeaderboard updated: data/benchmarks/leaderboard.jsonl"
Write-Host "Report:             data/benchmarks/REPORT.md"

if ($FailOnRegression -and $runExit -ne 0) {
    Write-Error "Serving benchmark regressed the contract (exit $runExit)."
    exit $runExit
}
exit 0
