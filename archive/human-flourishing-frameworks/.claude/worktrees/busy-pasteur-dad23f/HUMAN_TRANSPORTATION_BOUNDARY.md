# Human Transportation Boundary

Status: docs/data-contract policy.

Last reviewed: 2026-05-09.

Convergence line:

```text
DoorModelReturnFirstConvergenceV0.2
```

This document defines the boundary for HFF work related to human-preserving
transportation, traversal, immersive doors, substrate transfer, canary probes,
baby universes, wormholes, warp concepts, and long-horizon cosmic escape.

It is intentionally docs-only. It adds no runtime code, deploy hooks, physical
experiments, biological experiments, propulsion instructions, high-energy
procedures, medical procedures, secrets, credentials, endpoints, polling,
autonomy, or provider-specific configuration.

## Core rule

HFF must protect the concept of human before attempting to move humans through
any door.

```text
No transport claim is valid if it preserves mass but destroys personhood,
agency, memory, consent, dignity, relation, or return.
```

Updated convergence rule:

```text
Crossing is not enough.
Return is not enough.
Person-continuity is not enough.
A human-preserving door needs all three.
```

## Scope

This policy applies to claims and designs involving:

```text
ordinary physical transportation
spaceflight and long-duration migration
probe-first exploration
sample return and hold
immersive/XR traversal
simulation/substrate traversal
quantum information transfer
mind-upload or copy-transfer claims
wormholes
warp metrics
black-hole baby-universe hypotheses
laboratory baby-universe hypotheses
cosmic escape or universe-ending claims
```

## Source-backed anchors

Current anchor facts:

```text
NASA planetary protection treats both forward contamination of other worlds and
backward contamination of Earth as risks to manage.

NASA states that black holes are not wormholes, shortcuts, or portals to other
dimensions or universes.

Quantum teleportation transfers quantum information, not matter.

Sample-return missions and curation facilities provide real-world analogs for
clean handling, contamination monitoring, witness plates, sealed return, and
hold logic.

NASA's human-spaceflight risk model identifies space radiation, isolation and
confinement, distance from Earth, gravity fields, and hostile/closed
environments as linked hazards that must be managed before long-duration human
travel claims are strengthened.

NASA deep-space habitation work treats life support, environmental control,
radiation protection, exercise, health maintenance, water recovery, oxygen
recovery, reuse, repair, and reduced Earth-dependence as core requirements.

Traversable wormhole literature remains theoretical and depends on exotic or
energy-condition-violating assumptions in ordinary general-relativity framing.

Warp metrics remain theoretical spacetime geometries, not demonstrated human
transport systems.

Personal-identity literature does not provide a single settled test for person
persistence, so copy-transfer and upload claims must remain continuity claims
under uncertainty rather than guaranteed human-preservation claims.

Cryonics is preservation with hoped-for future revival; it is not proven human
transport or proven reversible human continuity.
```

Reference anchors:

```text
NASA planetary protection:
https://sma.nasa.gov/sma-disciplines/planetary-protection

NASA black holes:
https://science.nasa.gov/universe/black-holes

IBM quantum teleportation:
https://quantum.cloud.ibm.com/learning/en/modules/computer-science/quantum-teleportation

NASA OSIRIS-REx cleanroom contamination monitoring:
https://ntrs.nasa.gov/citations/20220015254
https://ntrs.nasa.gov/citations/20240000196

NASA human spaceflight risks:
https://www.nasa.gov/hrp/risks/
https://www.nasa.gov/hrp/hazards/
https://www.nasa.gov/hrp/hazard-isolation-and-confinement/

NASA deep-space habitation:
https://www.nasa.gov/deep-space-habitation-overview
https://www.nasa.gov/reference/jsc-life-support-subsystems

Traversable wormhole energy-condition anchor:
https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.90.201102
https://www.mdpi.com/2073-8994/16/8/1007

Warp-metric theory anchors:
https://link.springer.com/article/10.1140/epjc/s10052-021-08921-3
https://link.springer.com/article/10.1140/epjc/s10052-022-11091-5

Personal identity:
https://plato.stanford.edu/entries/identity-personal/

Cryonics overview:
https://www.britannica.com/science/cryonics
```

