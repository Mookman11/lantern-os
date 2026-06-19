# Convergence — Issue #628 Phase 4 Live Validation
Date: 2026-06-19
Issue: #628 — feat: Local Ollama coding agent — Σ₀ update
Branch: claude/sigma0-coder-gate-628 (PR #2)

## Instructions

[2026-06-19] - This is the Phase 4 validation record. Numbers come from a live run against a real local model (qwen2.5-coder via Ollama 0.30.10), not from unit tests. Harness: experiments/phase4_coder_validation.py. Raw receipt: data/phase4-coder-validation.json.

## Two real bugs the live run surfaced (and fixed)

[2026-06-19] - BUG 1 — coder model not applied: the Phase 2 wiring on master set provider=ollama for coder but still used the profile model llama3.2 (not pulled), so live coder calls returned HTTP 404. Fixed on this branch: stream(coder=True) swaps in qwen2.5-coder per-call via _stream_provider. Verified: instrumented call shows MODEL SENT: qwen2.5-coder.
[2026-06-19] - BUG 2 — Ollama streaming never produced tokens: _parse_sse only accepted SSE "data:"-prefixed lines, but Ollama /api/chat streams bare JSONL. Every Ollama token was silently skipped -> empty output -> 0/5 contract pass. Fixed: _parse_sse now strips the "data:" prefix when present and otherwise parses the line as JSONL; non-JSON framing lines still fail json.loads and are skipped, so SSE providers are unaffected.

## Model compliance finding (and fix)

[2026-06-19] - Before tuning: qwen2.5-coder produced correct code but paraphrased the verification footer in markdown ("### Confidence:", "- **Source:**") and sometimes dropped the Claim/Evidence labels — 80% (4/5) contract pass.
[2026-06-19] - Fix was to the PROMPT, not the gate: KEYSTONE_CODER_PROMPT now demands the five literal labels in order, no markdown/bold/bullets, no omission, with a format-only example footer. The gate (check_coder_output) was NOT loosened — the metric was earned, not relaxed.
[2026-06-19] - Added a warm-up call in the harness so the first task does not pay the cold model-load truncation cost.

## Verified result (success criteria)

[2026-06-19] - Local pass rate: 100% (10/10) on contract compliance — target was >= 90%. MEETS.
[2026-06-19] - Every passing output carried a parseable confidence in [0,1]; average confidence 0.895.
[2026-06-19] - Gate unit tests remain green after the prompt change: tests/test_sigma0_coder_gate.py 17 passed.
[2026-06-19] - External-API benchmark: SKIPPED — no cloud API key present in this environment. The `--benchmark <provider>` path exists in the harness but was not exercised; the local-only criterion stands on its own.

## Preferences

[2026-06-19] - The 100% figure is on 10 short, grounded coding tasks at temperature 0.2. It demonstrates contract compliance, not general coding quality on hard problems. Do not over-extrapolate to complex tasks without a larger/harder suite.
