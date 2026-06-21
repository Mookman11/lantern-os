# Hardening the Lantern reasoning loop against collapse — CSF-native, defense-in-depth

**Status:** research + plan (epic [#764]). Bug claims in §3 are **code-verified** against current `master`.
**Source:** a CSF-grounded analysis (mine → dedup → 3-lens adversarial verify → red-team → synthesize) over the existing CSF corpus: `Convergence-Core-Research-Program-v1.0/v1.1.pdf`, `CSF-Whitepaper-v0.3.pdf`, `CSF-FORMAT-SPECIFICATION.md`, `src/csf/*`, `src/convergence_io/*`, `src/cio_sde/*`, `src/convergence/*`.

## 1. Honest frame

The loop **cannot be made provably uncollapsible** — Theorem 1 ([SIGMA0-COLLAPSE-CERTIFICATE](SIGMA0-COLLAPSE-CERTIFICATE.md) §1; `src/cio_sde/collapse.py`) proves contraction only in a regime: normal/symmetric `A`, or the conservative small-gain bound `α = α_sym + ‖A−Aₛ‖₂ < −margin` (exact only for normal `A`). For strongly non-normal `A` the bound over-rejects, and the full-spectrum `max Re λ(A)` screen is necessary but not sufficient (transient growth; the `{−1, ±2i}` center never collapses). So collapse resistance is **regime-dependent by construction**.

The achievable goal is **maximal resistance via layered, CSF-native defense-in-depth** against three collapse modes:

- **Information collapse** — silent truncation, bit-rot, lossy compaction, dictionary/frequency erasure that lets a degraded archive masquerade as intact state.
- **Behavioral-mode collapse** — the parrot / "42-state" attractor: novelty reduction + self-repetition (measured signature self-repeat ≈ 0.46, echo ≈ 0.15), over-contraction, provider monoculture, livelock.
- **Ungrounded-fixed-point collapse** — converging on fluent-but-unsourced content; confidence inflation; self-citation; capability hallucination.

Every mechanism below is labeled **proven** (a theorem holds in-regime) or **heuristic/measured** (resists collapse empirically, not a theorem), per the repo's honesty contract.

## 2. The existing CSF anti-collapse stack

| Layer | CSF mechanism (file) | Mode resisted | proven / heuristic |
|---|---|---|---|
| Storage integrity | footer/section digests, verify-before-parse (`src/csf/csf_pack.py`, `csf_file.py`) | information | heuristic (v0.3 footer truncated to 64 bits) |
| Storage framing | length-prefixed self-delimiting records; bit-7 absolute/delta header (`src/csf/delta_stream.py`) | information | heuristic |
| Storage geometry | cyclic base-3 (Z/3Z) delta — alphabet matches lattice (`src/csf/base3.py`) | information | **proven** (exhaustive roundtrip test) |
| State space | 3¹² implicit-dust lattice; baseline vs active-delta (`src/csf/v07/quantum_dust.py`) | information / behavioral | heuristic |
| Memory substrate | append-only immutable JSONL; rebuildable indexes (`src/convergence/memory.py`, `src/csf/memory_engine.py`) | information / ungrounded | heuristic |
| Memory promotion | immutable lineage; confidence decay; staleness/contradiction halving (`memory_engine.py`) | ungrounded | heuristic |
| Grounding | External-Reality Rule: ≥2 distinct-domain corroboration (`src/convergence/research.py`) | ungrounded | heuristic |
| Verify | test/surprise fold-back: pass→↑, fail→×0.2, spook→×0.3 (`src/convergence/verify.py`) | ungrounded | heuristic |
| Collapse detect | Σ₀ trigger; small-gain certificate; NIS canary (`src/cio_sde/collapse.py`, `surprise.py`) | behavioral | **proven (normal A)** / heuristic (non-normal, trigger) |
| Collapse correct | Σ₀⁻¹ proximity-gated excitation (measured 1.674×; 180-trial 100%) (`collapse.py`) | behavioral | heuristic / measured |
| Capacity | PCSF circuit breaker + fallback chain; CCF capability gate (`src/convergence_io/pcsf.py`, `ccf.py`) | behavioral | heuristic |
| Control | dilation clamp; swap hysteresis; always-eligible-node invariant (`dilation.py`, `hot_swap.py`, `ceg.py`) | behavioral | heuristic |
| Authority | NAP denial-priority gate (denials override capability) (`nap.py`) | behavioral | proven (fixed floor) |
| Provenance | AAPF append-only ledger + integrity hash; DCF label propagation (`aapf.py`, `dcf.py`) | information / ungrounded | heuristic |

Only **Theorem 1 (normal regime)** and the **small-gain bound (exact for normal A)** are proven. The Tier A wideners below extend the *proven region* — they do not make the system globally uncollapsible.

## 3. Verified bugs (fix first)

Code-verified against `master`:

- **`pcsf.py:57` — live `AttributeError`.** `record_success` reads/writes undeclared `latency_p50_ms` (field is `latency_ema_ms`, L35) → first success of every provider raises, silently routing healthy providers to fallbacks. → [#765]
- **`loop_lm.py` — instrument↔actuator decoupling (G10).** `generate()` is greedy `argmax` (L116) + fixed `rep_penalty`, with **zero** `SurpriseMonitor`/`record_state`/`proximity` wiring. The collapse canary watches an abstract state the decoder never feeds. → [#766]
- **`memory.py` — confidence laundering (G2/G3).** `MemoryStore.append(confidence=0.9)` (L119) admits unverified writes high; `update_confidence` (L224) mutates cache only, diverging from the append-only log `query()` trusts. → [#767]

## 4. Hardening plan (19 adopted via 3-lens panel)

Ordered **proven-region wideners → grounding reinforcements → heuristic guards.**

**Tier A — provable:**
1. **Hash-chain every append-only ledger** (`prev_hash` + `verify_ledger()`) → tamper-*evident*. (`aapf.py`, `memory.py`, `kernel.py`, `delta_stream.py`) — [#767]
2. **Evidence-DAG external-leaf invariant** — no record trusted unless its evidence chain reaches ≥1 external observation; reject cycles. (`memory.py`, `kernel.py`)
3. **Lyapunov-SDP small-gain gate** — certify when `inf_T μ₂(TAT⁻¹) < −margin` (`AᵀP+PA ≺ 0`); widens the proven region for non-normal `A`. (`collapse.py`) — [#768]
4. **Pseudospectral / numerical-range abscissa gate** (`α_ε(A)`, Kreiss bound) — catches non-normal transient growth. (`collapse.py`) — [#768]
5. **Fail-closed, section-salvageable decode** — refuse out-of-range dictionary IDs (no silent token-drop); verify dict↔stream pairing; quarantine+salvage on load failure. (`dictionary.py`, `csf_pack.py`, `sparse.py`, `status_cube.py`)

**Tier B — grounding (External-Reality):**
6. Confidence may rise **only** with attached external ground-truth, else clamp to the Reason prior; failed verify decays the **source** memories. (`verify.py`)
7. Corroboration requires **independent, typed** sources — collapse same-registrant clusters; ≥2 source classes; hard `min_sources ≥ 2` floor. (`research.py`)
8. Dream-mode firewall as a single `Memory.append()` invariant — exploration/unverified → proposal store, confidence cap 0.3. (`memory.py`, `kernel.py`)

**Tier C — heuristic guards:**
9. Two-sided canary: add a **frozen**/contentless lower NIS tail + CUSUM/hysteresis. (`surprise.py`, `collapse.py`, `engine.py`)
10. Direction-targeted Σ₀⁻¹ with a re-excitation floor (inject along slowest-recovering near-null modes). (`collapse.py`)
11. Evidence-aware bidirectional confidence dynamics (deep ungrounded abstraction towers self-extinguish). (`memory_engine.py`, `pattern_extractor.py`)
12. Integrity-/freshness-ranked retrieval (`rec.verify()` on read path + recency term). (`memory_engine.py`)
13. Persist collapse/NIS events into Converge as a pattern-quality multiplier. (`pattern_extractor.py`)
14. Circuit-breaker hardening (the `pcsf.py` bug + quota recovery + half-open probe). (`pcsf.py`, `ccf.py`, `ceg.py`) — [#765]
15. Cross-model collapse-threshold regression gate on model swap (CI harness).
16. Bound delta blast-radius (periodic absolute resync records). (`base3.py`, `delta_stream.py`)
17. Full-width per-section CSF digests (drop the 16-hex truncation). (`csf_file.py`)
18. Reversible / auditable Collapse-Compact (retain coarse baseline + provenance stub). (`v07/convergence_engine.py`, `quantum_dust.py`)
19. Decode-time coverage invariants (unconfirmed regions surface as **"unknown"**, not defaulted to baseline). (`quantum_dust.py`, `v07/csf_file.py`)

## 5. Red-team — gap status (3 of the 5 sharpest closed)

**Closed** (application-layer gaps, each with a regression test that fails on the prior code):

- **G7 — wall-clock trust → closed.** `MemoryStore` now stamps every record with a monotonic Lamport `seq` (seeded from the max on-disk seq, so it stays monotonic across restarts), and ids are built from `seq` instead of `datetime.now()`. Load-time confidence-update replay and `query(order_by="seq")` order by `seq`, not the wall clock, so a backdated/clock-skewed `timestamp` can no longer forge ordering or win a last-writer race. `seq` is folded into the integrity hash, so it is tamper-evident too. (`src/convergence/memory.py`)
- **G9 — deterministic-reverification ratchet → closed.** Each confidence fold in the Verify stage is keyed on `(record_id, evidence_hash)` and recorded in `ConvergenceRecord.applied_evidence`; re-folding identical evidence is an idempotent no-op, so replaying one passing test/NIS reading can no longer ratchet confidence → 1.0. Independent corroborations still count (distinct `evidence_key`). The field is serialized on both the Python (`to_jsonl`) and Node (`convergence-records.js`) sides, preserving the cross-language contract. (`src/convergence/verify.py`, `src/convergence/objects.py`)
- **G11 — provider monoculture → closed.** `HotSwapRegistry` enforces a `provider_diversity_cap` (default 0.6): greedy "best health, lowest cost" selection is diverted to the best *different-provider* candidate whenever a single provider would otherwise exceed the cap of the fleet. The cap never blocks a swap that has no alternative (always-eligible-node invariant preserved). (`src/convergence_io/hot_swap.py`)

**Still open** (deferred to a follow-up PR — both live in the proven-region certificate math under `src/cio_sde/` and need the torch test harness + care not to weaken the certificate's honesty guarantees):

- **G1** observation-channel poisoning — NIS trusts unauthenticated `y` → confident-wrong fixed point; add an innovation-whiteness test + external-leaf requirement. (`src/cio_sde/surprise.py`)
- **G13** `eig_eps` threshold-edge evasion — modes parked just above ε read "structured" while Σ₀⁻¹ injects zero; use banded near-null classification. (`src/cio_sde/collapse.py`)

The remaining red-team gaps (G2–G6, G8, G10, G12, G14) were folded into the #765/#766/#767 fixes or remain lower-priority; see the epic [#764] for the full ledger.

## 6. What stays heuristic (honesty discipline)

The Σ₀ four-condition trigger, Σ₀⁻¹ persistent excitation (measured, no sufficiency theorem), Σ₀ᴿ reconstruction, the Kalman NIS canary (sound χ² math, but a heuristic *predictor* that trusts its input — see G1/G10), and the full-spectrum `max Re λ(A)` screen (necessary, not sufficient) all resist collapse **empirically or by construction but are not theorems.** Do not claim otherwise.

## 7. Top 3 to build first

1. **Close the instrument→actuator loop (G10)** — `loop_lm.generate()` → `SurpriseMonitor`; gate decode on `sigma0_proximity()`; looping-prompt regression test. *Every other collapse detector is watching the wrong system until this lands.* — [#766]
2. **Fix + harden the PCSF circuit-breaker** — the verified `latency_p50_ms` bug + EMA + quota recovery. Pure bug fix, immediate. — [#765]
3. **Hash-chain ledgers + honest `MemoryStore`** — tamper-evidence (provable) + close the two worst laundering paths (default 0.9, cache-only ratchet). — [#767]

[#764]: https://github.com/alex-place/lantern-os/issues/764
[#765]: https://github.com/alex-place/lantern-os/issues/765
[#766]: https://github.com/alex-place/lantern-os/issues/766
[#767]: https://github.com/alex-place/lantern-os/issues/767
[#768]: https://github.com/alex-place/lantern-os/issues/768
