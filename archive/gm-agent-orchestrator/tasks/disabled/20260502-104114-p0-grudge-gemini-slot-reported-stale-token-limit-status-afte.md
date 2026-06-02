ARCHIVE-RATIONALE: blocked-indefinite | archive-date: 2026-05-02 | ledger: 20260502-104114-task-closure-ledger.md

# P0 GRUDGE: Gemini slot reported stale token-limit status after fresh dispatch

Priority: P0
Owner: operator-intake
Created: 2026-05-01T21:34:48Z
Source: connector-action

Blocked by: Needs one-task/one-PR contract before implementation.

## Problem
After operator requested `gemini-main` for `P0: Validate ChatGPT bridge tool visibility`, the orchestrator successfully claimed the task and moved it to active, but the status layer immediately reported `gemini-main` as sleeping/token-limited using stale evidence.

## Evidence observed
- Start dry-run selected `tasks/queue/p0-validate-chatgpt-bridge-tool-visibility.md` for `gemini-main` with reasons `capability:validation` and `priority:urgent`.
- Live start succeeded and moved the task to `tasks/active/gemini-main__p0-validate-chatgpt-bridge-tool-visibility.md`.
- Start audit: `logs/control-actions/20260501-173119-start_agent-gemini-main.json`.
- Queue movement audit: `reports/queue-movements/20260501.jsonl`.
- Current status reports `gemini-main` as `sleeping` with blocker `token_limit`.
- `get_latest_agent_logs` still shows latest `gemini-main` log as `logs/gemini-main/20260428-173335-gemini-main__p0-expose-openapi-schema-for-chatgpt-connector.md.log`, last written `2026-04-29T01:01:06`, not a fresh log from the May 1 dispatch.

## Why this matters
The dashboard/status layer may be presenting a stale quota/sleeping state as if it were the result of the current dispatch. That misleads routing decisions and makes operators think Gemini is down or quota-limited when the actual runner/log freshness is unproven.

## Required fix
Add a freshness guard to agent status/log classification:
- If a task was claimed after the latest slot log timestamp, do not classify the current task from the old log.
- Surface `claimed_but_no_fresh_log` or `runner_start_unconfirmed` instead of `token_limit`.
- Include process ID, claim timestamp, active task path, newest log timestamp, and whether the log belongs to the active task.
- Require status to distinguish live blocker evidence from stale historical blocker evidence.

## Validation
- Start a Gemini slot on a test validation task.
- Confirm status shows a fresh run log or an explicit no-fresh-log state.
- Confirm stale April 29 quota logs cannot mark a May 1 active task as token-limited.

## Contract note
This is a grudge/remediation task. It should get a one-task/one-PR contract before implementation begins.

