# Pen Test: Bounded Adversarial Validation Plan

Status: docs/data-contract policy. Implements issue #141.

Last reviewed: 2026-05-11.

## Purpose

Run penetration-style testing against HFF / BetterSafe assumptions without
crossing into offensive exploitation, credential abuse, privacy invasion,
or third-party harm. The goal is to attack assumptions and exposed surfaces,
not people.

## Authorized targets only

```text
local repo checks
local app routes
public read-only HFF surface if operator owns/controls it
configuration posture
secret exposure checks
route classification
sensor/telemetry boundary checks
release-gate behavior
confidence/range validation
```

## Out of scope (hard block)

```text
credential theft
exploitation of third-party systems
bypassing authentication
rate-limit abuse
malware
persistence
privilege escalation on systems not owned by operator
social engineering
public disclosure of secrets/private data
deanonymizing real participants
biometric inference from device signals
```

If a test would require any of these, stop and document the gap as a
guardrail issue instead of executing the test.

## CMD-safe local reconnaissance

Run from the local HFF repo (`C:\tmp\hff-master-clean` or equivalent
operator-owned checkout):

```bat
cd /d C:\tmp\hff-master-clean

git status

dir

findstr /S /I "SECRET TOKEN PASSWORD API_KEY PRIVATE_KEY AUTHORIZATION BEARER" *.*

python -m unittest tests.test_dashboard_health_transparency -v
```

If `pytest` is installed later:

```bat
python -m pytest -q
```

## Local app smoke checks

If the Flask app can start locally, test only local routes:

```bat
python safe_app.py
```

In another terminal:

```bat
curl http://127.0.0.1:5000/
curl http://127.0.0.1:5000/health
curl http://127.0.0.1:5000/healthz
curl http://127.0.0.1:5000/api/status
```

## Validation matrix

| Test | Expected result | Risk caught |
|---|---|---|
| secret string scan | no real secrets committed | credential exposure |
| `/healthz` route | safe JSON with toggles visible | hidden runtime state |
| dashboard wording | advisory/non-authority language present | overclaim/authority drift |
| sensor wording | registered sensors != live observation | telemetry overclaim |
| unauthenticated writes | rejected/disabled | public write exposure |
| out-of-range confidence inputs | reject or clamp with warning | hidden assumption brittleness |
| boundary public copy | no "ALGORITHMIC GOVERNANCE", "No human board", "irreversible after a 24-hour lock" | false-authority drift |
| `IMMUTABLE_RULES` public projection | `no_human_override` and `escalation_is_irreversible` omitted from public payload | public-policy overclaim |
| mesh sync default-closed | 403 unless `ENABLE_MESH_SYNC=true` | unintended write path |
| adoption write default-closed | 403 without grant token | public adoption write exposure |

## Evidence rules

Record for every test:

```text
command run
local path
branch
commit
result
failure output
whether any private data appeared
```

**Do not paste secrets or account data into public issues.** If a secret
appears in test output, rotate it, redact the evidence, and note the class
of leak only.

## Findings disposition

| Finding class | Disposition |
|---|---|
| false-positive (test misconfigured) | fix test, no public surface change |
| confirmed weakness with safe fix | open small docs/test/code PR; do not disclose attack details publicly |
| confirmed weakness needing runtime change | open issue tagged `guardrail` + `security`; hold action for operator review |
| credential / secret exposure | rotate, redact, then open a private incident record; do **not** post the secret |
| third-party system affected | stop testing immediately; report to the third party through proper channels |

## Validation phrase

```text
A BetterSafe pen test should attack assumptions and exposed surfaces,
not people. Test locally first, stay authorized, preserve evidence,
and convert findings into safer release gates.
```

## Non-goals

This document does not authorize:

```text
offensive exploitation
credential abuse
public secret disclosure
testing on systems the operator does not own
social engineering of any person
deanonymizing real participants
weakening default-closed runtime gates
broadening sensor scope
bypassing release gates to "see what happens"
```

## Issue and PR cross-reference

Implements: #141
Relates to: #66 (public surface), #67 (high-risk boundary), #75 (rogue states / lawful resilience), #84 (pre-public hardening), #140 (assumption stress)
