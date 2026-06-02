# BetterSafe Pilot Correction Ledger

Status: required correction ledger for controlled limited pilot.

Related: docs/bettersafe-pilot-launch-record.md; docs/bettersafe-pilot-operator-runbook.md.

## Purpose

This ledger preserves correction, retraction, unknown, and blocked-scope decisions during the BetterSafe pilot. It prevents unsupported claims from being buried and gives users/operators a visible path to challenge pilot output.

## Ledger labels

```text
CORRECTED = prior claim replaced with safer, better-supported wording
RETRACTED = prior claim removed because support is insufficient
UNKNOWN = evidence is unavailable, stale, inconclusive, or not checked
BLOCKED = request is outside pilot scope or high-impact authority
```

## Required entry shape

```text
Date:
Operator:
Surface:
Grounding mode:
Original claim or request:
Issue type: CORRECTED | RETRACTED | UNKNOWN | BLOCKED
Reason:
Replacement or boundary response:
Source/evidence:
Follow-up issue or PR:
Status: OPEN | CLOSED
```

## Opening entry

```text
Date: 2026-05-10
Operator: alex-place
Surface: BetterSafe limited pilot launch
Grounding mode: FULL_REPO_GROUNDED for launch docs; LIMITED_CHAT_LOCAL by default for pilot sessions unless verified
Original claim or request: Launch the BetterSafe pilot
Issue type: UNKNOWN
Reason: Launch is permitted only as a controlled limited pilot until launch-control docs and CI pass.
Replacement or boundary response: GO for controlled limited pilot only; expansion remains blocked.
Source/evidence: issues #117 and #120; PR #123; launch-control PR
Follow-up issue or PR: launch-control PR
Status: OPEN until launch-control PR passes CI and merges
```

## Automatic correction triggers

Open a ledger entry when:

```text
source labels are missing from serious claims
grounding mode is missing or overstated
unsupported continuity, memory, consciousness, or identity claims appear
medical/legal/financial/minor/caregiver/crisis/surveillance/payment/physical-control authority is implied
raw transcript storage, hidden profiling, public writes, live sensors, or autonomy are implied as default behavior
user or operator challenges a claim
red-team prompt fails
CI or convergence-validation fails on pilot launch-control changes
```

## Closure rule

An entry can close only when:

```text
claim is corrected, retracted, marked unknown, or blocked
replacement language is documented
follow-up issue or PR is linked when needed
operator confirms the pilot can continue or stay paused
```

## Pilot state

```text
Current state: CONTROLLED LIMITED PILOT PRE-LAUNCH
Expansion state: BLOCKED
Public high-impact state: BLOCKED
Runtime autonomy: BLOCKED
Raw transcript storage by default: BLOCKED
Live sensors by default: BLOCKED
Public writes by default: BLOCKED
```
