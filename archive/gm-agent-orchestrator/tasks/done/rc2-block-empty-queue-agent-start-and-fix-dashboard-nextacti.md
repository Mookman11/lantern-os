# RC2: Block empty-queue agent start and fix dashboard nextAction

Priority: P0
Owner: operator-intake
Created: 2026-04-30T22:06:10Z
Source: connector-action

Blocked by: Do not dispatch automatically. First review dirty worktrees and choose an implementation slot manually. Codex may be preferred after quota recovery; avoid DeepSeek while disabled/auth-broken and avoid Gemini while quota-limited.

# RC2: Block empty-queue agent start and fix dashboard nextAction

## Goal
Prevent the orchestrator from recommending or previewing agent start when there is no queued work.

## Evidence
Published evidence ledger:

- Issue: `alex-place/gm-agent-orchestrator#238`
- Comment ID: `4356452331`
- PR: `alex-place/gm-agent-orchestrator#251`
- PR branch: `fix/exact-task-selection-agent-start`

Live state before handoff:

- Queue: 0
- Active: 0
- Done: 10
- Failed: 3

Current unsafe behavior:

- status/dashboard nextAction says: `Start an available slot on queued work.`
- `start_agent -DryRun` returned `ok: true` even when `queue=0`

This is unsafe because the system recommends dispatch when no claimable queued task exists.

## Required behavior
When `queue=0`:

- dashboard/status must not recommend `start_agent`
- `start_agent -DryRun` must return blocked/unsafe
- live `start_agent` must refuse to run
- next action should recommend stale task / stale PR / cleanup classification

Suggested blocker:

- `blockedBy: empty_queue`

## Intended agent and handoff contract
- Intended execution slot: `claude-main` (implementation lane).
- Fallback slot: `codex-main` only if `claude-main` is auth-blocked.
- This task is a PR-bound handoff. Update only files that satisfy PR #251 scope.
- Do not start dashboard redesign, service restarts, or cross-repo edits.
- If blocked, record exact blocker in `status/<slot>.json` and keep queue/active terminal-safe.

## Auditable work units (must be traceable in PR #251)
1. Add/verify empty-queue guard in `start_agent` path so dry-run and live both block when `queue=0`.
2. Ensure nextAction for empty queue does not recommend agent start.
3. Preserve existing dirty-worktree refusal behavior.
4. Add/adjust targeted validation for empty-queue dry-run/live guard behavior.
5. Attach evidence in PR #251 comment with:
   - commands run,
   - before/after behavior,
   - queue/active counts,
   - files changed.

## Acceptance criteria
- Empty queue produces `blockedBy: empty_queue` or equivalent.
- `start_agent -DryRun` returns blocked when no queued task exists.
- Live `start_agent` refuses when no queued task exists.
- Dashboard/status nextAction no longer says to start an agent when queue is empty.
- Next action recommends stale task / stale PR / cleanup classification.
- Existing dirty-worktree sync refusal remains unchanged.
- No broad dashboard redesign in this task.
- No task movement other than this handoff task creation.
- No repo sync.
- No service restart.
- No GitHub mutation except updating the #238 evidence ledger if validation results need to be appended.

## Validation plan
1. Run queue/status read-only checks with queue empty.
2. Run `start_agent` dry-run against an available slot and verify it is blocked with empty queue.
3. Verify dashboard/status nextAction changes away from agent start when queue is empty.
4. Run existing targeted tests for queue/agent action helpers if available.
5. Do not start any agent as part of validation.

## Done criteria for this handoff
- PR #251 contains the implementation and validation evidence for all acceptance criteria above.
- Handoff comment in PR #251 includes exact blocker text and nextAction value for `queue=0`.
- Queue lifecycle remains terminal-safe (`active=0` after validation runs).
