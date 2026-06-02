<#
.SYNOPSIS
Stop hook for Claude Code that cleans up scratch files from the worktree.

.DESCRIPTION
Reads the standard Stop-hook JSON payload on stdin, then:
  1. Resolves the project directory from env or payload.
  2. Removes known scratch file patterns (*.tmp, *.log.local, *.bak.local)
     that agents may leave behind.
  3. Never removes staged changes, tracked files, or anything not matched
     by the safe pattern list.
  4. Always allows stop — this hook never blocks.

.NOTES
Registered via .claude/settings.json Stop hooks array.
#>

[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

# ---- 0. Parse hook payload ----
$rawInput = ""
try { $rawInput = [Console]::In.ReadToEnd() } catch {}

$payload = $null
if (-not [string]::IsNullOrWhiteSpace($rawInput)) {
    try { $payload = $rawInput | ConvertFrom-Json -ErrorAction Stop } catch { $payload = $null }
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

# Short-circuit when agent is already handling a previous Stop block.
$stopHookActive = Get-PayloadProp -P $payload -Key "stop_hook_active"
if ($null -ne $stopHookActive -and [bool]$stopHookActive) { exit 0 }

# ---- 1. Resolve project dir ----
$projectDir = $env:CLAUDE_PROJECT_DIR
if ([string]::IsNullOrWhiteSpace($projectDir)) {
    $cwdVal = Get-PayloadProp -P $payload -Key "cwd"
    if (-not [string]::IsNullOrWhiteSpace($cwdVal)) { $projectDir = [string]$cwdVal }
}
if ([string]::IsNullOrWhiteSpace($projectDir)) {
    $projectDir = (Get-Location).Path
}
if (-not (Test-Path -LiteralPath $projectDir)) { exit 0 }

Set-Location -LiteralPath $projectDir

# ---- 2. Verify we are in a git work tree ----
$inWorkTree = & git rev-parse --is-inside-work-tree 2>$null
if ($LASTEXITCODE -ne 0 -or $inWorkTree -ne "true") { exit 0 }

# ---- 3. Remove only known safe scratch patterns ----
# These patterns are explicitly scoped to untracked files that agents produce.
# Tracked files are never touched.
$safePatterns = @("*.tmp", "*.log.local", "*.bak.local")

foreach ($pattern in $safePatterns) {
    # Use git clean dry-run to get candidate paths, then filter to pattern.
    $candidates = & git clean -fdn 2>$null | Where-Object { $_ -match "^Would remove " } |
        ForEach-Object { $_.Substring("Would remove ".Length).Trim() } |
        Where-Object { $_ -like $pattern }

    foreach ($candidate in $candidates) {
        $fullPath = Join-Path $projectDir $candidate
        if (Test-Path -LiteralPath $fullPath -PathType Leaf) {
            try {
                Remove-Item -LiteralPath $fullPath -Force -ErrorAction Stop
                [Console]::Error.WriteLine("[cleanup-worktree] Removed scratch file: $candidate")
            } catch {
                $errMsg = $_.Exception.Message
                [Console]::Error.WriteLine("[cleanup-worktree] Could not remove $candidate`: $errMsg")
            }
        }
    }
}

# Always allow stop.
exit 0
