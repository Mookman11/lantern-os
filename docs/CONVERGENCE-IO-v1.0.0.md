# Convergence IO v1.0.0

**Status:** Implemented  
**Date:** 2026-06-04  
**Replaces:** super-jarvis-default, super-jarvis-primary agent profiles  
**Source:** Regulatory Primitive Stack (RPS v0.1) derived specs  
**Location:** `src/convergence_io/`

---

## What is Convergence IO?

Convergence IO is the unified agent primitive stack for Lantern OS. It replaces the super-jarvis agent profiles with a clean, composable, testable implementation of the 5 specs derived from the Regulatory Primitive Stack research.

Where super-jarvis was a monolithic MCP-dependent profile that required `MCP_SERVER_URL` and `DISCORD_BOT_TOKEN`, Convergence IO is a pure Python library that composes 5 orthogonal primitives. Any surface (Dream Journal chat, Discord bot, CLI, API) can use it directly.

---

## The 5 Specs

### PCSF — Provider Capacity State Format

**File:** `src/convergence_io/pcsf.py`  
**Operationalizes:** P4 (Capability Constraints) for LLM provider routing  
**What it does:** Tracks which LLM providers are available, degraded, at quota, or circuit-broken. Routes requests through the fallback chain automatically.

**Default chain:** Anthropic → OpenAI → Google → Groq → DeepSeek → Ollama → Offline

Each provider has:
- Circuit breaker (3 failures → open for 30s → half-open probe)
- Latency tracking (p50, p99)
- Quota awareness
- Env var detection (no key = no route)

**Why this matters:** The Dream Journal chat was returning canned responses because `ANTHROPIC_API_KEY` wasn't set and no fallback chain existed. PCSF makes the server try every available provider before falling back to offline persona responses.

### CCF — Capability Claim Format

**File:** `src/convergence_io/ccf.py`  
**Operationalizes:** P4 (Capability Constraints), consumed by P5, P8, P10  
**What it does:** Each agent registers what it can actually do right now. Before an action, the CapabilityGate checks the claim against required capabilities.

Key principle: **hallucinated capability is a compliance failure.** If an agent claims it can do streaming inference but its provider is down, the gate rejects the action instead of silently failing.

### AAPF — Agent Action Provenance Format

**File:** `src/convergence_io/aapf.py`  
**Operationalizes:** P3 (Provenance and Audit), consumed by P6, P7, P9  
**What it does:** Every action (chat, save, dispatch, gate check) produces an append-only provenance record. The record ties the input to the output, the agent to the provider, the capability claim to the authority check.

Records are written to `data/provenance/actions.jsonl` as JSONL. Queryable by agent, action type, time range.

### NAP — Negative Authority Profiles

**File:** `src/convergence_io/nap.py`  
**Operationalizes:** P2 (Authority and Consent Gates) in denial form, composes M1  
**What it does:** Defines what agents are explicitly DENIED from doing. Hard denials cannot be overridden by capability claims.

Built-in profiles:
- `dreamer-safety` — No financial trades, no credential entry, no data deletion, no PII/PHI/COPPA actions
- `local-only` — Blocks all cloud providers, enforces on-device processing only

NAP composes with M1 (Dynamic External Predicates): external deny lists can be loaded and refreshed on a schedule.

### DCF — Data Classification Format

**File:** `src/convergence_io/dcf.py`  
**Operationalizes:** P1 (Data Classification), gates CCF  
**What it does:** Every piece of data carries classification labels that propagate through transformations. A summary of a dream entry still carries `dream_content` labels.

Standard Dream Journal labels:
| Label | Sensitivity | Propagates |
|-------|------------|------------|
| `dream_content` | standard | yes |
| `user_identity` | sensitive | yes |
| `symbolic_data` | standard | yes |
| `system_metadata` | public | no |
| `agent_response` | standard | no |
| `emotion_tag` | standard | yes |
| `csf_archive` | standard | yes |

---

## How It Replaces super-jarvis

| super-jarvis | Convergence IO |
|-------------|---------------|
| MCP-dependent (`MCP_SERVER_URL` required) | Pure Python, no external deps |
| Monolithic profile, hard to test | 5 composable specs with unit tests |
| Single provider, silent failure | PCSF fallback chain with circuit breakers |
| No authority gates | NAP denials + CCF capability checks |
| No provenance trail | AAPF records every action |
| No data classification | DCF labels propagate through transforms |
| `super-jarvis-default` + `super-jarvis-primary` | Single `ConvergenceIO` engine |

---

## Usage

```python
from convergence_io import ConvergenceIO

engine = ConvergenceIO(repo_root=Path("."))

# Register provider handlers (each is a callable that calls the actual LLM API)
engine.register_provider_handler("anthropic", anthropic_handler)
engine.register_provider_handler("ollama", ollama_handler)

# Route a chat message through the full stack
result = engine.route_chat(
    message="I dreamed of a door locked by god",
    agent_id="lantern",
    kind="dream",
    user="orion",
    system_prompt="You are Lantern...",
)

print(result.text)           # The LLM response (or offline fallback)
print(result.provider_used)  # "anthropic", "ollama", or "offline"
print(result.source)         # "llm", "offline", or "denied"
print(result.provenance_id)  # Action ID for audit trail
```

---

## Execution Flow

```
Dreamer sends message
  │
  ├─ 1. DCF: classify input (dream_content, symbolic_data, etc.)
  │
  ├─ 2. NAP: check authority gates
  │     └─ DENIED? → return denial, record provenance, stop
  │
  ├─ 3. PCSF: get routable provider chain
  │     └─ Check env vars, circuit states, quota
  │
  ├─ 4. Try each provider in chain:
  │     ├─ Anthropic → success? record latency, return
  │     ├─ OpenAI → success? record latency, return
  │     ├─ Gemini → success? record latency, return
  │     ├─ Groq → success? record latency, return
  │     ├─ Ollama → success? record latency, return
  │     └─ All failed → offline persona fallback
  │
  ├─ 5. Save dream entry (if save_fn provided)
  │
  └─ 6. AAPF: record full provenance
        └─ agent, provider, model, latency, status, data classes
```

---

## Health Endpoint

```python
engine.health()
# Returns:
{
    "ok": True,
    "version": "1.0.0",
    "service": "convergence-io",
    "providers": { ... PCSF snapshot ... },
    "authority_profiles": [ ... active NAP profiles ... ],
    "capabilities": { ... CCF claims ... },
    "provenance_counts": { "ok": 42, "offline": 3 }
}
```

---

## Relationship to Other Systems

- **CSF (Convergence-Searchable Format)** — Storage format, read/written by CIE (Convergence IO Engine)
- **Dream Journal chat** — Primary consumer via `route_chat()`
- **Orchestrator MCP server** — Can expose Convergence IO health via `/api/convergence/health`
- **Discord bot** — Routes through the same engine, same provenance
- **12-step Convergence Loop** — Validation loop in `convergence_io_engine.py`, now backed by PCSF for provider routing in validation steps

---

## Migration from super-jarvis

1. Remove `super-jarvis-default` and `super-jarvis-primary` from `config/agent-profiles.json`
2. Replace with `convergence-io` profile pointing to `src/convergence_io/`
3. Wire `server.js` dream chat endpoints to call Convergence IO (or use JS port)
4. Provenance records appear in `data/provenance/actions.jsonl`

---

**Version:** 1.0.0  
**Spec source:** `gm-agent-orchestrator/docs/research/regulatory-primitive-stack-glossary.md`  
**RPS version:** v0.1
