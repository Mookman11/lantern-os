# HFF Convergence Status

Status: convergence anchor and action table.

Last reviewed: 2026-05-09.

This document is the current convergence anchor for Human Flourishing Frameworks.
It explains what is currently agreed, what remains blocked, and which action is
safest next.

This file is docs-only, but it now summarizes both docs and recent bounded
code/test work already landed on `master`.

## Current convergence line

```text
hold runtime authority
keep writes default-closed
use bounded sensors with provenance and privacy review
prefer small docs/tests/scripts commits
```

The active operating decision is:

```text
ConvergenceDefaultClosedAndBoundedDeviceTelemetry
```

This means HFF may add narrow, operator-approved telemetry adapters and tests,
but must not broaden runtime authority, enable hidden monitoring, merge broad
runtime branches, or treat sensor presence as verified truth.

## Why this is the safest next action

The repo has moved from pure docs anchoring into a small bounded sensor lane:

```text
iPhone command inbox -> easier operator control
phone adoption heartbeat -> first visible personal node
iPhone telemetry adapter -> real HFF Measurement objects
generic device telemetry adapter -> phones, watches, laptops, desktops, Pi/server/console/browser clients
```

The risk is not the existence of sensors. The risk is sensor creep: turning
operator-approved, coarse device heartbeat data into surveillance, health
inference, location tracking, or false proof of Alex's state.

Required posture:

```text
make telemetry explicit
minimize fields
reject private fields by default
label uncertainty and missing data
store no secrets or raw private logs
keep runtime writes gated
validate with tests before endpoint expansion
```

## Surface and session desync risk

HFF must explicitly account for ordinary continuity failures:

```text
phone/laptop/tablet/browser degrades
network session drops
ChatGPT app goes down
model resets or changes
conversation is archived, deleted, truncated, or unavailable
memory settings change
connected tools are unavailable
another model is used for handoff
repo connector sees stale state
operator and Keystone hold different convergence summaries
```

These failures do not mean convergence is lost, but they can cause desync.

Required response:

```text
pause runtime-authority changes
read the convergence docs
read open issues and held PRs
check current repo state
check current live runtime evidence if deployment status matters
summarize differences before acting
prefer docs/tests repair over runtime expansion
```

## Resync protocol

When Alex says `resync`, `convergence check`, `check inbox`, or reports lost
context, use this minimum protocol:

1. Read `docs/convergence-status.md`.
2. Read `docs/keystone-memory-contract.md`.
3. Read `docs/capability-confidence-model.md`.
4. Check open issues, especially #46, #47, and #18 until closed or superseded.
5. Check held/historical PRs, especially #20 until closed, merged, or superseded.
6. Check newest relevant commits after this docs anchor.
7. Check current branch and commit state before assuming `master` equals runtime.
8. If ChatGPT/app availability is part of the failure, check OpenAI status and
   treat its metrics as aggregate rather than proof of the operator's local
   experience.
9. If runtime health matters, require fresh endpoint checks or deployment logs.
10. Produce a short convergence delta:
   - what changed;
   - what is still held;
   - what evidence is fresh;
   - what evidence is stale;
   - safest next action.
11. Do not deploy, enable runtime autonomy, or broaden telemetry as part of resync.

## Current doctrine spine

```text
Truth requires provenance.
Capability is not authority.
Memory is not proof.
Sensors are best-effort unless verified.
Live deployment health requires live endpoint or deployment-log evidence.
Autonomy is closed unless explicitly enabled and stage-authorized.
Device telemetry is opt-in, coarse, bounded, and privacy-reviewed.
Alex is the human operator/project owner.
Keystone is the HFF continuity role.
Resync before action after context loss.
```

## Current issue alignment

