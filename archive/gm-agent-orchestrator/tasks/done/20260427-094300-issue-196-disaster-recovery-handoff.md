# P0: Issue #196 disaster recovery - post grudge comment + remediation feature branch

Priority: P0
Owner: gpt
Created: 2026-04-27T13:43:00Z
Source: claude-cowork-handoff

Tracks: https://github.com/alex-place/gm-agent-orchestrator/issues/196

## Why this is a handoff

Claude (cowork session) drafted and verified the work but is token-constrained.
Codex is blocked on a Codex usage cap until 2026-04-30T08:56 (NOT auth failure - verify before retrying that slot).
GPT desktop client has MCP connector access and should pick this up.

## Step 1 - Post the grudge / contract-update comment to #196

Body file (already drafted, do not rewrite):
`C:\Users\alexp\AppData\Roaming\Claude\local-agent-mode-sessions\509a08ae-670c-4e20-b84f-f42c3fcbe567\21e585c3-b2b0-4272-bb81-85856c554538\local_31022a38-20c2-4a10-a662-7d833d0eda66\outputs\issue-196-grudge-comment.md`

Posting path (any of these is acceptable - pick the one your tool surface supports):
1. New `create_github_issue_comment` MCP tool if Alex's desktop_config update exposed it.
2. Local `gh issue comment 196 --repo alex-place/gm-agent-orchestrator --body-file <path-above>`.
3. Add `scripts/New-GitHubIssueComment.ps1` mirroring `Update-GitHubIssueComment.ps1` (gh-backed, dry-run guard, repo-allowlist), then post via that - but only if a create surface does not already exist; check first per AGENTS.md anti-redundancy rule.

After posting, capture the comment URL and append it to AGENT_LOG.md.

## Step 2 - Open feature branch for remediation

Branch: `feature/196-disaster-recovery-preflight` off fresh `master`.

Commits (small, focused, per agent-contract Commit Discipline):

1. `docs:` add note to docs/agent-contract.md or docs/mcp-connector-health.md describing the canonical-master rule (rule 1 of the comment).
2. `feat:` preflight guard that blocks disaster-recovery routing from non-`master` worktrees unless `--AllowNonMaster` is passed. Likely lives next to `Invoke-OrchestratorAgentAction.ps1` or in `Start-AgentSlot.ps1`.
3. `feat:` surface branch identity in dashboard/orchestrator status output (agent_status payload + dashboard panel). Probably in `scripts/Get-OrchestratorStatus.ps1` plus dashboard render.
4. `feat:` warn when `codex-main` is dirty and not on `master`. Status payload field + dashboard banner.
5. `feat:` separate Codex auth-fail vs Codex usage-cap signals. Currently both get bucketed as `auth_failed`. Add a `quota_capped` blocker kind with `nextWakeAt` derived from the Codex usage-limit error message. Reference issue #70 (Classify GPT quota failures and preserve runner API errors) for the existing pattern.
6. `feat:` slot reservation for claude-main - emergency-only routing.
   - Add `acceptOnly` (string array) and `reservedReason` (string) fields to slot schema in `config/agents.json`. Set `claude-main.acceptOnly = ["P0","emergency"]` and `claude-main.reservedReason = "Reserved for highest-priority orchestration requests per Alex 2026-04-27"`.
   - Teach the task router / queue strategy to honor `acceptOnly`: a task is only routable to a slot if its priority/tags intersect the slot's `acceptOnly` (or `acceptOnly` is unset/empty).
   - Surface the reservation in `get_agent_status` (per-slot `acceptOnly` + `reservedReason`) and in the dashboard agent panel so it's obvious why claude-main is sitting idle when work is queued.
   - Default routing must skip claude-main for non-P0 work even when claude-main is the only available slot - fall through to `human_review` instead, so claude-main truly stays in reserve.
   - Document the reservation in `docs/agents/local-routing-policy.md` and in `AGENT_RESPONSIBILITIES.md`.
7. `test:` syntax/parse + a targeted PowerShell unit or fixture confirming (a) the preflight guard rejects non-master worktrees, (b) the new `quota_capped` blocker kind round-trips through the status JSON, (c) a P1 task is NOT routed to claude-main and a P0 task IS, (d) status JSON exposes claude-main's `acceptOnly`/`reservedReason`.

Push, open PR, link #196 and #109 (queue movement reliability) and #70 (quota classification).

## Acceptance criteria

- Comment posted on #196 with body matching `outputs/issue-196-grudge-comment.md` exactly.
- PR open against master with the seven-ish commits above (combined sensibly), referencing #196.
- `get_agent_status` output for `codex-main` shows the new `quota_capped` blocker with `nextWakeAt = 2026-04-30T08:56` until the cap actually clears.
- `get_agent_status` output now includes `branch` field per slot.
- Dirty + non-master worktrees on any agent slot raise a visible warning in the dashboard.
- `get_agent_status` output for `claude-main` includes `acceptOnly: ["P0","emergency"]` and a non-empty `reservedReason`.
- Routing dry-run: a P1 task does NOT pick claude-main even when no other slot is available; a P0 task DOES.
- AGENT_LOG.md updated per the contract Done-format. If push or PR fails, switch to Blocked-format instead.

## Hard guards (do not skip)

- Do NOT `sync_repository` while `claude-main` or `codex-main` worktrees are dirty without inspecting changed files first. Their pending edits include `tools/gamemaker-room-editor`, `AGENT_LOG.md`, `AGENT_RESUME.md`, `TASK_QUEUE.md`.
- Do NOT post any additional comments to #196 beyond the one drafted.
- Do NOT touch master directly; feature branch only.
- Do NOT attempt to recover Codex via re-login - it's a usage cap, not an auth failure. Re-login attempts are wasted runs and a grudge.
- If anything in the comment body needs to change, stop and surface back to Alex.

## Read-first

1. AGENTS.md
2. docs/agent-contract.md
3. This file
4. outputs/issue-196-grudge-comment.md (the comment body)
5. Open issues #196, #194, #193, #112, #109, #70 (only the ones directly referenced above)
