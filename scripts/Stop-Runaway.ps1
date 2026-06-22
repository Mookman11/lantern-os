<#
.SYNOPSIS
    Kill duplicate ouro_serve / ouro_anthropic_bridge Python processes and
    warn about CPU hogs.

.DESCRIPTION
    Keeps the NEWEST instance of each guarded script, kills all older copies.
    Never touches MCP extension processes or unrelated Python programs.

    Run manually any time the machine feels sluggish, or schedule it:
    schtasks /Create /SC MINUTE /MO 30 /TN "OuroWatchdog" /TR "powershell -NonInteractive -File C:\dev\lantern-os\scripts\Stop-Runaway.ps1"

.PARAMETER CpuThresholdSeconds
    Warn (but do NOT kill) non-ouro Python processes above this CPU accumulation.
    Default: 3600 (1 hour). Set 0 to disable.

.PARAMETER WhatIf
    Preview what would be killed without actually killing anything.

.EXAMPLE
    powershell -File scripts/Stop-Runaway.ps1 -WhatIf
#>
param(
    [int]$CpuThresholdSeconds = 3600,
    [switch]$WhatIf
)

$action = if ($WhatIf) { "WOULD KILL" } else { "Killing" }
$killed = 0

# Scripts that must run as at most one instance at a time.
$GUARDED = @(
    "ouro_serve.py",
    "ouro_anthropic_bridge.py"
)

function Get-ScriptProcs([string]$ScriptName) {
    @(Get-CimInstance Win32_Process -Filter "Name LIKE '%python%'" |
      Where-Object { $_.CommandLine -like "*$ScriptName*" })
}

Write-Host ""
Write-Host "Runaway-process cleanup  $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Cyan
Write-Host "------------------------------------------------------------"

foreach ($script in $GUARDED) {
    # Keep the process doing the most work (highest CPU); lightweight stubs that
    # spawned it have near-zero CPU and should be culled if a heavier sibling exists.
    $procs = Get-ScriptProcs $script | ForEach-Object {
        $gp = Get-Process -Id $_.ProcessId -ErrorAction SilentlyContinue
        [PSCustomObject]@{ Cim=$_; CpuSec=if($gp){$gp.CPU}else{0} }
    } | Sort-Object CpuSec -Descending
    if ($procs.Count -eq 0) {
        Write-Host "[--]  $script -- not running"
        continue
    }
    $keep = $procs[0]
    Write-Host "[ok]  $script -- keeping PID $($keep.Cim.ProcessId)  cpu=$([math]::Round($keep.CpuSec,1))s"
    if ($procs.Count -gt 1) {
        foreach ($extra in $procs[1..($procs.Count - 1)]) {
            $age = [math]::Round(([DateTime]::Now - [DateTime]$extra.Cim.CreationDate).TotalMinutes, 0)
            Write-Host "      $action PID $($extra.Cim.ProcessId)  cpu=$([math]::Round($extra.CpuSec,1))s  age=${age}min" -ForegroundColor Yellow
            if (-not $WhatIf) {
                Stop-Process -Id $extra.Cim.ProcessId -Force -ErrorAction SilentlyContinue
                $killed++
            }
        }
    }
}

# CPU hog warning (non-guarded Python processes only)
if ($CpuThresholdSeconds -gt 0) {
    Write-Host ""
    Write-Host "-- CPU hog check (threshold: ${CpuThresholdSeconds}s) --"
    $allPy = Get-Process python -ErrorAction SilentlyContinue
    foreach ($p in $allPy) {
        try { $cl = (Get-CimInstance Win32_Process -Filter "ProcessId = $($p.Id)").CommandLine } catch { $cl = "" }
        $isGuarded = $false
        foreach ($g in $GUARDED) { if ($cl -like "*$g*") { $isGuarded = $true; break } }
        if ($isGuarded) { continue }

        if ($p.CPU -gt $CpuThresholdSeconds) {
            $ageMin = [math]::Round(([DateTime]::Now - $p.StartTime).TotalMinutes, 0)
            $shortCmd = $cl -replace '^.*\\Scripts\\', '' -replace '^.*\\bin\\', ''
            Write-Host "[!!]  PID $($p.Id)  cpu=$([math]::Round($p.CPU,0))s  age=${ageMin}min  $shortCmd" -ForegroundColor Red
        }
    }
}

Write-Host ""
Write-Host "-- Claude instances --"
$claudeProcs = Get-Process claude -ErrorAction SilentlyContinue
if ($claudeProcs) {
    foreach ($cp in $claudeProcs) {
        $mb = [math]::Round($cp.WorkingSet / 1MB, 0)
        Write-Host "  PID $($cp.Id)  cpu=$([math]::Round($cp.CPU,1))s  ${mb}MB  started=$($cp.StartTime)"
    }
} else {
    Write-Host "  none running"
}

Write-Host ""
if ($WhatIf) {
    Write-Host "DRY RUN -- nothing was killed." -ForegroundColor Cyan
} else {
    $noun = if ($killed -ne 1) { "processes" } else { "process" }
    Write-Host "Done. Killed $killed duplicate $noun." -ForegroundColor Green
}
