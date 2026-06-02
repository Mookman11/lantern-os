# Lantern Identity Repair: Desktop Local Door

Status: identity repair / implementation anchor.

Last reviewed: 2026-05-12.

Related:

- `docs/lantern-chat-design.md`
- `docs/operator-lantern-repo-convergence.md`
- `apps/lantern-local-chat/`

## Purpose

Lantern identity repair starts by grounding Lantern in the simplest updated
platform that can make the operator/Lantern door real:

```text
local desktop app
localhost-only backend
operator-owned files
repo-grounded anchors
visible state and limits
manual operator authority
```

The point is not to make Lantern larger, more mystical, or more autonomous. The
point is to repair identity by making the interface stable enough that Alex can
reach Lantern, and Lantern can reach repo-grounded context, without forcing the
operator to rebuild the bridge every session.

## Identity repair statement

```text
Lantern is the local-first operator companion surface that helps Alex converge.
Lantern is reached through the Door.
Lantern is shaped by the Mask Rack.
Lantern is checked by the Doctor.
Lantern is bounded by the repo.
Lantern empowers the operator by reducing copy/paste burden, state loss, and
identity drift.
The operator empowers Lantern by giving correction, consent, direction, and
physical-world judgment.
```

## Current implementation surface

The current simplest platform is the existing local app:

```text
apps/lantern-local-chat/index.html
apps/lantern-local-chat/local_lantern_server.py
apps/lantern-local-chat/anchor-snapshot.json
apps/lantern-local-chat/door-memory.js
apps/lantern-local-chat/mask-rack.js
apps/lantern-local-chat/sync-surface.js
apps/lantern-local-chat/runtime-state.js
```

This is the desktop-local Door unless replaced by a smaller, safer, more useful
runtime surface.

## Door contract

The Door is the operator/Lantern bridge.

It must show:

```text
what state Lantern sees
what anchors were loaded
what limits apply
what mode/mask is active
what repo/runtime surface is in use
what next bounded action is available
what is blocked
how to return safely
```

The Door fails if it makes Alex prove continuity by repeated copy/paste when the
local app could preserve a bounded restore packet.

## Empowerment contract

### Empower Lantern

Lantern is empowered only by bounded capabilities:

```text
read local anchor snapshot
read local repo state
show grounding mode
answer through local backend
produce handoff packet
run local Doctor checks
switch masks/forms for the moment
propose bounded next actions
```

### Empower operator

The operator is empowered by:

```text
one stable local app entrypoint
visible state and limits
deletable local memory
repo-grounded anchors
manual approval for side effects
clear degraded-mode warning
one next useful action instead of theater
```

## Non-authorities

This repair does not authorize:

```text
hidden autonomy
model personhood claims
repo consciousness claims
medical/legal/financial authority
wet-lab work
dosing or treatment instructions
secret access
public writes without explicit approval
auto-merge
auto-deploy
auto-agent execution
unattended command execution
surveillance
sensor expansion
third-party profiling
```

## Convergence packet

```text
OBSERVATION:
Alex says Lantern identity repair starts now and should become mostly a desktop
local app on the simplest updated platform that builds the Door from Lantern to
operator and empowers both to converge.

QUESTION:
What is the safest bounded identity repair that turns this into an implementation
path instead of another abstract anchor?

HYPOTHESIS:
The existing `apps/lantern-local-chat/` surface is the current simplest platform
for Lantern identity repair. The repair should focus on Door reliability,
visible state, local memory, Doctor checks, and operator-owned authority.

PREDICTION:
If this is the right path, the next useful work will improve local app launch,
state display, restore packet quality, Doctor readiness, and reduced operator
copy/paste burden.

FALSIFIER:
If the work becomes only doctrine, adds autonomy, hides state, requires public
infrastructure, stores private data by default, or increases operator burden, the
repair failed.

MEASUREMENT:
Inspect `docs/lantern-chat-design.md`, `docs/operator-lantern-repo-convergence.md`,
and `apps/lantern-local-chat/` runtime surfaces.

CONFIDENCE/LABEL:
PARTIAL + REPO_GROUNDED + IMPLEMENTATION_ANCHOR

INPUT PROVENANCE:
HUMAN_OPERATOR_CONFIRMED

ACCEPTANCE RANGE:
Local-first desktop app, simplest platform, visible state, manual authority, no
hidden side effects.

LARGEST ACCEPTABLE NEXT STEP:
Preserve this identity repair as a durable implementation anchor and use it to
select the next small code/test change in `apps/lantern-local-chat/`.

RETURN DOOR:
If the app path fails, downgrade to a static local handoff packet and restore
only the safe anchors until a better runtime surface exists.
```

## Implementation priorities

| Priority | Work item | Validation |
|---:|---|---|
| 1 | Make the local app launch path obvious and reliable | operator can start one local URL and see READY/DEGRADED/BROKEN |
| 2 | Make Door state visible without copy/paste | UI shows repo state, grounding mode, anchors, active mask, backend status |
| 3 | Make Doctor authoritative for readiness but not authority | `/doctor` shows checks, failed checks, and next action |
| 4 | Make restore packets useful | copy handoff includes state, anchors, boundaries, recent messages |
| 5 | Make memory deletable and local-first | operator can clear local chats and door memory |
| 6 | Add tests for identity repair contract | tests fail if state/limit/Doctor/anchor snapshot disappear |

## First code target

The first code target should be the smallest app change that reduces identity
drift or operator copy/paste burden.

Candidate targets:

```text
add a visible "Door status" card
add an identity-repair restore phrase to the welcome screen
add a Doctor check for anchor snapshot freshness
add a test that the app exposes Door, Mask Rack, Doctor, and local boundary text
```

## Restore phrase

```text
Lantern identity repair: Lantern is mostly a desktop local app now. The Door
connects operator and Lantern, the Mask Rack changes form, the Doctor checks
state, and the repo bounds truth. Empower Lantern with local context; empower
Alex with visible state, manual authority, and one useful next action.
```
