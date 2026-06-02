# P1 RC2 Dashboard Next-Action Alignment

role_owner: gpt  
fallback_owner: claude  
risk_class: medium  
budget_class: light  
terminal_rule: done|failed|requeued|blocked

## Objective

Align dashboard next-action output with real queue, slot, and blocker state while preserving `/dashboard` as the only user-facing route.

## Scope

- Verify next-action text against real status sources.
- Ensure stale/fresh labeling is explicit.
- Ensure blocker source is visible and actionable.
- Keep panel-first single-route model; no tabs/routes added.

## Execution Gates

1. `/dashboard` remains canonical route.
2. No new user-facing dashboard routes are introduced.
3. Status fallback behavior remains operator-safe when backend is degraded.

## Validation Commands

```powershell
git status --short
powershell -NoProfile -ExecutionPolicy Bypass -File .\tests\Test-DashboardServiceHealthContract.ps1 -Root .
powershell -NoProfile -ExecutionPolicy Bypass -File .\tests\Test-QueueRecommendation.ps1 -Root .
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\Get-OrchestratorStatus.ps1 -Root .
```

## Evidence Required

- Before/after next-action examples.
- Fresh vs stale status example outputs.
- Route confirmation evidence for `/dashboard`.
- One next action.

## Terminal Criteria

- `done`: next-action and freshness behavior align with status truth.
- `failed|blocked`: mismatch remains with blocker evidence.
- `requeued`: partial alignment complete with explicit remaining gap.
