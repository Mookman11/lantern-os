ARCHIVE-RATIONALE: superseded | archive-date: 2026-05-02 | ledger: 20260502-104114-task-closure-ledger.md

# P0: Make GitHub issues a managed local MCP surface

Priority: P0
Owner: claude
Created: 2026-04-27T10:06:39Z
Source: connector-action

Blocked by: https://github.com/alex-place/gm-agent-orchestrator/issues/112

## Objective
MCP must see GitHub issues, expose them to the dashboard, and create audited local tasks from selected issues. Source: #112.

## Requirements
1. Read AGENTS.md and docs/agent-contract.md before editing.
2. Keep the change scoped to this task.
3. Preserve existing public script parameters unless a breaking change is explicitly required.
4. Run the cheapest relevant validation first.

## Acceptance Criteria
- The intended change is implemented or the blocker is documented clearly.
- Validation command output is recorded in AGENT_LOG.md or the task handoff.
- Work is committed on a feature branch and opened as a pull request before being marked done.

## Notes
Created through the queue task creation helper.

