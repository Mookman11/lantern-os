# Add Courtney operator agent zero one Lantern gauge

Priority: P0
Owner: claude
Created: 2026-05-14T00:14:48Z
Source: connector-action

## Objective
Add a simple 0/1 Lantern performance gauge for Courtney, the operator, and each agent slot.

## State
Courtney is unhappy with Lantern performance today. Operator wants less words and more action. Agent state is degraded: Codex usage-limited, Gemini quota-limited, GPT-web crashed, operator-intake validation failed, only claude-main is clean and available.

## Rules
Use 0 for blocked/not trustworthy today and 1 for usable/clear today. Show state first, say the limit, then self-correct. Do not sync, reset, clean, merge, or start other agents. Keep output short.

## Deliverable
A Markdown gauge table with rows for Courtney trust, operator trust, claude-main, codex-main, gemini-main, gemini-flash, gpt-web, operator-intake, and overall Lantern. Include one concrete next action per 0 row.
