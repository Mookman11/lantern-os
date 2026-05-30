# Lantern House Thinker

Status: first resident thinker scaffold.

The House Thinker is the local, persistent reasoning layer for patents, claims,
and agent convergence. It is not yet a neural net. It is a deterministic
receipt writer that keeps the house thinking while the operator is outside the
repo.

## Purpose

The thinker watches the house and writes durable thoughts:

- patent and claim candidates;
- claim evidence state;
- agent convergence blockers;
- next smallest safe action;
- validation receipts that later model/vector layers can use.

## Thinking Method

The operator method is future-backcast first:

```text
converged future -> missing proof -> smallest current action
```

This is cheaper than exploring every possible present branch. The thinker should
hold the future state in one sentence, walk backward to the current proof gap,
and write only the next receipt-backed action.

The first sort is binary:

```text
safe? yes/no
fun? yes/no
```

Use this cheap 2-bit sort before deeper reasoning:

| Bucket | Meaning | Action |
| --- | --- | --- |
| safe + fun | best candidate | promote to next-action queue |
| safe + not fun | maintenance | batch or automate |
| not safe + fun | tempting risk | hold behind boundary |
| not safe + not fun | waste | reject or archive |

## HotSwapVM Lens

When the thinker sees "matrix" language, prefer the HotSwapVM lens:

```text
static matrix -> live block graph -> hot-swap receipt -> continuity decision
```

This keeps the matrix from becoming a fake work queue. The useful work is
proving that a block can slide out and another block can slide in while the
system keeps identity through receipts.

Ship-of-Theseus rule:

```text
same ship = stable intent + lineage + receipts + rollback + safe claim
fork/new ship = broken anchors or missing receipts
```

## Boundary

The thinker must not:

- claim a trained neural net exists;
- submit patents or legal filings;
- invent product revenue or public traction;
- wake agents;
- mutate source repos;
- read secrets or private folders;
- promote public claims without receipts.

## Inputs

| Input | Path | Role |
| --- | --- | --- |
| Flat RAG house | `data/rag-house/flat-rag-house-latest.json` | current source-labeled memory |
| World model | `data/world-model/belief-ledger.jsonl` | claims, priors, evidence, decisions |
| Patent reports | `reports/*PATENT*.md`, `reports/NOVEL-WORKSTREAM*.md` | claim candidate source |
| Convergence manifests | `manifests/*.md`, `manifests/validation/*.json` | gates and receipts |
| Internal RAG house | `data/internal-rag-house/` | indexed local files and hashes |

## Outputs

| Output | Path | Role |
| --- | --- | --- |
| Thought ledger | `data/house-thinker/thought-ledger.jsonl` | append-only inner monologue receipts |
| Patent candidates | `data/house-thinker/patent-claim-candidates.jsonl` | candidate claim rows |
| Agent convergence candidates | `data/house-thinker/agent-convergence-candidates.jsonl` | held blockers and next actions |
| Latest validation | `manifests/validation/HOUSE-THINKER-LATEST.json` | current status receipt |

## Cadence

Run once:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\Invoke-HouseThinker.ps1 -Once
```

Run as a local loop:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\Invoke-HouseThinker.ps1 -IntervalSeconds 900 -MaxCycles 0
```

`MaxCycles 0` means continue until the operator stops the process.

## Upgrade Path

1. Deterministic receipt writer. Current target.
2. Local model summarizer. Optional, only after an Ollama/LM Studio endpoint is
   verified.
3. Vector-backed retrieval. Optional, only after Qdrant/FAISS/Chroma collection
   receipts exist.
4. Patent/claim workbench. Only after legal-review boundaries are explicit.

## Safe Claim

Lantern OS has a resident claim/convergence receipt loop. It is not yet a
neural thinker. It becomes a neural thinker only after a verified local model or
vector-backed retrieval backend is wired and receipts prove it.
