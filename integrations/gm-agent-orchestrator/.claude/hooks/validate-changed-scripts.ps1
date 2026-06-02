<#
.SYNOPSIS
Stop hook that runs the PowerShell parser on any .ps1 files changed or staged
in the current session. Blocks stop if a changed script has a parse error.

.DESCRIPTION
Finds .ps1 files that differ from master (or HEAD if on master). Parses each
with the built-in parser. If any file has errors, emits a block decision with
the specific file and error list so Claude can fix before finishing.

This catches parse errors before CI does — cheaply, locally, without a push.
#>

[CmdletBinding()]
param()

$ErrorActionPreference = "SilentlyContinue"
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

$inWorkTree = & git rev-parse --is-inside-work-tree 2>$null
if ($LASTEXITCODE -ne 0 -or $inWorkTree -ne "true") { exit 0 }

# ---- find changed .ps1 files vs merge-base with master ----
$branch = (& git rev-parse --abbrev-ref HEAD 2>$null).Trim()
$baseRef = "master"
if ($branch -eq "master" -or $branch -eq "main") {
    # On master: check staged + unstaged changes only
    $changedFiles = @(& git diff --name-only HEAD 2>$null) + @(& git diff --name-only 2>$null)
} else {
    # On a feature branch: check everything changed vs master
    $mergeBase = (& git merge-base $baseRef HEAD 2>$null).Trim()
    if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($mergeBase)) {
        [Console]::Error.WriteLine("[validate-changed-scripts] Could not find merge base; skipping.")
        exit 0
    }
    $changedFiles = @(& git diff --name-only "$mergeBase..HEAD" 2>$null)
    # Also include uncommitted changes
    $changedFiles += @(& git diff --name-only 2>$null)
    $changedFiles += @(& git diff --name-only --cached 2>$null)
}

$ps1Files = @($changedFiles | Sort-Object -Unique | Where-Object { $_ -match '\.ps1$' })

if ($ps1Files.Count -eq 0) { exit 0 }

# ---- parse each file ----
$failures = @()

foreach ($rel in $ps1Files) {
    $full = Join-Path $projectDir $rel
    if (-not (Test-Path -LiteralPath $full -PathType Leaf)) { continue }

    $parseErrors = $null
    $null = [System.Management.Automation.Language.Parser]::ParseFile(
        $full, [ref]$null, [ref]$parseErrors)

    if ($parseErrors -and $parseErrors.Count -gt 0) {
        $summary = ($parseErrors | ForEach-Object {
            "  Line $($_.Extent.StartLineNumber): $($_.Message)"
        }) -join "`n"
        $failures += "$rel`n$summary"
    }
}

if ($failures.Count -eq 0) {
    [Console]::Error.WriteLine("[validate-changed-scripts] $($ps1Files.Count) changed script(s) parsed OK.")
    exit 0
}

$reason = "PowerShell parse errors in changed scripts - fix before finishing:`n`n" +
          ($failures -join "`n`n")

$block = [pscustomobject]@{
    decision = "block"
    reason   = $reason
} | ConvertTo-Json -Depth 4 -Compress

Write-Output $block
exit 0
