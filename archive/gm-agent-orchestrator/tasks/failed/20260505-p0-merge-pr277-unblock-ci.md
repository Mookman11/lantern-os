# Task: Merge PR #277  -  unblock CI

Priority: P0
Owner: human (alex)
Estimated time: 5 min
Depends on: nothing
Blocks: all other tasks (CI is red on master until this merges)

## Context

PR #277 (`fix/mcp-tools-parse-corruption-and-init-gate`) fixes a 12-line parse
corruption in `scripts/Start-OrchMcpServer.Tools.ps1` that causes the
Orchestrator Health CI job to fail on every PR. The CI runs `Test-PowerShellSyntax.ps1`
which parses every .ps1 file  -  the corruption at line 523 makes the whole suite fail.

All current open PRs (#276, #277) are showing red CI for this reason.
No new agent work can land with a green check until this merges.

## Done criteria

- PR #277 merged to master
- CI passes on master (Orchestrator Health workflow green)
- `scripts/Start-OrchMcpServer.Tools.ps1` no longer has the duplicate tail at line 523

## Verify

```powershell
gh run list --branch master --limit 3 --json status,conclusion,name
```

Expected: `conclusion: success` for the most recent Orchestrator Health run.
