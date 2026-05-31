# ARC Bounty Workbench

**Purpose:** Local workbench for ARC Prize 2026 competitions (ARC-AGI-3, ARC-AGI-2, ARC Paper Prize)

**Status:** Research lane - no live trading, no account action, no prize claim

## Target Competitions

| Competition | Prize | Deadline | Focus |
|---|---|---|---|
| ARC-AGI-3 | $850K | 2026-11-02 | Interactive agents in novel environments |
| ARC-AGI-2 | $700K | 2026-11-02 | Static reasoning tasks |
| ARC Paper Prize | $450K | 2026-11-08 | Conceptual progress with Kaggle submission |

## Lantern Attack Shape

1. **Local simulator** - Task loader, visual transform DSL, hypothesis search
2. **Agent stack** - Curiosity policy, map memory, action replay, failure compression
3. **Proof gates** - Deterministic seed receipts, reproducible runs
4. **Paper template** - Methods documentation tied to actual results

## Directory Structure

```
arc-bounty-workbench/
├── README.md
├── task_loader.py          # ARC task loading and preprocessing
├── visual_transform.py     # DSL for visual task transformations
├── agent_stack.py          # Curiosity policy + map memory
├── hypothesis_search.py    # Search over solution strategies
├── receipt_format.py       # Experiment run receipts
├── no_internet_test.py    # Evaluation boundary test
├── paper_template.md       # Methods paper outline
└── experiments/            # Run receipts and logs
```

## Boundaries

- No internet during evaluation
- No benchmark leakage
- No copied book text
- No private solution dumping
- No prize claim before official acceptance
- All work public-safe and reproducible

## Next Steps

1. Implement task loader stub
2. Define receipt format
3. Add no-internet boundary test
4. Create paper outline template
