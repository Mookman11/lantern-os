# Task: Agent reliability ledger  -  event tracking and routing signals (#18)

Priority: P1
Owner: claude
Estimated time: 2 hours
Depends on: CI green (PR #277 merged)
Blocks: cost-optimized routing (can't trust routing without reliability signal)

## Context

Issue #18. The orchestrator dispatches work to agents but has no durable memory
of which agent is reliable for which task class. Grudgebook entries exist in a
markdown file but are not queryable by the router. This means routing decisions
are vibes-based and the same agent gets the same class of failure repeatedly.

## Scope

### New scripts

**`scripts/Add-AgentReliabilityEvent.ps1`**
- Appends a structured event to `reports/agents/events.jsonl`
- Params: `-Agent`, `-Event`, `-Task`, `-Evidence`, `-Severity` (low/medium/high)
- Event names from AGENTS.md: `task_claimed`, `task_completed`, `task_failed`,
  `task_dropped`, `confident_false_claim`, `compact_report_good`, `token_waste`, `useful_handoff`

**`scripts/Get-AgentReliabilityReport.ps1`**
- Reads `reports/agents/events.jsonl`
- Outputs per-agent stats: completion rate, false claim count, task class breakdown
- Writes `reports/agents/reliability-latest.md` and `status/agent-reliability.json`

### Output files (new, gitignored runtime state)

- `reports/agents/events.jsonl`  -  append-only event log
- `reports/agents/reliability-latest.md`  -  human-readable summary
- `status/agent-reliability.json`  -  machine-readable, consumed by router

### Wire into existing flow

- `scripts/Start-AgentSlot.ps1`: call `Add-AgentReliabilityEvent` on task claim,
  task complete, and task failure  -  do not change slot behavior, just emit events.

### Out of scope for this task

- Do not change routing logic yet  -  that's a separate task once signal exists.
- Do not add UI  -  status JSON is enough for now.

## Done criteria

- `Add-AgentReliabilityEvent.ps1` writes a valid JSONL line; idempotent on empty file.
- `Get-AgentReliabilityReport.ps1` reads events, writes `status/agent-reliability.json`
  with schema: `{ agents: [ { name, completionRate, falseClaimCount, taskCount } ] }`.
- `Start-AgentSlot.ps1` emits `task_claimed` and `task_completed`/`task_failed` events.
- `Test-PowerShellSyntax.ps1` passes on all new/edited files.
- Branch pushed, PR open.

## Reference

- Issue: #18
- Grudgebook events: `docs/grudgebook.md`
- `status/agent-reliability.json` schema: new, documented in this PR
