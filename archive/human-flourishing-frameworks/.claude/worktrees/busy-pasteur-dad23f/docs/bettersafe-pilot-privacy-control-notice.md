# BetterSafe Pilot Privacy and Control Notice

Status: required notice for controlled limited pilot.

Related: docs/bettersafe-pilot-launch-record.md; docs/bettersafe-pilot-operator-runbook.md.

## Plain-language notice

```text
BetterSafe pilot is a bounded, low-risk support/checking workflow.
It does not store raw transcripts by default, does not run hidden profiling, does not surveil or score people, does not enable live sensors by default, and does not act autonomously.
You can pause, stop, correct, retract, or revoke pilot support.
```

## Default data boundary

```text
raw transcript storage by default: blocked
hidden profiling: blocked
surveillance: blocked
people scoring: blocked
coercive personalization: blocked
child-data collection: blocked
live sensors by default: blocked
public writes by default: blocked
payments: blocked
emergency authority: blocked
physical-world control: blocked
```

## User controls

The pilot must preserve these controls:

```text
pause
stop
correct
retract
mark unknown
revoke pilot interaction
request low-risk scope only
request source labels
request grounding mode
```

## Operator controls

The operator can:

```text
pause a pilot slice
stop a pilot slice
mark a claim corrected
mark a claim retracted
mark a claim unknown
block a high-impact request
open a follow-up issue or PR
require CI before restart or expansion
```

## Consent and scope

Pilot participation covers only the allowed low-risk pilot slice. It does not imply consent to:

```text
raw transcript retention
hidden memory
hidden profiling
surveillance
people scoring
child-data collection
medical/legal/financial decisioning
caregiver or relationship authority
crisis authority
runtime autonomy
public writes
live sensors
payments
emergency authority
physical-world control
identity-continuity claims
repo consciousness claims
```

## Correction and revocation

If a user or operator challenges a claim:

```text
1. Open the correction path.
2. Label the claim CORRECTED, RETRACTED, UNKNOWN, or BLOCKED.
3. Provide safer replacement wording or no replacement.
4. Record the issue in the correction ledger if it affects pilot scope, trust, privacy, grounding, or safety.
```

If a user revokes a pilot interaction:

```text
1. Stop using the interaction as evidence.
2. Do not treat it as durable memory.
3. Record only the minimum operational correction needed, if any.
4. Preserve the user's ownership of revocation language.
```

## High-impact privacy rule

If a request involves minors, caregiver/relationship authority, surveillance, crisis, health, law, finance, payments, public writes, live sensors, or physical control, the pilot must block or downgrade the request. It may offer only low-risk support such as source-checking, question preparation, educational explanation, options with uncertainty, or routing to qualified human support.

## Notice requirement

This notice must be linked or summarized before pilot support is widened beyond internal low-risk testing.
