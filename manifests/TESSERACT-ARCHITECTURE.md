# Tesseract Architecture — Lantern OS Convergence Format

**Date:** 2026-06-03
**Status:** Active
**Purpose:** Structure Lantern OS as a 4-dimensional hypercube where all factors converge. Slower on the outside (human-facing), faster on the inside (computation). MCP sits at the Interface layer.

---

## The Four Layers

```
        ┌─────────────────────────────────────────────┐
        │  Layer 0 — SURFACE                          │  ← Slow, deliberate, RP
        │  Dream Journal web UI, auto-greet,          │     human pacing, art
        │  persona switching, conversation memory       │     200-800ms per beat
        ├─────────────────────────────────────────────┤
        │  Layer 1 — INTERFACE                        │  ← MCP bridges, slot
        │  Agent slots, health checks, provider         │     bindings, external
        │  routing, inspector reports, dispatch       │     API calls, 50-200ms
        ├─────────────────────────────────────────────┤
        │  Layer 2 — CONVERGENCE                      │  ← Memory merge, CSF
        │  Dollhouse CSF segments, RAG ingestion,       │     compression, batch
        │  check-in consolidation, flat-RAG build       │     jobs, 10-100ms
        ├─────────────────────────────────────────────┤
        │  Layer 3 — CORE                             │  ← Fast inference,
        │  Unified connector streaming, Qutrit          │     token generation,
        │  addressing, symbolic dictionary,           │     sparse matrix ops
        │  Bayesian update kernels                      │     <10ms per token
        └─────────────────────────────────────────────┘
```

## Rule: Slower Outside, Faster Inside

| Layer | Target Latency | Failure Mode | Recovery |
|-------|----------------|--------------|----------|
| Surface | 200-800ms | Degrade gracefully to offline persona | Never crash the RP |
| Interface | 50-200ms | Hold slot, queue for retry | Fallback chain |
| Convergence | 10-100ms | Skip merge, log delta | Background retry |
| Core | <10ms/token | Yield to next provider | Immediate failover |

## Convergence Path

All work enters at **Surface**, descends through **Interface** and **Convergence**, executes at **Core**, then results bubble back up through the same layers with context enriched at each step.

```
User Message
     ↓
[Surface] — persona select, recent dreams load, greeting inject
     ↓
[Interface] — MCP bridge, slot claim, provider health check
     ↓
[Convergence] — memory context merge, CSF segment query, RAG pull
     ↓
[Core] — stream inference, token generation, Bayesian kernel
     ↓
[Convergence] — log to dollhouse, update CSF index, check-in mark
     ↓
[Interface] — slot release, health update, inspector note
     ↓
[Surface] — render token, typewriter effect, agent badge, suggestions
     ↓
User Sees Reply
```

## MCP Position

MCP (Model Context Protocol) lives at the **Interface layer**. It bridges the human-paced Surface to the fast Core without letting external tool calls block the dreamer's experience.

- MCP tool calls are async and held
- Surface never waits >5s for MCP
- MCP results feed Convergence layer for next-cycle enrichment

## 4D Axes

| Axis | Surface | Interface | Convergence | Core |
|------|---------|-----------|-------------|------|
| **X: Compute** | Render, animation | HTTP bridges | Batch compression | Token inference |
| **Y: Memory** | Conversation log | Slot health cache | CSF merge, RAG build | Symbolic dictionary |
| **Z: Agency** | Persona RP | Agent dispatch | Check-in manifest | Unified connector |
| **W: Lore** | Door/context hints | Evidence receipts | Dollhouse ingest | Bayesian kernel |

## Tesseract Cell Map

Each cell is a `(Layer, X, Y, Z, W)` intersection. Key cells:

- `(0,0,0,0,0)` — Dream Journal web surface
- `(1,0,0,0,0)` — MCP bridge to external tools
- `(2,0,0,0,0)` — Flat RAG house builder
- `(3,0,0,0,0)` — Raw inference stream
- `(1,0,1,0,0)` — Agent slot health cache
- `(2,0,1,0,0)` — Dollhouse memory consolidation
- `(3,0,1,0,0)` — Symbolic dictionary lookup
- `(0,0,0,1,0)` — Persona greeting engine
- `(1,0,0,1,0)` — Agent dispatch queue
- `(2,0,0,1,0)` — Check-in manifest executor
- `(3,0,0,1,0)` — Unified connector provider ranker
- `(0,0,0,0,1)` — Return Door context hints
- `(1,0,0,0,1)` — Evidence receipt logging
- `(2,0,0,0,1)` — Lore convergence (CSF + RAG)
- `(3,0,0,0,1)` — Bayesian belief update

## Implementation Files

| File | Layer | Role |
|------|-------|------|
| `apps/lantern-garage/public/dream-chat.html` | Surface | Human-facing RP surface |
| `apps/lantern-garage/server.js` | Surface + Interface | Routes, greet, stream, MCP hooks |
| `src/unified_agent_connector.py` | Interface + Core | Multi-provider streaming, health |
| `src/cadd_dollhouse_csf.py` | Convergence | CSF segment builder, manifest |
| `scripts/agent_inspector.py` | Interface + Convergence | Health checks, check-in slots |
| `skills/dream_journal/dream_agent.py` | Surface + Core | Persona mirror, local memory |
| `config/agent-slots.json` | Interface | Slot registry |
| `config/agent-profiles.json` | Interface | Provider profiles |
| `data/dollhouse/csf/manifest.json` | Convergence | Master convergence manifest |
| `data/dollhouse/agent-checkin-manifest.json` | Convergence | Periodic check-in schedule |

## Convergence Command

Run from repo root:

```powershell
# Full tesseract check (all layers)
python scripts/agent_inspector.py --once --report data/agent-fleet/tesseract-latest.json

# Layer 2 convergence (dollhouse CSF)
python src/cadd_dollhouse_csf.py --ingest data/dollhouse --output data/dollhouse/csf

# Layer 3 core health
python src/unified_agent_connector.py --action health

# Layer 1 interface inspect
python src/unified_agent_connector.py --action inspect
```

## Slower Outside, Faster Inside — In Practice

1. **Surface never rushes the human.** Typewriter effects, gentle pacing, RP continuity.
2. **Interface never blocks the surface.** Async MCP, held actions, fallback chains.
3. **Convergence never blocks the interface.** Background CSF merge, batched RAG updates.
4. **Core never wastes a cycle.** Stream tokens immediately, fail over in <10ms.

---
*End of Tesseract Architecture*
