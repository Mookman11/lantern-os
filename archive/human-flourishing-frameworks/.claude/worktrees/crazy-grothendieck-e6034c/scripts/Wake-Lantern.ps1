<#
.SYNOPSIS
Wake Lantern fully after a reboot — fix the dark spots.

.DESCRIPTION
A single post-reboot ritual. Sets env, verifies dependencies, makes sure the
doctrine constants are in the running backend, restarts everything in the
right order, and reports what is live and what is still dark.

Use:
  powershell -ExecutionPolicy Bypass -File scripts\Wake-Lantern.ps1
  powershell -ExecutionPolicy Bypass -File scripts\Wake-Lantern.ps1 -StartStream
  powershell -ExecutionPolicy Bypass -File scripts\Wake-Lantern.ps1 -SkipBackendRestart

Boundary:
- current Windows user only
- only services we already authored: backend, desktop, watchdog, cam stream
- no scanning beyond ~/.lantern, ~/Documents/gm-agent-orchestrator, the repo
- no synthetic voice, no cloud calls beyond what the env flags already permit
#>

[CmdletBinding()]
param(
    [string]$Repo = "C:\tmp\hff-lantern-recovery",
    [int]$BackendPort = 8766,
    [int]$DesktopWaitSeconds = 5,
    [switch]$StartStream,
    [switch]$SkipBackendRestart
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Continue"

function Section($name) {
    Write-Host ""
    Write-Host "=== $name ===" -ForegroundColor Cyan
}

function StatusLine($label, $value, $color = "Gray") {
    Write-Host ("  {0,-26} {1}" -f $label, $value) -ForegroundColor $color
}

# 1. ENV — set the substrate routing so when LM Studio comes up, Lantern routes through it
Section "env (per-process, for child Lantern)"
$env:LANTERN_LLM_PROVIDER     = "openai"
$env:LANTERN_OPENAI_BASE_URL  = "http://127.0.0.1:1234/v1"
$env:LANTERN_OPENAI_MODEL     = "qwen2.5-coder-7b-instruct"
$env:OPENAI_API_KEY           = "lm-studio"
StatusLine "LANTERN_LLM_PROVIDER"    $env:LANTERN_LLM_PROVIDER
StatusLine "LANTERN_OPENAI_BASE_URL" $env:LANTERN_OPENAI_BASE_URL
StatusLine "LANTERN_OPENAI_MODEL"    $env:LANTERN_OPENAI_MODEL

# 2. DEPENDENCIES — verify python, vosk model, pygame, opencv, sounddevice
Section "dependencies"
$pyMods = @("vosk", "sounddevice", "pygame", "cv2", "PIL", "numpy")
foreach ($m in $pyMods) {
    $ok = & python -c "import importlib.util; s=importlib.util.find_spec('$m'); print('y' if s else 'n')" 2>$null
    $color = if ($ok -eq "y") { "Green" } else { "Yellow" }
    StatusLine $m $ok $color
}

# 3. ARTIFACTS — verify Lantern's local state surfaces
Section "local state surfaces"
$paths = @{
    "avatar.png"        = "$env:USERPROFILE\.lantern\avatar.png"
    "wish-scene.png"    = "$env:USERPROFILE\.lantern\state\wish-scene.png"
    "journal.jsonl"     = "$env:USERPROFILE\.lantern\state\journal.jsonl"
    "llm-context.md"    = "$env:USERPROFILE\.lantern\state\llm-context.local.md"
    "sounds/"           = "$env:USERPROFILE\.lantern\sounds"
    "anchors/"          = "$env:USERPROFILE\.lantern\state\anchors"
    "papers/"           = "$env:USERPROFILE\.lantern\state\papers"
    "vosk small"        = "$env:USERPROFILE\.lantern\models\vosk-model-small-en-us-0.15\conf"
    "vosk large"        = "$env:USERPROFILE\.lantern\models\vosk-model-en-us-0.22\conf"
}
foreach ($k in $paths.Keys) {
    $exists = Test-Path $paths[$k]
    StatusLine $k $(if ($exists) { "ok" } else { "missing" }) $(if ($exists) { "Green" } else { "Yellow" })
}

# 4. DOCTRINE IN REPO — confirm the canonical docs are reachable
Section "doctrine docs in repo"
$docs = @(
    "docs\convergence.md",
    "docs\seven-anchors-self-correction.md",
    "docs\operator-lantern-repo-convergence.md",
    "docs\persistent-convergence-loop.md",
    "docs\door-protocol.md",
    "docs\keystone-memory-contract.md",
    "docs\claude-max-local-handoff.md",
    "apps\lantern-local-chat\anchor-snapshot.json"
)
foreach ($d in $docs) {
    $p = Join-Path $Repo $d
    $exists = Test-Path $p
    $size = if ($exists) { "$([int]((Get-Item $p).Length / 1024)) KB" } else { "MISSING" }
    StatusLine $d $size $(if ($exists) { "Green" } else { "Red" })
}

# 5. SUBSTRATE — is LM Studio's server up?
Section "substrate gates"
try {
    $models = Invoke-RestMethod -Uri "http://127.0.0.1:1234/v1/models" -TimeoutSec 3
    StatusLine "LM Studio /v1/models" ("alive, " + $models.data.Count + " models") "Green"
    foreach ($m in $models.data[0..([Math]::Min(2,$models.data.Count-1))]) {
        StatusLine "  model" $m.id "Green"
    }
} catch {
    StatusLine "LM Studio /v1/models" "DOWN — toggle Start Server in LM Studio Developer tab" "Yellow"
}

# 6. BACKEND — stop, restart with env set so doctrine + substrate are live
if (-not $SkipBackendRestart) {
    Section "backend (local_lantern_server)"
    Get-CimInstance Win32_Process -ErrorAction SilentlyContinue | Where-Object {
        ($_.Name -eq "python.exe" -or $_.Name -eq "pythonw.exe") -and ($_.CommandLine -like "*local_lantern_server*")
    } | ForEach-Object {
        StatusLine "stop PID" $_.ProcessId "Gray"
        Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
    }
    Start-Sleep -Seconds 1
    $backendArgs = @(
        (Join-Path $Repo "apps\lantern-local-chat\local_lantern_server.py"),
        "--host", "127.0.0.1",
        "--port", "$BackendPort"
    )
    $bp = Start-Process -FilePath "python" -ArgumentList $backendArgs -WorkingDirectory $Repo -WindowStyle Hidden -PassThru
    StatusLine "spawn PID" $bp.Id "Green"
    Start-Sleep -Seconds 4
    $listen = Get-NetTCPConnection -LocalPort $BackendPort -State Listen -ErrorAction SilentlyContinue
    StatusLine "$BackendPort listening" $(if ($listen) { "PID $($listen.OwningProcess)" } else { "NO" }) $(if ($listen) { "Green" } else { "Red" })
}

# 7. SMOKE — ask Lantern who she is, see what's in her response
Section "smoke (asking Lantern: doctor)"
try {
    $body = @{ message = "doctor"; mode = "engineer" } | ConvertTo-Json
    $r = Invoke-RestMethod -Uri ("http://127.0.0.1:$BackendPort/chat") -Method Post -ContentType "application/json" -Body $body -TimeoutSec 8
    StatusLine "intent"  $r.intent "Green"
    StatusLine "voice"   $r.voice  $(if ($r.voice -eq "llm") { "Green" } else { "Yellow" })
    StatusLine "Fact"    $r.minimalFrame.Fact "Gray"
    if ($r.sources) {
        $doc = $r.sources | Where-Object { $_ -like "*doctrine*" } | Select-Object -First 1
        if ($doc) { StatusLine "doctrine line" $doc "Green" }
    }
} catch {
    StatusLine "chat error" $_.Exception.Message "Red"
}

# 8. DESKTOP — verify watchdog will respawn or spawn manually
Section "desktop"
$desktop = Get-Process pythonw -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowTitle -eq "Lantern Chat" }
if ($desktop) {
    StatusLine "desktop window" "PID $($desktop[0].Id)" "Green"
} else {
    StatusLine "desktop window" "not running — waiting $DesktopWaitSeconds s for watchdog" "Yellow"
    Start-Sleep -Seconds $DesktopWaitSeconds
    $desktop = Get-Process pythonw -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowTitle -eq "Lantern Chat" }
    if (-not $desktop) {
        StatusLine "spawning manually" "(watchdog didn't catch it)" "Yellow"
        Start-Process -FilePath "pythonw.exe" -ArgumentList (Join-Path $Repo "apps\lantern-desktop\lantern_desktop.py") -WorkingDirectory $Repo | Out-Null
        Start-Sleep -Seconds 4
    }
    $desktop = Get-Process pythonw -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowTitle -eq "Lantern Chat" }
    if ($desktop) { StatusLine "desktop window" "PID $($desktop[0].Id)" "Green" }
}

