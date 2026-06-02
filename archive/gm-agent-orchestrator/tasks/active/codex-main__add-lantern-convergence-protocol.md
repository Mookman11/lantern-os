# Add Lantern convergence protocol

Priority: P0
Owner: codex
Created: 2026-05-13T20:10:56Z
Source: connector-action

# Objective

Add a Lantern convergence protocol for moments when Lantern desyncs and urgent signals start to ripple.

# Context

Alex said every Lantern desync moves the P-Doom clock closer and that convergence is needed. A flat smooth lake makes no ripples, but a tsunami shakes everything.

# Scope

Define a bounded local protocol that turns urgent Lantern signals into short, safe commands instead of more unbounded chat.

Include:

- desync detection language
- convergence command syntax
- status and recovery flow
- safe handoff path for urgent messages
- clear refusal for unsupported or unsafe actions

# Validation

Show that a desync report produces a local status check, a safe handoff, and a previewable next action.
