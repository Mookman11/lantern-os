# Restart handoff: ChatGPT and GitHub connector

Use this packet after the local PC restart to keep Codex usage low. Human plus ChatGPT/GitHub connector should do the first read-only validation pass before any coding agent is woken.

## Human steps

1. Restart the PC.
2. Open ChatGPT with the GitHub connector and the MCP connector available.
3. Paste or reference `tasks/queue/p0-validate-chatgpt-bridge-tool-visibility.md`.
4. Ask ChatGPT to compare the raw MCP tool list with the ChatGPT-visible tool list and classify the result as A, B, or C.

## ChatGPT/GitHub connector role

- Inspect GitHub issue and PR context only as read-only context.
- Verify whether the visible MCP/API tool list includes `run_safe_powershell`.
- Compare visible tools to the raw local/ngrok MCP `tools/list` evidence.
- Report one classification:
  - A: raw MCP has the tool, ChatGPT bridge does not.
  - B: raw MCP also lacks the tool.
  - C: raw MCP and ChatGPT bridge both have the tool.
- Do not create issues, close issues, move queue tasks, or start agents unless Alex explicitly asks.

## Codex wake conditions

Wake Codex only after the A/B/C classification is known:

- A: prepare a focused connector/bridge registration fix.
- B: prepare a focused MCP server startup/tool registration fix.
- C: prepare delegation validation and final queue cleanup.

Codex should not watch logs continuously or run broad repository scans for this lane.