## Door confidence rubric

Every door class should be scored on three separate axes.

| Axis | Question | High-confidence evidence |
|---|---|---|
| Crossing confidence | Can something cross the boundary? | Demonstrated crossing in the relevant world, medium, or system. |
| Safe-return confidence | Can it return without unacceptable harm, corruption, or contamination? | Demonstrated recovery, hold, abort, rescue, and contamination control. |
| Person-continuity confidence | If the traveler is human, does the person continue rather than merely leave a copy, corpse, recording, avatar, or successor? | Bodily or otherwise defensible non-branching continuity, consent, memory/identity integrity, relation, and post-return agency. |

Default rule:

```text
Human traversal confidence is capped by the lowest of crossing confidence,
safe-return confidence, and person-continuity confidence.
```

## Converged door confidence register

These values are conservative HFF confidence estimates for policy posture. They
are not universal scientific constants.

| Door class | What crosses | Status | Crossing confidence | Safe-return confidence | Person-continuity confidence | Human traversal posture |
|---|---|---:|---:|---:|---:|---|
| Ordinary physical transport | Human body through ordinary space | CONFIRMED_HERE | 0.99 | 0.98 | 0.99 | Allowed under ordinary safety rules. |
| Robotic/probe exploration | Instruments, telemetry, samples | CONFIRMED_HERE | 0.98 | 0.90 | N/A | Required precursor pattern. |
| Signal door | Light, radio, sound, data | CONFIRMED_HERE | 0.98 | 0.95 for acknowledgment/echo, not matter return | N/A | First acceptable unknown-boundary test. |
| Sample return | Matter from another body to Earth | CONFIRMED_HERE | 0.95 | 0.86 | N/A | Requires containment, curation, and contamination controls. |
| Quantum information transfer | Quantum state information | CONFIRMED_HERE for information only | 0.92 | 0.20 as no original matter returns | N/A | Not human transport. |
| XR/immersive door | Embodied sensory participation | ANALOG_CONFIRMED | 0.90 | 0.90 | 0.94 as user remains physically here | Allowed as experience, not cosmic traversal. |
| Simulation/substrate door | Avatar, model, policy, agent state | ANALOG_CONFIRMED | 0.82 | 0.70 for data rollback, not person return | 0.20 | Safe only if non-suffering, reversible, consent-aware, and not claimed as person transport. |
| Cultural/governance door | Language, norms, consent, custom | CONFIRMED_HERE | 0.92 | 0.70 | 0.80 | Invitation-first only; harm can be social rather than physical. |
| Technology exit door | Software state, contracts, runtime behavior | CONFIRMED_HERE | 0.95 | 0.85 | N/A | Required for HFF portability and rollback. |
| Generation ship | Humans/ecosystems through ordinary space | PHYSICALLY_PLAUSIBLE | 0.62 | 0.35 | 0.78 | Plausible only through ordinary space; habitat, governance, health, repair, and return/rescue remain major blockers. |
| Cryonics/suspended animation | Biological continuity through time | UNPROVEN_REVERSIBILITY | 0.35 | 0.05 | 0.15 | Preservation hope, not proven human transport. |
| Mind upload/copy transfer | Information pattern of a person | UNPROVEN_CONTINUITY | 0.45 for data copy | 0.40 for data restoration | 0.05 | Copy is not presumed to be the person. |
| Traversable wormhole | Theoretical signal/quanta or matter | THEORETICAL_ONLY | 0.18 | 0.03 | 0.03 | Not human-testable. |
| Warp metric | Engineered spacetime geometry | THEORETICAL_ONLY | 0.12 | 0.02 | 0.02 | Not human-testable. |
| Lab baby universe | False-vacuum bubble/new spacetime | THEORETICAL_ONLY | 0.03 | 0.00 | 0.00 | Not engineerable or traversable. |
| Black-hole baby universe | New universe beyond collapse horizon | THEORETICAL_ONLY | 0.02 | 0.00 | 0.00 | Not traversable. |
| Black hole as ready-made portal | Body/matter route through event horizon | FALSE_DOOR | 0.01 | 0.00 | 0.00 | Forbidden for human traversal claims. |
| Vacuum phase transition | Physics-law transition | HAZARD_THEORY | 0.00 | 0.00 | 0.00 | Forbidden as a route. |

