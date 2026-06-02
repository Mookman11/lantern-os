# Door Unknowns Hypothesis Matrix - 2026-05-09

Status: docs-only convergence addendum.

Related anchors:

```text
HUMAN_TRANSPORTATION_BOUNDARY.md
DoorModelReturnFirstConvergenceV0.2
docs/zenon-class-orbital-door-convergence-2026-05-09.md
```

## Purpose

Focus the door model on what HFF does not know yet, then define conservative
hypotheses and safe tests that can move the model toward convergence.

This document is allowed to make theories. It must label them as theories and
must define tests that do not require human traversal, physical experiments,
secrets, deployment changes, or unsafe operational procedures.

## Method rule

```text
Unknown -> hypothesis -> safe test -> evidence update -> convergence or blocker.
```

Tests allowed here:

```text
source audit
technology-readiness scoring
failure-mode table
analog mission comparison
simulation or tabletop exercise
repo test/lint/doc validation
human-factors checklist
return/rescue/hold checklist
```

Tests not allowed here:

```text
human traversal
biological experiments
propulsion or high-energy procedures
medical procedures
mission booking
secret access
runtime autonomy
one-way-door trials
```

## Readiness ladder

Use NASA/ESA technology-readiness thinking to prevent wishful convergence.

```text
TRL 1-2: concept / speculation
TRL 3-4: proof-of-concept / lab validation
TRL 5-6: relevant-environment validation / prototype demonstration
TRL 7-8: operational-environment demonstration / qualified system
TRL 9: proven in successful mission operations
```

For human doors, HFF requires not only technology readiness but also:

```text
return readiness
rescue readiness
medical readiness
social/human-factors readiness
person-continuity readiness
consent/readiness-to-refuse
```

## Current known unknowns

| Unknown | Why it matters | Current convergence posture |
|---|---|---|
| Whether a Zenon-class orbital habitat can become routine enough for a first trip | Courtney's preferred target is warm/social/orbital, not merely survival in orbit | Plausible future ordinary-space door, not current default-safe door |
| Whether safe return is routine enough for ordinary people rather than trained professionals | Crossing confidence without return confidence is not human-preserving | Return remains the limiting axis |
| Whether closed-loop life support is mature enough for family-scale orbital life | A friendly habitat needs air, water, food, waste, repair, and fire/pressure safety | Major gating unknown |
| Whether isolation/confinement risks can be reduced enough for non-professional crews | Zenon-like life is social, not only technical | Major human-factors unknown |
| Whether commercial LEO stations will achieve operational proof before ISS retirement | Emerging commercial station plans are not yet operational proof | Track as emerging evidence, not proof |
| Whether XR/analog rehearsal meaningfully predicts real trip readiness | The safest near-term first trip is simulated or analog | Testable with analog design, not proof of orbital readiness |
| Whether person-continuity language is protected across simulation/upload metaphors | A simulation visit is not person transport | Must keep copy/avatar/person distinct |

## HFF theories to test

These are HFF working hypotheses, not settled facts.

| ID | Theory | Current confidence | Safe test | Pass condition | Fail / blocker condition |
|---|---|---:|---|---|---|
| H1 | Return, not crossing, is the dominant limiter for most proposed doors. | 0.86 | Score each door by crossing, return, and person-continuity; compare the minimum axis. | Human traversal confidence is usually capped by return or continuity, not crossing. | A door has strong crossing, return, and continuity evidence and still scores low for unrelated reasons. |
| H2 | A Zenon-class orbital habitat is the safest high-imagination target because it uses ordinary-space travel and preserves bodily continuity. | 0.74 | Compare against wormhole, black-hole, upload, cryonics, generation ship, and XR alternatives. | Ordinary LEO habitat has higher continuity and lower metaphysical risk than speculative doors. | Commercial LEO return/rescue evidence stagnates or risk remains non-routine for civilians. |
| H3 | Analog-first travel is the fastest safe path for Courtney's first-trip wish. | 0.82 | Compare XR, Earth analog habitat, HERA/CHAPEA-like analogs, and real LEO mission gates. | Analog/XR can satisfy subjective rehearsal with near-perfect return and continuity. | Analog/XR is mistaken for literal traversal or produces false confidence for orbit. |
| H4 | Closed-loop life support and habitat maintenance are the main blockers to Zenon-like normal life, more than reaching orbit. | 0.77 | Audit ESA MELiSSA, NASA life-support subsystems, Biosphere 2 lessons, and commercial station life-support milestones. | Air/water/waste/food/repair/reuse are repeatedly identified as core habitat constraints. | Launch/return systems remain less mature than habitat life-support systems. |
| H5 | Social safety is a system requirement, not a comfort feature. | 0.79 | Audit NASA isolation/confinement, HERA, CHAPEA, and hostile/closed-environment hazards. | Behavioral health, sleep/circadian alignment, workload, social cohesion, and privacy appear as safety factors. | Human factors prove negligible compared with engineering hazards. |
| H6 | Commercial LEO station claims should be treated as vendor/emerging evidence until crewed operations and safe return are independently demonstrated. | 0.88 | Classify Axiom, Starlab, Orbital Reef, and Vast Haven-1 by evidence class and readiness. | Most claims remain design/milestone/vendor evidence rather than operational proof. | A station reaches crewed, certified, return-proven routine operations. |
| H7 | Any door that cannot support refusal, abort, rescue, hold, and return should be classified as blocked even if it is aesthetically appealing. | 0.93 | Apply return-first gate to each candidate. | Black-hole, wormhole, upload, baby-universe, and one-way-route claims remain blocked. | A speculative door demonstrates reversible, observable, rescue-capable traversal with continuity evidence. |

