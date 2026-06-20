<#
.SYNOPSIS
  Register (or remove) a Windows Scheduled Task that runs ONE improve_tick pass on
  an interval. This is the external "forever" for the autonomous improvement loop —
  the tick itself does a single observe -> verify -> converge -> learn pass and
  exits; the schedule is what makes it perpetual.

.DESCRIPTION
  Each fire runs:  python src/mcp_server/improve_tick.py
  which is read-mostly and safe: it never opens PRs or merges. It investigates the
  top issue, verifies prior bot PRs (upgrading the playbook when CI is green), and
  periodically runs the self-improvement analyzer. Output is appended to
  data/convergence/improve-tick.log; durable receipts go to
  data/convergence/improve-tick-records.jsonl.

  Autonomous worker pickup (-Autonomous) sets LANTERN_TICK_AUTONOMOUS=1 for the
  task, which lets the tick pull the worker when a lane is free. Code writes still
  require GITHUB_WRITE_ENABLED — this switch does NOT bypass the write gates.

.PARAMETER IntervalMinutes
  Minutes between ticks (default 30).

.PARAMETER Autonomous
  Enable worker pickup (sets LANTERN_TICK_AUTONOMOUS=1 for the task).

.PARAMETER StartNow
  Run the task once immediately after registering (useful to smoke-test).

.PARAMETER Unregister
  Remove the scheduled task and exit.

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File scripts/Register-ImproveTick.ps1
  powershell -ExecutionPolicy Bypass -File scripts/Register-ImproveTick.ps1 -IntervalMinutes 15 -StartNow
  powershell -ExecutionPolicy Bypass -File scripts/Register-ImproveTick.ps1 -Unregister
#>
[CmdletBinding()]
param(
    [int]    $IntervalMinutes = 30,
    [switch] $Autonomous,
    [switch] $StartNow,
    [switch] $Unregister
)

$ErrorActionPreference = "Stop"
$TaskName = "LanternImproveTick"

# Repo root = parent of this script's folder.
$RepoRoot = Split-Path -Parent $PSScriptRoot

if ($Unregister) {
    if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) {
        Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
        Write-Host "Removed scheduled task '$TaskName'."
    } else {
        Write-Host "No scheduled task '$TaskName' found."
    }
    return
}

# Prefer a repo virtualenv if present, else fall back to PATH python.
$Python = "python"
foreach ($candidate in @("$RepoRoot\.venv\Scripts\python.exe", "$RepoRoot\venv\Scripts\python.exe")) {
    if (Test-Path $candidate) { $Python = $candidate; break }
}

$Script  = "src\mcp_server\improve_tick.py"
$LogFile = "data\convergence\improve-tick.log"
$EnvPrefix = if ($Autonomous) { "set LANTERN_TICK_AUTONOMOUS=1&& " } else { "" }

# Run via cmd so we get inline env + log redirection. WorkingDirectory = repo root,
# so the relative paths above (and the tick's repo-root detection) resolve.
$cmdArgs = "/c $EnvPrefix`"$Python`" $Script >> $LogFile 2>&1"
$action  = New-ScheduledTaskAction -Execute "cmd.exe" -Argument $cmdArgs -WorkingDirectory $RepoRoot

# Fire once at registration, then repeat every N minutes for ~10 years (indefinite).
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) `
    -RepetitionInterval (New-TimeSpan -Minutes $IntervalMinutes) `
    -RepetitionDuration (New-TimeSpan -Days 3650)

$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable `
    -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Minutes 30)

# Run as the current interactive user so git/gh credentials (keyring) are available.
$principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType Interactive

Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger `
    -Settings $settings -Principal $principal -Force | Out-Null

Write-Host "Registered '$TaskName':"
Write-Host "  python   : $Python"
Write-Host "  command  : $Script"
Write-Host "  interval : every $IntervalMinutes min"
Write-Host "  autonomous: $([bool]$Autonomous)  (worker pickup; writes still need GITHUB_WRITE_ENABLED)"
Write-Host "  log      : $RepoRoot\$LogFile"
Write-Host "  remove   : scripts\Register-ImproveTick.ps1 -Unregister"

if ($StartNow) {
    Start-ScheduledTask -TaskName $TaskName
    Write-Host "Started one run now (-StartNow)."
}
