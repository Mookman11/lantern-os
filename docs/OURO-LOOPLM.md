# Ouro / LoopLM — looped latent reasoning in Lantern OS

**Source:** *Scaling Latent Reasoning via Looped Language Models* (Ouro,
[arXiv:2510.25741](https://arxiv.org/abs/2510.25741)). PDF in repo:
[`docs/research-papers/ouro-looped-llm-2510.25741.pdf`](research-papers/ouro-looped-llm-2510.25741.pdf).

> **Grounding status (2026-06-18):** the paper PDF was in the repo but **was NOT
> in the Knowledge Center grounding index** — so the LLM could not ground on it.
> This doc fixes that: it is markdown, indexed by `build_knowledge_index.py`, and
> now appears in `data/knowledge/index.jsonl` for retrieval/near-routing.

## The idea (paper)
LoopLM builds reasoning into computation by **reusing weight-tied layers R times**
in latent space (a "third scaling axis": loop depth). Key mechanisms we borrow:
- **Adaptive depth + learned early-exit (Q-exit):** a gate emits per-step exit
  probabilities; exit at the first step where the cumulative `CDF(t) ≥ q`. `q`
  trades compute for accuracy.
- **Entropy-regularized depth** (uniform prior) prevents collapse to always-shallow/deep.
- **Deeper-is-better, with diminishing returns** — most inputs converge by mid-depth.

## How it's implemented here

### 1. Native latent loop on real Ouro weights (the real thing)
[`src/sigma0/loop_lm.py`](../src/sigma0/loop_lm.py) — `Sigma0LoopLM` is our own
implementation of the paper's **Q-exit adaptive-depth policy** (λ→survival→CDF→
first-step-≥q), run on **Ouro's pretrained weight-tied block + exit gate** (we do
not pretrain a LoopLM — that needs 7.7T tokens). This activates the adaptive
inference the **stock Ouro checkpoint leaves off**: its config ships
`early_exit_threshold=1.0` and its `generate()` never threads a per-call threshold,
so it runs **fixed full depth**. Our module reads the per-step gates, applies Q-exit,
and **reports the realized per-token loop depth**.

- **Trained on our data:** QLoRA fine-tune of Ouro-1.4B on the Σ₀ Claude-session set
  ([`scripts/train-qlora-ouro.py`](../scripts/train-qlora-ouro.py); 3 epochs, loss
  ~2.25→1.74). Adapter loads via `Sigma0LoopLM.load(base, adapter=…)`.
- **Served without Ollama:** [`scripts/ouro_serve.py`](../scripts/ouro_serve.py)
  hosts it on the **Ollama HTTP API** (`/api/chat`, `/api/tags`) so the existing
  chat path works with **no Ollama binary** — set `OURO_ADAPTER` for the Σ₀ tune.
- **Verified:** realized depth is **~3.15/4** on Ouro-1.4B (adaptive, not fixed-4).
- **Honest caveat:** generation is currently **no-cache** (slow); integrating
  Ouro's `UniversalTransformerCache` is the next optimization.
- Needs **transformers 4.53–4.57** (Ouro's custom code requires `layer_type_validation`
  but still uses `config.pad_token_id`).

### 2. API-level re-prompt loop (legacy, provider-agnostic)
For the Ollama/Qwen path, we also approximate the loop by re-prompting:

- **[`lib/loop-reasoner.js`](../apps/lantern-garage/lib/loop-reasoner.js)** —
  `loopedReason()` runs the model up to `MAX_LOOPS` (4, = Ouro R4), feeding each
  prior answer back as a Coconut-style context prefix, and **exits via `cdfExit()`**:
  - `threshold_met` — confidence `≥ CDF_THRESHOLD` (0.85)
  - `converged` — `|Δconfidence| < CONVERGENCE_EPS` (0.04) (the entropy-plateau analog)
  - `max_loops` — compute budget hit
- **Wired into [`lib/stream-chat.js`](../apps/lantern-garage/lib/stream-chat.js)** —
  for `reasoning`/`coding` intents, a looped pass runs on the local model and the
  `done` event carries **`loop_n` / `confidence` / `exit_reason`**, which the
  *"Ouro Σ₀ CDF exit"* panel in [`dream-chat.js`](../apps/lantern-garage/public/js/dream-chat.js) already renders.

### Enable / tune
Off by default (it makes multiple model calls — latency vs quality). Turn on:
```
LOOP_REASONER=1   # enable looped reasoning for reasoning/coding intents
```
Tune in `lib/loop-reasoner.js`: `MAX_LOOPS`, `CDF_THRESHOLD`, `CONVERGENCE_EPS`.
The `q` threshold maps to the same compute/accuracy knob as the paper's Q-exit.

## Where it maps in the codebase
| Paper concept | Lantern |
|---|---|
| Recurrent steps R | `MAX_LOOPS` (loop-reasoner) |
| Q-exit `CDF(t) ≥ q` | `cdfExit()` threshold/converged/max_loops |
| Adaptive depth panel | `dream-chat.js` "Ouro Σ₀ CDF exit" (`loop_n`,`confidence`,`exit_reason`) |
| Deeper-is-better, diminishing | convergence loop early-exit |
| Knowledge manipulation > capacity | small local model + KB grounding ([CSF spec §2.9](CSF-FORMAT-SPECIFICATION.md)) |

## Honest scope
- This is an **inference-time, API-level replication** — not a trained weight-tied
  LoopLM. It refines via re-prompting, not shared-weight latent loops.
- Confidence is parsed from the answer's `Confidence:` field or estimated from
  structure; on a small model it's approximate, so the exit is heuristic.
- Off by default; each loop is a full model call (latency cost).

## Related
- [CSF-FORMAT-SPECIFICATION.md](CSF-FORMAT-SPECIFICATION.md) — KB grounding index + near routing
- [LANTERN-SIGMA0-CODER.md](LANTERN-SIGMA0-CODER.md) — the local model this runs on
