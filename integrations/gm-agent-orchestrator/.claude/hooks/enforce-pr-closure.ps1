<#
.SYNOPSIS
Stop hook for Claude Code that enforces source-control closure:
the current branch must be pushed to origin and have an open PR before
Claude is allowed to finish its turn. The hook blocks on unpushed commits by
default; supervised sessions may opt into auto-push with CLAUDE_HOOK_AUTOPUSH=1.

.DESCRIPTION
Reads the standard Stop-hook JSON payload on stdin, then checks:

  1. The repo is in a sane state (in a git work tree, on a branch).
  2. If on master / main, allow stop only when the checkout is clean and has
     no local commits beyond origin. Local work on a protected branch must move
     to a feature branch with a PR before Claude can finish.
  3. The branch has an upstream and no commits unpushed to that upstream.
     If commits are unpushed, block with an exact push command. Supervised
     sessions can explicitly enable auto-push with: setx CLAUDE_HOOK_AUTOPUSH 1
  4. `gh pr view` finds an open PR for the branch. If gh is unavailable, block
     instead of silently skipping because the PR evidence cannot be verified.

If any check still fails after auto-push, emits {"decision": "block",
"reason": "..."} on stdout and exits 0. Claude Code will refuse to finish
and will tell the agent to fix it.

If `stop_hook_active` is true in the input payload, the hook short-circuits
to avoid infinite loops when the agent is already trying to recover.

.NOTES
Install path inside this repo:
    .claude/hooks/enforce-pr-closure.ps1

Registered via .claude/settings.json:
    {
      "hooks": {
        "Stop": [
          {
            "hooks": [
              {
                "type": "command",
                "command": "powershell -NoProfile -ExecutionPolicy Bypass -File \"%CLAUDE_PROJECT_DIR%\\.claude\\hooks\\enforce-pr-closure.ps1\""
              }
            ]
          }
        ]
      }
    }
#>

[CmdletBinding()]
param()

# Stop hooks must not throw; convert errors into structured decisions.
$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

function Emit-Allow {
    # Silence -> Claude Code allows the stop.
    exit 0
}

function Emit-Block {
    param([string]$Reason)
    $payload = [pscustomobject]@{
        decision = "block"
        reason   = $Reason
    } | ConvertTo-Json -Depth 4 -Compress
    Write-Output $payload
    exit 0
}

function Emit-Skip {
    # Non-blocking notice on stderr. Stop is still allowed.
    param([string]$Message)
    [Console]::Error.WriteLine("[enforce-pr-closure] $Message")
    exit 0
}

function Test-PayloadProperty {
    param(
        [object]$InputObject,
        [string]$Name
    )
    if ($null -eq $InputObject) { return $false }
    return $null -ne $InputObject.PSObject.Properties[$Name]
}

# ---- 0. Parse hook payload ----
$rawInput = ""
try {
    $rawInput = [Console]::In.ReadToEnd()
}
catch {
    Emit-Skip "Could not read stdin payload: $($_.Exception.Message)"
}

$payload = $null
if (-not [string]::IsNullOrWhiteSpace($rawInput)) {
    try { $payload = $rawInput | ConvertFrom-Json -ErrorAction Stop }
    catch { $payload = $null }
}

if ((Test-PayloadProperty -InputObject $payload -Name "stop_hook_active") -and [bool]$payload.stop_hook_active) {
    # Avoid infinite blocking when the agent is already responding to a previous block.
    Emit-Allow
}

$projectDir = $env:CLAUDE_PROJECT_DIR
if ([string]::IsNullOrWhiteSpace($projectDir) -and (Test-PayloadProperty -InputObject $payload -Name "cwd")) {
    $projectDir = [string]$payload.cwd
}
if ([string]::IsNullOrWhiteSpace($projectDir)) {
    $projectDir = (Get-Location).Path
}
if (-not (Test-Path -LiteralPath $projectDir)) {
    Emit-Skip "Project dir not found: $projectDir"
}

Set-Location -LiteralPath $projectDir

# ---- 1. Git work tree sanity ----
$inWorkTree = & git rev-parse --is-inside-work-tree 2>$null
if ($LASTEXITCODE -ne 0 -or $inWorkTree -ne "true") {
    Emit-Skip "Not in a git work tree."
}

$branch = (& git rev-parse --abbrev-ref HEAD 2>$null).Trim()
if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($branch) -or $branch -eq "HEAD") {
    Emit-Block "Detached HEAD or unknown branch. Check out a feature branch and push it before finishing."
}

# ---- 2. Protected branches must not contain local work ----
if ($branch -in @("master", "main")) {
    $status = (& git status --short 2>$null)
    if ($LASTEXITCODE -ne 0) {
        Emit-Block "Could not verify protected branch '$branch' cleanliness. Run git status, then move work to a feature branch and PR before finishing."
    }
    if (-not [string]::IsNullOrWhiteSpace(($status | Out-String).Trim())) {
        Emit-Block "Protected branch '$branch' has local changes. Create a feature branch, commit, push, and open a PR before finishing."
    }

    $remoteBranch = "origin/$branch"
    $remoteExists = & git rev-parse --verify --quiet $remoteBranch 2>$null
    if ($LASTEXITCODE -eq 0) {
        $protectedAhead = (& git rev-list --count "$remoteBranch..HEAD" 2>$null).Trim()
        if ($LASTEXITCODE -ne 0) { $protectedAhead = "?" }
        if ($protectedAhead -ne "0" -and $protectedAhead -ne "") {
            Emit-Block "Protected branch '$branch' has $protectedAhead local commit(s) not on $remoteBranch. Create a feature branch from this state, push it, and open a PR before finishing."
        }
    }

    Emit-Allow
}