## Source anchors for tests

Use these sources as current test anchors.

```text
NASA/ESA technology readiness:
https://esto.nasa.gov/trl/
https://www.esa.int/Enabling_Support/Space_Engineering_Technology/Shaping_the_Future/Technology_Readiness_Levels_TRL

NASA human-spaceflight hazards and risks:
https://www.nasa.gov/humans-in-space/the-human-body-in-space/
https://www.nasa.gov/hrp/hazards
https://www.nasa.gov/hrp/risks/
https://www.nasa.gov/hrp/hazard-isolation-and-confinement/
https://www.nasa.gov/hrp/hazard-hostile-closed-environments/

NASA analog missions:
https://www.nasa.gov/analog-missions/
https://www.nasa.gov/mission/hera/
https://www.nasa.gov/humans-in-space/chapea/
https://www.nasa.gov/humans-in-space/chapea/about-chapea/

NASA Commercial Crew:
https://www.nasa.gov/commercialcrew
https://www.nasa.gov/humans-in-space/commercial-space/commercial-crew-program/commercial-crew-program-overview/

ESA MELiSSA closed-loop life support:
https://www.esa.int/Enabling_Support/Space_Engineering_Technology/Melissa
https://www.esa.int/Our_Activities/Space_Engineering_Technology/Melissa/Closed_Loop_Concept

Biosphere 2 historical/analog lesson source:
https://biosphere2.org/
```

## Test results from current pass

### Test H1: three-axis scoring

Result:

```text
SUPPORTED
```

Crossing confidence can be high while return or continuity is low. Examples:
quantum information transfer, copy transfer, wormhole theory, black-hole portal
claims, and XR/simulation all separate crossing from human return or continuity.

### Test H2: Zenon-class target comparison

Result:

```text
SUPPORTED WITH LIMITS
```

A warm, social, near-Earth orbital habitat is safer than speculative cosmic doors
because it preserves ordinary bodily travel and can in principle use known return
systems. It is still not routine or default-safe for ordinary family travel.

### Test H3: analog-first path

Result:

```text
SUPPORTED
```

NASA uses analog missions to test systems, protocols, scenarios, physical and
behavioral health, isolation, workload, communication, and habitat design before
crew missions. This supports XR/Earth analog rehearsal before real LEO travel.

### Test H4: closed-loop life support blocker

Result:

```text
SUPPORTED WITH PARTIAL EVIDENCE
```

ESA MELiSSA and NASA life-support materials treat air, water, waste, food,
recycling, oxygen recovery, and closed-loop ecology as central to long-duration
habitation. This is a blocker for Zenon-like normal life even if launch/return
mature first.

### Test H5: social safety requirement

Result:

```text
SUPPORTED
```

NASA's isolation/confinement and hostile/closed-environment hazards support the
theory that sleep, workload, stress, immune changes, privacy, behavioral health,
and crew interaction are safety factors, not luxuries.

### Test H6: commercial LEO evidence class

Result:

```text
SUPPORTED
```

Commercial station sources show design milestones, development progress, and
vendor plans. They do not yet prove routine family-scale orbital life with
validated return/rescue and health systems.

### Test H7: refusal/abort/rescue/hold/return gate

Result:

```text
SUPPORTED
```

The return-first door model correctly blocks aesthetically attractive but
unverified routes.

## Convergence update

The current convergence target should shift from:

```text
Can Courtney go to a Zenon-like place?
```

to:

```text
Which unknowns must be closed before a Zenon-class first trip becomes a safe
human-preserving door?
```

The answer is:

```text
1. routine bodily crossing to LEO
2. routine safe return from LEO
3. rescue/abort coverage
4. medical screening and response
5. closed-loop or reliably serviced habitat life support
6. social/behavioral safety for non-professional crews
7. honest informed consent
8. no confusion between XR/simulation and literal traversal
9. no one-way or copy-transfer route
```

## Current best theory

```text
Courtney's desired first trip should be treated as a staged Zenon-class door:
XR first, Earth analog second, medically cleared LEO visit third, routine
commercial habitat only after return/rescue/life-support/social-safety evidence
matures.
```

Confidence:

```text
0.84 as a planning theory
0.98 as a safety posture
0.35 as a claim that real orbital Zenon-class family life is currently ready
```

## Next safe tests

Near-term tests HFF can run without unsafe action:

```text
1. Add a compact Zenon-class row to HUMAN_TRANSPORTATION_BOUNDARY.md.
2. Add a machine-readable YAML/JSON door-confidence register.
3. Add a unit test that blocks human traversal when any of crossing, return, or continuity is below threshold.
4. Add a source-classification test that vendor station claims cannot be promoted to operational proof.
5. Add an analog-first checklist for Courtney-style first-trip planning.
```

## Non-goals

This addendum does not authorize:

```text
physical tests
human traversal
mission booking
medical advice
secret access
runtime code
deployment changes
autonomous planning
copy-transfer claims
unverified universe jumps
```
