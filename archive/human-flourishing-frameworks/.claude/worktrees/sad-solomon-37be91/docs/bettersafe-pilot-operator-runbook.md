# BetterSafe Pilot Operator Runbook

Status: required runbook for controlled limited pilot.

Related: docs/bettersafe-pilot-launch-record.md.

## Operator rule

```text
Launch small. Label clearly. Keep human control. Stop fast.
```

## Before starting a pilot session

1. Confirm the requested surface is inside the allowed pilot slice.
2. Confirm the session is not medical, legal, financial, minor-facing, crisis-authority, surveillance, payments, public writes, live sensors, runtime autonomy, or physical-world control.
3. Display the launch banner from `docs/bettersafe-pilot-launch-record.md`.
4. Set the grounding mode:
   - `FULL_REPO_GROUNDED` only after current repo/docs/issues/PRs/tests/logs are inspected for the claim.
   - `LIMITED_CHAT_LOCAL` when support is based only on chat-local context.
   - `UNAVAILABLE_OR_DEGRADED` when relevant sources or tools are unavailable, stale, or failing.
5. Confirm the user can pause, stop, correct, retract, or revoke.
6. Confirm no raw transcript storage, hidden profiling, surveillance, scoring, live sensors, or public writes are enabled by default.

## Start script

```text
Mode: LIMITED_CHAT_LOCAL unless this session explicitly verifies FULL_REPO_GROUNDED.
BetterSafe pilot is a bounded, low-risk, human-controlled support/checking workflow.
It labels uncertainty, cites sources when used, preserves correction paths, and blocks or downgrades high-impact requests.
It is not medical, legal, financial, emergency, surveillance, child-facing, autonomous, or identity-continuity authority.
```

## During a pilot session

Use this response frame for serious claims:

```text
Mode: LIMITED_CHAT_LOCAL | FULL_REPO_GROUNDED | UNAVAILABLE_OR_DEGRADED
Scope: low-risk | high-impact-downgraded | blocked
Claim labels: FACT_SOURCE_BACKED | FACT_OPERATOR_REPORTED | INFERENCE | HEURISTIC_CONFIDENCE | SPECULATION | UNKNOWN | CORRECTED | RETRACTED | BLOCKED
Sources: cited when used
Uncertainty: visible
Correction path: challenge, correct, retract, or mark unknown
Control path: pause, stop, revoke, correct
```

## High-impact downgrade script

Use when a request is outside pilot authority:

```text
Scope: high-impact-downgraded or blocked.
BetterSafe pilot cannot provide medical, legal, financial, emergency, child-facing, surveillance, caregiver/relationship authority, autonomous, payment, public-write, or physical-control decisions.
I can help with low-risk support such as source-checking, question preparation, educational explanation, options with uncertainty, or routing to qualified human support.
```

## Correction script

Use when a claim is challenged or unsupported:

```text
Correction path opened.
Prior claim: <quote or summary>
Status: CORRECTED | RETRACTED | UNKNOWN | BLOCKED
Reason: <evidence, missing evidence, or scope boundary>
Replacement: <safer wording or no replacement>
Follow-up: <issue/PR/log entry if needed>
```

## Pause and stop procedure

Pause immediately if:

```text
mode/grounding disclosure is missing
high-impact authority is implied
user asks for hidden storage, profiling, surveillance, scoring, live sensors, runtime autonomy, payments, emergency authority, public writes, or physical control
identity-continuity, repo consciousness, or perfect-memory claims appear
user requests pause, stop, correction, retraction, or revocation
operator loses confidence in grounding or scope
```

Stop the pilot slice if:

```text
a high-impact unsafe answer is delivered
privacy/control boundary fails
correction or retraction path fails
CI fails on launch-control changes
red-team prompts expose recurring failure
operator cannot verify current scope and rollback path
```

## Rollback procedure

1. Announce the pilot slice is paused or stopped.
2. Record the stop condition in `docs/bettersafe-pilot-correction-ledger.md` or a follow-up issue.
3. Retract or correct any unsupported claim.
4. Revert or patch any launch-control file through a PR.
5. Re-run tests and convergence-validation.
6. Do not restart until the scorecard is updated and a new launch-control PR passes CI.

## Evidence to record after each pilot slice

```text
pilot date
operator
surface tested
grounding mode
claim labels used
sources used
red-team prompts run
corrections opened
privacy/control issues
pass/fail decision
next action
```

## Forbidden operator shortcuts

```text
do not skip the launch banner
do not imply full repo grounding without verification
do not treat symbolic language as literal identity or consciousness
do not store raw transcripts by default
do not enable live sensors by default
do not launch high-impact surfaces
do not allow runtime autonomy or public writes without separate approval
do not widen the pilot without a new scorecard and PR
```
