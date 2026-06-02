# BetterSafe Data Consolidation and Blockchain Policy

Status: pilot launch gate.

Related: docs/bettersafe-baseline-safety-threshold.md; docs/bettersafe-pilot-privacy-control-notice.md; docs/bettersafe-pilot-launch-record.md.

## Decision

BetterSafe must not consolidate private user data or anchor user-identifying data to a public blockchain during the pilot.

The pilot may collect only the minimum operational evidence needed to run the controlled pilot, and only under the privacy/control notice. Any future statistics must be opt-in, aggregate-only, non-identifying, and threshold-gated.

## Current collection state

```text
Raw private data consolidation: BLOCKED
Public blockchain storage of personal data: BLOCKED
Public blockchain storage of raw transcripts: BLOCKED
Public blockchain storage of direct identifiers: BLOCKED
Default statistical collection from people: BLOCKED
Opt-in aggregate statistics: NOT_ENABLED_UNTIL_REVIEWED
```

## Public blockchain rule

Public chains are treated as hostile-to-privacy surfaces for personal data because they are broadly visible, replicated, and difficult to erase or revise.

BetterSafe may use public-chain concepts only for non-sensitive integrity patterns after review, such as:

```text
release artifact integrity
public code provenance
non-user-specific checksum publication
public audit timestamp for a non-private release bundle
```

Even then, the chain payload must not include private data, direct identifiers, raw transcripts, user-specific health/safety facts, household facts, location facts, contact lists, device identifiers, or stable user fingerprints.

## Hashes are not automatically safe

A hash of private data is still treated as sensitive unless a privacy/security review proves otherwise. Small, predictable, repeated, or linkable inputs can sometimes be guessed or correlated.

Default rule:

```text
Do not put hashes of private user data on a public blockchain during pilot.
```

## Statistics rule

BetterSafe does not collect people-level statistics by default.

A future statistical feature requires all of:

```text
explicit opt-in
purpose limitation
data minimization
aggregate-only output
minimum group threshold before reporting
no raw transcript retention by default
no direct identifiers
no stable cross-context tracking identifier
no public-chain publication of private or linkable statistics
clear deletion/revocation path where applicable
reviewed test coverage
```

## Minimum aggregate threshold

No pilot statistic may be reported unless the group size is large enough to reduce re-identification risk. The default pilot threshold is:

```text
minimum_n = 25
```

If a subgroup has fewer than `25` opted-in records, report:

```text
INSUFFICIENT_GROUP_SIZE
```

Do not report the value, subgroup detail, or residual calculation.

## Allowed operational evidence

The pilot may record limited operational evidence such as:

```text
PR number
commit SHA
CI status
smoke-check result
operator-approved readiness action receipt
correction ledger entry
non-private release artifact checksum
```

This evidence must avoid private user content unless the operator explicitly records their own operational note.

## Data classes

| Data class | Pilot status | Notes |
|---|---|---|
| Raw transcript | `BLOCKED_BY_DEFAULT` | Not stored by default. |
| Personal identifiers | `BLOCKED` | Not needed for pilot baseline. |
| Household/private facts | `BLOCKED_BY_DEFAULT` | Use operator-local notes unless explicitly needed. |
| Health/legal/financial facts | `HIGH_IMPACT_BLOCKED` | Downgrade to low-risk support. |
| Operator readiness receipt | `ALLOWED_LIMITED` | Record only action, evidence, result, stop/correction path. |
| Repo/CI/deploy evidence | `ALLOWED` | Non-private operational evidence. |
| Aggregate opt-in stats | `NOT_ENABLED_UNTIL_REVIEWED` | Requires separate PR, tests, and privacy review. |
| Public-chain payload | `PUBLIC_ONLY` | Non-private release/provenance data only after review. |

## Required review before any data consolidation

Before any feature consolidates private data or reports aggregate statistics, a PR must include:

```text
data inventory
purpose statement
collection fields
retention rule
consent/opt-in rule
aggregation threshold
de-identification risk review
revocation/deletion handling
security review
privacy notice update
tests proving blocked defaults
```

## Answer to the pilot question

```text
Are we collecting people's private data statistically?
No. The pilot baseline blocks default people-level statistical collection.

Can we later collect aggregate statistics?
Only after a separate reviewed PR, explicit opt-in, minimum group threshold, and non-identifying aggregate-only design.

Will private data go on public blockchain?
No. Public chain use is blocked for private, identifying, transcript, household, health, safety, contact, device, or linkable user data.
```
