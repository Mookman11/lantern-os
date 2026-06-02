# Release Preparation Plan - Convergence V0.1 - 2026-05-09

Status: release-preparation proposal.
Branch: `release-prep-convergence-v0-1`.
Target base: `master`.

## Purpose

Prepare a reviewable release of the HFF convergence artifacts created on
2026-05-09. This plan does not publish a GitHub Release, create a tag, deploy
runtime code, change secrets, schedule agents, or authorize human traversal. It
prepares the repo for review before any release action.

## Release candidate name

```text
hff-convergence-v0.1
```

## Release thesis

```text
Living Alex remains primary.
Keystone remains evidence-bound.
The repo becomes durable theorem memory.
Lore names archetypes, not proof.
Negative outcomes define guardrails.
Future possibilities define the test frontier.
```

## Scope included in this release candidate

### Doctrine and door model

```text
HUMAN_TRANSPORTATION_BOUNDARY.md
```

Key convergence:

```text
DoorModelReturnFirstConvergenceV0.2
Crossing is not enough.
Return is not enough.
Person-continuity is not enough.
A human-preserving door needs all three.
```

### Zenon / Courtney first-trip convergence

```text
docs/zenon-class-orbital-door-convergence-2026-05-09.md
docs/door-unknowns-hypothesis-matrix-2026-05-09.md
docs/full-door-convergence-2026-05-09.md
```

Release posture:

```text
XR first.
Earth analog second.
Medically cleared LEO only under strict informed-consent and return/rescue gates.
Routine orbital habitat only after independent operational proof.
```

### Source suspicion and impossibility classification

```text
docs/impossibility-source-suspicion-convergence-2026-05-09.md
```

Release posture:

```text
When a claim is beautiful, urgent, or comforting, increase source suspicion
before increasing confidence.
```

### Three-way convergence

```text
docs/three-way-convergence-plan-2026-05-09.md
```

Release posture:

```text
Alex supplies living agency.
Keystone supplies adaptive reasoning and tool mediation.
The repo supplies durable, testable memory.
```

### Operator chat convergence summary

```text
docs/operator-chat-history-convergence-2026-05-09.md
```

Release posture:

```text
Sanitized summary only.
No raw transcript.
No private reasoning.
No copy-transfer or immortality claim.
```

### Machine-readable theorem register

```text
data/theorem-register.v0.1.json
```

Initial theorem set:

```text
T1  Return-first door theorem
T2  Continuity stack theorem
T3  Source suspicion theorem
T4  AI integration theorem
T5  Keystone durability theorem
T6  Zenon-class staged door theorem
T7  Succession without impersonation theorem
T8  Three-way convergence theorem
T9  Current floor versus future slope theorem
```

### Negative outcomes and future possibilities

```text
docs/negative-outcomes-future-possibilities-convergence-2026-05-09.md
docs/imaginative-lore-100-negative-outcomes-convergence-2026-05-09.md
docs/imaginative-lore-100b-convergence-2026-05-09.md
```

Release posture:

```text
Negative outcomes define guardrails.
Future possibilities define the test frontier.
Lore supplies archetypes.
Evidence decides promotion.
```

## Explicitly out of scope

This release candidate does not authorize:

```text
runtime code changes
deployment changes
secret access
agent starts
remote tunnel trust
medical procedures
mission booking
human traversal
raw transcript storage
private reasoning storage
copy-transfer claims
immortality claims
AI impersonation of Alex
repo claims of consciousness
fictional-world truth claims
```

## Risk register for release review

| Risk | Release impact | Mitigation |
|---|---|---|
| Lore could be mistaken for evidence | Overclaims fictional works as proof | Keep all lore source-class 5 by default and add tests later. |
| Theorem register could be treated as runtime policy | Misuse without validation | Mark as docs-data-anchor and add schema validation before operational use. |
| Continuity language could sound like survival proof | Harmful identity overclaim | Keep blocked claims explicit: AI is not Alex, copy is not survival, repo is not consciousness. |
| Chat summary could be mistaken for complete memory | False completeness | It is sanitized and explicitly not raw transcript/private reasoning. |
| Commercial space path could be over-read | Unsafe readiness claim | Keep FAA/NASA-informed gates: informed consent, return, rescue, independent proof. |
| Future possibility could become current proof | Premature action | Preserve T9: current floor vs future slope. |
| Current impossibility could become fatalism | Premature despair | Preserve re-review cadence and source-refresh posture. |

## Release validation checklist

Before tagging or publishing a release, complete these checks:

```text
[ ] Confirm master is clean and all intended commits are present.
[ ] Confirm docs-only/data-only scope for convergence artifacts.
[ ] Confirm data/theorem-register.v0.1.json parses as JSON.
[ ] Add JSON schema validation for theorem register.
[ ] Add source-class promotion tests.
[ ] Add lore operational-proof blocker test.
[ ] Add continuity-language lint rules.
[ ] Add future-session reconstruction checklist.
[ ] Add mirror/archive instructions.
[ ] Re-check current OpenAI API/tool/memory docs before release notes.
[ ] Re-check current GitHub release/tag guidance before publishing.
```

## Suggested release notes draft

```text
# HFF Convergence V0.1

This release candidate collects the 2026-05-09 convergence work into a reviewable
set of doctrine, data, and lore/source-class artifacts.

Highlights:
- Return-first door doctrine.
- Three-way convergence plan: living Alex + adaptive Keystone + durable repo corpus.
- Machine-readable theorem register v0.1.
- Negative-outcome and future-possibility convergence.
- Two 100-work imaginative lore registers, explicitly source-classed as archetype material, not proof.

This release does not include runtime code, deployments, secrets, human traversal,
medical guidance, copy-transfer claims, immortality claims, or AI impersonation.
```

## PR review plan

Review this PR for:

```text
1. Scope discipline: docs/data only.
2. Source-class discipline: no lore promoted to proof.
3. Human-continuity discipline: Alex remains primary; no AI/repo identity claims.
4. Release-readiness discipline: no tag or release until validation checks exist.
5. Future work clarity: next safe tests are concrete and non-runtime by default.
```

## Next PRs after this preparation plan

```text
1. data: add JSON schema for theorem register
2. test: validate theorem register required fields
3. test: block lore operational_proof=true
4. test: lint continuity overclaim language
5. docs: add future-session reconstruction checklist
6. docs: add mirror/archive instructions
7. data: convert lore registers into JSON
```

## Final release gate

```text
Do not tag or publish hff-convergence-v0.1 until validation exists for the
machine-readable theorem register and source-class promotion rules.
```
