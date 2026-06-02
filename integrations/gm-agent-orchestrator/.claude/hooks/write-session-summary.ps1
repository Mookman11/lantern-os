<#
.SYNOPSIS
Stop hook that appends a structured session summary to AGENT_LOG.md.

.DESCRIPTION
After source-control closure is confirmed by enforce-pr-closure.ps1, this hook
writes a timestamped entry to AGENT_LOG.md capturing:
  - branch and worktree state
  - files changed vs master (or HEAD)
  - open PRs for the current branch (via gh)
  - a reminder to record grudgebook entries if warranted
  - a reminder that visible chat/final responses requiring handoff need a HANDOFF_PACKET block

Never blocks. Always allows stop.
#>

[CmdletBinding()]
param()

$ErrorActionPreference = "SilentlyContinue"
Set-StrictMode -Off

# ---- parse payload ----
$rawInput = ""
try { $rawInput = [Console]::In.ReadToEnd() } catch {}

$payload = $null
if (-not [string]::IsNullOrWhiteSpace($rawInput)) {
    try { $payload = $rawInput | ConvertFrom-Json -ErrorAction Stop } catch {}
}

function Get-PayloadProp {
    param([object]$P, [string]$Key)
    if ($null -eq $P) { return $null }
    try {
        $names = @($P.PSObject.Properties | Select-Object -ExpandProperty Name)
        if ($names -contains $Key) { return $P.PSObject.Properties[$Key].Value }
    } catch {}
    return $null
}

$stopHookActive = Get-PayloadProp -P $payload -Key "stop_hook_active"
if ($null -ne $stopHookActive -and [bool]$stopHookActive) { exit 0 }

# ---- resolve project dir ----
$projectDir = $env:CLAUDE_PROJECT_DIR
if ([string]::IsNullOrWhiteSpace($projectDir)) {
    $cwdVal = Get-PayloadProp -P $payload -Key "cwd"
    if (-not [string]::IsNullOrWhiteSpace($cwdVal)) { $projectDir = [string]$cwdVal }
}
if ([string]::IsNullOrWhiteSpace($projectDir)) { $projectDir = (Get-Location).Path }
if (-not (Test-Path -LiteralPath $projectDir)) { exit 0 }

Set-Location -LiteralPath $projectDir

$inWorkTree = & git rev-parse --is-inside-work-tree 2>$null
if ($LASTEXITCODE -ne 0 -or $inWorkTree -ne "true") { exit 0 }

# ---- gather facts ----
$timestamp   = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
$branch      = (& git rev-parse --abbrev-ref HEAD 2>$null).Trim()
$worktree    = (& git status --short 2>$null | Out-String).Trim()
$worktreeState = if ([string]::IsNullOrWhiteSpace($worktree)) { "clean" } else { "dirty" }

# Files changed vs master merge-base
if ($branch -notin @("master","main")) {
    $mergeBase   = (& git merge-base master HEAD 2>$null).Trim()
    $changedStat = (& git diff --stat "$mergeBase..HEAD" 2>$null | Out-String).Trim()
} else {
    $changedStat = (& git diff --stat HEAD 2>$null | Out-String).Trim()
}
if ([string]::IsNullOrWhiteSpace($changedStat)) { $changedStat = "none" }

# Last commit
$lastCommit  = (& git log --oneline -1 2>$null).Trim()

# PR for this branch
$prInfo = ""
$ghPath = (& where.exe gh 2>$null | Select-Object -First 1 -ErrorAction SilentlyContinue)
if (-not [string]::IsNullOrWhiteSpace($ghPath) -and $branch -notin @("master","main")) {
    $prJson = & gh pr view $branch --json number,url,state 2>$null
    if ($LASTEXITCODE -eq 0 -and -not [string]::IsNullOrWhiteSpace($prJson)) {
        try {
            $pr = $prJson | ConvertFrom-Json -ErrorAction Stop
            $prInfo = "PR #$($pr.number) ($($pr.state)): $($pr.url)"
        } catch {}
    }
}
if ([string]::IsNullOrWhiteSpace($prInfo)) { $prInfo = "none" }

# ---- build log entry ----
$entry = @"

---
Session: $timestamp
Branch: $branch
Worktree: $worktreeState
Last commit: $lastCommit
PR: $prInfo
Files changed vs base:
$changedStat
Grudgebook entry required: (fill in or remove this line before next session)
Chat handoff reminder: If the visible response asks a human/operator/agent to continue work elsewhere or run a copy/paste packet, include a HANDOFF_PACKET block in that same response per docs/work-transfer-request-format.md.
"@

# ---- append to AGENT_LOG.md ----
$logPath = Join-Path $projectDir "AGENT_LOG.md"
try {
    if (-not (Test-Path -LiteralPath $logPath)) {
        "# Agent Log`n" | Set-Content -LiteralPath $logPath -Encoding UTF8
    }
    $entry | Add-Content -LiteralPath $logPath -Encoding UTF8
    [Console]::Error.WriteLine("[write-session-summary] Appended session entry to AGENT_LOG.md.")
} catch {
    [Console]::Error.WriteLine("[write-session-summary] Could not write AGENT_LOG.md: $_")
}

exit 0
