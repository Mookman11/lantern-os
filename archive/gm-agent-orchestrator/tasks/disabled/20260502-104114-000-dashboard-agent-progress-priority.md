ARCHIVE-RATIONALE: superseded | archive-date: 2026-05-02 | ledger: 20260502-104114-task-closure-ledger.md

# Held Task: Dashboard must show agent progress, limits, and blockers

This task is intentionally outside `tasks/queue` so no agent auto-claims it before Alex can see clear dashboard notifications.

## Goal

Move the information Alex keeps asking for in PowerShell into the dashboard. The dashboard must show agent progress, queue state, stale active tasks, rate/token limits, latest logs, and next action without requiring manual PowerShell commands.

## Must show in dashboard

1. Agent slot status: Codex/Claude active, idle, sleeping, blocked, stale, or manually locked.
2. Current task title, issue number, repo, branch/worktree, start time, and elapsed time.
3. Latest meaningful event: claimed task, hit limit, failed auth, missing MCP/server, validation failed, committed work, moved task.
4. Clear stop reason: token limit, auth failure, missing tool, stale task, dirty worktree, validation failure.
5. Notifications/rewards: obvious cards for success/failure/blocker events.
6. Next action block:

```text
Next action: <one concrete action>
Owner: <Alex / Claude / Codex / ChatGPT / orchestrator>
When: <now / after reset / after current task finishes>
Blocked by: <none or one blocker>
```

## Safety

Do not move this file back to `tasks/queue` until dashboard visibility is good enough for Alex to monitor agents without PowerShell log spelunking.

