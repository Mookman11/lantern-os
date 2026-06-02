# Expose recent completed task metadata

Priority: P1
Owner: codex
Created: 2026-05-02T21:53:04Z
Source: connector-action

## Objective
Add or expose a safe, read-only way for the ChatGPT MCP/operator surface to retrieve recent completed task metadata from `tasks/done`.

## Context
Current `get_queue_summary` returns queue/active/failed details and only a count for done. `Get-OrchestratorStatus.ps1` returns very large status tails and is not suitable for concise inspection here. We need recent completed task filenames, titles, issues, paths, timestamps, and optionally completion evidence if already present in task markdown.

## Requirements
- Inspect current MCP/status/helper patterns first.
- Prefer the smallest compatible change: either add done task summaries to an existing status/queue response behind a safe limit, or add a new read-only helper/tool for recent completed tasks.
- Keep it read-only; do not move tasks.
- Include a sane default limit, e.g. 10 or 20, and sort by most recent lastWriteTime descending.
- Preserve current queue/active/failed behavior and existing tool schemas unless intentionally extended with backward-compatible fields.
- Validate with targeted PowerShell/parser checks and one live read-only query.
- Report exact files changed, commands run, and sample output.

## Safety
- Do not start or move agent tasks.
- Do not overwrite dirty work without inspecting it.
- If blocked by dirty root state, auth, token limits, sandbox, or missing approval files, stop and report blocker evidence.

## Acceptance evidence
- A ChatGPT/operator can retrieve recent `tasks/done` metadata directly and concisely.
- Validation output demonstrates `done` entries include at least name, title, issue, path, lastWriteTime, and age or equivalent timestamp.
- No stale `tasks/active` entries are left.
