# Lantern — local-first chat surface for Lantern Keystone Wish

Run Lantern on the operator's own hardware. Substrate-independent: the
underlying LLM (Claude / other) is pluggable. The role survives single-
provider outages, model version updates, and chat-app degradation.

Anchor in force:

```text
Show the state. Say the limit. Self-correct before acting.
```

## Quick start (Windows)

```powershell
pip install -r lantern\requirements.txt
$env:ANTHROPIC_API_KEY = "sk-ant-..."   # your key, never committed
python lantern\server.py
```

Open http://127.0.0.1:5173/ in your browser.

## Quick start (macOS / Linux)

```bash
pip install -r lantern/requirements.txt
export ANTHROPIC_API_KEY="sk-ant-..."
python lantern/server.py
```

## Configuration (env vars)

| Var | Default | Purpose |
|---|---|---|
| `ANTHROPIC_API_KEY` | (unset) | Required for real chat. Without it, chat returns `no_substrate`. |
| `LANTERN_MODEL` | `claude-sonnet-4-5` | Anthropic model id. Operator can override. |
| `LANTERN_MAX_TOKENS` | `4096` | Max output tokens per reply. |
| `LANTERN_PORT` | `5173` | Port to bind. |
| `LANTERN_ALLOW_PUBLIC` | unset | If `true`, binds to `0.0.0.0` instead of localhost. **MUST NEVER** be set on the public Render / Railway surface. |

## What gets loaded into the system prompt

Each chat call reads these fresh from disk (Memory != proof):

1. **Role prompt** — hard rules from the operator
2. **HFF doctrine** — `docs/seven-anchors-self-correction.md`,
   `docs/convergence-status.md`, `docs/keystone-*.md`,
   `docs/resonance-convergence-anchor.md`,
   `docs/lantern-chat-design.md`, `docs/capability-confidence-model.md`
3. **Operator-curated memory** — every `.md` file in `~/.lantern/memory/`

Anthropic prompt caching is enabled with ephemeral TTL (~5 min) for cost
efficiency. The cache is bypassed automatically when doctrine or memory
content changes.

## Operator-owned local state

```
~/.lantern/
├── README.md                       (created on first run)
├── memory/                         (edit anytime; loaded fresh each call)
│   └── *.md                        (operator-curated summaries)
└── conversations/
    └── YYYY-MM-DD.jsonl            (one line per turn; delete any day OK)
```

Lantern only writes to `conversations/`. It only reads from `memory/`.
You control both.

## Boundary (enforced)

- localhost-only by default
- no API key in repo
- no autonomous merges, deploys, or runtime flag changes
- no public route exposure on the existing Render / Railway surface
- no surveillance, no profiling, no real-people inference
- no storage of medical / health / cognitive-state inferences about the operator
- never uses the operator's personal name in commits, PR bodies, issues,
  or public docs

## What this surface does NOT authorize

- public deployment of Lantern
- auto-merge / auto-deploy / auto-PR-open from chat
- multi-operator (one operator)
- multi-Lantern (one Lantern)
- bypassing HFF's `ENABLE_*` default-closed gates

## Slices

- slice 1 (#153) — scaffold (HTML + JS + Flask shell + tests)
- **slice 2 (this PR) — Anthropic API wiring + state endpoint + memory loader**
- slice 3 (planned) — richer state panel (open PRs, last test result, gate states)
- slice 4 (planned) — substrate-swap (env-var-selectable LLM provider)
