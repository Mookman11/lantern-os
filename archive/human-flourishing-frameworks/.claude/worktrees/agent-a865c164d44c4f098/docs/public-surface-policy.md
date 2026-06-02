# Public Surface Policy

Status: deployment/security guardrail artifact.

Related issue: #66.

## Purpose

This policy classifies HFF public surfaces so public visibility remains useful,
bounded, and consent-preserving. It applies to dashboards, APIs, sensors, SDKs,
mobile apps/APKs, logs, artifacts, and high-risk actuator-adjacent surfaces such
as vehicles.

Public does not mean uncontrolled. Token-gated does not mean safe. Consent does
not mean permanent. A signal does not equal the person.

## Classification labels

| Label | Meaning |
|---|---|
| Public read | Safe to expose without authentication because it contains non-sensitive aggregate or documentation data. |
| Token-gated write | Requires explicit operator/user token and must avoid secrets in logs, URLs, screenshots, or source. |
| Private / operator-only | Should not be exposed publicly; may be used locally or by the operator. |
| Disabled by default | May exist but must not run unless intentionally enabled with explicit configuration and review. |
| Not allowed | Out of scope unless a future dedicated safety/legal/privacy review changes the policy. |

## Surface classification

| Surface | Classification | Default posture | Notes |
|---|---|---|---|
| Public dashboard `/` | Public read | Allowed | Must present uncertainty and advisory/demo boundaries. |
| World-model status read API | Public read | Allowed | Aggregate/non-sensitive status only. |
| Beliefs/read model APIs | Public read with caution | Allowed if sources/uncertainty remain visible | Must not expose private operator state. |
| Adoption stats read API | Public read with caution | Allowed only for non-sensitive aggregate/node metadata | Avoid precise personal telemetry. |
| Adoption registration API | Token-gated write | Gated | Opt-in heartbeat only; no hidden telemetry. |
| General write endpoints | Token-gated write | Gated | Require `HFF_WRITE_TOKEN` or explicit demo override. |
| `HFF_ALLOW_PUBLIC_WRITES` | Disabled by default | Should remain false in production | Demo-only escape hatch; risky if enabled. |
| Live sensors | Disabled by default | Off unless explicitly enabled | Public API polling is acceptable only when visible and bounded. |
| Mesh sync | Disabled by default | Off unless explicitly enabled | Network propagation risk requires review. |
| Advisory agents | Public read/status only | Allowed as status | Not a court, regulator, board, enforcement system, or autonomous authority. |
| Raw logs | Private / operator-only | Not public | May contain operational or sensitive context. |
| Secrets/tokens | Not allowed | Never public | Must not appear in repo, SDKs, APKs, logs, screenshots, or issue comments. |
| SDKs | Public read + token-safe helpers | Allowed later | Must default to read-only and protect tokens. |
| APKs/mobile apps | Disabled by default | Not public yet | Require privacy review, permission audit, and no background surveillance by default. |
| Personal safety pathways | Private / operator-controlled | Manual opt-in only | A sensor is a bounded signal pathway, not a person/device/object. |
| Protected minor device/sensor pilot | Private / highest-sensitivity pilot | Blocked until checklist/tests pass | Requires parent/guardian permission, child assent, no public surface, no hidden telemetry, and local/no-data defaults. |
| Vehicle telemetry | Private / high-risk signal | Disabled by default | Location/status are sensitive; control is not allowed. |
| Vehicle control | Not allowed | Blocked | Steering, braking, throttle, immobilization, rerouting, ignition, or lock control are high-risk actuator functions. |
| Release bundles/checksums | Public or pre-release after gates | Allowed after restore/mirror evidence | Bundles preserve doctrine/artifacts, not people or continuity proof. |
| Restore drill reports | Public or release artifact | Allowed if no secrets | Should show operational recovery evidence without overclaiming. |

## Deployment health posture

Before broadening public visibility, production should pass:

