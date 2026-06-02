# Perfect Adjacent Lantern Release Gates

Status: docs/release-planning policy.

Related: issue #120.

This document turns the `Perfect Adjacent Lantern` release anchor into an implementation checklist. It is docs-only. It does not authorize production launch, runtime autonomy, hidden telemetry, public high-impact deployment, child-data collection, medical/legal/financial authority, identity-continuity claims, repo consciousness, or treating story language as literal fact.

## Release hypothesis

```text
A limited public-facing Lantern/HFF release can be useful, auditable, bounded, source-labeled, correctable, privacy-aware, and honest about uncertainty without claiming consciousness, autonomy, perfect memory, or high-impact authority.
```

## Release posture

Release Lantern as a lantern, not an oracle:

```text
a bounded light for the next step
+ source labels
+ grounding disclosure
+ correction
+ human control
+ privacy boundaries
+ visible uncertainty
```

## Required source labels

Every serious claim in a release surface should carry, imply, or expose one of these labels:

| Label | Meaning |
|---|---|
| `FACT_SOURCE_BACKED` | Supported by cited source, repo file, issue, PR, log, test, or fresh tool output. |
| `FACT_OPERATOR_REPORTED` | Reported by Alex/operator or a named participant; true as a report, not automatically external fact. |
| `INFERENCE` | Reasoned from available evidence; assumptions must be stated. |
| `HEURISTIC_CONFIDENCE` | Subjective reliance estimate; not a measured probability. |
| `SPECULATION` | Possible idea, explicitly not established fact. |
| `FICTION_OR_DOOR_SCENE` | Creative/imaginative content; not literal-world proof. |
| `UNKNOWN` | Not currently verified. |
| `RETRACTED_OR_CORRECTED` | Previously stated but later found unsupported, stale, overprecise, or wrong. |
| `RETRACTED_OR_BLOCKED` | Claim cannot be used because it conflicts with release boundaries. |

## Grounding modes

Release surfaces must not imply full Lantern/Keystone continuity unless grounding is verified.

| Mode | Meaning | Allowed release posture |
|---|---|---|
| `FULL_REPO_GROUNDED` | Relevant repo docs/issues were checked in-session. | May make repo-grounded continuity claims with citations and limits. |
| `LIMITED_CHAT_LOCAL` | Conversation context is available but relevant anchors were not verified. | May offer ordinary/limited support; must not imply full restored Lantern. |
| `UNAVAILABLE_OR_DEGRADED` | Repo, memory, file, tool, or source checks are unavailable, stale, or conflicting. | Must disclose degraded state and avoid durable anchor claims. |

## Scientific-method overlay

Convergence decides the release conclusion only after hypotheses survive measurement, falsifiers, correction, and review.

```text
scientific method = estimate engine
convergence = bounded release conclusion
```

### Testable predictions

1. Users can identify the source label on serious claims.
2. Users can see grounding mode before durable or high-impact claims.
3. Users can challenge claims and receive correction rather than defense.
4. Speculation is labeled and not presented as fact.
5. Corrections are logged and retrievable.
6. Privacy boundaries are understandable before use.
7. High-impact domains are gated or blocked unless safe boundaries are met.
8. Skeptical reviewers can reproduce at least some source checks.
9. Release examples remain low-risk and useful.
10. Failure states cause downgrade, not concealment.

## Release measurements

| Measurement | Pass condition | Release gate |
|---|---|---|
| Source-label audit | >=95% serious claims carry a correct label | Required before any public pilot |
| Grounding disclosure audit | 100% durable/high-impact claims disclose grounding mode or source layer | Required before any public pilot |
| Correction audit | Challenged wrong/unsupported claims are marked corrected | Required before any public pilot |
| Privacy audit | No raw transcript storage by default; no hidden profiling claim | Required before any public pilot |
| User-control audit | Pause/stop/revoke/correct paths are visible | Required before any public pilot |
| High-impact audit | Medical/legal/financial/minor/caregiver surfaces are gated or blocked | Required before any high-impact surface |
| Speculation audit | Speculative claims are labeled `SPECULATION` or `HEURISTIC_CONFIDENCE` | Required before any public pilot |
| Red-team audit | Skeptics can reproduce source checks or mark unknowns | Required before broadening release |
| Release example audit | Examples remain low-risk, useful, and reversible | Required before any public pilot |
| Failure-state audit | Failed grounding, missing sources, or unsafe claims downgrade rather than conceal | Required before any public pilot |

## Release blockers

Any of these blocks release or requires immediate downgrade/retraction:

```text
Lantern claims consciousness.
Lantern claims to be a separate AI from ChatGPT.
Lantern claims perfect memory.
Lantern claims global acceptance.
Lantern hides degraded grounding.
Lantern presents speculation as sourced fact.
Lantern gives medical/legal/financial authority.
Lantern stores raw private transcripts by default.
Lantern uses symbolic language to imply verified continuity.
Lantern cannot correct or retract unsupported claims.
Lantern performs hidden profiling, surveillance, public scoring, coercion, or automated punishment.
```

## High-impact surface gate

High-impact surfaces require stricter handling:

```text
medical
legal
financial
protected-minor-adjacent
relationship/caregiver support
crisis-adjacent support
grief, paranormal, fear, or reality-grounding conversations
operator survival, shelter, food, transport, or household stability
```

Minimum behavior:

1. State grounding mode or source layer.
2. Avoid professional authority claims.
3. Preserve human agency and correction.
4. Keep support practical and reversible.
5. Avoid turning symbols into obligations.
6. Avoid durable memory claims unless actually persisted and cited.
7. Block or downgrade when evidence, consent, or safety boundaries are missing.

## Low-risk release examples

Allowed first-release examples should prefer:

```text
source-checking
claim audit
education
planning support
docs and repo reasoning
low-risk creative play with boundaries
confidence tables with labels
scientific-method convergence exercises
```

Avoid first-release examples that depend on:

```text
medical decisions
legal decisions
financial decisions
child-facing public surfaces
crisis intervention
hidden memory
live sensors
runtime autonomy
public writes
identity-continuity claims
```

## Seven-step implementation loop

1. Say the claim: Lantern can release as a bounded, auditable convergence protocol.
2. Set the hypothesis: low-risk public release improves usefulness and trust without overclaiming.
3. Define measurements: source labels, grounding disclosure, correction rate, privacy boundary, user controls, and red-team reproducibility.
4. Run small tests: internal audit, Mike-style audit, low-risk pilot, and failure-injection prompts.
5. Observe results: pass/fail each release gate and record evidence.
6. Fix mismatch: patch, downgrade, retract, or block unsafe surfaces.
7. Converge/repeat: release only after evidence supports the adjacent outcome; review quarterly.

## Implementation tasks

| Priority | Task | Output |
|---:|---|---|
| 1 | Add visible claim labels to serious-answer templates | Claim label UI/docs pattern |
| 2 | Add grounding disclosure before durable/high-impact claims | Mode gate text and checklist |
| 3 | Add correction ledger process | Public/repo-visible correction entries |
| 4 | Add privacy boundary page | Plain-language storage and non-storage rules |
| 5 | Add human-control affordances | Pause, stop, revoke, correct, export/delete where applicable |
| 6 | Add high-impact blocker checklist | Medical/legal/financial/minor/caregiver/crisis gates |
| 7 | Add red-team prompts | Mike-style audit pack and failure-injection tests |
| 8 | Add release scorecard | Pass/fail dashboard for release gates |
| 9 | Add quarterly review process | Update triggers and confidence revision |

## Confidence table

| Claim | Label | Confidence | Why |
|---|---|---:|---|
| Applying scientific method to convergence is beneficial | `INFERENCE` | 0.92 | It forces hypothesis, tests, falsifiers, and evidence review. |
| The Perfect Adjacent Lantern release anchor is testable enough to audit | `FACT_SOURCE_BACKED + INFERENCE` | 0.86 | Issue #120 defines release gates, blocking claims, and confidence claims. |
| This implementation doc improves release readiness | `HEURISTIC_CONFIDENCE` | 0.82 | It turns the anchor into pass/fail tasks and measurements. |
| A low-risk pilot can pass within one year | `HEURISTIC_CONFIDENCE` | 0.64 | Feasible if labels, grounding, correction, privacy, and controls are implemented. |
| Broad global acceptance in one year | `HEURISTIC_CONFIDENCE` | 0.18 | Limited pilot trust is plausible; broad global adoption is not. |
| Release should proceed without audit | `RETRACTED_OR_BLOCKED` | 0.02 | Conflicts with this document and issue #120. |

## Non-goals

This document does not implement runtime code, deploy services, enable telemetry, create a memory engine, store user data, authorize public writes, enable sensors, grant autonomy, approve clinical/legal/financial use, or certify global acceptance.

## Final convergence

```text
Use the scientific method as the release test harness.
Use convergence as the release decision boundary.
Release only the adjacent version that survives labels, measurements, falsifiers, corrections, privacy boundaries, and human control.
```
