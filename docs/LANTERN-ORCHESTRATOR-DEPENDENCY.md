# Lantern Orchestrator Dependency

Status: local dependency contract, not a live fleet claim.

Lantern OS depends on `gm-agent-orchestrator` for MCP tools, queue state, agent
slot status, and guarded dispatch. The orchestrator is not embedded inside the
dashboard and stale slot files are not treated as running agents.

## Source Of Truth

| Surface | Contract |
|---|---|
| Dependency manifest | `manifests/orchestrator-dependency.json` |
| Validation receipt | `manifests/validation/LANTERN-ORCHESTRATOR-DEPENDENCY-LATEST.json` |
| Local repo | `C:\Users\alexp\Documents\gm-agent-orchestrator` |
| MCP health | `http://127.0.0.1:8787/health` |
| MCP JSON-RPC | `http://127.0.0.1:8787/mcp` |

## Boundary

- Lantern can read MCP health, tool catalog, queue state, fleet state, logs, and
  recent failures.
- Lantern must not claim tasks are running unless `get_agent_status` reports
  active tasks and live runner evidence.
- Lantern must not treat stale `status/<slot>.json` files as availability.
- Lantern must not create new slots inside a dirty orchestrator worktree.
- Agent start, rerun, queue movement, repo sync, branch creation, commit, push,
  and PR actions stay behind explicit human approval.

## Why Not Just Make New Slots

The current slots are old and their runtime files are stale. Reusing them as if
they were alive causes false fleet confidence. Creating new slots directly in a
dirty orchestrator repo would add another split brain.

The safer path is:

1. Validate the orchestrator as a dependency from Lantern.
2. Preserve current dirty orchestrator state.
3. Mark stale slots as not runnable.
4. Prepare a clean orchestrator migration for `lantern-*` slots.
5. Only then approve one slot preflight and one task claim.

## Target Lantern Slots

| Slot | Purpose | Gate |
|---|---|---|
| `lantern-operator-approval` | Human approval and investor/auth gate. | Always manual. |
| `lantern-codex-impl` | Small implementation tasks. | Clean worktree plus task claim. |
| `lantern-gemini-research` | Low-cost research/source compression. | Auth/quota preflight. |
| `lantern-gpt-web-preview` | Browser preview validation. | Clean browser worktree and explicit task. |

## Validation Command

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\Test-LanternOrchestratorDependency.ps1
```

If the result says `fleet_rebuild_required`, Lantern can use MCP read tools but
must not claim an active fleet.
