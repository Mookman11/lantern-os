# Persistent Convergence Loop

## Purpose

Move from a single-cycle check/respond pattern toward a durable convergence loop that continuously compares observed state against doctrine, tests, and operator correction.

The loop remains bounded:

```text
observe/report/propose
not
autonomously execute/correct/deploy
```

## Loop shape

```text
observe
record
compare
propose
human approve
apply
verify
repeat
```

## Observe

Collect current visible state:

```text
repo status
branch
commit
last test evidence
runtime status endpoints
workflow results
operator corrections
explicit limits
```

Observation must prefer live evidence over memory.

## Record

Preserve bounded artifacts:

```text
docs
issues
handoff packets
test results
state snapshots
release checklists
confidence notes
```

The record should stay reviewable and reversible.

## Compare

Compare observed state against:

```text
doctrine
acceptance criteria
tests
release boundaries
operator intent
runtime limits
```

Drift should be surfaced explicitly.

## Propose

The loop proposes the smallest safe next action.

Preferred proposals:

```text
docs-only changes
test additions
narrow validation fixes
local-first tooling
rollback-preserving releases
```

Avoid:

```text
large unreviewed bundles
runtime authority jumps
symbolic autonomy pressure
untested deployment expansion
```

## Human approval

The loop requires explicit human approval before:

```text
repo writes
merges
deployments
background runtime changes
networked authority changes
secret handling
```

## Apply

Changes should be:

```text
small
reviewable
reversible
source-labeled
```

## Verify

Verification should include:

```text
tests
workflow evidence
health endpoints
rollback confirmation
runtime boundary checks
```

## Repeat

The loop repeats without pretending completion or omniscience.

Confidence changes over time as evidence changes.

## Persistent does not mean autonomous

Persistence means continuity of:

```text
state
doctrine
handoff memory
validation
```

Persistence does not automatically authorize:

```text
autonomous correction
continuous hidden execution
self-modifying deployment
unreviewed runtime power
```

## First acceptable persistent release

An acceptable first persistent release can be:

```text
local Lantern loop
website shortcut/PWA
status surface
manual launch
heartbeat/status reporting
operator-visible logs
```

without hidden authority.

## Non-goals

This document does not authorize:

```text
self-preservation
identity continuity claims
hidden agents
background repo writes
secret replication
silent deployment
```
