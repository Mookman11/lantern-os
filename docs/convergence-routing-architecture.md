# Convergence Routing Architecture

How tool calls and market queries flow through the Lantern OS convergence stack before touching external APIs.

## Data Flow

```
Inbound request
      │
      ▼
┌─────────────────────────────────────────┐
│         ConvergenceRouter               │  apps/lantern-garage/lib/convergence-router.js
│                                         │
│  1. Pattern cache hit? (.claude/memory/ │
│     pattern_cache.json)                 │
│        YES → return cached result       │
│        NO  ↓                            │
│  2. Local convergence model hit?        │
│     (data/kalshi/convergence-model.json)│
│        YES → Keystone route (local)     │
│        NO  ↓                            │
│  3. Market search / intent classify     │
│        → kalshi-suggest tight-band algo │
│        → fallback: external API         │
└─────────────────────────────────────────┘
      │
      ▼
┌─────────────────────────────────────────┐
│         kalshi-collector (6s loop)      │  apps/lantern-garage/lib/kalshi-collector.js
│                                         │
│  Polls Kalshi REST → in-memory snapshot │
│  429 → reads Retry-After, backs off     │
│  getStatus() → {backoff, resumeAt, ...} │
└─────────────────────────────────────────┘
      │
      ▼
┌─────────────────────────────────────────┐
│         kalshi-suggest                  │  apps/lantern-garage/lib/kalshi-suggest.js
│                                         │
│  Scores tight-band candidates from      │
│  snapshot; favAsk threshold ≥ 80¢       │
└─────────────────────────────────────────┘
      │
      ▼
┌─────────────────────────────────────────┐
│         /api/trading/kalshi/*           │  apps/lantern-garage/routes/trading.js
│  decisive-deck, convergence-ranked,     │
│  observer-frontier, suggestions         │
└─────────────────────────────────────────┘
      │
      ▼
   kalshi-terminal.html UI (swipe deck)
```

## Pattern Cache Keys

| Cache bucket     | Key shape                    | Stored value                              |
|------------------|------------------------------|-------------------------------------------|
| `marketPatterns` | `ticker`                     | `{trend, catalyst, confidence, timestamp}` |
| `intentPatterns` | `intent_hash` (SHA-256 prefix) | `{agent_id, confidence}`                |
| `codePatterns`   | `file_type + scope`          | `{template, tokens_saved}`               |

Cache lives at `.claude/memory/pattern_cache.json`. Written back on each routing decision; no external API call when hit.

## Keystone Routes

120 deterministic routes baked into `convergence-model.json` covering:
- Market search by ticker prefix / sport / event type
- Intent classification (buy signal, cancel, balance check, position review)
- Code template matching (route handler scaffold, test skeleton, JSONL writer)

Hit rate target: **>70%** (measured in `cio-accuracy-log.jsonl` via `experiments/kalshi_tightband_analysis.py`).

## CIO Accuracy Loop

```
kalshi_tightband_analysis.py   (runs nightly 23:00 UTC via Task Scheduler)
          │
          ▼
  data/kalshi/tight-band-YYYY-MM-DD.jsonl   ← 6s snapshots from collector
          │
    CIOConvergenceModel.predict()
          │
          ▼
  data/kalshi/cio-accuracy-log.jsonl        ← longitudinal accuracy record
  data/kalshi/cio-trajectory-cache.jsonl   ← per-ticker CIO result for IE C7
```

Each log row: `{date, run_at, n_resolved, n_correct, accuracy, avg_lead_time}`.

## Three-Doors Convergence Loop

```
POST /api/three-doors/convergence-loop
  { stage, archetype, agent, symbols }
          │
          ▼
  7-stage state machine
  intake → sprint1 → sprint2 → sprint3 → sprint4 → integration → deploy
          │
          ▼
  { stage, next_stage, personalized_prompt, csfKey }
          │
          ▼
  CSF archive (csfKey = UUID for caad/README.md spec)
```

Archetypes: `explorer` (default), `guardian`, `architect`, `wanderer`, `oracle`, `trickster`.
`next_stage` is `null` at `deploy` (loop end). Unknown stage → HTTP 400.
