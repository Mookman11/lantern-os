# P0 RC2 Lifecycle Enforcement Smoke

role_owner: gpt  
fallback_owner: codex  
risk_class: high  
budget_class: medium  
terminal_rule: done|failed|requeued|blocked

## Objective

Prove one controlled queue lifecycle transition (`queue -> active -> terminal`) without stale active state.

## Scope

- Run exactly one bounded smoke attempt.
- Validate claim/start behavior and terminalization behavior.
- Capture movement evidence and latest slot/log alignment.
- If patch needed, route to Codex/Claude as separate follow-up, not in this same unit.

## Execution Gates

1. `active=0` before start.
2. Selected slot worktree has no unexpected tracked diffs.
3. Task claim must be explicit and auditable.
4. If limiter/policy block occurs, stop after one failed cycle and terminalize.

## Validation Commands

```powershell
git status --short
powershell -NoProfile -ExecutionPolicy Bypass -File .\tests\Test-QueueClaimHardness.ps1 -Root .
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\Get-OrchestratorStatus.ps1 -Root .
```

Optional supervised dry-run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\Invoke-OrchestratorAgentAction.ps1 -Root . -Action start_agent -SlotName codex-main -DryRun
```

## Evidence Required

- Counts before and after (`queue/active/done/failed`).
- Task movement path observed.
- Latest relevant slot log line.
- Confirmation that no stale active remains.
- One next action.

## Terminal Criteria

- `done`: smoke passes with explicit lifecycle evidence and no stale active.
- `failed|blocked`: lifecycle contract broken with first blocker recorded.
- `requeued`: no safe attempt possible but queue state preserved with reason.
