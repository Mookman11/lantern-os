# P1 RC2 Headless Agent Console Launch Default

role_owner: implementation
fallback_owner: implementation
risk_class: medium
budget_class: restricted
terminal_rule: done|failed|requeued|blocked

## Objective

Prevent visible PowerShell popups during agent slot launch by default, while preserving an explicit visible opt-in.

## Scope

- Target file: `scripts/Start-GmAgentOrchestrator.ps1`
- Keep launch behavior change minimal and auditable.
- No dashboard or queue-lifecycle expansion in this task.

## Required Patch Shape

1. Add a `-Visible` switch for explicit opt-in foreground launches.
2. Default non-supervised, non-headless launch path to hidden window style.
3. Preserve existing supervised and headless behavior.

## Validation Commands

```powershell
git diff -- scripts/Start-GmAgentOrchestrator.ps1
```

## Evidence Required

- Before/after launch-path behavior statement.
- Exact diff summary for launch command.
- One next action for dispatch verification.

## Terminal Criteria

- `done`: default launcher path hides windows and visible behavior requires explicit opt-in.
- `failed|blocked|requeued`: include blocker/evidence and one safe next action.
