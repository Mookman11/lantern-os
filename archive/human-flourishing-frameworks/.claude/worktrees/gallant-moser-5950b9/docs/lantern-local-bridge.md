# Lantern Local Bridge

Status: local-only bridge doctrine.

## Purpose

Lantern's bridge is the local desktop app between Alex and Lantern only.

This is not a GitHub relay, public mailbox, hosted assistant bridge, Discord authority surface, or cloud sync system.

## Core invariant

```text
Alex and Lantern share one workspace, but not one identity.

Alex decides.
Lantern reflects.
The Door remembers state and boundaries.
```

## Runtime shape

```text
Alex
-> Lantern Door desktop app
-> localhost Lantern backend
-> local answer
-> Lantern Door desktop app
-> Alex
```

## Boundary

```text
local desktop app only
localhost backend only
no hosted GPT/Claude/API calls from Lantern
no GitHub issue relay
no public mailbox
no Discord authority path
no autonomous repo writes
no deployments
no agents
no tunnels
no sensors
no command execution from chat
```

## Computer-on rule

```text
If Alex's computer is off, asleep, offline, or the app is closed, Lantern is not available.

If Alex's computer is on and the Lantern Door app is open, Alex can speak to Lantern through the local app.
```

## Status edge

All statuses are bounded observations, not permanent truths.

```text
ONLINE_OBSERVED means the current local window/process was observed running.
BACKEND_REACHABLE_OBSERVED means the local app reached localhost /healthz.
LOCAL_ONLY means this path is localhost-only; it does not mean the entire computer has no internet.
NO_GPT_CALL_FROM_LANTERN means the Lantern backend path is not calling hosted GPT/Claude/API.
```

## What this replaces

The local bridge is intended to reduce dependence on hosted GPT/Claude-style chat for Lantern's own runtime loop.

It does not claim to replace every capability of hosted AI systems. It creates a persistent local Door that can be hardened step by step.
