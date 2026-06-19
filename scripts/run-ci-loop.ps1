<#
.SYNOPSIS
  One hourly batch of the Creator Intelligence metadata loop. Rotates gaming
  search topics (by hour) so 12 runs cover a wide set, collects PUBLIC metadata
  via the YouTube Data API (loaded from .env), recalibrates, logs to
  research/ci_loop/logs. Invoked by the scheduled task; safe by hand too.
.NOTES
  Skips gracefully (exit 0) if the loop script or node is missing, so a
  registered task never errors loudly.
#>
$ErrorActionPreference = "Continue"
$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $RepoRoot

$logDir = Join-Path $RepoRoot "research\ci_loop\logs"
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$log = Join-Path $logDir ("ci-" + (Get-Date -Format "yyyy-MM-dd_HHmmss") + ".log")
function Log($m) { ("[" + (Get-Date -Format o) + "] " + $m) | Add-Content -Path $log -Encoding utf8 }

$script = Join-Path $RepoRoot "scripts\creator-intelligence-loop.js"
if (-not (Test-Path $script)) { Log "creator-intelligence-loop.js not on the checked-out branch; skipping."; exit 0 }
$node = (Get-Command node -ErrorAction SilentlyContinue).Source
if (-not $node) { Log "node not found on PATH; skipping."; exit 0 }

$queries = @(
  "gaming shorts","fortnite clips","minecraft shorts","valorant clips","warzone clips","apex legends clips",
  "call of duty shorts","roblox shorts","gta clips","rocket league clips","fps montage","gaming highlights",
  "speedrun clips","clutch moments","funny gaming moments","rage clips","insane plays","gaming fails",
  "battlefield clips","overwatch clips","league of legends clips","csgo clips","sniper montage","gaming reactions"
)
# Rotate by hour so each hourly run covers different topics.
$h = [int](Get-Date -Format "HH")
$pick = @()
for ($i = 0; $i -lt 5; $i++) { $pick += $queries[(($h * 5 + $i) % $queries.Length)] }

Log ("metadata cycle queries: " + ($pick -join ", "))
foreach ($q in $pick) {
  & $node "scripts\creator-intelligence-loop.js" "--cycle" ("--query=" + $q) *>> $log
}
& $node "scripts\creator-intelligence-loop.js" "--calibrate" *>> $log
$st = & $node "scripts\creator-intelligence-loop.js" "--status" | Out-String
Log ("status: " + $st.Trim())
Log "done"
