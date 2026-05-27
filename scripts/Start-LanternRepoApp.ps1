[CmdletBinding()]
param(
    [int]$Port = 8787,
    [switch]$NoBrowser,
    [switch]$RebootAfterLaunch,
    [int]$RebootDelaySeconds = 300
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot '..')
$surfacePath = Join-Path $repoRoot 'surfaces\tony-garage\index.html'

if (-not (Test-Path $surfacePath)) {
    throw "Tony Garage surface not found: $surfacePath"
}

Write-Host "Lantern OS repo root: $repoRoot"
Write-Host "Tony Garage surface: $surfacePath"
Write-Host "Requested port: $Port"

$python = Get-Command py -ErrorAction SilentlyContinue
$pythonArgs = @('-3', '-m', 'http.server', $Port.ToString(), '--bind', '127.0.0.1')

if (-not $python) {
    $python = Get-Command python -ErrorAction SilentlyContinue
    $pythonArgs = @('-m', 'http.server', $Port.ToString(), '--bind', '127.0.0.1')
}

$appUrl = "http://127.0.0.1:$Port/surfaces/tony-garage/index.html"

if ($python) {
    Write-Host "Starting local static server with $($python.Source)"
    $process = Start-Process -FilePath $python.Source -ArgumentList $pythonArgs -WorkingDirectory $repoRoot -PassThru -WindowStyle Minimized
    Start-Sleep -Seconds 2
    Write-Host "Local app URL: $appUrl"
    if (-not $NoBrowser) {
        Start-Process $appUrl
    }
    Write-Host "Server PID: $($process.Id)"
    Write-Host "Stop server: Stop-Process -Id $($process.Id)"
} else {
    Write-Warning "Python was not found. Opening the file directly instead of serving over localhost."
    if (-not $NoBrowser) {
        Start-Process $surfacePath
    }
}

if ($RebootAfterLaunch) {
    if ($RebootDelaySeconds -lt 60) {
        throw "Refusing to schedule reboot with delay under 60 seconds. Use at least 60 seconds so it can be aborted."
    }
    Write-Warning "Scheduling Windows reboot in $RebootDelaySeconds seconds. Abort with: shutdown /a"
    shutdown /r /t $RebootDelaySeconds /c "Lantern OS requested reboot after local app launch. Abort with shutdown /a."
}