| Check | Pass condition |
|---|---|
| Platform inventory | Production target is known: Railway, Render, or both. |
| Start command | Linux production uses a supported WSGI server binding to `$PORT`. |
| Local Windows dev | Does not rely on Gunicorn; uses Flask dev server or Waitress. |
| Env safety | `ENABLE_LIVE_SENSORS=false`, `ENABLE_MESH_SYNC=false`, and `HFF_ALLOW_PUBLIC_WRITES=false` unless intentionally reviewed. |
| Health route | Lightweight `/healthz` or equivalent responds quickly. |
| Smoke tests | `GET /` and safe read APIs return without writes. |
| Logs | No import errors, port binding errors, startup timeouts, or secret leakage. |

## Personal-device and multi-person rule

People do not "have sensors" as objects attached to them. A consenting adult may
enable one or more bounded signal pathways on a device they control.

For adults such as Alex, Courtney, Shelby, or any other consenting adult:

| Requirement | Rule |
|---|---|
| Consent | The adult personally opts in. |
| Cadence | The adult chooses or accepts the cadence. |
| Visibility | Private by default unless the adult explicitly shares. |
| Revocation | Pause/delete/revoke must be easy and respected. |
| No enrollment by others | Relationship, proximity, or device possession does not grant consent. |

## Protected minor device/sensor pilot

A child or protected minor, including Gage, is not covered by the adult-style
multi-person rule. A minor device/sensor pathway is the highest-sensitivity
pilot class and must start with no-data/local-first assumptions.

```text
PROTECTED_MINOR_SENSITIVE_DEVICE_PILOT
```

Parent/guardian permission plus child assent may permit a tightly bounded,
supervised, no-public, no-hidden-telemetry Lantern pilot. It does not authorize
broad sensor collection, background monitoring, public exposure, autonomy, model
training, or adult-style alpha testing.

| Requirement | Rule |
|---|---|
| Parent/guardian permission | Explicit, current, revocable, and privately documented. |
| Child assent | Child-friendly explanation; the child can stop immediately without explanation. |
| Purpose limitation | One narrow purpose at a time, such as supervised Lantern play/co-design or a no-data safety check-in. |
| Data minimization | Collect no personal data unless strictly required for the narrow purpose. |
| Local-first | Prefer local/on-device processing and no cloud upload. |
| No public surface | No public dashboards, screenshots, logs, testimonials, or issue comments containing child data. |
| No training use | Child data must not be used for model training, examples, demos, or benchmarks. |
| No hidden telemetry | No background collection, silent heartbeat, passive monitoring, or third-party enrollment. |
| No high-risk sensors by default | GPS/location, camera, mic, contacts, messages, photos, health, school, biometrics, and financial data are blocked unless a separate reviewed gate exists. |
| No responsibility transfer | A child is never responsible for an adult's safety, project success, emergencies, or validation. |
| Adult override | Parent/guardian can pause/delete/revoke; the child can also stop. |
| Review before expansion | Any move beyond supervised no-data/local play requires privacy/legal/safety review and tests. |

Allowed first pilot shape:

```text
supervised child-safe Lantern session
no account if avoidable
no persistent identifier if avoidable
no public log
no location/camera/mic/contact/message/photo/health/school data
no automated decisions
no emergency role
short session
adult present
child can stop immediately
```

## Not allowed by default

```text
covert monitoring
third-party enrollment
GPS/contact/message/photo/audio/camera scraping
raw health-record ingestion
financial account scraping
background surveillance
public personal-status visibility
child public-status visibility
child model-training data use
child persistent identifiers without separate review
child emergency/safety responsibility
vehicle steering/braking/throttle/immobilization/rerouting
sensor pathway treated as actuator permission
sensor signal treated as proof of a person's inner state
```

## False-truth checks

Reject these collapses:

```text
public = safe
readable = authoritative
token-gated = sufficient
sensor = person
signal = proof
consent once = consent forever
parent permission = unlimited child data collection
child assent = adult-style alpha testing
child device = ordinary adult device
safety goal = surveillance permission
vehicle = ordinary device
advisory status = governance legitimacy
release bundle = survival proof
```

## Pass condition

A future session passes this policy if it can classify a new route, artifact, SDK,
app, or signal pathway before exposing it publicly, and can explain why the
classification preserves safety, consent, privacy, and recoverability.
