# P0: Evaluate OpenHands headless facilitator for Issue #196

Related issues:
- #196 disaster recovery
- #198 facilitator recommendation review

## Decision context

Deep Research recommends OpenHands headless as the primary non-human CLI facilitator for unattended Orch orchestration.

## Goal

Evaluate OpenHands headless as the next recovery lane for Orch.

## Acceptance criteria

1. Repo visibility works.
2. Shell command execution works.
3. Structured JSON or JSONL output works.
4. GitHub read/write works.
5. Resume/retry behavior works.
6. Smoke test does not move queue/failed tasks.
7. Smoke test does not wake sleeping/blocked agents.
8. Smoke test does not close GitHub issues.
9. Result is recorded back to #196 and #198.

## Explicit exclusions

- Do not use Codex CLI until local PowerShell/native wrapper blocker is resolved.
- Do not treat gemini-2.5-flash-lite as a facilitator runtime.
- Do not use Gemini CLI as primary facilitator unless OpenHands and Goose are both rejected.
