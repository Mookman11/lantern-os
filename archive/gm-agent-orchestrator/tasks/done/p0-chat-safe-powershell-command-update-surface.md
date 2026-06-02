# P0: Implement chat-safe PowerShell command update surface

Related issues:

- #196 disaster recovery
- #197 MCP self-update/comment mutation rollout
- #198 facilitator research lane
- #199 chat-safe PowerShell command update surface

## Context

During disaster recovery, the head chat repeatedly reached a blocker where it could identify required PowerShell/script changes but could not safely stage, validate, promote, or roll back those changes through MCP. This caused paste-packet escalation and status loops.

## Goal

Expose a safe MCP-managed PowerShell patch/update workflow so the head chat can propose, validate, candidate-test, promote, and roll back script changes without touching live `8787` until proof passes.

## Files to create/modify

- `scripts/Invoke-OrchestratorPowerShellPatch.ps1`
- `scripts/Test-OrchestratorPowerShellPatch.ps1`
- `scripts/Start-OrchMcpServer.ps1`

## Tools to expose

- `propose_powershell_patch`
- `validate_powershell_patch`
- `promote_powershell_patch`
- `start_candidate_mcp`
- `validate_candidate_mcp`
- `promote_candidate_mcp`
- `rollback_last_mcp_promotion`

## Required safety

- Stage-only proposal.
- Parser gate before promotion.
- Backup before write.
- Candidate MCP on separate port before live `8787` restart.
- Dry-run proof of new tools.
- Audit JSON for every action.
- No agent wakeups.
- No queue moves.
- No issue closes.

## Acceptance criteria

1. `propose_powershell_patch` writes only to a staging directory and returns `patch_id`.
2. `validate_powershell_patch` parser-checks staged PowerShell files and reports structured JSON.
3. `promote_powershell_patch` backs up target files before atomic write.
4. `start_candidate_mcp` starts candidate on non-live port, default `8788`.
5. `validate_candidate_mcp` proves health, existing tools, and new patch tools.
6. `promote_candidate_mcp` only touches live `8787` after candidate proof.
7. `rollback_last_mcp_promotion` restores the last backup or emits a clear stop condition.
8. All actions emit audit JSON under `logs/control-actions`.
9. No tool performs agent wakeups, queue moves, or GitHub issue closure.

## Stop conditions

Stop and report if:

- staged PowerShell parser gate fails,
- target file backup cannot be created,
- candidate MCP health fails,
- candidate tool list does not expose the new patch tools,
- live `8787` health fails before promotion,
- rollback backup is missing or ambiguous.

## Initial implementation split

Commit 1: add stage/validate/promote PowerShell patch scripts.
Commit 2: expose read-only and dry-run MCP patch tools.
Commit 3: add candidate MCP start/validate/promote/rollback tooling.
Commit 4: add audit JSON and runbook docs.

## UX follow-up: shell result feedback buttons

After assistant-provided shell commands, the chat UI should expose two immediate result buttons under the command message:

- Green: "That worked"
- Red: "That didn't work"

Purpose:
- Let Alex report shell outcome without typing.
- Reduce recovery latency.
- Convert command-result feedback into structured MCP/task context.
- Avoid repeated status loops after failed paste packets.

Acceptance:
- Button clicks are recorded as structured feedback on the current task/action.
- "That worked" advances to the next planned validation step.
- "That didn't work" asks for or captures the failed output and marks the command step as failed.
- Feedback must not wake agents, move queue, close issues, or restart MCP by itself.
