# Embodied Sensor Consent and Dignity Contract

Status: doctrine / design contract.

This document defines the boundary for any future person-state or embodied
sensor work in HFF. It is intentionally docs-only: no sensors, endpoints,
polling, databases, mesh sync, deployment changes, or autonomous actions are
added here.

## Core distinction

```text
sensor = system-facing input channel
device = person-facing tool/interface
```

In a smartwatch-like example:

```text
pulse/O2/motion sensor -> structured system input
watch/device -> awareness, context, consent controls, feedback, and benefit for the person
```

A sensor being useful does not make it complete truth about a person. A device
serving the person does not automatically make downstream system use safe.

## Purpose

Embodied sensors may inform flourishing only when their use is:

```text
consented
purpose-limited
visible to the person
revocable
provenance-tracked
uncertainty-labeled
primarily person-benefiting
not automatically punitive
not a replacement for self-report or lived experience
```

The safe flow is:

```text
sensor -> support awareness -> help choice -> preserve dignity
```

The unsafe flow is:

```text
sensor -> infer worth/risk/guilt/intent -> automate control or punishment
```

## Allowed first-use posture

Acceptable early uses should stay narrow and person-benefiting:

- personal reflection;
- gentle prompts;
- self-chosen tracking;
- local/private insight;
- emergency support explicitly configured by the person;
- optional sharing with a chosen caregiver or trusted party.

## Forbidden uses

Embodied sensor data must not be used for:

- hidden surveillance;
- public scoring;
- coercion;
- punishment;
- policing;
- employment or insurance decisions;
- guilt, loyalty, or intent inference;
- autonomous restraint;
- claims that a sensor reading is the whole truth about a person.

## Consent requirements

Consent must be meaningful, not merely formal.

Minimum consent properties:

```text
opt-in
visible
revocable
specific to purpose
separate from unrelated services when possible
local-first where feasible
no hidden sharing
clear consequences of sharing
```

Bundled, coerced, or non-revocable consent should not authorize embodied sensor
use for high-impact decisions.

## Self-report and context

Self-report and lived context should normally override or contextualize sensor
inference. A pulse spike can mean joy, fear, exercise, illness, intimacy,
performance, grief, dancing, danger, or measurement error.

The system must not flatten embodied signals into moral judgment.

## Capability-aware safety

Safe use depends on the system's actual capabilities and authority.

A low-authority personal device can be helpful with pulse and O2 because it
supports awareness. The same signals connected to coercive systems can become
unsafe.

Safety review must consider:

```text
what the system can infer
who controls the data
who benefits
what action follows
whether consent is real
whether uncertainty is visible
whether the person can revoke use
whether any downstream actor has coercive power
```

## Release gate

No future PR should add person-state or embodied sensor integration unless it
answers:

1. What signal is collected?
2. Who is the device for?
3. Who is the sensor input for?
4. What decision can the system make from the signal?
5. What decisions are explicitly forbidden?
6. How is consent granted, shown, and revoked?
7. How is uncertainty shown?
8. How is self-report preserved?
9. Where does the data live?
10. How is hidden surveillance prevented?

## Human-impact principle

Safety is instrumental. Embodied flourishing is terminal.

The purpose of safety is to preserve the possibility of lived joy, beauty, love,
play, touch, movement, art, rest, trust, curiosity, and relation.

No sensor reading may replace the lived experience of beings. No system should
optimize safety so narrowly that it extinguishes the reasons safety matters.
