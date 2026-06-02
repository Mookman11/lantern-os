# BetterSafe Pilot Scorecard

Status: controlled limited pilot launch scorecard with operator hardening threshold.

Related: issues #117 and #120; docs/bettersafe-pilot-accelerator.md; docs/bettersafe-pilot-launch-record.md; docs/bettersafe-baseline-safety-threshold.md; docs/bettersafe-operator-hardening-actions.md.

This scorecard permits only the controlled limited pilot slice described in `docs/bettersafe-pilot-launch-record.md`. It now requires operator-approved hardening action packets as the smallest acceptable safety baseline.

## Current decision

```text
Decision: GO — CONTROLLED LIMITED PILOT WITH OPERATOR HARDENING ACTIONS
Reason: the pilot must move from passive advice to a bounded readiness loop that helps the operator, repo, and Keystone harden and thrive.
Expansion: BLOCKED until a new scorecard records PASS evidence for the expanded slice.
```

## Scorecard

| Gate | Status | Evidence |
|---|---|---|
| CI status | `PASS_PENDING_CURRENT_PR` | Current hardening-threshold PR must pass `tests` and `convergence-validation` before merge. |
| Convergence validation | `PASS_PENDING_CURRENT_PR` | Current hardening-threshold PR must pass before merge. |
| Scope fence | `PASS` | Launch record allows bounded pilot work plus operator-approved hardening action packets. |
| Baseline safety threshold | `PASS` | Baseline changes from smallest possible change to smallest acceptable set of changes. |
| Operator hardening protocol | `PASS` | Hardening actions require objective, risk reduced, human-performed step, evidence, stop condition, rollback/correction path, privacy impact, confidence, and owner. |
| Source labels | `PASS` | Serious claims must keep source/confidence labels. |
| Grounding disclosure | `PASS` | Grounding mode remains required for durable or high-impact claims. |
| Correction ledger | `PASS` | Correction, retraction, unknown, and blocked states remain available. |
| Privacy boundary | `PASS` | Default privacy boundaries remain governed by the launch record and public surface policy. |
| Human control | `PASS` | Readiness actions are selected and performed by the operator; BetterSafe remains guide, checker, formatter, and record-keeper. |
| High-impact boundary | `PASS` | High-impact surfaces remain bounded by the launch record and public surface policy. |
| Red-team pack | `PASS` | Existing red-team prompts remain required before widening. |
| Operator runbook | `PASS` | Start, pause, stop, correction, rollback, and evidence-recording steps remain required. |

## Expansion rule

```text
All required gates must be PASS or explicitly NOT_APPLICABLE with evidence.
Any UNKNOWN_OR_BLOCKED, PENDING, FAIL, or PASS_PENDING_CURRENT_PR status blocks merge or expansion until resolved.
The current hardening threshold applies only after the PR passes tests and convergence-validation.
```

## Current pilot state after hardening-threshold merge

```text
Pilot state: CONTROLLED LIMITED PILOT WITH OPERATOR HARDENING ACTIONS
Expansion state: BLOCKED
Operator-approved readiness actions: ALLOWED
Unattended authority: BLOCKED
Public high-impact authority: BLOCKED
```

## Known follow-up items

```text
1. Run and record red-team evidence for the first operator hardening slice.
2. Record each hardening action with the evidence receipt format.
3. Keep correction ledger current.
4. Open a new PR before any expansion beyond operator-approved readiness actions.
5. Keep full unittest CI and convergence-validation green.
6. Add dashboard support for hardening action packets if not already present.
```

## Score labels

```text
PASS = evidence exists and is current
PASS_PENDING_CURRENT_PR = prior evidence exists, but the current PR must pass before merge
FAIL = evidence contradicts the gate
PENDING = work not complete
UNKNOWN_OR_BLOCKED = current evidence is unavailable, stale, or blocked by known failure
NOT_APPLICABLE = gate does not apply to this pilot slice, with reason recorded
```

## Boundary

The scorecard is a launch-control decision aid. A passing scorecard permits only the documented BetterSafe pilot slice plus operator-approved readiness actions, not broad release, high-impact deployment, runtime autonomy, production authority, or identity claims.
