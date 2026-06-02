# P0: Validate ChatGPT bridge tool visibility

Priority: P0
Owner: human-chatgpt
Created: 2026-04-30
Source: low-burn-workstream-consolidation

## Goal

Prove whether the current MCP tool mismatch is in raw MCP, the ChatGPT bridge, or stale cached state before waking implementation agents.

This is a validation task only. Do not start agents, move active tasks, retry failed tasks, stop services, restart services, run `Cold-Start.ps1`, or make architecture changes while performing this task.

## Known baseline

- Default MCP health URL: `http://127.0.0.1:8787/health`
- Default MCP endpoint: `http://127.0.0.1:8787/mcp`
- External ngrok gateway endpoint: `https://crinkle-utmost-debit.ngrok-free.dev/mcp`
- MCP must run with `noAuth: true` for this restart validation lane.
- ngrok is only the external gateway exposing local MCP on port 8787. It is not the MCP server.

## Validation steps

1. Confirm local health:
   - URL: `http://127.0.0.1:8787/health`
   - Expected: healthy response with `noAuth: true`.
2. Confirm local raw MCP tools:
   - POST `{"jsonrpc":"2.0","method":"tools/list","id":1}` to `http://127.0.0.1:8787/mcp`.
   - Expected tools include `run_safe_powershell` and `create_queue_task`.
3. Confirm ngrok raw MCP tools:
   - POST the same `tools/list` request to `https://crinkle-utmost-debit.ngrok-free.dev/mcp`.
   - Expected tools match local raw MCP for `run_safe_powershell` and `create_queue_task`.
4. Confirm ChatGPT-visible tools from the ChatGPT MCP connector UI or active chat tool list.
   - Expected tools include `run_safe_powershell`.
5. Record the result using exactly one classification below.

## Classification

- A: Raw local/ngrok MCP has `run_safe_powershell`, but ChatGPT-visible tools do not.
  - Next owner: connector/bridge registration investigation.
- B: Raw local/ngrok MCP also lacks `run_safe_powershell`.
  - Next owner: MCP server startup/tool-list/dispatch investigation.
- C: Raw local/ngrok MCP and ChatGPT-visible tools all expose `run_safe_powershell`.
  - Next owner: delegation validation and queue cleanup.

## Acceptance

- Evidence includes the local health result, local `tools/list` result, ngrok `tools/list` result, and ChatGPT-visible tool result.
- One A/B/C classification is recorded.
- No agents are started during validation.
- No stale held tasks are resumed until this task has a classification.
