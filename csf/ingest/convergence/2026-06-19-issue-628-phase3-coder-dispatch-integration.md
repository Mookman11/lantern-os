# Convergence — Issue #628 Phase 3 Coder Dispatch Integration
Date: 2026-06-19
Issue: #628 — feat: Local Ollama coding agent — Σ₀ update
Branch: claude/sigma0-coder-gate-628 (PR #2)

## Instructions

[2026-06-19] - This CSF ingest is the Phase 3 integration record. It documents only behaviors verified by a passing test or an observed command exit code — no claimed-but-unrun behavior.
[2026-06-19] - There is no separate "keystone-test-engine" module in this repo (searched: zero matches). Per the anti-sprawl constraint, autonomous verification IS the Σ₀ gate, exposed as a callable; no new engine was invented.

## Projects & Systems

[2026-06-19] - Wired code generation into the deterministic dispatch router: `ConvergenceRouter.routeCodeGeneration()` (apps/lantern-garage/lib/convergence-router.js) now returns `source: "keystone_coder"` with the full Σ₀ contract (agent=keystone, contract=sigma0, provider=ollama, model=qwen2.5-coder, verificationFields, ungroundedConfidenceCap=0.3) instead of a bare `needs_llm` sentinel. A cached template still wins over coder dispatch.
[2026-06-19] - Added the autonomous verification entry point `verify_coder_output()` plus a stdin/file CLI in src/sigma0_coder_gate.py. It returns a plain JSON dict (no dataclass import needed by callers) and exits non-zero when output is not promotable, so the convergence dispatch loop / MCP / CI can gate on it.
[2026-06-19] - Fixed the model gap from Phase 2: the Keystone coder task now dispatches with `qwen2.5-coder` (env OLLAMA_CODER_MODEL) via a per-call config copy in `_stream_provider`, while the shared ollama profile that serves Dream Chat stays on `llama3.2`. "Coder is a task type, not a separate system."

## Verified Behaviors (evidence)

[2026-06-19] - tests/test_sigma0_coder_gate.py: 17 passed (was 13; +4 cover verify_coder_output JSON shape, ungrounded confidence cap, dream-tone rejection, ConvergenceRecord projection).
[2026-06-19] - tests/test_convergence_router_deployment.js: 12 passed (+2 cover the keystone_coder route and cache-precedence).
[2026-06-19] - CLI: well-formed five-field output exits 0 and emits a ConvergenceRecord; dream-tone text exits 1 with all five fields reported missing and convergenceRecord=null.
[2026-06-19] - Connector inspect()['coderAgent'].preferredModel reports qwen2.5-coder; the shared ollama profile model remains llama3.2 after a coder dispatch (no mutation leak).
[2026-06-19] - node --check passes on convergence-router.js and convergence-dispatch.js.

## Preferences

[2026-06-19] - Phase 4 (validation/benchmark against a live Ollama and an external API) is NOT done here — these behaviors are structural/unit-level only. Do not claim end-to-end coder quality until a live `qwen2.5-coder` run is benchmarked.
