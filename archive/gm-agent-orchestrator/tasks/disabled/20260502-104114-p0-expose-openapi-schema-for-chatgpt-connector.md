ARCHIVE-RATIONALE: superseded | archive-date: 2026-05-02 | ledger: 20260502-104114-task-closure-ledger.md

# P0: Expose OpenAPI schema for ChatGPT Deep Research connector

## Context
MCP server running at https://crinkle-utmost-debit.ngrok-free.dev
ChatGPT custom connector needs an OpenAPI 3.0 schema at /openapi.json
Current server returns 404 on that path.

## Task
1. Inspect current MCP server routes in scripts\Start-OrchMcpServer.ps1
2. Add a /openapi.json endpoint that generates a valid OpenAPI 3.0 schema
   from the existing MCP tool definitions
3. Restart the MCP server after the change
4. Test: curl https://crinkle-utmost-debit.ngrok-free.dev/openapi.json
5. Commit, update AGENT_LOG.md, complete task

## Acceptance
- /openapi.json returns valid OpenAPI 3.0 JSON with paths for all MCP tools
- No existing MCP functionality broken