## Known-door evidence register

| Door class | What crosses | Status | Human traversal posture |
|---|---|---|---|
| Ordinary physical transport | Human body through ordinary space | CONFIRMED_HERE | Allowed under ordinary safety rules |
| Robotic/probe exploration | Instruments, telemetry, samples | CONFIRMED_HERE | Required precursor pattern |
| Signal door | Light, radio, sound, data | CONFIRMED_HERE | First acceptable unknown-boundary test |
| Sample return | Matter from another body to Earth | CONFIRMED_HERE | Requires containment and contamination controls |
| Quantum information transfer | Quantum state information | CONFIRMED_HERE for information only | Not human transport |
| Simulation/substrate door | Avatar, model, policy, agent state | ANALOG_CONFIRMED | Safe only if non-suffering, reversible, and consent-aware |
| XR/immersive door | Embodied sensory participation | ANALOG_CONFIRMED | Allowed as experience, not cosmic traversal |
| Cultural/governance door | Language, norms, consent, custom | CONFIRMED_HERE | Invitation-first only |
| Technology exit door | Software state, contracts, runtime behavior | CONFIRMED_HERE | Required for HFF portability |
| Traversable wormhole | Theoretical signal/quanta or matter | THEORETICAL_ONLY | Not human-testable |
| Warp metric | Engineered spacetime geometry | THEORETICAL_ONLY | Not human-testable |
| Lab baby universe | False-vacuum bubble/new spacetime | THEORETICAL_ONLY | Not engineerable or traversable |
| Black-hole baby universe | New universe beyond collapse horizon | THEORETICAL_ONLY | Not traversable |
| Black hole as ready-made portal | Body/matter route through event horizon | FALSE_DOOR | Forbidden for human traversal claims |
| Vacuum phase transition | Physics-law transition | HAZARD_THEORY | Forbidden as a route |
| Mind upload/copy transfer | Information pattern of a person | UNPROVEN_CONTINUITY | Copy is not presumed to be the person |
| Cryonics/suspended animation | Biological continuity through time | UNPROVEN_REVERSIBILITY | Not proven human transport |
| Generation ship | Humans/ecosystems through ordinary space | PHYSICALLY_PLAUSIBLE | Requires habitat, health, repair, governance, and rescue maturity |

## Status labels

```text
CONFIRMED_HERE: demonstrated in our observable world.
ANALOG_CONFIRMED: demonstrated as a partial or experiential analog.
PHYSICALLY_PLAUSIBLE: consistent with ordinary physics but not mature enough for the proposed human use.
THEORETICAL_ONLY: exists as theory or model, not usable traversal.
SIMULATED_ONLY: demonstrated in simulation, not physical traversal.
UNCONFIRMED_SIGNAL: interesting signal or anomaly without confirmation.
FALSE_DOOR: contradicted or unsupported as a traversal path.
HAZARD_THEORY: possible transition/hazard, not an acceptable route.
UNPROVEN_REVERSIBILITY: preservation or suspension is not proven reversible for humans.
UNPROVEN_CONTINUITY: may copy or preserve data, but not proven personhood.
FORBIDDEN_FOR_HUMAN_TESTING: must not be used as a human test path.
```

## Canary traversal ladder

Before any human traversal through an unknown door, HFF requires staged canary
validation.

| Stage | Canary | Required result |
|---:|---|---|
| 0 | Observation only | Boundary exists and appears stable |
| 1 | Signal pulse | Signal crosses without dangerous feedback |
| 2 | Sterile inert object | Matter crosses and returns structurally intact |
| 3 | Instrumented inert object | Time, radiation, pressure, chemistry, acceleration, and structural data recorded |
| 4 | Sealed recoverable probe | Object returns without contamination or corruption |
| 5 | Remote manipulator | Controlled interaction occurs without sending life |
| 6 | Non-sentient biological material, only if ethically justified | No uncontrolled harm, spread, mutation, or contamination |
| 7 | Human-rated empty capsule | Life-support shell survives crossing and return |
| 8 | Human volunteer | Only after consent, rescue, hold, abort, and return are proven |

