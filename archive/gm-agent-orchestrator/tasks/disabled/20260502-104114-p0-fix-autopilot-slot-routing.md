ARCHIVE-RATIONALE: superseded | archive-date: 2026-05-02 | ledger: 20260502-104114-task-closure-ledger.md

# P0: Fix autopilot slot routing — include gemini-main and all new slots

## Context
Autopilot cycles every 5 min but only tries gemini-lite and headless.
gemini-main, deepseek-main, gemini-flash, headless-2 are never tried.
This means the queue never drains automatically.

## Task
1. Read scripts\Start-GmOrchestratorAutopilot.ps1
2. Find where slot filter is applied (likely a hardcoded list or role filter)
3. Update to include all enabled slots from agents.json dynamically
4. Test: trigger one autopilot cycle and confirm gemini-main gets tried
5. Commit, update AGENT_LOG.md, complete task.

## Acceptance
- autopilot.log shows gemini-main being tried in next cycle
- No previously working slots broken

