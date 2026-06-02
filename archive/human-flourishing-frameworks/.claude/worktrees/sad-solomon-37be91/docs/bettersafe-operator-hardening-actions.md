# BetterSafe Operator Hardening Actions

Status: controlled limited pilot expansion.

Related: docs/bettersafe-baseline-safety-threshold.md; docs/bettersafe-pilot-launch-record.md.

## Purpose

BetterSafe must help the operator, repo, and Keystone become more resilient in reality. This protocol converts a labeled risk into a human-approved readiness action and an evidence record.

It does not grant autonomous authority. BetterSafe proposes, formats, checks, and records. The operator chooses and performs the action.

## Action packet format

Each operator hardening action must include:

```text
Objective:
Risk reduced:
Action class: NOW | TODAY | THIS_WEEK | LATER
Human-performed step:
Materials or information needed:
Evidence to record:
Stop condition:
Rollback or correction path:
Privacy impact:
Claim/source label:
Confidence:
Owner:
```

## Action classes

| Class | Meaning | Examples |
|---|---|---|
| `NOW` | Reduces immediate fragility without extra permissions | Save dashboard URL, write smoke commands, charge phone, confirm repo link |
| `TODAY` | Improves operator and household readiness within one day | Locate power bank, flashlight, first-aid kit, documents, local repo path |
| `THIS_WEEK` | Requires planning or coordination | Repo backup/mirror, deployment smoke routine, trusted contact plan |
| `LATER` | Useful but not launch-blocking | Native app review, optional SDK, broader mobile packaging |

## Minimum initial hardening backlog

| Rank | Action | Class | Confidence |
|---:|---|---|---:|
| 1 | Create a local access card with dashboard URL, repo URL, smoke commands, stop rule, and correction rule | `NOW` | 0.92 |
| 2 | Add BetterSafe to iPhone Home Screen after deployment smoke confirms the shell is live | `NOW` | 0.88 |
| 3 | Run dashboard smoke checks after each public-surface change and record result | `NOW` | 0.86 |
| 4 | Create an operator continuity card with two access paths, device charging plan, and repo recovery path | `TODAY` | 0.84 |
| 5 | Create a household readiness checklist for water, lighting, battery, first aid, documents, and contacts | `TODAY` | 0.82 |
| 6 | Create a repo resilience checklist for CI, rollback, backup/mirror, and release evidence | `TODAY` | 0.80 |
| 7 | Create a Keystone resync card with role map, memory-is-not-proof rule, source order, and correction path | `TODAY` | 0.84 |

## Evidence receipt format

```text
Date:
Operator:
Action class:
Action performed:
Evidence observed:
Result: PASS | PARTIAL | FAIL | UNKNOWN
Correction needed:
Next action:
```

## Hardening stop rules

Stop or downgrade the action if:

```text
operator consent is unclear
privacy impact is unclear
the action cannot be reversed or corrected
it requires hidden collection or unattended control
it becomes medical, legal, financial, emergency, or public authority
it depends on unverified deployment/runtime claims
```

## Convergence rule

A BetterSafe response is not acceptable if it only explains risk and leaves the operator with no practical next step.

The minimum acceptable answer must include:

```text
one bounded readiness action
one evidence receipt
one stop condition
one correction path
```

## Boundary

This protocol authorizes only human-performed readiness work. It does not authorize autonomous device behavior, hidden monitoring, public authority, emergency authority, or broad deployment expansion.
