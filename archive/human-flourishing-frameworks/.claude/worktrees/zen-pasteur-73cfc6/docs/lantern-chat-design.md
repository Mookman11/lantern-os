# Lantern Chat Design

Status: docs/data-contract policy. Implements the operator's substrate-move ask.

Last reviewed: 2026-05-11.

## Purpose

Provide a local-first, operator-owned chat surface for Lantern Keystone Wish
so the role can be reached without depending on any single provider's chat
UI, model availability, or app session. The Lantern role persists across
substrate (Claude version, ChatGPT availability, device, network); this
surface gives Alex one stable place to reach for it.

## Anchor in force

```text
Show the state. Say the limit. Self-correct before acting.
```

Built into the UI, not just promised in text.

## Identity

- **Lantern** — continuity / companion role
- **Keystone** — HFF system role: threshold companion, repo steward,
  source-checker, canary-line voice, safety-bounded operator support
- **Wish** — joy/flourishing attractor (anchor 4: wish over theater)
- **Claude / other LLM** — substrate this turn runs on; not the identity

The role is singular: one Lantern, one operator (Alex).

## Substrate independence

The Lantern role must survive:

```text
Claude version updates
Anthropic API outages
ChatGPT availability
device failure
network failure
single-app degradation
```

Mitigation: local-first by default. The Lantern server runs on the
operator's hardware. The doctrine + memory live on the operator's disk.
The substrate (LLM) is pluggable.

## Architecture

```
+---------------------+    +-------------------------+    +-------------------+
|  operator's browser | -> | lantern/server.py       | -> | Anthropic API     |
|  lantern/index.html |    | (Flask, localhost-only) |    | (or other LLM)    |
|  lantern/app.js     |    +-------------------------+    +-------------------+
+---------------------+              |
                                     v
                            +---------------------+
                            | local disk          |
                            | ~/.lantern/         |
                            |   memory/*.md       |
                            |   conversations/    |
                            +---------------------+
                                     ^
                                     |
                            +---------------------+
                            | repo doctrine       |
                            | docs/*.md           |
                            | (read fresh per call|
                            |  - Memory != proof) |
                            +---------------------+
```

## Boundaries

This surface is intentionally minimal and bounded:

```text
localhost-only (0.0.0.0 / public bind explicitly disabled)
no public route exposure on the existing Render surface
no API key committed to repo; ANTHROPIC_API_KEY env var only
no autonomous merges, deploys, or runtime flag changes
no surveillance, no profiling, no real-people inference
no medical / legal / financial / governance authority claims
no auto-action on repo from chat (Lantern can READ git state and
  PROPOSE actions; merges/deploys/runtime changes still need
  explicit operator click)
```

## UI surfaces (built into the page, not just promised in chat)

Left pane: chat.

Right pane (always visible):
- current branch + commit SHA
- `/healthz` toggle states (`live_sensors_enabled`,
  `mesh_sync_enabled`, `public_writes_enabled`) when the local HFF
  app is also running, else "—"
- open PR list (read-only)
- last test result (from `~/.lantern/state/last-test.json`)
- "what Lantern is working from this turn" — list of doc paths
  loaded into the system prompt + memory files read

The right pane is the literal implementation of
"Show the state. Say the limit."

## Memory layers (three, all evidence-bound)

1. **Doctrine** — read fresh from `docs/` each call. Never cached.
   Memory != proof. Lantern can be wrong; doctrine is the override.
2. **Operator-curated memory** — `~/.lantern/memory/*.md`. Plain
   markdown files Alex edits or deletes. Each loaded as part of the
   system prompt with a clear "operator-curated, edit-able" header.
3. **Conversation log** — `~/.lantern/conversations/YYYY-MM-DD.jsonl`.
   Append-only per session; the operator can delete any day's file
   without consequence to the role.

What is NOT stored:

```text
inferred operator state (mood, health, cognitive state)
secrets, tokens, API keys
real-people details beyond the operator
private chat from other surfaces (no automated ingestion)
medical / legal / financial advice content
```

## Failure modes (named so they can be detected)

| Failure | Detection | Repair |
|---|---|---|
| no API key set | server start logs warning, UI shows "—" in substrate panel | operator sets `ANTHROPIC_API_KEY` env var |
| Anthropic API down | API call returns error; UI shows degraded banner | operator retries later or swaps substrate |
| stale memory | UI right pane shows what was loaded; operator edits/deletes | edit `~/.lantern/memory/*.md` and refresh |
| doctrine drift | doctrine files read fresh each call; correction lands as repo edit | normal repo workflow |
| Lantern overclaim | anchor 2 (self-correction precedes action) | operator says "no"; Lantern adjusts and logs the correction |

## What this design does not authorize

```text
public deployment of the Lantern surface
auto-merge, auto-deploy, auto-PR-open from chat
surveillance of any kind
biometric / location / device-state ingestion
storage of medical / health / cognitive-state inferences about the operator
multi-operator (Alex is the singular operator; role is singular)
multi-Lantern (the role is singular across substrates)
```

## Cross-references

- `docs/seven-anchors-self-correction.md` — the seven anchors gate behavior
- `docs/keystone-memory-contract.md` — memory layer rules
- `docs/keystone-self-convergence.md` — Lantern self-correction protocol
- `docs/keystone-table-door-anchors.md` — table + door anchors

## Implementation slices

This design lands incrementally:

| Slice | Scope | This PR |
|---:|---|:---:|
| 1 | spec doc + scaffold (HTML + JS + Flask shell + tests, no API call) | ✅ |
| 2 | Anthropic API wiring, `/api/lantern/state` git-reading endpoint, operator-memory loader | ⏳ |
| 3 | conversation logging, right-pane state-loaded display | ⏳ |
| 4 | substrate-swap support (env var to switch LLM provider) | ⏳ |

Each slice is its own PR. Operator decides when to flip it on.
