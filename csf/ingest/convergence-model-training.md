# CSF Ingestion — Training a Lantern Dream Model

**Status:** queued — research complete, ready to plan  
**Priority:** 1 for long-term convergence autonomy  
**Estimated effort:** Phase 1 (dataset + RAG): 4–6 hrs | Phase 2 (QLoRA): 1 day + $15–25 cloud

## Research Sources
- [Fine-tuning LLMs 2026 — SitePoint](https://www.sitepoint.com/fine-tune-local-llms-2026/)
- [RAG-Tuned-LLM — arxiv 2503.16071](https://arxiv.org/pdf/2503.16071)
- [MemOS: Memory OS for AI — arxiv 2507.03724](https://arxiv.org/abs/2507.03724)
- [Unsloth Llama-3 → Ollama tutorial](https://unsloth.ai/docs/get-started/fine-tuning-llms-guide/tutorial-how-to-finetune-llama-3-and-use-in-ollama)
- [Fine-Tuning vs RAG 2026 — BigData Boutique](https://bigdataboutique.com/blog/fine-tuning-llms-when-rag-isnt-enough)
- [Memory Tokens — arxiv 2506.15001](https://arxiv.org/html/2506.15001v1)
- [MemOS GitHub](https://github.com/MemTensor/MemOS)

## Architecture Decision

Do NOT try to train a model to speak binary CSF format directly.
Train the model to UNDERSTAND convergence concepts and PRODUCE CTF symbols + door options.
CSF stays as the compression/retrieval layer. The model learns the symbolic language.

```
User message
    ↓
CSF retrieval (src/csf_search.py) → top-3 relevant segments
    ↓
Symbol mesh (co-occurrence pairs from dream journal)
    ↓
Fine-tuned Lantern model (Llama 3.2 3B + LoRA)
    ↓
Reply + [DOORS: A | B | C] in CTF symbolic language
```

## Phase 1 — Wire CSF as retrieval (no training needed)

Add `GET /api/csf/search?q=<query>` to `routes/dream.js`:
```js
// calls src/csf_search.py via child_process
// returns top-3 CSF segment excerpts as plain text
// inject into system prompt before each dream chat turn
```

## Phase 2 — Build instruction-tuning dataset

Source: `data/dream_journal/*.jsonl` (50+ entries already)
Format each entry into 3 training pairs:
```jsonl
{"instruction": "The dreamer says: '{entry.text}'. Respond as Lantern with CTF doors.",
 "input": "Symbol mesh: {top_symbols}. Co-occurrence: {top_pairs}.",
 "output": "{ideal_lantern_response}\n[DOORS: door1 | door2 | door3]"}
```

Use Claude API to generate ideal responses from existing entries.
Target: 500–2000 pairs. Store in `data/training/dream-instruct.jsonl`.

## Phase 3 — QLoRA fine-tune with Unsloth

```bash
pip install unsloth
# Fine-tune Llama 3.2 3B on dream-instruct.jsonl
# Unsloth auto-exports to Ollama GGUF format
# Resulting model: ~2GB, runs CPU-only on 8GB RAM
```

Cloud option: RunPod RTX 4090 ~$0.44/hr → ~$4–8 for full run.
Local option: Apple M1/M2 with 16GB unified RAM (no GPU needed).

## Phase 4 — Deploy as Ollama provider

```env
# .env addition
OLLAMA_MODEL=lantern-dream-v1
OLLAMA_BASE_URL=http://127.0.0.1:11434
```

The existing Ollama provider in `stream-chat.js` picks it up automatically.
No code changes needed once the model is in Ollama.

## MemOS Parallel

MemOS (EMNLP 2025, 35.24% token savings) architecture maps directly:
- MemCube = CSF segment
- Plaintext memory = data/dream_journal/*.jsonl
- Parameter memory = LoRA adapter (the trained behavior)
- Activation memory = KV cache (see convergence-kvcache-compression.md)
- MemCube scheduler = TesseractEngine in src/convergence_io_engine.py

## Files to Create/Change
- `routes/dream.js` — `GET /api/csf/search`
- `scripts/build-dream-dataset.py` — generates training JSONL from journal
- `data/training/dream-instruct.jsonl` — training data (gitignored)
- `scripts/finetune-dream-model.py` — Unsloth training script
- `.env.example` — add OLLAMA_MODEL=lantern-dream-v1
- `data/pcsf/model.pcsf.json` — add lantern-dream-v1 entry
