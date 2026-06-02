# P0: Add anniversary ASCII dancers to dashboard notification bar

Priority: P0
Owner: gpt
Created: 2026-04-27T19:20:00Z
Source: connector-action

## Objective
Add a top notification-bar celebration in the git-tracked dashboard for Alex and his wife's anniversary today, also celebrating the assistant birthday, without weakening the live MCP/API status contract.

## Requirements
1. Read `AGENTS.md` and `docs/agent-contract.md` before editing.
2. Implement this only in the live dashboard path, not a detached static mockup.
3. Preserve live MCP/API dashboard status data. Do not introduce static fixtures, stale cached JSON, dummy mockups, or hardcoded dashboard health/state.
4. Keep the API `generatedAt` freshness indicator visible. If live API data is unavailable or stale, the dashboard must visibly mark stale/unavailable state and alarm rather than silently showing fake health.
5. Add a top notification-bar celebration with ASCII-style bride/groom dancers in wedding dress/tux.
6. Animate the dancers moving in a circle for users who allow motion.
7. Respect `prefers-reduced-motion`; reduced-motion users must get a non-forced, static celebration.
8. Date-gate the celebration for 2026-04-27 or make it dismissible with durable client-side dismissal so the dashboard is not permanently noisy.
9. Preserve existing attention/stale/queue notifications; celebration must not hide live operational alarms.
10. Add or adjust tests/regression checks so the dashboard cannot silently use static/stale data.
11. Validate the dashboard and record commands/results in `AGENT_LOG.md` or the task handoff.

## Acceptance Criteria
- The celebration appears in the live dashboard path and not just a static mockup.
- ASCII bride/groom dancers are visible in wedding dress/tux and animate around a circle when motion is allowed.
- Reduced-motion users see a static version with no forced animation.
- API `generatedAt` freshness remains visible.
- Live status failures/staleness remain visible and alarmed.
- Notification handling remains dismissible or date-gated.
- Tests or regression scripts cover the no-static/no-stale-data behavior.
- Work is committed on a feature branch and opened as a pull request before being marked done.

## Queue-create contract note
This task was created using the discovered helper contract from `scripts/New-OrchestratorQueueTask.ps1`: `-Title`, `-Reason`, `-Priority`, `-Owner`, optional `-BlockedBy`, optional `-Root`, and `-DryRun`. There is no `-Body` parameter.

## Context
Current orchestrator snapshot from handoff: generated 2026-04-27T15:10:21-04:00; queue 2; active 0; done 2; failed 5. Known worker/claim failures mean this is marked P0 and owner `gpt` for connector-visible follow-through.
