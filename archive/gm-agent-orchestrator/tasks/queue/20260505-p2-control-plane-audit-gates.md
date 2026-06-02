# Task: Control plane audit gates  -  queue lifecycle and dry-run gate (#259 Phase 2.1)

Priority: P2
Owner: claude
Estimated time: 2 hours
Depends on: P1 tasks complete (CI green, dispatch unblocked)
Blocks: Phase 2.2 (safe MCP repair tools), bulk task requeue

## Context

RC3 tracker #259 Phase 2.1. Queue state transitions (queue→active→terminal) are
not audited. Orphaned active tasks, double-claims, and silent failures leave the
queue in an ambiguous state that misleads the dashboard and causes bad routing.

## Scope

### Edit: `scripts/Invoke-OrchestratorTaskAction.ps1`

- Add dry-run mode (`-WhatIf`): log what would happen without moving files.
- Add orphan detection: before claiming a task, check if any task in `tasks/active/`
  has no matching running slot process. Surface orphans as a warning in the log.
- Add policy gate: refuse to move a task to `done` unless the caller provides
  `branch`, `pushed`, and `pr` evidence fields. Log the refusal with a clear message.

### New: `reports/queue-movements.jsonl`

Append-only record of every task state transition:
```jsonl
{"at":"<iso>","task":"<filename>","from":"queue","to":"active","slot":"claude-main","branch":"feature/x"}
{"at":"<iso>","task":"<filename>","from":"active","to":"done","slot":"claude-main","pr":"https://..."}
```

### New: `tests/Test-QueueAuditGates.ps1`

- Test dry-run mode returns no file changes.
- Test orphan detection fires for a task with no matching slot.
- Test policy gate blocks `done` transition with missing evidence fields.

## Done criteria

- Dry-run mode works: no files moved, log shows intent.
- Orphan detection warns when active task has no live slot.
- Done transition blocked without branch+pushed+pr fields.
- `reports/queue-movements.jsonl` written on every transition.
- New test passes; `Test-QueueClaimHardness.ps1` still passes.
- Branch pushed, PR open.

## Reference

- Issue: #259 Phase 2.1
- Queue contract: `docs/agent-contract.md` (source-control closure requirements)
- Existing movement helper: `scripts/Move-OrchestratorTask.ps1`
