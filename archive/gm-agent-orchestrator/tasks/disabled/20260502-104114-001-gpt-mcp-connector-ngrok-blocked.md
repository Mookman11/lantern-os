ARCHIVE-RATIONALE: superseded | archive-date: 2026-05-02 | ledger: 20260502-104114-task-closure-ledger.md

# Blocked: GPT MCP Connector via ngrok

**Status:** Blocked â€” resume tomorrow  
**Priority:** P1  
**Owner:** Alex  
**Blocked by:** ngrok auth token not yet configured

## Context

The orchestrator MCP server is healthy (18 tools, correct JSON schemas, SSE endpoint working).  
trycloudflare.com is blocked by OpenAI for custom MCP connectors.  
ngrok tunnel (`ngrok http 8787`) is the fix â€” ngrok-free.app is allowed by OpenAI.

## Remaining steps

1. Sign up at dashboard.ngrok.com and copy your authtoken
2. `winget install ngrok.ngrok`
3. `ngrok config add-authtoken <TOKEN>`
4. In a new terminal: `ngrok http 8787`
5. Paste `https://<random>.ngrok-free.app/mcp` into GPT as the connector URL

## Known good

- MCP endpoint: `http://127.0.0.1:8787/mcp` (verified working)
- Tools list: 18 tools, valid JSON schemas
- SSE: `/mcp/sse` returns `text/event-stream` with correct endpoint payload

## Resume note

Do not move to queue until Alex has an ngrok authtoken ready.

