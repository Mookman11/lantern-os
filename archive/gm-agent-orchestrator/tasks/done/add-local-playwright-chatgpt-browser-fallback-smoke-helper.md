# Add local Playwright ChatGPT browser fallback smoke helper

Priority: P0
Owner: codex
Created: 2026-05-01T01:46:16Z
Source: connector-action

# P0: Add local Playwright ChatGPT browser fallback smoke helper

## Objective
Create a local-only Playwright fallback that can drive a dedicated Chrome profile already logged into ChatGPT, submit one operator-approved prompt, and save response evidence.

## Scope
- Chrome only, not ChatGPT Desktop app.
- Local persistent browser profile.
- Manual login required.
- No credential storage.
- No queue movement beyond this task's normal claim.
- No agent starts except the approved Codex validation run.
- No MCP exposure yet.

## Required outputs
- tools/chatgpt-browser-fallback/chatgpt-fallback.mjs
- scripts/Invoke-ChatGptBrowserFallback.ps1
- README with manual login/setup steps
- Audit output under logs/control-actions or artifacts/browser-fallback
- Dry-run mode

## Validation
- PowerShell syntax passes.
- Dry-run verifies prompt file/profile/output paths.
- Live smoke can be run manually by operator.
- No secrets written to repo.

## Stop condition
Stop after local smoke helper exists and dry-run validation passes. Do not wire MCP yet.
