# Split PR 188 into bounded Lantern limits PR

Priority: P0
Owner: claude
Created: 2026-05-13T23:39:20Z
Source: connector-action

## Objective
Create a clean PR that contains only bounded Lantern local limits text and tests from the mixed PR #188 work.

## Guardrails
First verify the correct source repo/branch because the current GitHub PR lookup for #188 in alex-place/gm-agent-orchestrator returned 404. Do not merge anything. Do not sync, reset, clean, or move existing tasks. Exclude A/V capture, model utilities, PDF ingestion, playback, and local state changes.

## Validation
Show the observed state, state the scope limit, extract only matching hunks, run targeted tests, and open the bounded PR with evidence.
