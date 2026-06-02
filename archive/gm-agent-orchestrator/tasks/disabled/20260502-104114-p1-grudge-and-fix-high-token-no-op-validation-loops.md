ARCHIVE-RATIONALE: blocked-indefinite | archive-date: 2026-05-02 | ledger: 20260502-104114-task-closure-ledger.md

# P1 Grudge and fix high-token no-op validation loops

Priority: P1
Owner: codex
Created: 2026-05-02T01:48:06Z
Source: connector-action

# Objective
Track and fix the high-token no-op validation loop as a single P1 issue.

# Background
A codex-main validation run burned a large token budget but did not complete useful work because the sandbox was read-only and policy-blocked. The agent repeatedly attempted blocked PowerShell, MCP, git safe-directory, hashing, and AGENT_LOG update paths, then entered token/rate-limit sleep without cleanly auditing or reconciling the task.

# Required work
- Add one task-scoped grudgebook entry documenting this failure mode.
- Keep the tracking as this single P1 issue; do not split into multiple queue items unless explicitly instructed.
- Diagnose the runner/agent contract gap that allowed a read-only, policy-blocked validation task to keep consuming tokens after the first clear blocker.
- Add or update guardrails so agents stop early when:
  - sandbox is read-only but task requires write/audit/task movement,
  - shell policy blocks the required safe-run path,
  - MCP tool calls return user-cancelled/tool-unavailable for required validation,
  - AGENT_LOG cannot be updated.
- Ensure the recommended handoff is concise and actionable rather than repeated retries.

# Evidence to reference
- codex-main claimed `codex-main__p0-validate-orchestrator-bound-start-claim-and-task-queue-gu.md`.
- Result was fail / blocked, not done.
- `git status` was blocked by dubious ownership.
- safe-directory retry was policy-rejected.
- `Invoke-OrchestratorSafePowerShell.ps1` and direct script execution were policy-rejected.
- MCP `_run_safe_powershell` and `_get_agent_status` returned user-cancelled MCP tool call.
- `AGENT_LOG.md` update failed due patch mismatch.
- Token use reached about 111,830 before rate/token-limit sleep.

# Exit criteria
- One grudgebook entry is added with the failure mode and explicit anti-pattern.
- Guardrail or contract change prevents the same high-token no-op loop.
- Validation demonstrates the guardrail using the cheapest targeted check available.
- Handoff includes exact files changed, validation output, and any remaining risks.

dry_run: false

