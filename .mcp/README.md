# Lantern OS MCP Settings

Model Context Protocol (MCP) configuration for Lantern OS.

## Server

- **Host:** `127.0.0.1:8771`
- **Transport:** SSE (`/sse`) + JSON-RPC messages (`/messages`)
- **Health:** `GET /health`
- **Startup:** `python src/mcp_server/server.py`

## Tools

| Tool | Description |
|------|-------------|
| `queue_status` | View work queue depth and pending tasks |
| `task_intake` | Submit a task to the queue with priority |
| `dispatch_work` | Dispatch work to an orchestrator agent |
| `boot_check` | Check orchestrator boot status and fleet counts |
| `list_skills` | List available skills (dream_journal, lucid_dreaming, archive_curator, voice_curator) |
| `get_status` | Overall system status with uptime and queue depth |
| `fleet_status` | Read agent fleet status from `data/status/super-jarvis-fleet.json` |

## Client Configurations

### Claude Desktop

Copy `.mcp/claude-desktop.json` to your Claude Desktop config directory:

- **macOS:** `~/Library/Application Support/Claude/mcp-settings.json`
- **Windows:** `%APPDATA%\Claude\mcp-settings.json`

### Windsurf

Config is already at `.windsurf/mcp.json` — Windsurf loads it automatically from the workspace.

### VS Code

Config is already at `.vscode/mcp.json` — VS Code MCP extension loads it from the workspace.

### Manual SSE Connection

```bash
curl -N http://127.0.0.1:8771/sse
```

## Prerequisites

```bash
pip install fastapi uvicorn python-dotenv
python src/mcp_server/server.py
```

Server listens on `http://127.0.0.1:8771`.
