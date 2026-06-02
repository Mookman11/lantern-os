# Assumption Stress: Out-of-Range Convergence Values

Status: docs/data-contract policy. Implements issue #140.

Last reviewed: 2026-05-11.

## Purpose

Document the convergence anchor that confidence/risk validation must be
tested with values **outside** the expected range, not only inside it.
Out-of-range inputs expose hidden assumptions, brittle validators,
silent clipping, and false absolutes. Final user-facing confidence
displays still use percentages and bounded ranges; this doctrine is
about validation surface, not display.

## Core correction

```text
Do not only test the normal range.
Test outside the range to discover what the model actually assumes.
```

This is not a claim that confidence should literally be less than 0% or
greater than 100% in final user-facing output. It is a robustness method.

## Test classes

| Input class | Example | Required system behavior |
|---|---|---|
| below range | `-1`, `-20`, `-999` | reject via `Sensor.validate()` or clamp with explicit warning |
| above range | `1.5`, `99`, `999` | reject via `Sensor.validate()` or clamp with explicit warning |
| boundary exact | `0.0`, `1.0` | accept but require evidence for absolute-style use |
| near boundary | `0.01`, `0.99` | accept; do not treat as absolute |
| non-number | `"unknown"`, `"symbolic"`, `"high"` | classify evidence class; do not coerce silently into numeric uncertainty |
| missing value | blank/null | mark unknown or stale; do not invent |
| conflicting values | `confidence=0.95` with `evidence=[]` | lower reliance or require evidence note |
| `NaN` / `inf` | float `nan`, float `inf` | reject; do not allow into the belief ledger |

## Convergence rule

```text
Confidence display may stay 0-100%.
Assumption tests should go outside 0-100 to validate the boundary.
```

## Anti-patterns to catch

```text
silently clipping impossible values
allowing impossible values into release gates
mistaking test values for real confidence
using 0 or 100 as casual language
turning confidence into authority
ignoring evidence mismatch
treating NaN/inf as a valid uncertainty
combining inputs whose ranges have not been validated
```

## Acceptance criteria

- Tests exist for confidence/uncertainty values outside the normal range.
- `Sensor.validate()` rejects `uncertainty` outside `[0.0, 1.0]`.
- `Sensor.validate()` rejects `confidence_interval` where `lo > hi`.
- `Sensor.uncertainty_of()` keeps its output clamped to `[0.0, 1.0]` even
  when penalties from confounders/missing/sample_size would push above 1.
- If a value is clamped at display, the system says it was clamped.
- If a value is rejected, the error is explicit.
- Final user-facing confidence tables continue to use percentages.
- Confidence remains evidence-weighted, not rule-justified.

## Validation phrase

```text
Convergence improves when the system tests the impossible edges:
values outside the expected range reveal hidden assumptions,
while final confidence remains evidence-bound and human-readable.
```

## Non-goals

This document does not authorize:

```text
displaying confidence values outside 0-100% to users
disabling validation
allowing NaN/inf in production payloads
allowing silent coercion of non-numeric inputs
weakening the existing Sensor.validate() rejection rules
```

## Issue and PR cross-reference

Implements: #140
Relates to: #92 (self-correction), #78 (lockstep confidence)