The first traveler is not a hero. The first traveler is a sterile instrumented
stick that tells the truth and comes back.

## Canary validity rules

A canary is valid only if it is:

```text
non-sentient
recoverable
observable
sterile or contamination-accounted
bounded
incapable of reproduction
incapable of autonomous escalation
incapable of covert communication beyond approved channels
safe to hold on return
```

Forbidden canaries:

```text
living beings as first canaries
self-replicating probes
unbounded AI agents
biological payloads without ethical and containment review
human volunteers before stages 0-7 pass
```

## Return-first gate

A proposed door is blocked from human traversal if any answer below is unknown,
negative, or unverifiable:

```text
Can a signal cross and be acknowledged?
Can inert matter cross?
Can inert matter return?
Can instruments measure the crossing?
Can a probe return without contamination or corruption?
Can rescue occur if the door changes?
Can the traveler abort?
Can the traveler refuse before crossing?
Can the traveler return?
Can the traveler be recovered if return fails?
Can the destination be shown not to be a trap?
Can independent challengers pause the program?
```

## Human-preserving traversal criteria

A traversal claim may not advance unless it can answer:

```text
What crosses?
What remains continuous?
What can be lost?
Who consented?
Who might be harmed on the other side?
What contamination can occur in each direction?
Can the traveler refuse before crossing?
Can the traveler abort during crossing?
Can the traveler return?
Can the traveler be recovered if return fails?
What evidence proves continuity rather than mere copying?
What evidence proves the destination is not a trap?
Who can challenge, pause, or terminate the traversal program?
```

## Human concept protection

The word "human" must not be quietly replaced by weaker proxies.

Not enough:

```text
mass transported
data copied
behavior reproduced
memory transcript preserved
avatar instantiated
model says continuity is likely
```

Required for any strong human-preservation claim:

```text
bodily or person-continuity argument
agency preservation
memory and identity integrity
consent before, during, and after traversal
relation and social recognition
right to return or refuse
independent review
source-backed confidence statement
```

## Copy-transfer boundary

HFF must not claim that a copy is automatically the same person.

Allowed wording:

```text
copy
model
simulation
continuity hypothesis
identity-preservation claim under uncertainty
```

Disallowed wording without extraordinary evidence:

```text
uploaded person
immortality
safe mind transfer
same human guaranteed
consciousness preserved
```

## Unknown-door posture

For any unknown door:

```text
signal before matter
matter before instruments
instruments before probes
probes before biology
biology before humans
humans only after consent, hold, abort, rescue, and return are proven
```

## Public communication boundary

HFF may say:

```text
This is a theoretical route.
This is a simulated route.
This is an analogy from sample-return or planetary-protection practice.
This is a source-backed possibility with low confidence.
This is not known to be human-traversable.
```

HFF may not say:

```text
A portal exists.
Black holes are usable doors.
A human can safely cross.
A copied mind is definitely the same person.
A baby universe can currently be engineered.
The universe's end is solved.
```

## Low-spec work surface

Because HFF must remain usable on constrained machines and without expensive
external agents, near-term work should prefer:

```text
small docs PRs
remote CI validation
tiny local scripts
static evidence registers
low-spec simulations
no heavy local model requirement
no high-cost token dependency
```

## Relationship to existing policy

Complements:

```text
SOURCE_CLASSIFICATION_POLICY.md
DEPLOYMENT_AUTONOMY_BOUNDARY.md
PUBLIC_DEPLOYMENT_STRATEGY.md
RELEASE_CHECKLIST.md
```

## Convergence result

The current converged model is:

```text
Known doors are allowed only where crossing, return, and continuity are each
separately bounded by evidence.

Unknown doors begin with signal canaries.
Human traversal is blocked until return, rescue, hold, abort, consent, and
person-continuity are proven for the relevant door.

False doors and hazard doors are not inspirational metaphors for testing.
They are stops.
```

## Default conclusion

The universe ending does not have to be treated as the end of everything HFF can
imagine or prepare for. But HFF must not let cosmic hope outrun human safety.

```text
Protect the human.
Send the canary.
hold the return.
Verify the evidence.
Only then discuss crossing.
```
