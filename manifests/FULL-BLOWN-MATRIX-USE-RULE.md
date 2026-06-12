# Full Blown Matrix Use Rule

Status: operating rule for Lantern OS decisions.

## Rule

Use the full Lantern OS matrix whenever a task is more than a trivial single-file documentation edit or one-off local command.

The full matrix means combining:

1. top-down project/control-plane view;
2. dependency graph and dependency classes;
3. single-points-of-failure and fallback matrix;
4. RAG dollhouse truth states;
5. Bayesian evidence/posterior decision model;
6. validation matrix and receipts;
7. held-boundary rules;
8. operator approval gates.

Do not use a narrow repo-only or route-only view when the task can affect runtime, public surfaces, dependency intake, MCP tools, agent capacity, release readiness, local device actions, customer/payment claims, or artifact promotion.

## When Applicable

Use the full matrix for:

| Task Type | Matrix Required? | Reason |
|---|---|---|
| public route, Render, dashboard, or website changes | yes | hosted route can fail independently from local app |
| MCP/orchestrator/tool changes | yes | advertised tools can differ from exposed tools |
| agent capacity or queue claims | yes | queue, active, failed, and config counts must agree |
| all-repo/dependency intake | yes | old repos are dependencies, not Lantern OS roots |
| GameMaker/game/runtime work | yes | engine, assets, toolchain, and fallback must be known |
| RAG/index/asset work | yes | source state, hashes, rights, and flat-file freshness matter |
| cash/wallet/payment surfaces | yes | no cleared-cash claim without external payment truth |
| Archive/Wayback/media work | yes | rights and storage gates override convenience |
| dual boot/device/local control work | yes | physical operator and rollback gates apply |
| release/v1/readiness claims | yes | production claim requires fallback and validation receipts |
| tiny typo/docs-only edit | optional | use normal inspect/edit/validate loop |

## Full Matrix Checklist

Before changing or claiming anything substantial, answer:

```text
surface:
primary goal:
control-plane owner:
dependency provider:
current truth state:
local evidence:
remote evidence:
MCP/tool evidence:
SPOF status:
fallback local:
fallback static/read-only:
held boundaries:
validation command:
validation receipt path:
safe claim after validation:
next smallest change:
rollback path:
```

## Decision Output

Use this decision vocabulary:

| Decision | Meaning |
|---|---|
| `promote` | evidence, validation, fallback, and approval are sufficient |
| `adapter_first` | wrap dependency without moving code |
| `index_only` | RAG/metadata only, no runtime claim |
| `fallback_first` | build fallback before adding features |
| `hold` | blocked by secrets, rights, dirty state, physical action, or missing proof |
| `reject` | unsafe, stale, unsupported, or outside Lantern OS boundary |

## Minimal Mode Exception

Do not overuse the full matrix for tiny changes. If the work is a typo, wording clarification, or a non-semantic manifest cleanup, record normal evidence and skip the heavy checklist.

If there is any uncertainty about risk, use the full matrix.

## Related Manifests

```text
manifests/TOP-DOWN-DEPENDENCY-GRAPH.md
manifests/SINGLE-POINTS-OF-FAILURE.md
manifests/ALL-REPOS-INVENTORY.md
skills/lantern-rag-dollhouse/references/LANTERN-OS-RAG-DOLLHOUSE.flat.md
skills/bayesian-world-model/SKILL.md
manifests/open-issues.md
```
