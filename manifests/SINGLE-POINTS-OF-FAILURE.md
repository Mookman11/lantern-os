# Single Points Of Failure And Redundancy Matrix

Status: resilience control-plane manifest.

## Rule

Lantern OS must not depend on one repo, one hosted route, one MCP tunnel, one agent runner, one local directory, one generated flat file, one cloud provider, or one operator-only memory path for any critical claim or workflow.

Every critical surface needs:

1. a primary path;
2. a local fallback;
3. a static/read-only fallback;
4. a recovery source;
5. a validation command or receipt;
6. an explicit degraded-mode claim.

If a surface has only one path, mark it `single_point_risk` and do not claim production readiness.

## Redundancy States

| State | Meaning | Allowed Claim |
|---|---|---|
| `primary_only` | one working path only | demo/candidate only |
| `single_point_risk` | one path exists and its failure blocks the workflow | risk recorded, not production-ready |
| `dual_path` | primary plus one verified fallback | resilient candidate |
| `triple_path` | primary, local fallback, static/read-only fallback | preferred release shape |
| `degraded_ready` | fallback is slower or manual but documented and tested | operational with limitations |
| `held` | fallback depends on physical action, credentials, rights, secrets, or operator approval | no availability claim |

## Critical Surface Matrix

| Surface | Current Primary | Single Point Risk | Required Fallbacks | Validation |
|---|---|---|---|---|
| Lantern OS control plane | `alex-place/lantern-os` | GitHub availability / local clone drift | local clone at `C:\tmp\lantern-os`; exported ZIP/PDF/HTML bundle; manifest snapshots | `git status`, latest commit, artifact hashes |
| Operator cockpit | Tony Garage local HTML/app | local PC path only | static HTML fallback; printable front page PDF; README commands | open file/app, screenshot or health receipt |
| Public HFF `/os` route | Render route | route can 404 or stale deploy | local Lantern app; static fallback page; source route smoke test | live HTTP 200 check |
| MCP/orchestrator | `gm-agent-orchestrator` local service | local dirty state / tunnel mismatch / MCP unavailable | read-only PowerShell inspection; GitHub metadata; queue snapshot JSON | MCP tool list, git status, health JSON |
| Agent fleet capacity | local orchestrator config | unverified queue/slots | offline config count; active/failed/queued snapshot; dry-run supervisor report | no 600-agent claim until verified |
| RAG dollhouse | one flat markdown file plus assets | flat file stale or asset drift | SHA256 asset manifest; source repo paths; compressed rebuild instructions | manifest hash check, asset count check |
| COMET LEAP PDFs/images | copied local skill assets | copied assets can drift from source | source paths; SHA256 manifest; source repo metadata | hash receipt and count receipt |
| Wallet/cash sprint | local JSON/JSONL ledger | local file only, no cleared cash truth source | invoice markdown; ledger append script; bank/payment external truth held | parser check, no cleared-cash claim until funds clear |
| Archive/Wayback lane | script + rights gate | rights decisions can be missed | metadata-only mode; `downloadAllowed=false`; operator review queue | validation JSON with download decision |
| Dependency repo universe | connector inventory | connector scope mismatch | local clone/read-only inventory; all-repos inventory manifest; dependency graph | per-repo intake record |
| GameMaker/game lane | source repos and local tools | old build chains/assets unknown | preservation summaries; asset manifests; toolchain notes | build/test discovery before migration |
| Dual boot/device lane | local Windows PC | physical disk action | prep-only scripts; rollback docs; readiness JSON | `readyForPrep=true`, `readyForInstall=false` until unallocated space exists |
| Render deployment | Render service | provider outage/stale deploy | local Flask run; static generated page; GitHub Pages/static candidate | live HTTP check and local smoke test |
| GitHub connector | ChatGPT GitHub MCP | scoped/misresolved repository actions | browser/Git CLI local path; GitHub web; local clone | compare repo name, remote, branch before writes |
| Human operator memory | chat instruction/context | forgotten state or ambiguous goal | manifests, receipts, issues, README first commands | record decisions in repo before claiming done |

## Required Fallback Pattern

Each new Lantern surface must define this block before being called stable:

```text
surface:
primary_path:
primary_owner:
fallback_local:
fallback_static:
recovery_source:
validation_command:
last_validation_receipt:
degraded_mode_claim:
held_boundaries:
```

## Immediate Fix Queue

### 1. HFF `/os` route

State: `single_point_risk`.

Fix path:

- add explicit `/os` route in HFF `safe_app.py`;
- add local smoke test;
- push HFF;
- verify Render returns HTTP 200;
- keep local Lantern app as fallback.

### 2. MCP/orchestrator capacity

State: `single_point_risk` until local status, tools, queues, and agent config are rechecked.

Fix path:

- run read-only local MCP/orchestrator status;
- save queue/active/failed snapshot;
- verify actual exposed MCP tools, not advertised capability;
- do not claim 600 agents until counts prove it.

### 3. Dependency repo intake

State: `primary_only` for many old repos.

Fix path:

- clone missing repos only into explicit intake directory;
- do not clone over existing paths;
- record branch, remote, status, language, top artifacts, and fallback;
- keep old repos as dependencies, not Lantern OS project roots.

### 4. Public/static fallback bundle

State: `missing`.

Fix path:

- export key local surfaces to a static bundle;
- include README, top-down graph, SPOF matrix, front page, RAG index summary, and launch commands;
- publish only non-secret, rights-cleared artifacts.

## Release Gate

Lantern OS is not release-ready if any critical surface remains `primary_only` without a degraded-mode fallback.

A claim can be upgraded only when the fallback has been exercised and a receipt is stored in `manifests/validation/`.