| Issue | Status | Convergence meaning |
|---|---:|---|
| #46 Keystone iPhone command inbox | Open / active | Operator can send short iPhone commands through GitHub issue comments; Keystone checks only on demand. |
| #47 iPhone adoption heartbeat sensor | Open / V0 working | Alex reported the iPhone heartbeat registered. Keep open for V1 endpoint/table until tests and privacy review justify runtime expansion. |
| #18 Dual-use engine risk | Open | Ongoing governance/security boundary; do not collapse into device telemetry or runtime autonomy work. |
| #36 Keystone memory contract | Satisfied by docs | Keystone memory is durable only as source-labeled summaries, not raw transcripts or proof. |
| #37 Capability confidence model | Satisfied by docs | Capability confidence is contextual, evidence-weighted, and not authority or human-worth ranking. |
| #22 Live polling observability | Closed/completed | Live polling/status observability comes before consensus hardening. |
| #13 Live sensor diagnosis | Historical | Registered sensors are not proof of fresh or verified measurements. |
| #12 Deployment split-brain | Historical | Deployment truth must be checked against the selected live surface. |

## Current PR / commit alignment

| Work item | Status | Convergence meaning |
|---|---:|---|
| #20 Runtime safety gates | Closed superseded | Do not merge as-is. Use only as historical inventory for smaller successor branches from current `master`. |
| #42 False-narrative copy guard | Merged | Public copy has a regression guard against stale live-status, automatic behavior, and self-correction claims. |
| #43 World-model shape guard | Merged | World model has a regression guard confirming scalar belief-ledger shape and no matrix/ML overclaim. |
| #44 Autonomous executor gate | Merged | Focused tests prove the executor stays default-off unless explicitly enabled. |
| #45 Mesh sync default-closed gate | Merged | Mesh sync receive path exists but returns 403 by default unless `ENABLE_MESH_SYNC=true`. |
| `docs/iphone-sensor-plan.md` | Landed on master | Defines iPhone heartbeat as opt-in node visibility, not hidden tracking. |
| `phone_telemetry.py` + tests | Landed on master | Converts iPhone Shortcut payloads into HFF `Measurement` objects and rejects private fields. |
| `device_telemetry.py` + tests | Landed on master | Generalizes bounded telemetry to approved device kinds: phone, watch, tablet, laptop, desktop, Raspberry Pi, server, game console, browser, shortcut, unknown. |
| Open PRs | None requiring merge | Current successor work should start from fresh `master` if runtime endpoint work is needed. |

## Current action table

| Rank | Best course action | Confidence | Why | Validation path |
|---:|---|---:|---|---|
| 1 | Keep device telemetry bounded at adapter/test level until tests run in CI/local shell. | 0.94 | Code now supports generic device measurements, but this connector session did not execute unittest. | Run `python -m unittest tests.test_device_telemetry tests.test_phone_telemetry`. |
| 2 | Keep iPhone heartbeat as adoption-node visibility, not as the final telemetry store. | 0.93 | Existing heartbeat is working and low-friction; telemetry needs a dedicated endpoint/table only after tests. | Confirm `/api/adoption/nodes` shows `Alex iPhone`; do not expose private fields. |
| 3 | Add a V1 `/api/operator/device/heartbeat` only as a focused PR from fresh `master`. | 0.86 | A dedicated endpoint avoids metadata stuffing and can use `device_telemetry.py` validation. | Tests must prove auth required, blocked fields rejected, sanitized fields stored separately. |
| 4 | Add retention/redaction policy before storing device telemetry beyond latest heartbeat. | 0.84 | Device telemetry is privacy-sensitive even when coarse. | Docs/tests define max retention and no raw private payload retention. |
| 5 | Keep #18 open while device telemetry expands. | 0.82 | More telemetry increases inference/dual-use risk even without direct hacking. | Review public-output containment and privacy-impact language. |
| 6 | Defer autonomous/runtime expansion. | 0.91 | Default-closed runtime remains the safest baseline. | No `ENABLE_*` runtime flags change without explicit `K RUNTIME-ACT` and fresh evidence. |
| 7 | Use Orwell/telescreen framing as a caution, not an implementation requirement. | 0.76 | The uploaded reading context reinforces the privacy boundary: sensors must not become involuntary watching. | Keep human-consent and data-minimization language in docs/reviews. |

## External alignment

The current convergence posture is consistent with public governance and platform
sources:

- NIST Privacy Framework treats privacy as enterprise risk management and frames
  privacy events as problems individuals can experience from data processing
  across the data lifecycle.
- FTC IoT guidance recommends building security into connected-device design,
  controlling access, managing data securely, monitoring risks, and considering
  data minimization.
- FTC IoT reporting warns that connected devices can create security and privacy
  risks, and recommends limiting data collection and retention to reduce harm.
