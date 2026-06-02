# Queue Recommendation Script (Issue #109)

**Priority:** P0  
**Owner:** Codex (implementation) → Claude (review)  
**Issue:** #109  
**Source:** docs/handoffs/queue-recommendation-morning-handoff.md

## Goal

Build `Get-QueueRecommendation.ps1` so the orchestrator can explain the next queue action using the editable cost-optimized strategy, without moving files or starting agents automatically.

## Inputs to read first

1. `AGENTS.md`
2. `docs/agent-contract.md`
3. `config/queue-strategies/default.cost-optimized.json`
4. `scripts/Move-OrchestratorTask.ps1`
5. `scripts/Get-OrchestratorStatus.ps1`
6. `scripts/Start-AgentSlot.ps1`
7. `tests/Test-TaskMovement.ps1`
8. `tests/Test-AgentSlotUsesTaskMovement.ps1`
9. `tasks/queue/`, `tasks/active/`, `tasks/failed/`, `tasks/done/`

## Deliverables

- `scripts/Get-QueueRecommendation.ps1` — outputs JSON recommendation
- `tests/Test-QueueRecommendation.ps1` — compact temp-directory fixtures

## Output contract

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

## Decision rules

1. Active tasks present → recommend `inspect` before claiming more
2. Repeated failures/churn → recommend `hold` or `inspect`, not retry
3. Failed task, no active work → recommend `inspect` unless clearly transient
4. Queued tasks, no active work → recommend `claim` for first safe task
5. Prefer local/free lanes for triage/status/docs per cost-optimized strategy
6. Do not recommend local/read-only routing for code-edit tasks
7. Do not recommend auto-action for tasks mentioning secrets, credentials, billing, production, deploy
8. No queued/failed/active tasks → recommend `none`

## Safety rules

- Do not move queue files
- Do not start agents
- Do not auto-rerun failed tasks
- Stop after one script + one test, or after first concrete blocker

## Validation

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tests\Test-PowerShellSyntax.ps1 -Root "$PWD"
powershell -NoProfile -ExecutionPolicy Bypass -File .\tests\Test-QueueRecommendation.ps1 -Root "$PWD"
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\Get-QueueRecommendation.ps1 -Root "$PWD" | ConvertFrom-Json | Out-Null
```

## Suggested commits

1. `feat(queue): add cost-aware queue recommendation command`
2. `test(queue): cover queue recommendation decisions`

## Final report format

```
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
