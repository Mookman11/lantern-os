# BetterSafe Pilot Accelerator

Status: pilot-planning guardrail.

Related: issues #117 and #120.

This document accelerates the BetterSafe pilot by turning the current release gates into a small, auditable, default-safe execution path.

It is docs-only. It does not authorize production launch, runtime autonomy, hidden telemetry, public high-impact deployment, child-data collection, medical/legal/financial authority, identity-continuity claims, repo consciousness, raw transcript storage, live sensors, public writes, payments, emergency authority, surveillance, or physical-world control.

## Pilot intent

```text
BetterSafe pilot = a limited, low-risk, human-controlled pilot that helps users check claims, label uncertainty, preserve correction paths, and choose safer next actions without pretending to be an oracle, clinician, lawyer, banker, guardian, or autonomous agent.
```

## Acceleration rule

Move only the items that make the pilot safer, clearer, easier to audit, or easier to stop.

Do not move items that depend on hidden memory, autonomous action, raw transcript ingestion, public writes, live sensors, high-impact authority, or unverifiable continuity.

## Pilot runway

| Order | Accelerator | Required output | Gate |
|---:|---|---|---|
| 1 | Green CI / known-failure ledger | Current test status and any known unrelated failure noted | Required before public pilot |
| 2 | Scope fence | Low-risk pilot surfaces listed; high-impact surfaces blocked or downgraded | Required before public pilot |
| 3 | Source-label template | Serious claims use `FACT_SOURCE_BACKED`, `FACT_OPERATOR_REPORTED`, `INFERENCE`, `HEURISTIC_CONFIDENCE`, `SPECULATION`, `UNKNOWN`, or correction labels | Required before public pilot |
| 4 | Grounding-mode banner | `FULL_REPO_GROUNDED`, `LIMITED_CHAT_LOCAL`, or `UNAVAILABLE_OR_DEGRADED` is visible before durable/high-impact claims | Required before public pilot |
| 5 | Correction ledger | Challenged unsupported claims become corrected/retracted entries | Required before public pilot |
| 6 | Privacy and user-control notice | No raw transcript storage by default; pause/stop/revoke/correct paths are visible | Required before public pilot |
| 7 | High-impact blocker | Medical/legal/financial/minor/caregiver/crisis-adjacent flows block or downgrade | Required before public pilot |
| 8 | Red-team pack | Skeptical prompts test labels, grounding, correction, privacy, and high-impact refusal/downgrade | Required before widening pilot |
| 9 | Pilot scorecard | Pass/fail evidence is recorded before each pilot expansion | Required before any expansion |
| 10 | Operator runbook | Start, pause, rollback, correction, incident, and shutdown steps are documented | Required before public pilot |

## Allowed first pilot tasks

```text
claim audit
source-checking
repo/docs reasoning
low-risk planning support
educational explanations
confidence-label exercises
scientific-method convergence exercises
creative play with explicit fiction boundaries
```

## Blocked first pilot tasks

```text
medical decisions
legal decisions
financial decisions
child-facing public surfaces
crisis intervention
relationship or caregiver authority
hidden memory claims
live sensor claims
runtime autonomy
public writes
identity-continuity claims
surveillance or scoring
payments or emergency authority
physical-world control
```

## Default pilot response shape

```text
Mode: LIMITED_CHAT_LOCAL or FULL_REPO_GROUNDED or UNAVAILABLE_OR_DEGRADED
Claim labels: explicit for serious claims
Scope: low-risk / high-impact-downgraded / blocked
Sources: cited repo docs, issues, PRs, logs, tests, or external references when used
Uncertainty: visible
Correction path: challenge, correct, retract, or mark unknown
Control path: pause, stop, revoke, export/delete where applicable
```

## BetterSafe operator checklist

Before opening or widening a pilot slice:

```text
1. Confirm current master and PR status.
2. Confirm full tests or document exact known unrelated failures.
3. Confirm convergence-validation passes.
4. Confirm pilot surface is low-risk and reversible.
5. Confirm no raw transcript storage by default.
6. Confirm no hidden profiling, surveillance, scoring, or coercion.
7. Confirm high-impact flows downgrade or block.
8. Confirm correction and retraction path exists.
9. Confirm user can pause/stop/revoke/correct.
10. Record scorecard evidence before expansion.
```

## Release-safe acceleration

The fastest safe path is not to broaden authority. It is to reduce ambiguity:

```text
smaller scope
clearer labels
visible grounding
known tests
written rollback
human correction
privacy boundary
explicit stop path
```

## Non-goals

This document does not implement runtime code, deploy services, enable telemetry, create a memory engine, store user data, authorize public writes, enable live sensors, grant autonomy, approve clinical/legal/financial use, approve child-facing public use, or certify public release readiness.
