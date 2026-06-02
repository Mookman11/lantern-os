ARCHIVE-RATIONALE: superseded | archive-date: 2026-05-02 | ledger: 20260502-104114-task-closure-ledger.md

# P0: Chat-safe PowerShell command update surface

## Goal
Allow the MCP-connected chat to safely stage, validate, and promote missing PowerShell helper commands without ad hoc paste packets, while preserving live MCP uptime.

## Required tools
- propose_powershell_patch
- validate_powershell_patch
- promote_powershell_patch
- start_candidate_mcp
- validate_candidate_mcp
- promote_candidate_mcp
- rollback_last_mcp_promotion

## Safety contract
- No queue moves during patch proposal or validation.
- No issue closes.
- No agent wakeups.
- No live 8787 restart during proposal or validation.
- Stage first; never write live files directly.
- Parser gate every changed PowerShell file.
- Candidate MCP must start on a separate port before promotion.
- Existing tools must pass smoke tests on candidate.
- New/changed tool must pass dry-run on candidate.
- Live promotion must emit rollback command and audit JSON.

## Acceptance criteria
- A patch can be proposed from chat and written only to a staging area.
- A staged patch can be validated without touching live service.
- A staged patch can be promoted atomically with backup.
- Candidate MCP validation proves current and new tools before 8787 restart.
- Rollback path is recorded and tested in dry-run.
- Manual verification note confirms no focus stealing and no foreground UI flicker.

## Related
- Issue #169: Fix screen flicker from local health checks pulling focus.
- Disaster recovery lock-down: autopilot cycles do not count as stability unless useful task movement occurs.

