<#
.SYNOPSIS
    Drive Claude Code with the local Sigma-0 Ouro coder instead of a cloud model.

.DESCRIPTION
    Claude Code only speaks the Anthropic /v1/messages API; ouro_serve.py speaks
    the Ollama API. The translator is scripts/ouro_anthropic_bridge.py, which also
    fakes tool-calling (Ouro-1.4B has no native tool training). This script wires
    the whole chain in one shot:

        Claude Code --/v1/messages(+tools)--> bridge :8788 --/api/chat--> ouro_serve :11434 --> Ouro-1.4B

    It (1) verifies the model server on :11434 (optionally starts ouro_serve with
    OURO_NO_STOP=1, required for tool-calling), (2) starts the bridge on :8788 if
    it isn't already up, (3) sets the ANTHROPIC_* env vars in THIS session so the
    launched `claude` inherits them, then (4) launches Claude Code.

    GPU CAVEAT (from prior findings): the 8GB GPU holds ONE model process at a
    time. Running ouro_serve here while another Claude/Ouro session is live has
    crashed sessions. -StartModel is therefore OPT-IN, not the default - by default
    this script assumes the model is already serving and only probes it.

    EXPERIMENTAL: stock Sigma-0-1.4B does not reliably drive the full Claude Code agent
    loop (automatic tool_choice + ~20k-token system prompt). It partially works and
    is useful for short, forced, single-tool turns. See
    docs/SIGMA0-OURO-CODER.md -> "Drive Claude Code with Ouro".

.PARAMETER Model
    Model id sent upstream and shown to Claude Code (default "ouro:latest").

.PARAMETER BridgePort
    Port the Anthropic<->Ollama bridge listens on (default 8788).

.PARAMETER OllamaPort
    Port the Ollama-API model server (ouro_serve) listens on (default 11434).

.PARAMETER StartModel
    Also launch ouro_serve.py on :OllamaPort (OURO_NO_STOP=1) in a new window.
    Off by default - see the GPU caveat above.

.PARAMETER NoLaunch
    Set env + start the bridge, but do NOT launch `claude` (env is set in this
    session; type `claude` yourself, or inspect with `Get-ChildItem Env:ANTHROPIC_*`).

.EXAMPLE
    # Model already serving on :11434 - just bridge + wire + launch
    pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/Start-OuroClaudeCode.ps1

.EXAMPLE
    # Cold start everything (only when the GPU is otherwise idle)
    pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/Start-OuroClaudeCode.ps1 -StartModel
