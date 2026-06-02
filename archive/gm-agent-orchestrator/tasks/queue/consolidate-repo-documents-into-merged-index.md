# Consolidate repo documents into merged index

Priority: P0
Owner: claude
Created: 2026-05-14T16:05:20Z
Source: connector-action

## Objective
Read the repository documentation and produce one merged document index that makes the repo understandable without deleting or overwriting existing files.

## Scope
- Inventory Markdown/text documentation in the repo, especially `docs/`, `lantern/`, root handoff files, task docs, and relevant reports.
- Merge by reference and summary, not by destructive file replacement.
- Produce the smallest useful consolidation artifact, preferably `docs/repo-document-merge-index.md`.

## Guardrails
- Do not delete, reset, clean, or overwrite existing documents.
- Do not merge to `master` while the root worktree is dirty.
- Preserve staged and untracked files.
- Use CMD-compatible handoff notes for Alex.
- Treat existing dirty root state as important evidence: staged `lantern/liberty-freedom-radio-paper.md`; untracked `.local/`; untracked `reports/queue-movements/20260513.jsonl`; untracked `reports/queue-movements/20260514.jsonl`.

## Required output
- A merged index with sections for purpose, active systems, documents, blocked runners, Lantern/bot state, validation commands, and safe next action.
- Evidence of files inspected.
- Git status before and after.

## Validation
- Confirm the generated document exists.
- Confirm no unrelated files were changed.
- Stop after one completed merge-index artifact or one failed validation cycle.
