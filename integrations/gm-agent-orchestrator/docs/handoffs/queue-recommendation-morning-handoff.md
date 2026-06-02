# Morning handoff: queue recommendation blocker

Issue: #109
Owner candidates: Gemini or Claude
Priority: P0
Status: ready for next implementation pass

## Goal

Make the orchestrator help with queue decisions, not just move task files safely.

The queue movement foundation is now in `master`:

- `scripts/Move-OrchestratorTask.ps1`
- `tests/Test-TaskMovement.ps1`
- `tests/Test-AgentSlotUsesTaskMovement.ps1`
- `config/queue-strategies/default.cost-optimized.json`
- `config/queue-strategies/README.md`
- `Start-AgentSlot.ps1` now routes claim/done/failed movements through the helper

The remaining blocker is a queue recommendation/status layer.

## Required next feature

Add a minimal queue recommendation command that reads the current queue state, slot state, movement audit, and active queue strategy, then outputs one recommended next queue action.

Suggested script:

```text
scripts/Get-QueueRecommendation.ps1
```

Suggested test:

```text
tests/Test-QueueRecommendation.ps1
```

## Inputs to read

Read only these files/areas first:

1. `AGENTS.md`
2. `docs/agent-contract.md`
3. `config/queue-strategies/default.cost-optimized.json`
4. `scripts/Move-OrchestratorTask.ps1`
5. `scripts/Get-OrchestratorStatus.ps1`
6. `scripts/Start-AgentSlot.ps1`
7. `tests/Test-TaskMovement.ps1`
8. `tests/Test-AgentSlotUsesTaskMovement.ps1`
9. `tasks/queue/`, `tasks/active/`, `tasks/failed/`, `tasks/done/`
10. `reports/queue-movements/`, if present
11. `status/*.json`, if present

Do not scan unrelated repos. Do not touch `ChildOfLevistus` or `gamemaker-room-editor` for this task.

## Recommendation output contract

`Get-QueueRecommendation.ps1` should output JSON by default.

Minimum fields:

```json
{
  "ok": true,
  "generatedAt": "<ISO timestamp>",
  "strategyName": "default.cost-optimized",
  "costMode": "minimize_paid_tokens",
  "recommendedAction": "hold|claim|retry|requeue|inspect|none",
  "taskName": "<task file or empty>",
  "from": "queue|active|failed|done|hold|",
  "to": "queue|active|failed|done|hold|",
  "slot": "<recommended slot or empty>",
  "reason": "<human-readable reason>",
  "risk": "low|medium|high",
  "requiresHuman": false,
  "command": "<safe suggested command or empty>"
}
```

The command field may suggest `Move-OrchestratorTask.ps1`, but it must not execute movement automatically.

## Minimal decision rules

Keep this conservative and human-review friendly.

1. If there are active tasks, recommend `inspect` before claiming more work.
2. If the same task appears to have repeated failures or recent movement churn, recommend `hold` or `inspect`, not automatic retry.
3. If a failed task exists and no active work is present, recommend `inspect` unless the failure reason is clearly transient.
4. If queued tasks exist and no active work is present, recommend `claim` for the first safe task.
5. Prefer local/free/read-only lanes for triage/status/docs tasks according to `default.cost-optimized.json`.
6. Do not recommend local/read-only routing for code-edit tasks.
7. Do not recommend automatic action for tasks mentioning secrets, credentials, billing, production, or deploy.
8. If no queued/failed/active tasks exist, recommend `none`.

## Cost strategy requirement

The recommendation must include why the strategy chose the action.

Examples:

```text
Reason: No active tasks. First queued task is docs/status work, so default.cost-optimized prefers free-tier/local-safe routing before paid high-context agents.
```

```text
Reason: Failed task has repeated movement entries; holding to avoid burning tokens on same-cause retry.
```

## Status/dashboard follow-up

Do not implement a dashboard button yet.

After `Get-QueueRecommendation.ps1` exists and tests pass, the next pass should wire its output into:

- `scripts/Get-OrchestratorStatus.ps1`
- dashboard queue/activity card

## Safety rules

- Do not move queue files in this task.
- Do not start agents.
- Do not auto-rerun failed tasks.
- Do not delete task content.
- Do not overwrite `status/orchestrator.json` manually.
- Avoid broad refactors.
- Stop after one script plus one test, or after the first concrete blocker.

## Validation

Run the cheapest relevant validation first:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tests\Test-PowerShellSyntax.ps1 -Root "$PWD"
powershell -NoProfile -ExecutionPolicy Bypass -File .\tests\Test-QueueRecommendation.ps1 -Root "$PWD"
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\Get-QueueRecommendation.ps1 -Root "$PWD" | ConvertFrom-Json | Out-Null
```

If `Test-QueueRecommendation.ps1` does not exist yet, create it with compact temp-directory fixtures similar to `Test-TaskMovement.ps1`.

## Suggested commits

1. `feat(queue): add cost-aware queue recommendation command`
2. `test(queue): cover queue recommendation decisions`
3. Optional only if tiny: `ci(queue): validate queue recommendation contract`

## Final report format

```text
Result: pass/fail/partial
Issue: #109
Branch: master or <branch>
Command: <exact command or not run>
Files changed: <short list>
Validation: <pass/fail/not run + reason>
Verified: <facts verified>
Assumed: <assumptions or none>
Grudgebook entry required: <yes/no + reason>
Next: <one action only>
```

## Current known good local validation

Alex reported the following passed after syncing `origin/master`:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tests\Test-PowerShellSyntax.ps1 -Root "$PWD"
powershell -NoProfile -ExecutionPolicy Bypass -File .\tests\Test-TaskMovement.ps1 -Root "$PWD"
powershell -NoProfile -ExecutionPolicy Bypass -File .\tests\Test-AgentSlotUsesTaskMovement.ps1 -Root "$PWD"
```

## One-sentence task brief

Build `Get-QueueRecommendation.ps1` so the orchestrator can explain the next queue action using the editable cost-optimized strategy, without moving files or starting agents automatically.