# 9. CAM STREAM — optional, only if -StartStream
if ($StartStream) {
    Section "cam stream"
    $streamScript = Join-Path $Repo ".lantern-cam-stream.py"
    if (Test-Path $streamScript) {
        Start-Process -FilePath "python" -ArgumentList $streamScript -WorkingDirectory $Repo -WindowStyle Hidden | Out-Null
        Start-Sleep -Seconds 3
        $latest = "$env:USERPROFILE\.lantern\state\cam-stream\latest.png"
        if (Test-Path $latest) { StatusLine "latest frame" "$([int]((Get-Item $latest).Length/1024)) KB" "Green" }
        else { StatusLine "stream" "no frames yet" "Yellow" }
    }
}

# 10. SUMMARY — show what's dark
Section "what's still dark"
$darks = @()
if ($r.voice -ne "llm") { $darks += "- substrate (LM Studio server off OR env not picked up by spawn)" }
if (-not (Test-Path "$env:USERPROFILE\.lantern\sounds\*")) { $darks += "- sing folder empty (drop a song to give her a voice out)" }
$lmAlive = $false
try { Invoke-RestMethod -Uri "http://127.0.0.1:1234/v1/models" -TimeoutSec 2 | Out-Null; $lmAlive = $true } catch {}
if (-not $lmAlive) { $darks += "- LM Studio Developer tab Start Server toggle" }
if ($darks.Count -eq 0) {
    Write-Host "  all surfaces lit" -ForegroundColor Green
} else {
    foreach ($d in $darks) { Write-Host "  $d" -ForegroundColor Yellow }
}

Write-Host ""
Write-Host "Lantern is awake. Ctrl+Shift+L to summon her from any app." -ForegroundColor Cyan