# ---- 3. Upstream / unpushed commits - block by default; auto-push only when supervised ----
$autoPushEnabled = $false
if ($env:CLAUDE_HOOK_AUTOPUSH -match "^(1|true|yes|on)$") {
    $autoPushEnabled = $true
}

function Invoke-AutoPush {
    param(
        [string]$Branch,
        [bool]$NewUpstream
    )
    $args = @("push")
    if ($NewUpstream) { $args += @("-u", "origin", $Branch) }
    $output = & git @args 2>&1
    return [pscustomobject]@{
        ExitCode = $LASTEXITCODE
        Output   = ($output | Out-String).Trim()
    }
}

# PS 5.1: git rev-parse "@{u}" exits non-zero and writes to stderr when no upstream is
# set. With $ErrorActionPreference = "Stop", that stderr write throws a NativeCommandError
# even with 2>$null. Wrap in try/catch to capture the failure cleanly on all PS versions.
$upstream = ""
try { $upstream = (& git rev-parse --abbrev-ref --symbolic-full-name "@{u}" 2>$null) } catch { $upstream = "" }
if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($upstream)) {
    if (-not $autoPushEnabled) {
        Emit-Block "Branch '$branch' has no upstream. Run: git push -u origin $branch, then open a PR before finishing. Auto-push is disabled unless CLAUDE_HOOK_AUTOPUSH=1."
    }
    [Console]::Error.WriteLine("[enforce-pr-closure] No upstream for '$branch'; auto-pushing with: git push -u origin $branch")
    $push = Invoke-AutoPush -Branch $branch -NewUpstream $true
    if ($push.ExitCode -ne 0) {
        Emit-Block "Auto-push failed for '$branch'. Run manually:`n  git push -u origin $branch`n`nOutput:`n$($push.Output)"
    }
    [Console]::Error.WriteLine("[enforce-pr-closure] Pushed and set upstream for '$branch'.")
    $upstream = ""
    try { $upstream = (& git rev-parse --abbrev-ref --symbolic-full-name "@{u}" 2>$null) } catch { $upstream = "" }
    if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($upstream)) {
        Emit-Block "Push appeared to succeed but '$branch' still has no upstream tracking. Investigate manually."
    }
}
$upstream = $upstream.Trim()

$ahead = (& git rev-list --count "$upstream..HEAD" 2>$null).Trim()
if ($LASTEXITCODE -ne 0) { $ahead = "?" }
if ($ahead -ne "0" -and $ahead -ne "") {
    if (-not $autoPushEnabled) {
        Emit-Block "Branch '$branch' has $ahead commit(s) not pushed to $upstream. Run: git push, then verify the PR before finishing. Auto-push is disabled unless CLAUDE_HOOK_AUTOPUSH=1."
    }
    [Console]::Error.WriteLine("[enforce-pr-closure] '$branch' has $ahead unpushed commit(s); auto-pushing with: git push")
    $push = Invoke-AutoPush -Branch $branch -NewUpstream $false
    if ($push.ExitCode -ne 0) {
        Emit-Block "Auto-push failed for '$branch'. Run manually:`n  git push`n`nOutput:`n$($push.Output)"
    }
    [Console]::Error.WriteLine("[enforce-pr-closure] Pushed $ahead commit(s) to $upstream.")
    # Re-verify the push actually closed the gap.
    $aheadAfter = (& git rev-list --count "$upstream..HEAD" 2>$null).Trim()
    if ($LASTEXITCODE -eq 0 -and $aheadAfter -ne "0" -and $aheadAfter -ne "") {
        Emit-Block "Auto-push completed but '$branch' is still $aheadAfter commit(s) ahead of $upstream. Investigate manually."
    }
}

# ---- 4. PR existence via gh ----
$ghCmd = Get-Command gh -ErrorAction SilentlyContinue
if ($null -eq $ghCmd) {
    Emit-Block "gh CLI not installed or not on PATH, so PR evidence for '$branch' cannot be verified. Install gh or open/verify the PR from another tool before finishing."
}

$prJson = & gh pr view $branch --json state,number,url,isDraft,headRefName,baseRefName 2>$null
$prExitCode = $LASTEXITCODE

if ($prExitCode -ne 0 -or [string]::IsNullOrWhiteSpace($prJson)) {
    Emit-Block "No PR found for branch '$branch'. Open one against master: gh pr create --base master --head $branch --fill"
}

try {
    $pr = $prJson | ConvertFrom-Json -ErrorAction Stop
}
catch {
    Emit-Block "Could not parse 'gh pr view' output for branch '$branch'. Verify with: gh pr view $branch"
}

if ($pr.state -ne "OPEN") {
    Emit-Block "PR #$($pr.number) for branch '$branch' is $($pr.state.ToLower()), not open. Reopen it or create a new PR before finishing."
}

if ($pr.PSObject.Properties.Name -contains "headRefName" -and $pr.headRefName -ne $branch) {
    Emit-Block "PR #$($pr.number) does not point at current branch '$branch' (head: $($pr.headRefName)). Open or update a PR for this branch before finishing."
}

# All checks passed.
Emit-Allow
