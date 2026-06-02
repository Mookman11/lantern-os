# ALEX HANDOFF: Status queue recommendation integration

Issue: #109
Related contract issue: #160
Status: ready for local safe merge

## Reason this is for Alex

This step must be done in your local checkout because a connector edit hit a GitHub `409` while updating `scripts/Get-OrchestratorStatus.ps1`. The file is large and has rich slot/dashboard logic, so it should be patched locally instead of overwritten through a simplified connector replacement.

## What I changed

Already committed on `master`:

- `scripts/Get-QueueRecommendation.ps1`
- `tests/Test-QueueRecommendation.ps1`
- this Alex handoff

## What I could not do here

I could not safely patch `scripts/Get-OrchestratorStatus.ps1` through the connector without risking deletion of existing slot, watcher, worktree, availability, activity-log, and warning fields.

## Where to run them

Shell: PowerShell

Directory:

```powershell
cd <LOCAL_GM_AGENT_ORCHESTRATOR_PATH>
```

Replace `<LOCAL_GM_AGENT_ORCHESTRATOR_PATH>` with your local `gm-agent-orchestrator` checkout, for example:

```powershell
cd "$env:USERPROFILE\Documents\gm-agent-orchestrator"
```

## Copy/paste commands

First sync the repo:

```powershell
git status --short
git pull --ff-only origin master
```

Open the status script:

```powershell
notepad .\scripts\Get-OrchestratorStatus.ps1
```

Add this helper near the other helper functions:

```powershell
function Get-QueueRecommendationOrNull {
    $script = Join-Path $Root "scripts\Get-QueueRecommendation.ps1"
    if (-not (Test-Path -LiteralPath $script -PathType Leaf)) { return $null }
    try {
        $json = & powershell -NoProfile -ExecutionPolicy Bypass -File $script -Root $Root 2>$null
        if ($LASTEXITCODE -ne 0) { return $null }
        return (($json | ForEach-Object { $_.ToString() }) -join "`n") | ConvertFrom-Json
    }
    catch { return $null }
}
```

Find the line that computes the task summaries. It starts like this:

```powershell
$queueTasks = @(Get-FileSummary $queueDir); $activeTasks = @(Get-FileSummary $activeDir); $doneTasks = @(Get-FileSummary $doneDir); $failedTasks = @(Get-FileSummary $failedDir);
```

After that task-summary line, add:

```powershell
$queueRecommendation = Get-QueueRecommendationOrNull
```

In the final `$status = [pscustomobject]@{ ... }` block, add this field near `availability` or `nextAction`:

```powershell
    queueRecommendation = $queueRecommendation
```

Then run validation:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tests\Test-PowerShellSyntax.ps1 -Root "$PWD"
powershell -NoProfile -ExecutionPolicy Bypass -File .\tests\Test-QueueRecommendation.ps1 -Root "$PWD"
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\Get-QueueRecommendation.ps1 -Root "$PWD" | ConvertFrom-Json | Out-Null
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\Get-OrchestratorStatus.ps1 -Root "$PWD" | ConvertFrom-Json | Out-Null
```

Commit if validation passes:

```powershell
git status --short
git add .\scripts\Get-OrchestratorStatus.ps1
git commit -m "feat(queue): include recommendation in orchestrator status"
git push origin master
```

## Expected result

- All validation commands exit successfully.
- `status/orchestrator.json` is regenerated.
- The JSON output from `Get-OrchestratorStatus.ps1` includes a top-level `queueRecommendation` object.
- Existing fields such as `availability`, `activityLog`, `watcher`, `counts`, `tasks`, and `slots` remain present.

## If it fails

If `git pull --ff-only` fails:

```powershell
git status --short
git branch --show-current
```

Stop and inspect local changes before pulling.

If syntax validation fails, undo only the local status-script edit and retry the minimal patch:

```powershell
git restore .\scripts\Get-OrchestratorStatus.ps1
```

If `Test-QueueRecommendation.ps1` fails, do not patch dashboard/status yet. Fix `scripts/Get-QueueRecommendation.ps1` or the test first.

If `Get-OrchestratorStatus.ps1` runs but `queueRecommendation` is missing, check that the field was added inside the final `$status` object and that `$queueRecommendation = Get-QueueRecommendationOrNull` runs before `$status` is constructed.

## Evidence

This proves:

- The queue recommendation command exists and returns parseable JSON.
- The recommendation tests pass locally.
- The status command still returns parseable JSON after the patch.
- The status JSON now exposes `queueRecommendation` for dashboard/status consumers.

This does not prove:

- The dashboard UI renders the new field.
- Any queue task was moved.
- Any agent was started.

## What not to do

- Do not replace `scripts/Get-OrchestratorStatus.ps1` with a simplified version.
- Do not delete existing slot, watcher, worktree, availability, activity-log, warning, count, task, or slot fields.
- Do not move queue files as part of this step.
- Do not start agents as part of this step.
- Do not commit if validation fails.

## Next single action

Patch `scripts/Get-OrchestratorStatus.ps1` locally with the three small additions above, then run the four validation commands.
