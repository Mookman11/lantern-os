# BetterSafe Baseline Safety Threshold

Status: pilot launch threshold.

Related: issues #117 and #120; docs/bettersafe-pilot-launch-record.md; docs/bettersafe-operator-hardening-actions.md.

## Operator correction

The BetterSafe pilot cannot remain only a source-checking or packet-formatting surface. If it cannot help the operator, the repo, and Keystone harden and thrive, it will not credibly help anyone else harden and thrive.

The baseline changes from:

```text
smallest possible change
```

to:

```text
smallest acceptable set of changes
```

## Safety threshold

A BetterSafe pilot slice is acceptable only if it can complete this loop:

```text
risk identified
-> claim/source label assigned
-> practical readiness action selected
-> human operator approves
-> human performs the action
-> evidence is recorded
-> result is checked
-> correction or rollback path remains open
```

## Required baseline capabilities

| Capability | Required? | Meaning |
|---|---:|---|
| Claim audit | Yes | Identify what is being asserted and label the claim. |
| Source check | Yes | Check repo/runtime/operator/external evidence before relying on a claim. |
| Operator hardening action | Yes | Convert an identified risk into a human-performed readiness action. |
| Evidence receipt | Yes | Record what was done, when, by whom, and what evidence supports it. |
| Stop/rollback path | Yes | Pause, correct, retract, undo, or mark unknown when scope/evidence fails. |
| Human control | Yes | Operator chooses and performs readiness actions. |
| High-impact downgrade | Yes | High-impact authority remains out of scope and is downgraded to low-risk support. |

## Operator hardening action definition

```text
Operator hardening action = a practical, reversible, human-performed action that improves readiness without giving BetterSafe autonomous control.
```

Examples:

```text
charge critical devices
verify backup battery or UPS status
save an offline copy of the dashboard link and smoke commands
confirm two ways to access the dashboard
place flashlight, water, first aid, keys, or documents in a known location
check that repo clone and recovery instructions are accessible
verify local worktree path and backup location
prepare a human contact list
record a stop condition and rollback note
```

## Exclusions

The pilot still excludes autonomous control, hidden data collection, public writes without separate approval, and high-impact authority. Those exclusions stay governed by the public surface policy and pilot launch record.

## Minimum acceptable pilot set

The pilot must include all of these before claiming to be useful for hardening:

1. A visible safety threshold.
2. An operator hardening action protocol.
3. A dashboard or runbook path that helps select a human-performed hardening action.
4. A record format for evidence and outcome.
5. A stop/rollback rule.
6. Tests that prevent the threshold from regressing into passive advice only.
7. Tests that preserve human control.

## Confidence table

| Claim | Label | Confidence |
|---|---|---:|
| BetterSafe needs a real-world hardening loop to satisfy the operator intent | FACT_OPERATOR_REPORTED + INFERENCE | 0.94 |
| Human-performed readiness actions can improve operator/repo/Keystone resilience | INFERENCE | 0.86 |
| The baseline should expand from passive planning to operator-approved hardening actions | HEURISTIC_CONFIDENCE | 0.90 |
| BetterSafe is ready for unattended physical-world action | BLOCKED | 0.01 |

## Launch boundary

This threshold permits readiness actions only when:

```text
the action is selected by the human operator
the action is performed by a human
the action is reversible or low-risk
the action records evidence and stop conditions
```

BetterSafe remains a guide and record-keeper for operator-approved readiness, not an autonomous physical-world authority.
