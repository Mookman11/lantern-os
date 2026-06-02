# Sensor Convergence

Status: sensor boundary and taxonomy anchor.

## Purpose

The repo uses the word `sensor` in several places. This document converges that word with the rest of HFF's public-surface, consent, and no-hidden-telemetry posture.

## Core distinction

```text
sensor definition != live observation
live observation != personal monitoring
aggregate public-data polling != device enrollment
signal != person
signal != proof of inner state
```

## Current sensor classes

| Class | Current status | Meaning |
|---|---|---|
| Static seed measurements | Active as seeded model data | Published/reviewed source-backed measurements loaded from repo data. |
| Public-data sensor definitions | Defined, disabled by default | Code definitions that can poll public aggregate APIs only if explicitly enabled. |
| Live public-data observation | Disabled by default | Runtime polling of public aggregate APIs behind `ENABLE_LIVE_SENSORS=true`. |
| Personal/device sensors | Not active | Requires separate consent, privacy, security, and operator review. |
| Protected-minor sensors | Blocked by default | Highest-sensitivity class; no-data/local-first unless separately reviewed. |
| Actuator or control pathways | Not sensors; not allowed by default | No steering, braking, throttle, immobilization, device control, or physical-world control. |

## Current public-data live sensor definitions

The current live sensor definitions are public aggregate indicators, not personal sensors:

```text
wb-life-expectancy
wb-infant-mortality
wb-maternal-mortality
wb-gdp-per-capita
wb-gini-index
wb-adult-literacy
wb-co2-per-capita
wb-forest-area
wb-protected-areas
```

They use World Bank indicator data when enabled. A WHO sensor class also exists, but the current `create_live_sensors()` list instantiates World Bank sensors only.

## Public API source posture

World Bank Indicators API use is acceptable only as public aggregate data polling. WHO GHO API use is acceptable only as public aggregate health-statistics polling. Both must remain bounded by source attribution, uncertainty, stale-data disclosure, and runtime opt-in.

## Runtime default

```text
ENABLE_LIVE_SENSORS=false
ENABLE_MESH_SYNC=false
HFF_ALLOW_PUBLIC_WRITES=false
```

The public UI should show runtime state from `/healthz`, not infer it from sensor-definition counts.

## Naming rule

Prefer:

```text
sensor definitions
public-data sensors
live observation disabled
time-lagged aggregate indicators
```

Avoid:

```text
people sensors
child sensors
personal sensors
live sensors active
observing users
monitoring people
```

unless a separate reviewed gate actually exists.

## UX rule

The dashboard should never make a `0 live sensors` value look inconsistent with a separate count of available sensor definitions. Public copy should state both facts separately:

```text
live sensors: disabled
9 sensor definitions available
```

## Non-goals

This convergence does not enable live sensors, mesh sync, public writes, analytics, personalization, geolocation, user profiling, device enrollment, protected-minor data collection, SDK/APK expansion, or actuator behavior.
