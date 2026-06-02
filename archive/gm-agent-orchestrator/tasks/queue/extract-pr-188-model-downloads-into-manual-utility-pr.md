# Extract PR 188 model downloads into manual utility PR

Priority: P1
Owner: claude
Created: 2026-05-13T23:48:06Z
Source: connector-action

## Objective
Move any model download or setup changes from mixed PR #188 into a separate manual utility PR.

## Guardrails
Do not merge PR #188 as-is. Do not include model download behavior in the Lantern limits-only PR. No automatic downloads at runtime. No implicit network calls. Utility must be manual, explicit, documented, and safe to dry-run where possible.

## Validation
Verify the source diff first, preserve only manual utility behavior, add tests or dry-run checks that prove no automatic runtime download path exists, and open a separate PR with evidence.
