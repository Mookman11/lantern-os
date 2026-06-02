ARCHIVE-RATIONALE: blocked-indefinite | archive-date: 2026-05-02 | ledger: 20260502-104114-task-closure-ledger.md

# P9 E2E codex-main dispatch smoke

## Goal
Validate that `Invoke-OrchestratorAgentAction.ps1 start_agent codex-main` can claim one queued task and hand the claimed active path into `Start-AgentSlot.ps1` without double-claiming.

handoff: yes

## Steps
1. Run one dry-run start on `codex-main` and capture claim preview.
2. Run one live start on `codex-main` with headless supervised launch.
3. Verify queue->active movement and launch audit evidence path.
4. Stop after one cycle.

