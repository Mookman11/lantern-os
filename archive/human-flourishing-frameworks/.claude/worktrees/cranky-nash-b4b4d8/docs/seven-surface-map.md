# Seven Surface Map

Status: low-overhead repo-wide convergence map.

## Purpose

Use the Seven pattern to keep the repo moving without turning every decision into heavy policy work.

```text
1. Say the claim.
2. Set the guard.
3. Add tiny checks.
4. Try safely.
5. Look at reality.
6. Fix mismatch.
7. Repeat later.
```

## Current high-weight surfaces

| Surface | Claim | Guard | Tiny check |
|---|---|---|---|
| Public surface | Public read surfaces are useful and bounded. | Public does not mean uncontrolled. | `docs/public-surface-policy.md` anchors disabled live sensors, mesh sync, and public writes. |
| Sensor taxonomy | Sensor definitions are not live observation. | Signals are not people, consent, proof, or actuator permission. | `docs/sensor-convergence.md` and `tests/test_sensor_convergence.py`. |
| Public UX/i18n | The dashboard should show state and limits clearly. | Do not claim localization before reviewed copy exists. | `docs/public-ux-baseline.md` and `tests/test_public_ui_baseline.py`. |
| Safe entrypoint | Public copy is sanitized before serving. | No route, write, sensor, mesh, agent, or deployment authority expansion. | `safe_app.py` anchors advisory copy, skip link, and `/healthz` sensor state. |
| Game/play surfaces | Door, Lantern, and Campaign anchors are continuity/play surfaces. | They do not authorize runtime, public exposure, sensors, child data, or table canon changes. | Keep them as issue/doc anchors unless a specific reviewed implementation exists. |

## New surfaces from today's games

```text
Lantern/Binx creative surface
Campaign 2/Tinfist tabletop surface
protected-minor Lantern door surface
wish/door/return-word continuity surface
public sensor-definition vs live-observation surface
static-dashboard/no-local-dependency surface
```

## Action rule

When a new surface appears, do the smallest useful version of the Seven:

```text
claim: what this surface is allowed to mean
guard: what it must not mean
tiny check: one doc phrase, unit test, issue anchor, or smoke result
reality: live evidence if deployed; otherwise repo evidence only
mismatch: fix wording, route, gate, or test
repeat: leave a command or issue note for the next pass
```

## Non-goals

This map does not enable live sensors, mesh sync, public writes, analytics, personalization, location logic, user profiling, device enrollment, protected-minor data collection, SDK/APK behavior, actuator behavior, runtime autonomy, deployment-setting changes, or route expansion.
