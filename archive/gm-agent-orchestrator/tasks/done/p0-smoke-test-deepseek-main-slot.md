# P0: Prepare deepseek-main slot and smoke test DeepSeek V4-Pro

## Context
deepseek-main slot added to agents.json. Uses Claude Code binary pointed at
DeepSeek V4 API via ANTHROPIC_BASE_URL env var override.
Cost: ~7-9x cheaper than Claude Opus per token.

## Task
1. Verify worktree exists: agent-worktrees\deepseek-main
2. Verify ANTHROPIC_BASE_URL is set to https://api.deepseek.com/anthropic
3. Run smoke test from the worktree:
   cd agent-worktrees\deepseek-main
   claude --dangerously-skip-permissions --print "Reply with exactly: DEEPSEEK_SLOT_OK"
4. If DEEPSEEK_SLOT_OK returned, slot is healthy. Update AGENT_LOG.md.
5. Complete task.

## Acceptance
- claude binary returns DEEPSEEK_SLOT_OK via DeepSeek endpoint
- No errors in output
