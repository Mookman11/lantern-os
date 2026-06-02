# P9 E2E claude-main focused review canary

role_owner: gpt
fallback_owner: human
risk_class: high
budget_class: light
terminal_rule: done|failed|requeued|blocked

Priority: P0 urgent canary

## Objective

Run a focused Claude review work unit for today's shipped changes while still proving start/claim lifecycle with exact auditable movement:

`queue -> active -> terminal (done|failed|requeued|blocked)`

Review scope (only):

- `c819e6b` safe-runner/e2e lifecycle patch
- `07dfb7d` explicit agent profiles/slot bindings + known-slot dispatch guard
- related contract docs touched today

Do not implement broad new changes in this unit. Review and findings only.

## Rules

1. Attempt exactly one supervised start for `claude-main`.
2. If claim occurs, verify `TASK_QUEUE.md` install path consistency.
3. Produce review findings in severity order (`P0/P1/P2`) with file references.
4. If no issues are found, explicitly state that and list residual risk/test gaps.
5. If provider/quota/policy block appears, return task cleanly to queue or fail with evidence.
6. Never leave stale `tasks/active` entry.

## Required Evidence

- counts before/after,
- active path if created,
- final task location,
- latest log important line,
- review findings (or explicit no-findings statement),
- blocker and next action.

## Validation Commands

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\Invoke-OrchestratorAgentAction.ps1 -Root . -Action start_agent -SlotName claude-main -DryRun
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\Invoke-OrchestratorAgentAction.ps1 -Root . -Action start_agent -SlotName claude-main
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\Get-OrchestratorStatus.ps1 -Root .
```