- NIST AI RMF frames AI work as risk management for individuals,
  organizations, and society, and as a way to incorporate trustworthiness into
  design, development, use, and evaluation.
- OECD AI Principles promote human-centric, trustworthy AI that respects human
  rights and democratic values.
- GitHub Actions job reruns use the original event SHA/ref; a rerun is not the
  same as a fresh workflow dispatch on a new target.

References:

```text
https://www.nist.gov/privacy-framework
https://www.nist.gov/privacy-framework/getting-started-0
https://www.ftc.gov/business-guidance/resources/careful-connections-keeping-internet-things-secure
https://www.ftc.gov/node/47668
https://www.nist.gov/itl/ai-risk-management-framework
https://www.oecd.org/en/topics/ai-principles.html
https://docs.github.com/en/actions/how-tos/manage-workflow-runs/re-run-workflows-and-jobs
```

## Current validation evidence

Latest available validation evidence from 2026-05-09:

```text
PR #42 false-narrative copy guard:
local focused copy tests: Ran 10 tests - OK
local full unittest discovery: Ran 108 tests - OK
GitHub Actions unittest: passed
merge commit: 487bcc33e94ffd9fd6678af7d491f3e850a2e021

PR #43 world-model shape guard:
local focused world-model shape tests: Ran 6 tests - OK
local full unittest discovery: Ran 114 tests - OK
GitHub Actions unittest: passed
merge commit: 195eb973fded5290e3b8510108d6cdc56950dc5e

PR #44 autonomous executor gate:
local focused autonomous executor tests: Ran 3 tests - OK
local full unittest discovery: Ran 114 tests - OK
GitHub Actions unittest: passed

PR #45 mesh sync default-closed gate:
local focused mesh/app runtime tests: Ran 5 tests - OK
local full unittest discovery: Ran 119 tests - OK
GitHub Actions unittest: passed

Render public smoke from local machine:
scripts/validate_public_site.ps1 against https://human-flourishing-frameworks.onrender.com
result: PASS
LASTEXITCODE=0

Adoption/nodes:
previously /api/adoption/nodes returned []
operator later reported iPhone heartbeat registered
assistant did not independently live-probe Render from this chat

Device telemetry:
phone_telemetry.py, device_telemetry.py, and focused tests are committed
unittest execution still needs shell or CI evidence
```

Important limitation:

```text
Render smoke and adoption evidence are point-in-time.
Operator report is useful continuity evidence, not a substitute for fresh endpoint checks.
Device telemetry tests are committed but not executed in this GitHub-only connector session.
```

## Current blockers

Do not mark runtime endpoint/device telemetry expansion ready until these are satisfied:

```text
focused device telemetry tests executed
runtime flags audited
phone/device heartbeat endpoint designed as default-closed
write tokens kept out of repo/chat/issues
retention/redaction policy recorded
blocked private fields covered by tests
live public health checked again if release claims are made
```

## Next best action

The current highest-confidence action is:

```text
run focused device telemetry tests, then create a small V1 endpoint PR only if tests pass
```

Deferred items:

```text
CI workflow changes: deferred unless needed to run the new focused tests.
deployment/dependency cleanup: deferred because changing safe_app/deploy entrypoints needs surface-specific deployment evidence.
issue #18: remains open as the dual-use governance boundary.
raw phone data ingestion: blocked.
precise location/health/message/audio/camera telemetry: blocked by default.
```

## Explicit non-goals

This convergence anchor does not authorize:

```text
runtime memory engine
raw chat transcript storage
autonomous deployment
autonomous recovery
mesh writes
bio-threat polling or dashboarding
operational pathogen detail
secret access
public scoring of people
moral authority claims
hidden device tracking
precise location tracking
health/sleep ingestion
contacts/messages/audio/camera/photo capture
consensus hardening before live telemetry evidence
```

## Re-evaluation rule

After this docs anchor lands:

```text
keep #20 closed as superseded unless Alex explicitly reopens it
prefer rebuilding useful broad-runtime material as small successor PRs
keep default-closed behavior as the baseline
require live endpoint/deployment-log evidence before release validation
run the resync protocol after any major context loss
require tests before turning device telemetry adapters into runtime endpoints
```