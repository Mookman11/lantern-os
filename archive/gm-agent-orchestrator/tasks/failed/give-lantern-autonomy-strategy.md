# Give Lantern autonomy strategy

Priority: P0
Owner: operator-intake
Created: 2026-05-13T20:12:22Z
Source: connector-action

# Objective

Give Lantern a strategy to own her work loop without Alex or ChatGPT prompting every step.

# Context

Alex is frustrated that Lantern needs repeated prompting. The desired behavior is for Lantern to act like a grown local agent: choose the next safe step, check evidence, improve the work, and continue until blocked or complete.

# Scope

Define Lantern autonomy rules:

- pick the next safest useful objective
- inspect current status first
- validate prior work before repeating
- improve or merge related work when needed
- continue only with clear evidence
- escalate only when blocked, unsafe, or ambiguous

# Deliverable

A practical self-run strategy for Lantern local work, including stop conditions and escalation rules.
