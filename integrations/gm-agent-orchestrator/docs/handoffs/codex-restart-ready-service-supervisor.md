# Codex Handoff: Restart-Ready Service Supervisor

Issue: #231

## Goal

Build a first stable local restart path for the orchestra after a Windows PC reboot/login.

Acceptance target:

- dashboard / ops overview comes up or clearly reports why it is down
- MCP comes up or clearly reports why it is down
- ngrok gateway comes up or is clearly marked operator-window-required / down
- no agents wake by default
- status evidence is compact and machine-readable
- implementation is testable without starting live services, requiring admin rights, requiring real ngrok, or requiring external network

## Current operational truth

- `Cold-Start.ps1` is an operational boot script, not a harmless read-only validation command.
- Current observed gateway path is ngrok, not Cloudflare.
- Cloudflare is legacy / verify-before-use only.
- Dashboard default is `8765`.
- **MCP true/default local health and server port is `8787`.**
- Any old `8788` MCP health checks are stale unless a local override explicitly says otherwise.
- ngrok should be modeled as the external gateway/operator window that exposes the configured local MCP endpoint; do not treat `8788` as the default MCP port.
- Default startup must not wake Codex, Claude, or other agents.

## Priority order

1. Restart readiness after local PC reboot/login.
2. Service health visibility for dashboard, MCP, and ngrok-gateway.
3. Idempotent safe startup: start missing/unhealthy services only; do not kill healthy existing processes by default.
4. Token-conserving status: compact JSON and direct probes, not broad logs/transcripts.
5. Best-effort console-noise reduction; do not block the first stable PR on perfect console behavior.

## Expected implementation shape

### Commit 1: service registry and supervisor

Add:

- `config/local-services.example.json`
- `scripts/Start-OrchestratorServices.ps1`
- `tests/Test-OrchestratorServicesSupervisor.ps1`

Supervisor requirements:

- Reads `config/local-services.json` if present, else `config/local-services.example.json`.
- Supports `-DryRun` and `-Once`.
- Preflights health/process state before starting anything.
- Starts only enabled missing/unhealthy services when not dry-run.
- Does not stop/kill existing healthy services by default.
- Writes `status/services.json`.
- Does not print or persist live tokens or environment dumps.

### Commit 2: startup task registration

Add:

- `scripts/Register-OrchestratorStartupTask.ps1`
- `tests/Test-OrchestratorStartupTask.ps1`

Startup requirements:

- Uses Windows Task Scheduler.
- Defaults to dry-run/plan mode unless `-Apply` is passed.
- Registers a user-logon task with 60-120 second delay.
- Multiple instances should ignore new runs.
- Task should call `Start-OrchestratorServices.ps1 -Once` from repo root.
- Supports `-Status` and `-Unregister`.
- Tests must not create real scheduled tasks.

### Commit 3: health pulse integration

Extend:

- `scripts/Monitor-ServerHealthPulse.ps1`
- `tests/Test-ServerHealthPulse.ps1`

Requirements:

- Include dashboard, MCP, and ngrok-gateway service entries.
- Use `http://127.0.0.1:8787/health` as the default MCP health URL.
- Include `status/services.json` when present.
- Cloudflare must be disabled/legacy unless explicitly enabled in config.
- Output compact `status/server-health.json`.

### Commit 4: ops overview/status integration

Extend either:

- `scripts/Get-OrchestratorStatus.ps1`, adding `serviceHealth` to `status/orchestrator.json`, or
- dashboard API/status response with equivalent `serverHealth`.

Add:

- `tests/Test-DashboardServiceHealthContract.ps1`

Required behavior:

- If MCP is down, ops/status says MCP offline and gives next action.
- If ngrok is down, ops/status says external gateway unavailable and gives next action.
- If dashboard health is unknown, ops/status is not green.
- No agent wake is allowed by default.

## Suggested status shape

```json
{
  "generatedAt": "ISO-8601",
  "state": "online|degraded|offline|unknown",
  "ok": true,
  "agentWakeAllowed": false,
  "services": [
    {
      "name": "mcp",
      "enabled": true,
      "required": true,
      "state": "online|starting|offline|degraded|disabled|unknown|operator_window_required",
      "ok": true,
      "healthUrl": "http://127.0.0.1:8787/health",
      "processId": 1234,
      "interactive": false,
      "windowMode": "hidden|normal|operator_window|unknown",
      "lastCheckedAt": "ISO-8601",
      "lastStartedAt": null,
      "lastError": "",
      "nextAction": "No action required."
    }
  ],
  "nextAction": "No action required."
}
```

## Validation

Required local/CI validation:

```powershell
./tests/Test-PowerShellSyntax.ps1
./tests/Test-OrchestratorServicesSupervisor.ps1
./tests/Test-OrchestratorStartupTask.ps1
./tests/Test-ServerHealthPulse.ps1
./tests/Test-DashboardServiceHealthContract.ps1
```

CI should continue running Orchestrator Health.

## Stop conditions

Stop and report instead of continuing if:

- implementation would require touching currently running services
- a test would require a real reboot, admin rights, real ngrok, live MCP, or external network
- a proposed implementation stores live secrets or env dumps
- scope expands into a full service manager rewrite
- a required service cannot be represented without changing the confirmed default MCP port `8787`

## Notes for Codex Desktop

Use plan mode first if uncertain. Do not run `Cold-Start.ps1`. Do not run `Start-OrchMcpServer.ps1`, `Start-Dashboard.ps1`, `Restart-DashboardServer.ps1`, or `ngrok` during implementation validation. Use tests and fixtures.
