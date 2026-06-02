# P1 RC2 Claude Fallback Final Pass

role_owner: claude  
fallback_owner: human  
risk_class: medium  
budget_class: light  
terminal_rule: done|failed|requeued|blocked

## Objective

Provide fallback conformance review and minimal corrective recommendation when Codex is not preferred/available, or when final RC2 contract pass is needed.

## Scope

- Validate contract conformance for ingress/routing/lifecycle outputs.
- Provide minimal corrective patch recommendation; no broad redesign.
- Run only after wake-safe preflight passes.

## Wake-Safe Preflight Gate

Dispatch allowed only if all are true:

1. slot is available (not sleeping/locked/blocked),
2. worktree has no unexpected tracked diffs,
3. `active=0` before start,
4. no conflicting higher-priority active dispatch.

If any gate fails, do not start Claude; set `requeued` or `blocked` with evidence.

## Validation Commands

```powershell
git status --short
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\Get-OrchestratorStatus.ps1 -Root .
# add targeted validation command for any touched contract/test file
```

## Evidence Required

- Preflight pass/fail details.
- Conformance checklist result (pass/fail per contract area).
- Minimal corrective recommendation or patch summary.
- One next action.

## Terminal Criteria

- `done`: conformance review complete with evidence and actionable output.
- `failed|blocked`: preflight or validation blocker with explicit reason.
- `requeued`: fallback not safe now; clear trigger to retry later.
