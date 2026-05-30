# HotSwapVM Ship-Of-Theseus Patent Candidate

Status: patent candidate / claim workbench item. Not a filed patent, legal
opinion, or freedom-to-operate claim.

## Signal

Switch from static matrix thinking to a live HotSwapVM model:

```text
running system -> slide block out -> slide block in -> continuity receipt
```

The useful invention shape is not "a giant matrix exists." The useful shape is
a running system that can replace parts while preserving identity, safety, and
operator trust.

## Core Idea

HotSwapVM treats a Lantern/agent/RAG/product system as a live vessel made of
replaceable blocks:

- memory blocks;
- model blocks;
- agent blocks;
- dashboard blocks;
- claim/evidence blocks;
- deployment blocks;
- revenue/product blocks.

Each block can be removed, replaced, or upgraded while the system keeps running,
but only if a continuity gate passes.

## Ship Of Theseus Resolution

The system is the same "ship" when these identity anchors persist:

1. stable operator intent;
2. stable root identity / repo lineage;
3. block lineage graph;
4. evidence ledger;
5. continuity receipts before and after swap;
6. rollback path;
7. safe public claim after view transform.

If those anchors break, the system is not the same ship. It is a fork, clone, or
new vessel and must be labeled that way.

## Candidate Claim Language

Investigate these as claim candidates, not final patent claims:

| Candidate | Plain claim | Evidence needed |
| --- | --- | --- |
| HSVM-001 | A live control plane can hot-swap functional blocks while preserving identity through a continuity ledger. | before/after receipt, block id, lineage id, rollback id |
| HSVM-002 | A RAG/agent system can slide memory/model/agent blocks in and out while maintaining a stable operator-facing identity. | RAG block manifest, model/agent block manifest, identity check |
| HSVM-003 | Ship-of-Theseus ambiguity can be resolved operationally by declaring continuity anchors and labeling failed swaps as forks. | continuity gate examples and failed-fork examples |
| HSVM-004 | Public claims can be derived from raw block state only after a view transform applies evidence, freshness, fallback, and boundary gates. | view-transform receipt |

## Safe / Fun Sort

| Field | Decision |
| --- | --- |
| Safe? | yes, as a research/patent-candidate workbench item |
| Fun? | yes, because it turns the tesseract/matrix idea into a live replaceable ship |
| Bucket | `safe_fun` |
| Hold boundary | no legal filing, ownership, novelty, or patentability claim without attorney review |

## Fit With House Thinker

The House Thinker should use HotSwapVM as its future-backcast target:

```text
future: live house swaps blocks safely while preserving identity
gap: no block ledger / continuity receipt yet
now: create block schema, swap receipt, and one simulated swap
```

## First Implementation Target

```text
data/hotswapvm/blocks.jsonl
data/hotswapvm/swap-ledger.jsonl
scripts/Invoke-HotSwapVmReceipt.ps1
tests/Test-HotSwapVmReceipt.ps1
manifests/validation/HOTSWAPVM-LATEST.json
```

The first test should simulate a documentation block swap:

```text
old block: static RAG matrix concept
new block: HotSwapVM continuity concept
identity anchor: Lantern OS local-first evidence-gated control plane
result: same ship if receipts pass; fork if anchors fail
```

## Rejected Overclaims

- Do not claim this is already patented.
- Do not claim novelty without prior-art search.
- Do not claim runtime hot-swap works until a script proves a simulated swap.
- Do not claim neural mesh until model/vector receipts exist.
- Do not claim MK1 until actual product revenue reaches 1000 USD.
