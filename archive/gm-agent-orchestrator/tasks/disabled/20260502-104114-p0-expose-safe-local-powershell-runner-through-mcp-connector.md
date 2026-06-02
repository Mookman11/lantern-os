ARCHIVE-RATIONALE: superseded | archive-date: 2026-05-02 | ledger: 20260502-104114-task-closure-ledger.md

# P0: Expose safe local PowerShell runner through MCP connector

Priority: P0
Owner: claude
Created: 2026-04-29T00:00:00Z
Source: connector-action

## Problem

MCP capability status may report local execution as available in some environments, but the ChatGPT connector wrapper does not yet expose a callable, bounded safe PowerShell command tool.

Do not treat a concrete local shell path, command availability, PATH state, or running process state as proven from this task file. Those values must be discovered from the local MCP/server capability response or direct local validation at runtime.

This gap prevents the dispatcher from using existing local helper scripts such as:

- scripts\New-OrchestratorQueueTask.ps1
- scripts\Get-OrchestratorStatus.ps1
- scripts\Invoke-OrchestratorTaskAction.ps1
- scripts\Invoke-OrchestratorRepoSync.ps1

## Prior work considered

- #199 / `scripts\Invoke-OrchestratorPowerShellPatch.ps1`: provides a staged patch/validate/promote/rollback flow, but it is focused on controlled file replacement rather than general allowlisted helper execution.
- #215: defines the broader MCP repair-surface gap, but it does not by itself expose a concrete safe runner tool.
- Existing status/task/repo helper scripts: already provide bounded operations, but the connector has no single audited MCP runner surface for invoking them safely.

These were insufficient because the recovery loop needs a small, auditable MCP-facing runner that can call existing approved helpers without becoming an arbitrary shell.

## Goal

Expose a constrained, auditable PowerShell runner through the MCP connector.

## Requirements

1. Add a connector tool for safe local PowerShell execution.
2. The tool must be allowlist-based, not arbitrary shell by default.
3. Allowed commands/scripts should initially include only orchestrator helper scripts:
   - Get-OrchestratorStatus.ps1
   - New-OrchestratorQueueTask.ps1
   - Invoke-OrchestratorTaskAction.ps1
   - Invoke-OrchestratorAgentAction.ps1
   - Invoke-OrchestratorRepoSync.ps1
   - build/status read-only helpers
4. Every invocation must write an audit JSON record under logs\control-actions.
5. The tool must support dry-run / plan-only where possible.
6. The tool must refuse dangerous commands by default:
   - destructive filesystem operations
   - arbitrary git reset/clean
   - credential/environment dumping
   - process killing outside known orchestrator scripts
   - direct branch mutation unless routed through approved helper
7. The response must return:
   - command
   - args
   - exit code
   - stdout tail
   - stderr tail
   - audit path
   - whether the command mutated state
8. Documentation must explain that this is an operational surface, not the website dashboard.

## Acceptance criteria

- ChatGPT connector exposes a callable safe PowerShell tool.
- Dispatcher can create queue tasks without manual copy/paste.
- Dispatcher can run status/sync/task-action helpers through MCP.
- Unsafe commands are rejected with a clear reason.
- CI/regression tests cover allowed and blocked commands.
- MCP capability status reports the exact exposed shell runner name.
- Local shell command/path state is validated at runtime rather than asserted in this task.

## Related issues

- #199: chat-safe PowerShell command update surface
- #188: dashboard-forwardable local shells and remediation tools
- #215: safe MCP repair tools for local orchestrator recovery
- #112: restore MCP connector online/write action path

