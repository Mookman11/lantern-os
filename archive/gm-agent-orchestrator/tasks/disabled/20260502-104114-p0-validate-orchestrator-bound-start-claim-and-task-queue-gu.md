ARCHIVE-RATIONALE: blocked-indefinite | archive-date: 2026-05-02 | ledger: 20260502-104114-task-closure-ledger.md

# P0 Validate orchestrator-bound start/claim and TASK_QUEUE guard

Priority: P0
Owner: codex
Created: 2026-05-02T01:15:41Z
Source: connector-action

# Objective
Validate that start/claim now binds codex-main to orchestrator project/worktree and that TASK_QUEUE.md must equal claimed active task before launch.

# Required checks
- run_safe_powershell: Get-OrchestratorStatus.ps1 with args [-Root,.]
- run_safe_powershell: Invoke-OrchestratorAgentAction.ps1 dry-run start_agent codex-main
- confirm action result includes:
  - projectBinding = C:\Users\alexp\Documents\gm-agent-orchestrator
  - claim state is sane for current queue state
- run one supervised live start_agent for codex-main only if a queue task exists
- confirm:
  - claimed task path in tasks/active matches codex-main claim
  - TASK_QUEUE.md installed in codex-main worktree equals claimed task content
- if mismatch occurs:
  - task must be returned to queue
  - status reason must include task_queue_mismatch_before_launch

# Exit criteria
- pass/fail with evidence paths and exact command outputs summarized
- no dashboard/bridge retry in this task

