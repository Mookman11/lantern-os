<#
.SYNOPSIS
Stop hook that checks out master after Claude finishes a turn on a feature branch.

.DESCRIPTION
Runs after enforce-pr-closure.ps1 (which already guarantees the branch is pushed
and has an open PR). If the current branch is not master/main, attempts
`git checkout master`. Never blocks stop — emits allow regardless of outcome.

.NOTES
Order in settings.json must be AFTER enforce-pr-closure.ps1 so master checkout
only happens when source-control closure is already satisfied.
#>

[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

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

# ---- verify git work tree ----
$inWorkTree = & git rev-parse --is-inside-work-tree 2>$null
if ($LASTEXITCODE -ne 0 -or $inWorkTree -ne "true") { exit 0 }

# ---- get current branch ----
$branch = (& git rev-parse --abbrev-ref HEAD 2>$null).Trim()
if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($branch) -or $branch -eq "HEAD") { exit 0 }

# Already on master — nothing to do.
if ($branch -in @("master", "main")) { exit 0 }

# ---- verify worktree is clean before switching ----
$dirty = (& git status --porcelain 2>$null)
if (-not [string]::IsNullOrWhiteSpace($dirty)) {
    [Console]::Error.WriteLine("[return-to-master] Worktree is dirty on '$branch'; skipping checkout master. Dirty files:`n$dirty")
    exit 0
}

# ---- checkout master ----
$output = & git checkout master 2>&1
if ($LASTEXITCODE -eq 0) {
    [Console]::Error.WriteLine("[return-to-master] Checked out master (was on '$branch').")
} else {
    [Console]::Error.WriteLine("[return-to-master] Could not checkout master from '$branch': $($output | Out-String)")
}

exit 0
