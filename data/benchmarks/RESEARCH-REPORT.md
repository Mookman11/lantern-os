# Serving Research Benchmark — FAST vs DEEP grounding (#731)

_Generated 2026-06-20T21:59:48.563166+00:00 · 8 successful run(s) of 8 total._

Grounding is measured by `src/grounding.py`: every file path a reply cites is checked against the checkout. **grounding_score** = grounded / (grounded + hallucinated + 1); **path accuracy** = real paths / cited paths (— when the reply named no file); **invented** = paths that do not exist on disk.

| Provider | Model | Mode | Avg latency (ms) | Grounding score | Path acc. | Invented paths | Density/100w | Repetition | Last run |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| ollama | lantern-sigma0-coder | deep | 4693.9 | 0.167 | — | 0 | 0.57 | 0.765 | 2026-06-20T21:59:20 |
| ollama | lantern-sigma0-coder | fast | 5102.4 | 0.167 | — | 0 | 0.51 | 0.860 | 2026-06-20T21:58:49 |
| ollama | qwen2.5-coder | deep | 4182.6 | 0.139 | 0.00 | 1 | 0.61 | 0.794 | 2026-06-20T21:58:23 |
| ollama | qwen2.5-coder | fast | 5355.7 | 0.167 | — | 0 | 0.54 | 0.807 | 2026-06-20T21:57:51 |