#>
param(
    [string]$Model      = "ouro:latest",
    [int]$BridgePort    = 8788,
    [int]$OllamaPort    = 11434,
    [switch]$StartModel,
    [switch]$NoLaunch
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot

function Test-Port([int]$Port) {
    $c = New-Object Net.Sockets.TcpClient
    try { if ($c.ConnectAsync("127.0.0.1", $Port).Wait(400)) { return $true } }
    catch {} finally { $c.Dispose() }
    return $false
}

# Find live python processes whose command line contains $ScriptName.
# Returns CimInstance objects (have .ProcessId, .CommandLine, .CreationDate).
function Get-ScriptProcs([string]$ScriptName) {
    @(Get-CimInstance Win32_Process -Filter "Name LIKE '%python%'" |
      Where-Object { $_.CommandLine -like "*$ScriptName*" })
}

# If more than one instance of $ScriptName is running, kill all but the newest.
function Remove-ExtraCopies([string]$ScriptName, [string]$Label) {
    $procs = Get-ScriptProcs $ScriptName | Sort-Object CreationDate -Descending
    if ($procs.Count -le 1) { return }
    Write-Host "[warn] $Label: $($procs.Count) instances found; culling $($procs.Count - 1) older cop$(if($procs.Count-1-gt 1){'ies'}else{'y'})." -ForegroundColor Yellow
    foreach ($extra in $procs[1..($procs.Count - 1)]) {
        Stop-Process -Id $extra.ProcessId -Force -ErrorAction SilentlyContinue
        Write-Host "       killed PID $($extra.ProcessId) (started $($extra.CreationDate))" -ForegroundColor DarkGray
    }
}

Write-Host "Ouro -> Claude Code wiring" -ForegroundColor Cyan
Write-Host "  chain: claude -> bridge :$BridgePort -> model :$OllamaPort ($Model)`n"

# Cull any leftover duplicates from prior invocations before we start.
Remove-ExtraCopies "ouro_serve.py"            "ouro_serve"
Remove-ExtraCopies "ouro_anthropic_bridge.py" "ouro_bridge"

# --- 1. model server (:11434) ------------------------------------------------
$serveProcs = Get-ScriptProcs "ouro_serve.py"
if ($serveProcs.Count -gt 0) {
    # Process exists — wait for it to bind the port rather than spawning another.
    Write-Host "[ok]   ouro_serve already running (PID $($serveProcs[0].ProcessId))" -ForegroundColor Green
    if (-not (Test-Port $OllamaPort)) {
        Write-Host "       port :$OllamaPort not yet open; waiting up to 90s for weights to load..." -ForegroundColor Yellow
        $waited = 0
        while ($waited -lt 90 -and -not (Test-Port $OllamaPort)) { Start-Sleep 3; $waited += 3 }
        if (Test-Port $OllamaPort) { Write-Host "[ok]   model server ready on :$OllamaPort" -ForegroundColor Green }
        else { Write-Host "[warn] model server still not answering after ${waited}s" -ForegroundColor Yellow }
    }
} elseif (Test-Port $OllamaPort) {
    Write-Host "[ok]   model server reachable on :$OllamaPort" -ForegroundColor Green
} elseif ($StartModel) {
    $venvPy = Join-Path $RepoRoot ".venv-train\Scripts\python.exe"
    $py = if (Test-Path $venvPy) { $venvPy } else { "python" }
    Write-Host "[..]   starting ouro_serve on :$OllamaPort (OURO_NO_STOP=1) via $py" -ForegroundColor Yellow
    $env:OURO_NO_STOP = "1"
    $env:OURO_PORT    = "$OllamaPort"
    Start-Process -FilePath $py -ArgumentList @("scripts/ouro_serve.py") -WorkingDirectory $RepoRoot
    Write-Host "       (loading weights can take ~30-60s; the bridge will retry)"
} else {
    Write-Host "[warn] nothing listening on :$OllamaPort." -ForegroundColor Yellow
    Write-Host "       Start the model first, then re-run, e.g.:"
    Write-Host "         .venv-train\Scripts\python scripts/ouro_serve.py   (set OURO_NO_STOP=1)" -ForegroundColor DarkGray
    Write-Host "       or pass -StartModel to launch it here (GPU must be idle)."
}

# --- 2. bridge (:8788) -------------------------------------------------------
$bridgeProcs = Get-ScriptProcs "ouro_anthropic_bridge.py"
if ($bridgeProcs.Count -gt 0) {
    Write-Host "[ok]   bridge already running (PID $($bridgeProcs[0].ProcessId)) on :$BridgePort" -ForegroundColor Green
} elseif (Test-Port $BridgePort) {
    Write-Host "[ok]   bridge already up on :$BridgePort" -ForegroundColor Green
} else {
    Write-Host "[..]   starting ouro_anthropic_bridge on :$BridgePort" -ForegroundColor Yellow
    $env:BRIDGE_PORT     = "$BridgePort"
    $env:OURO_OLLAMA_URL = "http://127.0.0.1:$OllamaPort"
    $env:OURO_MODEL_NAME = $Model
    $venvPy = Join-Path $RepoRoot ".venv-train\Scripts\python.exe"
    $py = if (Test-Path $venvPy) { $venvPy } else { "python" }
    Start-Process -FilePath $py -ArgumentList @("scripts/ouro_anthropic_bridge.py") -WorkingDirectory $RepoRoot
    Start-Sleep -Milliseconds 800
    if (Test-Port $BridgePort) { Write-Host "[ok]   bridge up" -ForegroundColor Green }
    else { Write-Host "[warn] bridge not yet answering - check its window" -ForegroundColor Yellow }
}

# --- 3. point Claude Code at the bridge --------------------------------------
$env:ANTHROPIC_BASE_URL         = "http://127.0.0.1:$BridgePort"
$env:ANTHROPIC_API_KEY          = "local-noauth"   # bridge ignores it; CC requires it set
$env:ANTHROPIC_MODEL            = $Model
$env:ANTHROPIC_SMALL_FAST_MODEL = $Model
$env:ANTHROPIC_DEFAULT_OPUS_MODEL   = $Model
$env:ANTHROPIC_DEFAULT_SONNET_MODEL = $Model
$env:ANTHROPIC_DEFAULT_HAIKU_MODEL  = $Model
$env:ANTHROPIC_CUSTOM_MODEL_OPTION  = $Model
Write-Host "`n[ok]   ANTHROPIC_* env set -> :$BridgePort ($Model)" -ForegroundColor Green

# --- 4. launch ---------------------------------------------------------------
if ($NoLaunch) {
    Write-Host "`n-NoLaunch: env is set in this session. Run 'claude' to start." -ForegroundColor Cyan
    return
}
if (-not (Get-Command claude -ErrorAction SilentlyContinue)) {
    Write-Host "`n[warn] 'claude' not on PATH. Env is set - open Claude Code from this shell." -ForegroundColor Yellow
    return
}
Write-Host "`nLaunching Claude Code on Ouro...`n" -ForegroundColor Cyan
& claude @args
