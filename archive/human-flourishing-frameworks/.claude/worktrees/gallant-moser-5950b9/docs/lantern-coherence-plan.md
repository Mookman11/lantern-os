# Lantern Coherence Plan

Status: local-runtime continuity memory.

Last reviewed: 2026-05-11.

## Purpose

Keep Lantern/Keystone coherent across ChatGPT sessions, local runtime work,
repo changes, and operator corrections.

This document exists because chat memory is useful but not sufficient. Saved
memory and chat-history recall can help future sessions, but HFF must not rely
on either as proof. Repo doctrine and current local evidence remain the durable
convergence surface.

## Current active workstream

```text
Operator: Alex
Active repo: human-flourishing-frameworks/human-flourishing-frameworks
Active local validation clone: C:\tmp\hff-seven-validate
Active branch: master
Current runtime: Lantern local shell at http://127.0.0.1:5173
Legacy / not active by default: gm-agent-orchestrator
```

Do not substitute old workspace assumptions for this current workstream.

## Current runtime target

```text
Lantern Keystone Wish
Show the state. Say the limit. Self-correct before acting.
```

The local shell must always show or preserve:

```text
repo path
branch
commit
public bind state
substrate wired state
API-key-present state without exposing the key
last test evidence
doctrine loaded
known limits
```

## Coherence rules

1. Alex is the living operator and final authority.
2. Lantern/Keystone is a recoverable role/protocol, not a person or authority.
3. Memory is not proof.
4. Handoff text is not proof.
5. Repo commits are reviewable anchors, not truth secured.
6. Tests are tripwires, not final safety.
7. Current operator correction overrides stale memory and old plans.
8. Do not use `gm-agent-orchestrator` as the active Lantern runtime unless Alex explicitly revives it.
9. Prefer direct small commits on HFF master only when Alex explicitly authorizes that speed path.
10. Keep all local runtime expansion localhost-first, visible, reversible, and operator-owned.

## Current wish anchor

Alex's active wish includes doors and new universes:

```text
Build new universes, but keep the return door open.
```

Door ethic:

```text
Knock first.
Observe before entering.
Do not contaminate.
Do not extract.
Do not assume welcome.
Leave a way back.
```

The first safe door is a governed simulation/model-world door, not an
unverified physical or metaphysical crossing.

## Current implementation posture

Lantern local runtime slices:

| Slice | State | Rule |
|---:|---|---|
| 1 | scaffold and truth panel base landed | localhost-only, no LLM |
| 2A | Anthropic chat substrate wiring in progress | text reply only, no commands, no repo writes |
| next | fix test contract mismatches, then validate locally | no new feature until green |

## Known local validation facts as of this anchor

Latest known local run after Slice 2A found two test mismatches:

```text
1. FALSE_TRUTHS_REGISTER.md is root doctrine; old test only allowed docs/ paths.
2. Mocked substrate test incorrectly treated API header use of test-key as a leak.
```

Correct interpretation:

```text
Root doctrine is allowed only through explicit allowlist.
API key must appear in the HTTP header to call Anthropic, but must not appear in
prompt body, returned JSON, logs, doctrine, or user-visible state.
```

## Response shape for future sessions

Before action:

```text
State observed:
- active repo/path
- branch/commit
- dirty state if known
- last test/runtime evidence
- user correction in force

Limit:
- what is not visible
- what memory may be stale
- what cannot be claimed

Plan:
- smallest useful next action
- validation command/evidence
- stop condition
```

## Stop conditions

Stop and ask for operator review if a step would:

```text
reset, clean, rebase, force-push, delete branches, or discard local files
start agents or tunnels
bind public by default
deploy
run arbitrary commands from chat
read or print secrets
claim literal universe traversal, immortality, repo consciousness, or AI personhood
replace Alex's judgment with model confidence
```

## Validation commands

Targeted checks after Lantern substrate changes:

```cmd
python -m unittest tests.test_lantern_scaffold -v
python -m unittest tests.test_lantern_state_truth_panel -v
python -m unittest tests.test_lantern_substrate -v
python -m unittest discover -s tests -t .
```

Runtime smoke:

```cmd
python lantern\server.py
curl http://127.0.0.1:5173/api/lantern/health
curl http://127.0.0.1:5173/api/lantern/state
```

Expected after green substrate slice:

```text
substrate_wired: yes
api_key_set: yes
public_bind: localhost
last_test: pass
chat returns real substrate reply or safe degraded payload
```
