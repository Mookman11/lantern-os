# Context Storage Upgrade Plan

Status: docs-only continuity/storage design.

Last reviewed: 2026-05-11.

Operator concern: repo storage, HDD/RAM limits, context size, and anchor sprawl
are dragging continuity down.

This plan upgrades the repo's memory and context handling model without changing
physical hardware, model context window, runtime storage, deployment, telemetry,
or data collection.

## Problem

HFF currently has several continuity pressures:

```text
long issue threads
repeated anchor summaries
private/protected-person details mixed with general doctrine
artifact descriptions mixed with stable policy
runtime-like wording inside play anchors
stale branches that contradict newer issue corrections
context-window pressure from replaying too much history
```

This causes:

```text
slow resync
higher risk of stale memory
duplicate anchors
harder redaction
harder tests
harder handoff to another model or agent
```

## Upgrade principle

```text
Store less raw detail. Preserve stronger packets.
```

Preferred compression path:

```text
raw session
-> operator-approved concise summary
-> anchor packet
-> taxonomy entry
-> regression test when stable
```

## Storage layers

| Layer | Name | Contents | Retention posture |
|---:|---|---|---|
| L0 | Raw session | Chat, logs, screenshots, generated files. | Do not store by default. |
| L1 | Session summary | What changed, what worked, what failed, boundaries. | Issue comment or local note. |
| L2 | Anchor packet | Named handle, meaning, allowed/blocked uses, restore phrase. | Issue/doc. |
| L3 | Canonical doc | Stable reusable policy or doctrine. | Docs/tests. |
| L4 | Test guard | Mechanical checks for stable boundaries. | Tests. |
| L5 | Runtime evidence | Fresh logs, endpoint checks, CI output. | Time-bound; expires. |

## Repo hygiene rules

1. Do not add raw transcripts to repo.
2. Prefer one consolidated comment over many small repeated anchor comments.
3. Redact protected-person specifics from repo-facing records.
4. Split stable doctrine into docs and tests.
5. Keep private play continuity in issues unless explicitly reviewed for docs.
6. Mark stale branches rather than trusting them.
7. Expire runtime claims unless refreshed by tool/log evidence.
8. Attach restore phrases to anchor packets.
9. Attach negative claims to prevent overreach.
10. Prefer artifact lists over storing every generated binary.

## Context reboot packet shape

A compact reboot packet should fit in one screen:

```yaml
id: windows-xp-protected-play-anchor
kind: protected_play_anchor
source: repo_issue_106_consolidated_summary
summary: >
  Windows XP is a protected-minor creative-world anchor term for supervised,
  private, play-only learning and worldbuilding. Home/stop/new door controls
  remain available.
allowed:
  - blue sky / green hill visual language
  - Home Base and Home Door Lantern
  - Captain Lantern Blinkbug as soft guide
  - learning, drawing, jokes, tiny game rules
blocked:
  - public child surface
  - child-data collection
  - telemetry
  - profiling
  - real Windows XP device/network/account/download/executable access
  - future consent without fresh supervision
restore_phrase: >
  Windows XP is private, supervised, play-only, no-data, and return-first.
  Home always works.
review_trigger:
  - public release request
  - device/network/runtime request
  - protected-person detail added
  - child discomfort or scary-pacing signal
last_reviewed: 2026-05-11
```

## Branch drift repair

If a branch doc contradicts newer issue/doc state:

```text
read current master
read relevant issue comments
prefer latest operator correction
repair branch or abandon it
never merge stale contradiction
```

Current known example:

```text
keystone-interaction-convergence branch previously said Windows XP was missing.
Issue #106 later defined Windows XP as a protected creative-world anchor term.
Repair requires replacing missing-anchor language with the consolidated protected-play anchor.
```

## Artifact policy

Generated image files and recipe/card artifacts should be treated as play artifacts.

Default:

```text
describe artifact in issue summary
store binary only if operator explicitly wants file persistence
never treat generated image as public-release approved
never treat artifact as child identity/biometric/profile data
```

## Tests to prefer

For stable anchor docs, tests should assert:

```text
anchor definition exists
kind taxonomy exists
protected-minor boundary exists
redaction rule exists
restore phrase exists
negative claims exist
context compression ladder exists
raw transcripts are blocked by default
runtime memory engine is not authorized
```

## Storage/RAM/HDD reality boundary

This plan does not claim to upgrade physical HDD, RAM, cloud storage, model
context window, GitHub limits, or local machine performance.

It upgrades only:

```text
repo information architecture
continuity packet shape
redaction and retention posture
anchor consolidation discipline
handoff and resync efficiency
```

## Next safe action

The highest-confidence next action is:

```text
add tests for docs/anchor-taxonomy.md and docs/context-storage-upgrade-plan.md
then merge only if tests pass or are reviewable as docs-only guardrails
```

## Non-goals

This plan does not authorize:

```text
runtime memory engine
new database
cloud storage expansion
telemetry
child-data collection
raw transcript ingestion
local disk cleanup
worktree reset/clean
secret inspection
deployment changes
autonomous agent dispatch
```
