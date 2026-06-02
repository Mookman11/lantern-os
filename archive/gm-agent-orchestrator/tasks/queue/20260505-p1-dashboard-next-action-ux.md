# Task: Dashboard next-action UX  -  Action Center and watcher status (#24)

Priority: P1
Owner: claude
Estimated time: 1.5 hours
Depends on: CI green (PR #277 merged)
Blocks: nothing (operator visibility improvement)

## Context

Issue #24. Alex should not need to ask an agent "what do I do next?"  -  the
dashboard should surface the answer directly. Currently the dashboard shows
agent state but no clear recommended next action, and watcher online/offline
status is invisible.

## Scope

Work only in `dashboard/index-v3.html` (source of truth per grudgebook).
Do NOT edit `dashboard/index.html`  -  that is managed by the update script.

### Required additions

**Action Center panel** (below notifications bar, above agent grid):

```
┌────────────────────────────────────────────┐
│ ⚡ Next action                              │
│ Wake Claude for task: <task title>          │
│ Owner: Alex   When: now                     │
│ [Copy command]   Blocked by: none           │
└────────────────────────────────────────────┘
```

- Read from `status/orchestrator.json` field `nextAction` (already present in status output).
- Show "System healthy  -  no action needed" when queue is empty and all slots are idle.
- If action requires a shell command, show a one-click copy block (not a menu of options).

**Watcher status indicator** (in Queue sidebar):

- Check for `status/orchestrator.json` `lastUpdated` timestamp.
- If age > 5 minutes: show amber "Watcher stale" indicator.
- If age > 15 minutes: show red "Watcher offline" indicator.
- If fresh: show green "Live" dot.

## Out of scope

- Do not add new backend scripts.
- Do not change `status/orchestrator.json` shape  -  read what's already there.
- Do not implement button-executed commands (copy-to-clipboard only for MVP).

## Done criteria

- Action Center is visible in `dashboard/index-v3.html` and reads from real `nextAction` field.
- Watcher status indicator reflects real `lastUpdated` age.
- Dashboard renders without JS errors on file:// protocol.
- `Test-PowerShellSyntax.ps1` still passes (no PS changes needed).
- Branch pushed, PR open.

## Verify

Open `dashboard/index-v3.html` in browser with `status/orchestrator.json` present.
Confirm Action Center shows current `nextAction` value. Confirm watcher dot changes
color based on `lastUpdated` age (mock the timestamp to test stale case).

## Reference

- Issue: #24
- Dashboard source of truth: `dashboard/index-v3.html`
- `status/orchestrator.json` shape: run `scripts/Get-OrchestratorStatus.ps1 -Root .`
