# Live Polling Readiness

This checklist answers one operational question:

```text
Is Human Flourishing Frameworks actually polling live sources and updating the model?
```

The answer must come from runtime status, not from the presence of code, a README claim, or a successful deploy alone.

## Highest-confidence next action

Make live polling observable before hardening consensus.

Confidence: 92/100.

Why: polling visibility proves the app can start, run sensors, update the world model, and report degraded states honestly. PBFT consensus is a separate research path and should not be treated as the blocker for basic live observation.

## Minimal local run

Bash:

```bash
pip install -r requirements.txt
ENABLE_LIVE_SENSORS=true python app.py
```

PowerShell:

```powershell
pip install -r requirements.txt
$env:ENABLE_LIVE_SENSORS = "true"
python app.py
```

Then check:

```bash
curl http://localhost:5000/health
curl http://localhost:5000/api/status
curl http://localhost:5000/api/world/status
```

## What must be true

A polling-ready local run should show:

- `/health` returns a healthy response.
- `/api/status` returns the app status without crashing.
- `/api/world/status` includes `live_observation_status`.
- `live_observation_status.enabled` is `true` when `ENABLE_LIVE_SENSORS=true`.
- `live_observation_status.sensor_count` is greater than zero.
- `live_observation_status.status_reason` is one of the known explicit states below.
- Errors are visible through `last_error_count` and `last_errors`; they are not silent.
- The UI/API does not imply live updates are happening when live sensors are disabled.

## Status reason guide

| `status_reason` | Meaning | Operator interpretation |
|---|---|---|
| `not_enabled` | Live polling was not enabled for this process. | Expected when `ENABLE_LIVE_SENSORS` is false or unset. Not a failure. |
| `registered_not_run` | Sensors were registered but no observation cycle has completed yet. | Wait briefly, then re-check. If it remains stuck, inspect startup logs. |
| `running` | An observation cycle has started and has not finished yet. | Usually transient. If it remains stuck, a sensor call may be hanging. |
| `ran_no_measurements` | Polling ran, but sensors returned no measurements. | Degraded. Public APIs may be unavailable, rate-limited, or missing data. |
| `ran_with_measurements_no_updates` | Measurements arrived, but the world model did not update beliefs. | Investigate mapping, entity keys, or duplicate/no-op observations. |
| `ran_with_updates` | Polling ran, measurements arrived, and beliefs were updated. | Healthy live best-effort observation. |
| `failed` | The observation loop caught an error. | Check `last_errors` and logs. Do not claim live polling is healthy. |

## Fields to inspect in `/api/world/status`

Look under `live_observation_status`:

```json
{
  "enabled": true,
  "best_effort": true,
  "sensor_count": 9,
  "observation_count": 1,
  "last_observation_started_at": "...",
  "last_observation_finished_at": "...",
  "last_measurement_count": 9,
  "last_update_count": 9,
  "last_correction_count": 0,
  "last_error_count": 0,
  "last_errors": [],
  "status_reason": "ran_with_updates"
}
```

`last_correction_count = 0` is not automatically bad. It can mean the model updated beliefs without triggering correction logic. Use `last_measurement_count`, `last_update_count`, and `status_reason` together.

## Confidence-weighted work queue

| Rank | Work item | Confidence |
|---:|---|---:|
| 1 | Keep this readiness checklist current and linked from operator workflows. | 92/100 |
| 2 | Preserve deterministic tests for live observation telemetry states. | 88/100 |
| 3 | Keep `/api/world/status` honest about disabled, running, degraded, failed, and updated states. | 86/100 |
| 4 | Add a one-command smoke script only after the manual checks are stable. | 82/100 |
| 5 | Add PBFT readiness docs after polling observability is proven. | 78/100 |
| 6 | Add a multi-node PBFT smoke test after the single-node live polling path is trusted. | 70/100 |

## Consensus boundary

PBFT consensus is not required for live polling to start.

Live polling requires:

```text
ENABLE_LIVE_SENSORS=true
app process running
network access to configured public APIs
visible status in /api/world/status
```

PBFT consensus requires a separate multi-node setup with peer URLs and quorum behavior. Until multi-node behavior is validated, describe consensus as teaching/research-grade and do not use it as evidence that live data is independently verified.

## Done condition for issue #22

Issue #22 can be considered satisfied when:

- this checklist exists and is easy to find;
- telemetry tests cover explicit status states;
- a local operator can run the commands above and tell whether polling is active, disabled, degraded, failed, or updated;
- consensus language remains clearly separated from live polling readiness.
