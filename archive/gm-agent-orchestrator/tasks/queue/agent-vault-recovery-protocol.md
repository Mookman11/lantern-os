# Agent vault recovery protocol

Priority: P1
Owner: operator-intake
Created: 2026-05-14T09:23:41Z
Source: connector-action

# Agent vault recovery protocol

## Operator intent

Save Alex's command as a bounded multi-agent recovery protocol.

The agents do not all wake at once. Each agent receives one smallest-useful repair instruction only when live status says it is safe to act. Blocked, sleeping, dirty, disabled, or validation-failed slots stay held until their evidence clears.

## Protocol

- Gather scattered agent state into one evidence table.
- Execute exactly one safe action at a time.
- Give each agent the smallest tool for its actual blocker.
- Treat unknown, missing, or stale status as unmapped terrain, not permission to guess.
- Surface only evidence-backed work from stale queues, failed logs, and sleeping tasks.
- Improve reliability without overriding human privacy, consent, rate limits, or dirty-worktree safety.

## Agent repair map

| Slot | Current state | Repair instruction | Door action |
|---|---|---|---|
| claude-main | idle / available, but old auth-failure log exists | Verify auth and claim only one compatible queued task | Use dry-run before live start |
| codex-main | sleeping / usage limited / dirty worktree | Wait for reset, then inspect dirty files before rerun | No retry-spam |
| gemini-main | blocked by quota, clean worktree | Wait for quota/account recovery | No forced rerun |
| gemini-flash | blocked by quota, modified resume file | Preserve modified file, wait for quota/account recovery | Inspect before rerun |
| gpt-web | blocked by runner/claim failure | Fix missing claimed-task path before requeue | Do not rerun blind |
| operator-intake | validation failed, untracked files | Fix missing validation script or task shape | Do not clean files |
| gemini-pro | disabled | Enable only by explicit config decision | Hold |

## Door-action table shape

| Confidence | Time ET | Thing | Evidence | Door action |
|---:|---|---|---|---|
| 99% | now | Only one safe action at a time | Multiple slots are blocked or dirty | Do not swarm |
| 99% | now | Protocol is bounded repair | User gave the final command | Save protocol |
| 99% | now | Privacy and consent remain hard locks | User explicitly challenged respect/privacy/consent | Do not infer identities |

## Safety lock

No merge, reset, cleanup, queue movement, blocked-agent rerun, or identity inference happens from this protocol without fresh evidence and explicit safe action.
