ARCHIVE-RATIONALE: superseded | archive-date: 2026-05-02 | ledger: 20260502-104114-task-closure-ledger.md

# Low-burn workstream consolidation note

Created: 2026-04-30
Source: low-burn-workstream-consolidation

## Reason

The previous P0 queue mixed stale validation, broad implementation, and autopilot routing work. That made it easy to wake expensive agents before proving the next blocker.

The active queue is intentionally reduced to one validation task:

- `tasks/queue/p0-validate-chatgpt-bridge-tool-visibility.md`

## Held tasks

- `p0-expose-safe-local-powershell-runner-through-mcp-connector.md`
  - Held because raw MCP and ngrok MCP must first be compared against ChatGPT-visible tools.
- `p0-wire-chatgpt-jsonrpc-mcp-connector.md`
  - Folded into the canonical bridge visibility validation task.
- `p0-expose-openapi-schema-for-chatgpt-connector.md`
  - Held unless bridge validation proves OpenAPI is the required connector path.
- `p0-chat-safe-powershell-command-update-surface.md`
  - Held because it is broader than the current validation blocker.
- `p0-make-github-issues-a-managed-local-mcp-surface.md`
  - Held until the MCP bridge baseline is proven.
- `p0-fix-autopilot-slot-routing.md`
  - Held until dirty worktrees are inspected and delegation validation is safe.

## Resume rule

Do not resume any held task until `p0-validate-chatgpt-bridge-tool-visibility.md` has an A/B/C classification.

