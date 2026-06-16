# Restart-Services.ps1 — stop and restart Lantern server + Discord bot
Set-Location "C:\dev\lantern-os"
$logDir = "C:\dev\lantern-os\logs"
New-Item -ItemType Directory -Force -Path $logDir | Out-Null

function Log($msg) {
    $line = "[$(Get-Date -Format 'u')] $msg"
    Write-Host $line
    Add-Content "$logDir\restart.log" $line
}

# ── Stop existing processes ────────────────────────────────────────────────

Log "Stopping Lantern server..."
Get-Process node -ErrorAction SilentlyContinue |
    Where-Object { $_.CommandLine -like "*lantern-garage*" -or $_.CommandLine -like "*server.js*" } |
    ForEach-Object { Stop-Process -Id $_.Id -Force; Log "  Killed node PID $($_.Id)" }

Log "Stopping Discord bot..."
Get-Process python -ErrorAction SilentlyContinue |
    Where-Object { $_.CommandLine -like "*bot_v2.py*" } |
    ForEach-Object { Stop-Process -Id $_.Id -Force; Log "  Killed python PID $($_.Id)" }

Start-Sleep -Seconds 2

# ── Start Lantern server ───────────────────────────────────────────────────

Log "Starting Lantern server..."
$serverLog = "$logDir\lantern-autostart.log"
$serverProc = Start-Process node -ArgumentList "server.js" `
    -WorkingDirectory "C:\dev\lantern-os\apps\lantern-garage" `
    -RedirectStandardOutput $serverLog `
    -RedirectStandardError "$serverLog.err" `
    -WindowStyle Hidden -PassThru
Log "  Server PID $($serverProc.Id) -> $serverLog"

# Wait for port 4177
$ready = $false
for ($i = 0; $i -lt 20; $i++) {
    Start-Sleep -Milliseconds 500
    try {
        $null = Invoke-WebRequest -Uri "http://127.0.0.1:4177/" -TimeoutSec 2 -ErrorAction Stop
        $ready = $true; break
    } catch {}
}
if ($ready) { Log "  Server ready on :4177" } else { Log "  [WARN] Server not responding after 10s — check $serverLog" }

# ── Start Discord bot ──────────────────────────────────────────────────────

Log "Starting Discord bot..."
$botLog = "$logDir\discord-autostart.log"
$pythonExe = if (Test-Path "C:\dev\lantern-os\.venv\Scripts\python.exe") {
    "C:\dev\lantern-os\.venv\Scripts\python.exe"
} else { "python" }

$botProc = Start-Process $pythonExe `
    -ArgumentList "C:\dev\lantern-os\src\discord_lounge_bot\bot_v2.py" `
    -WorkingDirectory "C:\dev\lantern-os" `
    -RedirectStandardOutput $botLog `
    -RedirectStandardError "$botLog.err" `
    -WindowStyle Hidden -PassThru
Log "  Bot PID $($botProc.Id) -> $botLog"

# Wait for bot ready line in log
$botReady = $false
for ($i = 0; $i -lt 20; $i++) {
    Start-Sleep -Milliseconds 500
    if ((Get-Content $botLog -ErrorAction SilentlyContinue) -match "Logged in as") {
        $botReady = $true; break
    }
}
if ($botReady) { Log "  Bot logged in" } else { Log "  [WARN] Bot not ready after 10s — check $botLog" }

# ── Summary ────────────────────────────────────────────────────────────────

Log "Done. Server PID $($serverProc.Id), Bot PID $($botProc.Id)"
