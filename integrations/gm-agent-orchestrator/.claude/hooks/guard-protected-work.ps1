<#
.SYNOPSIS
PreToolUse hook that blocks Claude from mutating protected branches or creating
agent commits with the operator's personal Git identity.

.DESCRIPTION
This hook is intentionally conservative. Stop hooks can catch bad closure, but
PreToolUse is the right layer for preventing the first bad edit or commit.

It blocks:
  - file mutation tools while the repo is on master/main;
  - shell commands that look like write operations while on master/main;
  - git commit / MCP commit tools when local Git config would author/commit as
    Alex Place <alex.place.7@gmail.com> unless the command explicitly overrides
    user.email to a non-operator identity with `git -c user.email=... commit`.
#>

[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$ProtectedBranches = @("master", "main")
$ProtectedNames = @("Alex Place")
$ProtectedEmails = @("alex.place.7@gmail.com")
$MutatingToolNames = @("Edit", "MultiEdit", "Write", "NotebookEdit")
$ShellToolNames = @("Bash", "PowerShell")
$McpCommitToolPattern = "commit_staged_changes"
$WriteCommandPattern = '(?i)(^|[;&|`n`r]\s*)(git\s+(add|commit|merge|pull|push)|Set-Content|Add-Content|Out-File|Remove-Item|Move-Item|Copy-Item|New-Item|ni\s|rm\s|del\s|mv\s|cp\s)'
$GitCommitPattern = '(?i)(^|[;&|`n`r]\s*)git(\s+-c\s+[^`n`r;&|]+)*\s+commit(\s|$)'
$ExplicitEmailPattern = '(?i)(?:^|\s)-c\s+user\.email=(?:"([^"`r`n]+)"|''([^''`r`n]+)''|([^\s`r`n;&|]+))'

function Emit-Allow { exit 0 }

function Emit-Block {
    param([string]$Reason)
    [pscustomobject]@{
        decision = "block"
        reason = $Reason
    } | ConvertTo-Json -Depth 4 -Compress
    exit 0
}

function Get-PropValue {
    param([object]$Object, [string]$Name)
    if ($null -eq $Object) { return $null }
    $prop = $Object.PSObject.Properties[$Name]
    if ($null -eq $prop) { return $null }
    return $prop.Value
}

function ConvertTo-Text {
    param([object]$Value)
    if ($null -eq $Value) { return "" }
    if ($Value -is [string]) { return $Value }
    try { return ($Value | ConvertTo-Json -Depth 12 -Compress) } catch { return [string]$Value }
}

function Get-ExplicitCommitEmail {
    param([string]$CommandText)
    $match = [regex]::Match($CommandText, $ExplicitEmailPattern)
    if (-not $match.Success) { return $null }
    foreach ($groupIndex in 1..3) {
        if ($match.Groups[$groupIndex].Success -and -not [string]::IsNullOrWhiteSpace($match.Groups[$groupIndex].Value)) {
            return $match.Groups[$groupIndex].Value.Trim()
        }
    }
    return $null
}

$rawInput = ""
try { $rawInput = [Console]::In.ReadToEnd() } catch { Emit-Allow }
if ([string]::IsNullOrWhiteSpace($rawInput)) { Emit-Allow }

$payload = $null
try { $payload = $rawInput | ConvertFrom-Json -ErrorAction Stop } catch { Emit-Allow }

$toolName = [string](Get-PropValue -Object $payload -Name "tool_name")
$toolInput = Get-PropValue -Object $payload -Name "tool_input"
$toolCommand = Get-PropValue -Object $toolInput -Name "command"
if ($null -ne $toolCommand -and -not [string]::IsNullOrWhiteSpace([string]$toolCommand)) {
    $toolText = [string]$toolCommand
} else {
    $toolText = ConvertTo-Text -Value $toolInput
}

$projectDir = $env:CLAUDE_PROJECT_DIR
if ([string]::IsNullOrWhiteSpace($projectDir)) {
    $cwdVal = Get-PropValue -Object $payload -Name "cwd"
    if (-not [string]::IsNullOrWhiteSpace([string]$cwdVal)) { $projectDir = [string]$cwdVal }
}
if ([string]::IsNullOrWhiteSpace($projectDir)) { $projectDir = (Get-Location).Path }
if (-not (Test-Path -LiteralPath $projectDir)) { Emit-Allow }

Set-Location -LiteralPath $projectDir

$inside = & git rev-parse --is-inside-work-tree 2>$null
if ($LASTEXITCODE -ne 0 -or $inside -ne "true") { Emit-Allow }

$branch = (& git rev-parse --abbrev-ref HEAD 2>$null).Trim()
if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($branch) -or $branch -eq "HEAD") {
    Emit-Allow
}

$isMutatingTool = $MutatingToolNames -contains $toolName
$isShellWrite = ($ShellToolNames -contains $toolName) -and ($toolText -match $WriteCommandPattern)

if (($ProtectedBranches -contains $branch) -and ($isMutatingTool -or $isShellWrite)) {
    Emit-Block "Claude is on protected branch '$branch' and is trying to mutate the repo. Create/switch to a feature branch before editing, staging, committing, pushing, or changing files."
}

$isCommitTool = ($toolName -match $McpCommitToolPattern) -or (($ShellToolNames -contains $toolName) -and ($toolText -match $GitCommitPattern))
if (-not $isCommitTool) { Emit-Allow }

$configName = (& git config user.name 2>$null | Out-String).Trim()
$configEmail = (& git config user.email 2>$null | Out-String).Trim()
$explicitEmail = Get-ExplicitCommitEmail -CommandText $toolText

if (-not [string]::IsNullOrWhiteSpace($explicitEmail)) {
    if ($ProtectedEmails -contains $explicitEmail) {
        Emit-Block "Agent commit explicitly uses protected operator email '$explicitEmail'. Use a bot/agent email instead."
    }
    Emit-Allow
}

if (($ProtectedNames -contains $configName) -or ($ProtectedEmails -contains $configEmail)) {
    Emit-Block "Agent commit would use protected operator Git identity '$configName <$configEmail>'. Use an explicit bot identity, for example: git -c user.name=\"Claude Code\" -c user.email=\"claude-code@agents.local\" commit -m \"...\"."
}

Emit-Allow
