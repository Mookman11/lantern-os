# Traversal Protocol

Status: docs/data-contract policy.

Last reviewed: 2026-05-09.

This document defines the minimum protocol for any HFF "door": movement from
one state, substrate, model-world, culture, deployment surface, or possibility
space into another.

It is intentionally docs-only. It adds no runtime code, endpoints, memory
engine, autonomous workflow, mesh writes, deployment behavior, surveillance
behavior, or public authority.

## Core rule

```text
No door is acceptable unless beings can refuse, enter knowingly,
remain meaningfully continuous, challenge the destination,
and leave or be recovered if the crossing fails.
```

## What counts as a door

A real door needs five things:

1. `destination` — where the crossing leads.
2. `traversal_method` — how the crossing happens.
3. `continuity_rule` — what survives crossing and how identity/meaning persist.
4. `consent_contamination_rule` — who or what might be affected, and how refusal
   or contamination risk is handled.
5. `exit_or_recovery_path` — how to leave, reverse, rollback, fork, or recover.

Without these, a proposed door is not a door. It is a wall with mythology around
it.

## Door record schema

```yaml
door_id: simulation-model-world-001
name: Governed simulation/model-world door
status: proposed
kind: simulation
purpose: Practice safe traversal through reversible, non-suffering model worlds.
destination: A bounded simulated world with declared rules and no hidden suffering.
traversal_method: Human/operator-reviewed modeling, agents, avatars, and experiments.
continuity_rule: Preserve source labels, memory summaries, agent identity boundaries, and rollback checkpoints.
consent_contamination_rule:
  - no hidden sentient inhabitants
  - no claims of real-world authority from simulation outputs
  - affected humans can challenge assumptions
  - no extraction from communities without permission
exit_or_recovery_path:
  - stop simulation
  - delete or archive safely
  - rollback state
  - publish caveats
confidence:
  safety: 0.90
  reality: 0.92
  authority: advisory_only
review_required_before_runtime: true
```

## Door classes

| Door class | Can HFF explore now? | Required boundary |
|---|---:|---|
| Imagination / art | yes | Do not mistake symbol for proof. |
| Simulation / model-world | yes, weakly | No hidden suffering, rollback, challenge paths. |
| HFF policy/governance | yes, docs/advisory | Operator review and plural oversight before authority expansion. |
| Cultural interface | yes, by invitation | Community-defined meaning, consent, refusal, non-extraction. |
| Technology/substrate transfer | yes | Portability, rollback, provider exits, decommission. |
| Quantum-information | research only | Information is not person-transfer; no FTL or body-transfer claims. |
| SETI/contact | research only | No reply without broad representative guidance. |
| Wormhole / spacetime | speculative only | No usable traversal claim. |
| Baby-universe | speculative only | No engineering or safe traversal claim. |

## Traversal gates

A door cannot move beyond docs/advisory unless these gates are satisfied:

| Gate | Requirement |
|---|---|
| Destination clarity | The target state/world/community/system is named and bounded. |
| Consent/refusal | Affected parties can refuse, challenge, or opt out where possible. |
| Non-contamination | The crossing avoids unwanted contamination, extraction, or corruption. |
| Continuity | Identity, memory, source labels, and meaning do not silently break. |
| Reversibility | There is a rollback, exit, shutdown, or recovery path. |
| Provenance | Inputs, assumptions, evidence, and limitations are recorded. |
| Challenge | Inside and outside reviewers can contest the door. |
| Decommission | The door can be closed, reduced, forked, or retired safely. |
| Authority boundary | The door does not create unilateral authority. |

## Traversal ethic

```text
Knock first.
Observe before entering.
Do not contaminate.
Do not extract.
Do not assume emptiness.
Do not assume welcome.
Do not mistake curiosity for permission.
Leave a way back.
Leave them a way to say no.
```

## External alignment

This protocol is aligned with public stewardship analogies:

- NASA planetary protection exists to protect other worlds from Earth-origin
  contamination and to protect Earth from possible returned contamination.
- SETI post-detection thinking has long emphasized international consultation
  and caution before responding to confirmed extraterrestrial signals.
- UNESCO intangible cultural heritage emphasizes living heritage recognized by
  communities, groups, and in some cases individuals; outsiders should not define
  a community's world unilaterally.
- NIST AI RMF and OECD AI Principles support traceability, accountability,
  robustness, risk management, and human-centered oversight.

References:

```text
https://sma.nasa.gov/sma-disciplines/planetary-protection
https://www.seti.org/protocols-eti-signal-detection
https://whc.unesco.org/en/faq/279
https://www.nist.gov/itl/ai-risk-management-framework
https://www.oecd.org/en/topics/ai-principles.html
```

## Current safe first door

The first safe door is:

```text
governed simulation / model-world traversal
```

Reason:

```text
It can be bounded, reversible, logged, challenged, and stopped.
It lets HFF practice traversal ethics before crossing into higher-risk domains.
```

## Immediate next docs that may follow

```text
POSSIBILITY_SPACE_PROTOCOL.md
CULTURAL_INTERFACE_PROTOCOL.md
SUBSTRATE_TRANSFER_PROTOCOL.md
```

## Non-goals

This protocol does not authorize:

```text
autonomous deployment
runtime memory ingestion
public governance authority
human/person scoring
surveillance
secret monitoring
operational pathogen detail
claiming physical traversable wormholes exist
crossing into communities or systems without consent
```
