# Task: Service supervisor hardening  -  auto-restart and health reporting (#259 Phase 3.1)

Priority: P2
Owner: codex
Estimated time: 1.5 hours
Depends on: CI green, P1 tasks complete
Blocks: unattended overnight runs

## Context

RC3 tracker #259 Phase 3.1. The orchestrator's background services (MCP server,
dashboard) crash silently and are not restarted automatically. The operator has
to notice manually. For unattended runs, this means hours of wasted time.

`scripts/Run-ServiceSupervisor.ps1` exists and the MCP tool `run_service_supervisor`
is wired. Hardening means: reliable restart logic, max-retry cap, health status
visible in dashboard, and operator alert when a service repeatedly crashes.

## Scope

### Edit: `scripts/Run-ServiceSupervisor.ps1` (or the service supervisor implementation)

- Max restart attempts: 3 per service per hour. After 3 failures, mark service
  `degraded` in `status/services.json` and stop retrying  -  require human restart.
- Restart backoff: 10s, 30s, 60s between attempts.
- Write `status/services.json` on every state change:
  ```json
  {
    "updatedAt": "<iso>",
    "services": {
      "mcp-server":  { "state": "running|stopped|degraded", "restarts": 0, "lastRestart": null },
      "dashboard":   { "state": "running|stopped|degraded", "restarts": 0, "lastRestart": null }
    }
  }
  ```

### Edit: `dashboard/index-v3.html`

- Add a small "Services" status widget to the queue sidebar (below watcher status
  added in the dashboard UX task). Read from `status/services.json`.
- Show per-service state as a colored dot + label.

### Edit: `tests/Test-OrchestratorServicesSupervisor.ps1`

- Add test: service marked `degraded` after exceeding max restarts.
- Add test: `status/services.json` written on state change.

## Done criteria

- Service supervisor caps restarts at 3 and marks `degraded` correctly.
- `status/services.json` written on every state change.
- Dashboard sidebar shows service states from `status/services.json`.
- Existing supervisor test still passes; new degraded-state test added and passing.
- Branch pushed, PR open.

## Reference

- Issue: #259 Phase 3.1
- Existing supervisor: `scripts/Run-ServiceSupervisor.ps1` (or `Start-OrchMcpServer.ps1` watchdog)
- Existing test: `tests/Test-OrchestratorServicesSupervisor.ps1`
- Dashboard UX task (for sidebar widget placement): `20260505-p1-dashboard-next-action-ux.md`
