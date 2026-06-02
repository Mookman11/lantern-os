# Extract PR 188 PDF ingestion into local-only PR

Priority: P1
Owner: claude
Created: 2026-05-13T23:49:01Z
Source: connector-action

## Objective
Move any local PDF extraction or ingestion changes from mixed PR #188 into a separate local-only ingestion PR.

## Guardrails
Do not merge PR #188 as-is. Do not include PDF extraction in the Lantern limits-only PR. File scope must be explicit and user-selected. No broad disk scans. No cloud calls. No background ingestion. No automatic startup.

## Validation
Verify the source diff first, add explicit file-scope checks, prove local-only behavior with tests or mocks, and open a separate PR with evidence.
