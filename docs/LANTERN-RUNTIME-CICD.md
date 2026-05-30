# Lantern Runtime CI/CD

Status: local-first runtime with an explicit AWS cloud mirror.

This contract keeps the local operator app and the public cloud app from drifting
into separate dashboards.

## Runtime Commands

From `apps/lantern-garage`:

| Command | Runtime | Purpose |
|---|---|---|
| `npm start` | local | Backward-compatible alias for `node server.js`. |
| `npm run start:local` | local | Full Lantern Garage app on `http://127.0.0.1:4177`. |
| `npm run start:cloud` | cloud | AWS-safe public app via `node cloud-server.js`. |
| `npm run check` | CI | Syntax-check local server, cloud server, and browser app. |
| `npm run validate` | local | Poll local APIs and write the validation receipt. |

## Local Runtime

Local is the only runtime allowed to touch MCP, Windows controls, dispatch,
operator notes, source worktrees, and local conversation storage.

Validation:

```powershell
cd C:\tmp\lantern-os\apps\lantern-garage
npm run check
npm run start:local
node validate.js
```

Expected local URLs:

| Surface | URL |
|---|---|
| Dashboard | `http://127.0.0.1:4177/` |
| Health | `http://127.0.0.1:4177/api/health` |
| Cloud mirror state | `http://127.0.0.1:4177/api/cloud-mirrors` |
| MCP catalog | `http://127.0.0.1:4177/api/mcp-catalog` |

## Cloud Runtime

AWS must run the cloud runtime, not the local runtime. The cloud runtime is
read-only and must not expose local dispatch, Windows control, or source-tree
mutation.

AWS deploy gate:

| Check | Expected |
|---|---|
| Container image | `apps/lantern-garage/Dockerfile` builds and starts `npm run start:cloud` |
| Runtime | AWS ECS Fargate or compatible AWS container service exposes port `8080` |
| Root URL | AWS service URL returns the dashboard |
| Health | AWS service URL `/api/health` returns HTTP 200 |
| Mirror API | AWS service URL `/api/cloud-mirrors` returns AWS metadata |

Render was retired on 2026-05-29 after live 404s. Do not re-add `render.yaml`
or `onrender.com` as a Lantern source of truth without a separate operator
decision.

Cloud hardening:

| Guard | Contract |
|---|---|
| Browser headers | Both local and cloud responses include no-store, nosniff, referrer, frame, and permissions policy headers. |
| Write methods | AWS cloud mode allows only `GET`, `HEAD`, held `/api/actions/*` POSTs, and read-only `/api/chat` POSTs. |
| Local controls | Windows controls, MCP dispatch, queues, and source-tree writes remain local-only. |
| Model copy | The dashboard describes per-user model/RAG/MCP/cloud-url bundles without claiming public runtime access to local secrets or worktrees. |

## CI/CD

Primary workflow: `.github/workflows/static-surface-ci.yml`.

Required lanes:

| Lane | What it protects |
|---|---|
| `repo-surface` | top-level repo and operator anchors |
| `manifests` | required Lantern manifest files |
| `html-links` | static surface link integrity |
| `runtime-contract` | Node runtime scripts, AWS cloud command, Dockerfile, and this document |
| `python-tests` | dashboard, mirror, policy, and report tests |
| `convergence-cloud` | cloud-safe convergence loop without local mutation |
| `summary` | final gate that depends on every lane |

Release rule: do not call a cloud mirror fixed until `/`, `/api/health`, and
`/api/cloud-mirrors` all pass on the AWS service URL after deployment.

## HFF Anchor Alignment

Checked against the HFF `origin/master` docs tree, because the public GitHub web
URL may return `404` when auth is not present. Current remote docs use the Door
Protocol and Lantern Chat Design vocabulary as the source of truth.

Anchors carried into this runtime contract:

| HFF source | Anchor used here |
|---|---|
| `docs/lantern-chat-design.md` | `Show the state. Say the limit. Self-correct before acting.` |
| `docs/door-protocol.md` | `A door is a protocol boundary, not a proof of personhood transfer.` |
| `docs/door-protocol.md` | Release evidence must state what changed, what did not change, how it launches, how it stops, what state it reads/writes, what tests passed, and how to rollback. |
| `docs/keystone-table-door-anchors.md` | Runtime claims stay advisory, source-backed, operator-reviewed, and challengeable. |
| `docs/bettersafe-data-center-physical-infrastructure-anchor.md` | Cloud language must not hide physical infrastructure cost; private data stays minimized. |

Important difference: HFF `docs/lantern-chat-design.md` describes a stricter
localhost-only Lantern chat surface. Lantern Cloud OS is therefore documented as
a read-only public mirror and per-user model/RAG/MCP/cloud-url bundle, not as the
local operator chat runtime itself.
