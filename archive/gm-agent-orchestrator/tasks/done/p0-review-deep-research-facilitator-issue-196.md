# P0: Review Deep Research GPT connector facilitator recommendation for Issue #196

Related issues:

- #196 disaster recovery
- #198 facilitator recommendation review

## Source

Deep Research GPT connector review uploaded in chat.

## Context

Issue #196 disaster recovery needs a non-human CLI facilitator strategy for unattended orchestration.

The research recommends:

- OpenHands headless as the primary facilitator.
- Goose as the open-source fallback.
- Claude Code as an alternate proprietary fallback.
- Gemini CLI as research/web-grounded auxiliary.
- Codex CLI excluded for now due to current operational blockage.
- gemini-2.5-flash-lite is a model only, not a standalone facilitator runtime.

## Acceptance criteria

1. Add this research to Issue #196 review context.
2. Create or update a local queue item linked to Issue #196.
3. Evaluate OpenHands headless as primary facilitator for orch.
4. Evaluate Goose as fallback.
5. Explicitly mark Gemini Flash-Lite as model-only, not facilitator.
6. Exclude Codex CLI from active facilitator plan until local blocker is resolved.
7. Add a runbook/validation plan for facilitator smoke test:
   - repo visibility,
   - shell command,
   - structured JSON/JSONL output,
   - GitHub read/write,
   - resume/retry behavior.
8. Decide whether OpenHands/Goose should become the next recovery lane after Gemini pickup remains unproven.

## Safety

- Do not wake sleeping/blocked agents.
- Do not move queue/failed tasks except through approved queue flow.
- Do not close #196 or #198 until the facilitator lane decision is recorded.
- Treat Codex CLI as excluded until the local auth/sign-in blocker clears.

## Initial recommended decision

Primary candidate: OpenHands headless.
Fallback candidate: Goose.
Auxiliary research lane: Gemini CLI.
Alternate proprietary fallback: Claude Code.
Excluded until unblocked: Codex CLI.
Model-only: gemini-2.5-flash-lite.
