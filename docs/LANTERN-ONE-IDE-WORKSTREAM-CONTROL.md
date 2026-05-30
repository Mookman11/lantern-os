# Lantern One IDE Workstream Control

Status: drift-reduction contract for local repos, agents, runtimes, and cloud URLs.

Lantern One IDE is not a new editor app yet. It is the single control-plane
contract every local agent should read before changing repos, starting services,
dispatching work, or claiming a cloud surface is fixed.

## Source Of Truth

| Layer | Canonical source | Rule |
|---|---|---|
| Product/control plane | `C:\tmp\lantern-os` | Promote only validated artifacts here. |
| HFF world model and anchors | `human-flourishing-frameworks` docs | Show the state. Say the limit. Self-correct before acting. |
| MCP and fleet execution | `C:\Users\alexp\Documents\gm-agent-orchestrator` | Live tools and queue state beat cached claims. |
| Agent worktrees | `C:\Users\alexp\Documents\agent-worktrees` | Dirty worktrees block sync, reset, dispatch, and broad mutation. |
| Local browser front door | `http://127.0.0.1:4177/` | Full local Lantern Garage with controls and receipts. |
| Cloud front door | AWS service URL pending | Read-only public mirror until `/`, `/api/health`, and `/api/cloud-mirrors` pass on the AWS endpoint. |
| BETTER product lane | `docs/BETTER-IPHONE-APP-CONCEPT.md` | Future iPhone shell with BetterSafe and BetterFun, PWA/Shortcut-first until native gates pass. |
| BETTER stone parable | `docs/BETTER-STONE-PARABLE.md` | Symbolic reminder: one precise reversible action, not proof or command authority. |
| BETTER entropy study | `docs/BETTER-FORWARD-ENTROPY.md` | Study drift direction and reverse it with the smallest validated force. |
| Command entrypoint | `POST /api/command` | `!one`, `!converge`, and `!superjarvis` share one local-first route. |

## One IDE Preflight

Run this before any agent performs repo, runtime, queue, deploy, or reporting
work:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\Get-OneIdeStatus.ps1
```

The script is read-only by default. It polls:

- declared repos and their git dirtiness;
- orchestrator `config/local-services.json` health URLs;
- agent worktree dirtiness;
- Lantern cloud mirror URLs;
- current MCP connector receipt status when present.

## Drift Gates

| Drift | Gate |
|---|---|
| Dirty repo or worktree | Record it; do not reset, clean, sync, or dispatch until reviewed. |
| Cloud route 404 | Treat as deploy-state failure; do not rewrite local app blindly. |
| MCP advertised tools mismatch actual tools | Trust `tools/list` and validation receipts over docs. |
| Agent wants to start work from stale queue state | Poll queue/active/failed first. |
| Local service has `healthUrl` | Use it as the authoritative liveness check. |
| Remote tunnel exists | Verify public fetch behavior before trusting it as a clean endpoint. |

## HFF Anchor Alignment

The One IDE contract uses these HFF repo anchors:

| HFF anchor | Lantern One IDE behavior |
|---|---|
| `Show the state. Say the limit. Self-correct before acting.` | Every status surface must show live state, boundary, and next repair action. |
| `A door is a protocol boundary` | Cloud/local/browser/agent doors are launch boundaries, not proof of authority transfer. |
| `observe -> record -> compare -> propose -> human approve -> apply -> verify -> repeat` | Agents inspect and propose before mutation. |
| `what changed / what did not change / how to rollback` | Deploy and runtime fixes require validation evidence and rollback path. |
| `cloud language must not hide physical infrastructure cost` | Cloud URLs are mirrors; local ownership and resource cost stay visible. |

## Split-Brain Control Rule

Use split-brain only as an engineering metaphor: repos, agents, dashboards, and
product modes may specialize, but they must communicate through one protocol
bottleneck. The One IDE board records both sides of a mismatch, compares live
evidence, proposes the smallest reversible action, and waits for human approval
before mutation.

## Future IDE Shape

The eventual app can be one browser IDE with panes for:

- Lantern Cloud OS chat and per-user model bundle;
- BETTER iPhone lane with BetterSafe, BetterFun, PWA, Shortcut, privacy, and rollback status;
- HFF world model beliefs and live polling status;
- MCP tool catalog and advertised-vs-actual mismatch report;
- repo/worktree dirty-state board;
- queue/active/failed task board;
- cloud/local runtime health and deploy receipts;
- rollback and validation receipts.

Until that UI exists, `scripts/Get-OneIdeStatus.ps1` is the contract probe.
