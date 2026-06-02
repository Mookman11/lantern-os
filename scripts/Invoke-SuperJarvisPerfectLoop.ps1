[CmdletBinding()]
param(
    [int]$Passes = 10,
    [switch]$LaunchAfter,
    [int]$Port = 8787
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot '..')
$resultsDir = Join-Path $repoRoot 'data\validation'
New-Item -ItemType Directory -Force -Path $resultsDir | Out-Null

$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$logPath = Join-Path $resultsDir "superjarvis-perfect-loop-$stamp.log"

function Write-LoopLog {
    param([string]$Message)
    $line = "[{0}] {1}" -f (Get-Date -Format o), $Message
    Write-Host $line
    Add-Content -Path $logPath -Value $line
}

function Invoke-OptionalCommand {
    param(
        [string]$Name,
        [scriptblock]$Command
    )

    Write-LoopLog "START $Name"
    try {
        & $Command *>&1 | ForEach-Object { Write-LoopLog "  $_" }
        Write-LoopLog "PASS  $Name"
        return $true
    } catch {
        Write-LoopLog "WARN  $Name :: $($_.Exception.Message)"
        return $false
    }
}

Push-Location $repoRoot
try {
    Write-LoopLog "Super Jarvis perfect loop starting from $repoRoot"
    Write-LoopLog "Passes requested: $Passes"

    $overallPass = $true

    for ($i = 1; $i -le $Passes; $i++) {
        Write-LoopLog "=== PASS $i / $Passes ==="

        $statusOk = Invoke-OptionalCommand -Name 'git status --short --branch' -Command {
            git status --short --branch
        }

        $diffCheckOk = Invoke-OptionalCommand -Name 'git diff --check' -Command {
            git diff --check -- README.md docs manifests scripts skills reports .github
        }

        $skillValidateOk = $true
        $quickValidate = 'C:\Users\alexp\.codex\skills\.system\skill-creator\scripts\quick_validate.py'
        if (Test-Path $quickValidate) {
            $skillValidateOk = Invoke-OptionalCommand -Name 'quick_validate super-jarvis skill' -Command {
                python $quickValidate '.\skills\super-jarvis-lantern-os'
            }
        } else {
            Write-LoopLog "SKIP  quick_validate missing at $quickValidate"
        }

        $convergenceOk = $true
        $convergenceScript = Join-Path $repoRoot 'scripts\Invoke-LanternConvergenceLoop.ps1'
        if (Test-Path $convergenceScript) {
            $convergenceOk = Invoke-OptionalCommand -Name 'Invoke-LanternConvergenceLoop.ps1' -Command {
                powershell -NoProfile -ExecutionPolicy Bypass -File $convergenceScript
            }
        } else {
            Write-LoopLog "SKIP  convergence loop missing at $convergenceScript"
        }

        if (-not ($statusOk -and $diffCheckOk -and $skillValidateOk -and $convergenceOk)) {
            $overallPass = $false
            Write-LoopLog "PASS $i completed with warnings. Continuing because loop is diagnostic, not destructive."
        } else {
            Write-LoopLog "PASS $i clean."
        }
    }

    if ($overallPass) {
        Write-LoopLog "RESULT: all requested passes completed cleanly."
    } else {
        Write-LoopLog "RESULT: loop completed with warnings. Review $logPath before public release claims."
    }

    if ($LaunchAfter) {
        $launcher = Join-Path $repoRoot 'scripts\Start-LanternRepoApp.ps1'
        if (Test-Path $launcher) {
            Write-LoopLog "Launching Lantern app with $launcher"
            powershell -NoProfile -ExecutionPolicy Bypass -File $launcher -Port $Port
        } else {
            Write-LoopLog "WARN launcher missing: $launcher"
        }
    }

    Write-LoopLog "Log saved to $logPath"
} finally {
    Pop-Location
}
