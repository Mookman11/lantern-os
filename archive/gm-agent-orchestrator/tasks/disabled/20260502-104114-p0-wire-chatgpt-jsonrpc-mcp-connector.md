ARCHIVE-RATIONALE: superseded | archive-date: 2026-05-02 | ledger: 20260502-104114-task-closure-ledger.md

# P0: Wire ChatGPT Deep Research as non-local orch agent via JSON-RPC MCP

## Context
MCP server is live at https://crinkle-utmost-debit.ngrok-free.dev/mcp
This is a JSON-RPC 2.0 endpoint. ChatGPT can connect to MCP servers directly
without an OpenAPI schema if the server implements the MCP SSE or streamable
HTTP transport correctly.

## Task
1. Test current /mcp endpoint transport: does it support SSE or streamable HTTP?
   curl -X POST https://crinkle-utmost-debit.ngrok-free.dev/mcp \
     -H 'Content-Type: application/json' \
     -d '{"jsonrpc":"2.0","method":"tools/list","id":1}'
2. If SSE not supported, add SSE transport to Start-OrchMcpServer.ps1
3. Document the working connection method in docs\deep-research-connector.md
4. Include the exact ChatGPT connector config (URL, auth, transport type)
5. Commit, update AGENT_LOG.md, complete task

## Acceptance
- ChatGPT Deep Research can call get_agent_status via the MCP endpoint
- Connection method documented with working config

