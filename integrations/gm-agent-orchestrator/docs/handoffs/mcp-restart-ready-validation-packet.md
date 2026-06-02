# MCP Restart-Ready Validation Packet

## Purpose

This packet is for the local Orchestra MCP server or MCP-connected review chat. It summarizes the current restart-ready supervisor PR state and gives a narrow, safe validation path.

Use this packet only for PR #232 / issue #231.

```text
PR: #232 feat(ops): add restart-ready service supervisor
Branch: feature/restart-ready-service-supervisor
Latest known head when packet was written: 92b5d261be4c321a907f3cf99a15bb530b8e5422
Issue: #231 Build local service supervisor and ops overview health reporting
```

## Current state

The branch implements a restart-ready local service supervisor and status reporting layer for:

```text
- dashboard / ops overview on port 8765
- MCP server on port 8787
- ngrok gateway as the external/operator-window path
```

Default startup and validation must not wake Codex, Claude, Gemini, GPT, or any agent slot.

Recent manual validation found two blockers:

```text
1. Some new tests resolved Root incorrectly to C:\ when launched from an unexpected location.
2. Start-OrchestratorServices.ps1 threw under Set-StrictMode when optional JSON property processName was missing.
```

Those fixes were pushed to the feature branch:

```text
- Start-OrchestratorServices.ps1 now uses optional JSON property handling in Test-ServiceHealth.
- Test-OrchestratorServicesSupervisor.ps1 now uses safer Root resolution.
- Test-OrchestratorServicesSupervisor.ps1 is dry-run-only and should not start services.
- Test-OrchestratorStartupTask.ps1 now uses safer Root resolution.
- Test-DashboardServiceHealthContract.ps1 now uses safer Root resolution.
```

## Files of interest

```text
config/local-services.example.json
scripts/Start-OrchestratorServices.ps1
scripts/Register-OrchestratorStartupTask.ps1
scripts/Monitor-ServerHealthPulse.ps1
scripts/Get-OrchestratorStatus.ps1
tests/Test-OrchestratorServicesSupervisor.ps1
tests/Test-OrchestratorStartupTask.ps1
tests/Test-ServerHealthPulse.ps1
tests/Test-DashboardServiceHealthContract.ps1
```

## Safety rules

Do not run these during validation unless Alex explicitly asks for an operational/manual startup phase:

```text
Cold-Start.ps1
Start-OrchMcpServer.ps1
Start-Dashboard.ps1
Restart-DashboardServer.ps1
ngrok
Register-OrchestratorStartupTask.ps1 -Apply
```

Do not stop or restart live services.
Do not move live queue, active, done, failed, or hold tasks.
Do not wake agents.
Do not store secrets, bearer tokens, environment dumps, screenshots, or full logs.
Do not broaden the PR into a service-manager rewrite.

## Safe validation command block

Run from repo root only:

```powershell
cd C:\Users\alexp\Documents\gm-agent-orchestrator
git branch --show-current
```

Expected branch:

```text
feature/restart-ready-service-supervisor
```

Then run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tests\Test-PowerShellSyntax.ps1

powershell -NoProfile -ExecutionPolicy Bypass -File .\tests\Test-OrchestratorServicesSupervisor.ps1 -Root .
powershell -NoProfile -ExecutionPolicy Bypass -File .\tests\Test-OrchestratorStartupTask.ps1 -Root .
powershell -NoProfile -ExecutionPolicy Bypass -File .\tests\Test-ServerHealthPulse.ps1 -Root .
powershell -NoProfile -ExecutionPolicy Bypass -File .\tests\Test-DashboardServiceHealthContract.ps1 -Root .
```

After tests:

```powershell
git status
```

Expected: clean working tree, or only intentionally ignored/generated local evidence files.

## What the MCP review should confirm

If the local MCP server has file/status access, confirm:

```text
- Branch is feature/restart-ready-service-supervisor.
- The working tree is clean before validation.
- Test-OrchestratorServicesSupervisor.ps1 is dry-run-only and does not start services.
- Start-OrchestratorServices.ps1 uses optional-property access for healthUrl, port, and processName.
- Register-OrchestratorStartupTask.ps1 mutates only with -Apply.
- Monitor-ServerHealthPulse.ps1 reports dashboard, mcp, and ngrok states.
- Get-OrchestratorStatus.ps1 surfaces serviceHealth.
```

## Stop conditions

Stop and report if any of these occur:

```text
- A test resolves paths under C:\scripts instead of the repo root.
- A test tries to start dashboard, MCP, ngrok, or any agent.
- Scheduled task registration asks for Apply/admin mutation.
- Any JSON parse error appears.
- Any StrictMode missing-property error appears.
- git status shows generated files that may be accidentally committed.
```

## Known limitations

This packet is for local validation and MCP-connected review. It does not prove a real reboot/login startup. Reboot validation comes later, after PR #232 passes safe local tests and is intentionally moved out of draft.

## Recommended next action

Run the safe validation block above. If it passes, append the output summary to PR #232 and decide whether the new tests should be wired into Orchestrator Health CI before marking the PR ready for review.
