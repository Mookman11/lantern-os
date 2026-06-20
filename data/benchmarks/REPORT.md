# Serving Benchmark Leaderboard

_Generated 2026-06-20T13:03:40.348431+00:00 · 4 successful run(s) of 4 total._

Validation contract (#730): FAST → latency <2s (hard), repetition target 0.85 / floor 0.80; DEEP → repetition target 0.80 / floor 0.75. Repetition is WARN below target but ERROR only below floor (token-loop territory). The 70-85s DEEP latency band applies to the native Σ₀ runtime only.

| Provider | Model | Mode | Avg latency (ms) | Avg repetition | Success | Tok/s | Cost (USD) | Last run |
|---|---|---|---:|---:|---:|---:|---:|---|
| ollama | qwen2.5-coder | fast | 970.5 | 0.848 | 100% | 58.6 | free | 2026-06-20T13:00:38 |
| ollama | lantern-sigma0-coder | fast | 1483.3 | 0.830 | 100% | 44.6 | free | 2026-06-20T12:53:54 |
| ollama | qwen2.5-coder | deep | 1520.9 | 0.814 | 100% | 46.6 | free | 2026-06-20T12:54:18 |

**Distinct days with a successful run:** 1 (Definition of Done target: ≥7)
