# P1 RC2 Codex Narrow Fix (Budgeted)

role_owner: codex  
fallback_owner: claude  
risk_class: medium  
budget_class: restricted  
terminal_rule: done|failed|requeued|blocked

## Objective

Apply one medium-light, targeted fix discovered by RC2 smoke/contract validation. No broad refactors.

## Scope

- Exactly one bounded patch area (one module or one test path).
- Keep change minimal and auditable.
- Stop after one completed task or one failed validation cycle.

## Mandatory Approval Gate

Codex start requires a valid sticky approval record including:

- approval reference id,
- scope that matches this task class,
- non-expired TTL.

Without all three, do not dispatch; mark `blocked` or `requeued` with evidence.

## Execution Gates

1. `active=0` before claim/start.
2. No unexpected tracked diffs in selected slot worktree.
3. Patch stays within declared target path.

## Validation Commands

```powershell
git status --short
# run only the narrowest relevant tests for the touched path
```

## Evidence Required

- Approval reference and TTL confirmation.
- Exact target path fixed.
- Validation command output summary.
- One next action.

## Terminal Criteria

- `done`: one targeted fix merged into task output with passing narrow validation.
- `failed|blocked`: approval gate missing, limiter, or failing validation with blocker note.
- `requeued`: fix deferred with explicit safe handoff and unchanged scope.
