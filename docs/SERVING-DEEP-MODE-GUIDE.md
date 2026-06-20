# When to Use FAST vs DEEP — Serving Mode Guide & Grounding Case Study

**Issue:** [#731](https://github.com/alex-place/lantern-os/issues/731) Phase 3 — Serving optimization research: DEEP mode vs alternatives
**Status:** Measured, 2026-06-20
**Builds on:** [SERVING-ARCHITECTURE-2026.md](SERVING-ARCHITECTURE-2026.md) (Phase 1–2), PR #723/#729/#730
**Evidence:** `data/benchmarks/RESEARCH-REPORT.md` · `data/benchmarks/research-leaderboard.jsonl` · `src/grounding.py`

---

## TL;DR — the decision

| You are doing… | Use | Why |
|---|---|---|
| Interactive dream-chat, UX, anything user-facing | **FAST** (default) | Sub-2s product guarantee; anti-repetition decode |
| Bulk/batch generation, drafting | **FAST** | DEEP buys no measurable quality on the cached path |
| Architecture / grant / core-design reasoning **with the native Σ₀ runtime** | **DEEP** (upstream Ouro) | Adaptive depth-3 reasoning — see [§5](#5-the-real-deep-the-native-σ₀-runtime-upstream) |
| Wanting *grounded* answers (cite real files/components) | **Neither alone** — add retrieval | Grounding is a *retrieval* property, not a decode-mode one — see [§4](#4-case-study-grounding-quality-fast-vs-deep) |

**One-sentence finding:** On Lantern OS's cached Ollama serving path, "DEEP" changes only the
decode parameters, and that change does **not** improve grounding quality — so prefer **FAST**
everywhere on this path, and reach for true DEEP only on the native Σ₀ runtime, where the
[owner's upstream measurements](#5-the-real-deep-the-native-σ₀-runtime-upstream) show the actual
reasoning-depth payoff.

---

## 1. What FAST and DEEP actually are

Two different things share the name "DEEP". Keep them apart:

| | **FAST mode** | **DEEP (decode-param)** — this serving path | **DEEP (native Σ₀)** — upstream Ouro |
|---|---|---|---|
| Trigger | default | `OURO_NATIVE=1` (on the cached path) | `OURO_NATIVE=1` with the native runtime wired |
| What changes | `top_p=0.95`, `repeat_penalty=1.1`, `repeat_last_n=64` | `top_p=0.98`, `repeat_penalty=1.05`, `repeat_last_n=128` | adaptive recurrent **depth-3** Q-exit loop |
| Compute | one cached pass | one cached pass (same engine) | multi-step adaptive inference |
| Latency | sub-2s target | **same order as FAST** (no extra compute) | 70–85s band (per architecture doc) |
| Defined in | `src/serving_modes.py` | `src/serving_modes.py` | upstream model runtime |

> **The critical distinction.** On this fork's serving path the only LLM backend that runs is the
> cached Ollama engine (`src/unified_agent_connector.py::_stream_ollama`). Setting `OURO_NATIVE=1`
> there swaps the decode parameters — it does **not** invoke a native Σ₀ Q-exit adaptive-depth loop,
> because that runtime is not wired for Ollama. So on this path DEEP does not, and is not expected
> to, hit the 70–85s band. The validation gate already treats that band as a **WARN** for non-native
> providers (`src/serving_benchmark.py::THRESHOLDS`).

---

## 2. The question this phase answers

The #731 Definition of Done asks: *test ≥5 research questions on both FAST and DEEP, measure
grounding accuracy, and publish a use-case guide.* The interesting variable is **grounding** — the
External Reality Rule operationalized: *of the concrete things a reply asserts, how many are real?*

So we built an objective, offline grounding measure and ran the two decode modes head-to-head on a
set of repository-knowledge questions where a good answer cites real files and a bad one invents
them.

---

## 3. How grounding is measured (`src/grounding.py`)

No LLM judge, no network — every signal is checkable against the checkout:

- **Path references** (`src/serving_modes.py`, `docs/…`) are **grounded** iff the file exists on
  disk; a path that does not exist is a **hallucination** (the model claimed a file that is not
  there). `..` traversal is rejected.
- **Glossary references** are distinctive, real Lantern OS identifiers (component names, module
  basenames, core concepts). They cannot be hallucinated by construction, so they measure *coverage*
  of real concepts. The test suite asserts every glossary file basename actually exists, so the
  glossary cannot silently rot into fiction (`tests/test_grounding.py::test_glossary_files_exist`).

Headline metrics:

| Metric | Definition | Reads as |
|---|---|---|
| `grounding_score` | `grounded / (grounded + hallucinated + 1)` | 0 = cited nothing real; →1 = many verified refs, none invented |
| `path_grounding_accuracy` | real paths / cited paths (`—` if no path cited) | "of the files it named, how many are real" |
| `grounding_density_per_100w` | verified refs per 100 words | how reference-dense the reply is |
| `hallucinated_paths` | cited paths that don't exist | invented-file count |

Reproduce:

```bash
python src/serving_benchmark.py --research ollama:lantern-sigma0-coder --mode deep
python src/serving_benchmark.py --research ollama:qwen2.5-coder --mode fast
python src/serving_benchmark.py --research-report   # → data/benchmarks/RESEARCH-REPORT.md
```

The research set (6 questions across **architecture / core-design / grant-writing**) lives in
`src/serving_benchmark.py::RESEARCH_SET`. Research runs are tracked in their own
`research-leaderboard.jsonl` so the FAST/DEEP repetition gate is not applied to the longer prompts.

---

## 4. Case study: grounding quality, FAST vs DEEP

**Setup.** 6 research questions × {FAST, DEEP} × {`qwen2.5-coder` (7.6B), `lantern-sigma0-coder`
(7.6B, Σ₀-tuned)} on the local Ollama host, `max_tokens=256`, 2 passes each (cold + warm).
**No retrieval/RAG context was injected** — this isolates the *decode mode*, which is exactly the
variable under test. These are real numbers from `src/serving_benchmark.py`; see
`data/benchmarks/research-leaderboard.jsonl`.

### Measured results (warm pass, latest per config)

| Model | Mode | Avg latency (ms) | Grounding score | Path acc. | Invented paths | Density/100w | Repetition |
|---|---|---:|---:|---:|---:|---:|---:|
| lantern-sigma0-coder | DEEP | 4693.9 | 0.167 | — | 0 | 0.57 | 0.765 |
| lantern-sigma0-coder | FAST | 5102.4 | 0.167 | — | 0 | 0.51 | 0.860 |
| qwen2.5-coder | DEEP | 4182.6 | 0.139 | 0.00 | 1 | 0.61 | 0.794 |
| qwen2.5-coder | FAST | 5355.7 | 0.167 | — | 0 | 0.54 | 0.807 |

### Findings

1. **Grounding is low and essentially mode-independent.** Every configuration lands at
   **0.14–0.17** grounding score. DEEP decode parameters did not raise grounding; for
   `qwen2.5-coder`, DEEP was *worse* — it invented a real-looking path (`config/settings.conf`) that
   FAST avoided by not citing files at all.

2. **No model ever cited a real file path.** Across all 8 runs, `grounded_paths` is empty. The only
   grounded references were a handful of widely-described **concepts** the models had seen in the
   wild — "Deep mode", and the "External Reality Rule":

   | Question (qwen DEEP) | What the model said | Grounded? |
   |---|---|---|
   | How is memory persisted? | invented a `StorageManager` / `DiskDr…` module | ✗ (0.0) |
   | The 6-stage Convergence loop? | poetic prose, no module named | ✗ (0.0) |
   | Where are decode params defined? | "`config/settings.conf`" (**invented**; real: `src/serving_modes.py`) | ✗ (0.0, 1 invented) |
   | How are honest metrics enforced? | vague "series of checks" | ✗ (0.0) |
   | Which module routes providers? | invented a "Neural Network Gateway" | ✗ (0.0) |
   | The External Reality Rule (grant) | named it correctly | ✓ (0.5) |

3. **Grounding is a *retrieval* property, not a *decode* one.** A 7B code model with no repository
   context cannot cite this repo's files, and softening the decode distribution (DEEP) does nothing
   to change that — it occasionally makes hallucination *more* likely. To raise grounding you must
   feed the model real context (the RAG house, `apps/lantern-garage/lib/rag-house.js`, and memory
   retrieval), which this decode-isolated benchmark deliberately excludes.

4. **Latency is not a function of mode on this path.** Warm latencies (4.2–5.4s) are driven by
   output length and host load, not by FAST vs DEEP — DEEP, which does no extra compute here, is if
   anything marginally *faster*. The first (cold) run inflated to 7.4s purely from model load. This
   confirms §1: decode-param DEEP carries none of the native runtime's 70–85s cost **and** none of
   its reasoning-depth benefit.

> ⚠️ **Limitations.** Two 7.6B local models, 6 questions, no retrieval, single host. The result is a
> clean statement about *decode mode in isolation*, not a claim about the product's end-to-end
> grounding (which adds RAG + memory). It is reported honestly as such.

---

## 5. The real DEEP: the native Σ₀ runtime (upstream)

Where DEEP genuinely earns its latency is the **native Σ₀ Q-exit runtime** (upstream Ouro line,
post-Ollama-sunset) — not the decode-param path benchmarked above. Those numbers were measured by
the repo owner and are reproduced here, **attributed**, because they are the authoritative source
for the native-runtime claims this fork cannot reproduce:

> **Upstream native-Σ₀ measurements** — issue #731 comment (alex-place, 2026-06-20, 65-prompt golden
> set; `scripts/bench_*.py`):
> - **Recurrent depth is the lever, not attention.** `OURO_UT_STEPS=3` is **1.28× faster than 4 at
>   equal/better accuracy** (0.34 vs 0.28); depth ≤2 collapses accuracy. Shipped as default.
> - **KV-cache through the loop:** token-identical, **~7% faster** on the served chat-template path →
>   `OURO_KV_CACHE=1` default.
> - **Q-exit early-exit gate:** implemented and **CLOSED** — the trained gate keeps mean depth
>   ~3.8/4, so every early-exit config is slower than fixed depth-3 and no more accurate. No headroom
>   below 3.
> - **Quantization (bitsandbytes):** **rejected** — int8 5× slower, nf4 4× slower on the 1.4B model;
>   `torch.compile` unavailable (no Triton on Windows).
> - **Decode floor:** depth-3 + merged-LoRA + sdpa + KV-cache ≈ **~5 tok/s served**. Remaining lever
>   is accuracy (chat-template drop), tracked in #810.

**Reading those results against ours:** the native runtime's payoff is *adaptive reasoning depth*
(fixed depth-3 is the sweet spot), and even there the headline lever turned out to be depth tuning
and caching — not exotic attention or early-exit, both of which were closed off as dead ends. That
reinforces our fork-side finding from the opposite direction: the win is in **how much grounded
reasoning you do** (depth, retrieval), not in nudging the decode temperature.

---

## 6. Recommendations

1. **Default to FAST on the cached serving path** for everything — interactive and batch. On this
   path DEEP decode params are not worth a separate mode for quality reasons; keep DEEP available
   only as the switch that the native Σ₀ runtime binds to.
2. **Do not expect decode mode to fix grounding.** If an answer must cite real code/docs, route it
   through retrieval (RAG house + memory), then optionally verify with `src/grounding.py`.
3. **Reserve true DEEP for the native Σ₀ runtime** and architecture/grant/core-design questions,
   per the owner's depth-3 guidance — that is the only configuration where the latency buys
   reasoning depth.
4. **Make grounding a standing metric.** `src/grounding.py` is a reusable Verify-stage primitive;
   wiring it onto RAG-backed answers would measure the product's *real* grounding (the natural
   Phase-4 follow-up).

---

## References

- Architecture & decode params — [SERVING-ARCHITECTURE-2026.md](SERVING-ARCHITECTURE-2026.md)
- Benchmark + grounding code — `src/serving_benchmark.py`, `src/grounding.py`, `src/serving_modes.py`
- Machine-generated evidence — `data/benchmarks/RESEARCH-REPORT.md`, `research-leaderboard.jsonl`
- Native Σ₀ depth research — issue #731 comment (upstream); follow-up accuracy work — #810
- External Reality Rule — [CONVERGANCE-SIGMA0-BRIEFING.md](CONVERGANCE-SIGMA0-BRIEFING.md)
