[CmdletBinding()]
param([string]$Root = "")

if ([string]::IsNullOrWhiteSpace($Root)) {
    $Root = (Resolve-Path "$PSScriptRoot\.." ).Path
}

$tasksPath = Join-Path $Root "tasks"
$statusFile = Join-Path $tasksPath "QUEUE_STATUS.json"

# Count current state from filesystem
$todo = @(Get-ChildItem "$tasksPath\queue" -File -ErrorAction SilentlyContinue | Where-Object { $_.Name -ne ".gitkeep" }).Count
$working = @(Get-ChildItem "$tasksPath\active" -File -ErrorAction SilentlyContinue | Where-Object { $_.Name -ne ".gitkeep" }).Count
$done = @(Get-ChildItem "$tasksPath\done" -File -ErrorAction SilentlyContinue | Where-Object { $_.Name -ne ".gitkeep" }).Count
$blocked = @(Get-ChildItem "$tasksPath\disabled" -File -ErrorAction SilentlyContinue | Where-Object { $_.Name -ne ".gitkeep" }).Count
$failed = @(Get-ChildItem "$tasksPath\failed" -File -ErrorAction SilentlyContinue | Where-Object { $_.Name -ne ".gitkeep" }).Count

$status = @{
    timestamp = (Get-Date -Format "o")
    queue = @{
        todo = $todo
        working = $working
        done = $done
        blocked = $blocked
        failed = $failed
    }
    health = @{
        isWorking = $working -gt 0
        needsAttention = ($blocked -gt 0) -or ($failed -gt 0)
        hasWork = ($todo -gt 0) -or ($working -gt 0)
    }
}

$status | ConvertTo-Json -Depth 3 | Set-Content $statusFile -Encoding UTF8
$status
