# Task: Rebase PR #276 on fixed master and mark ready

Priority: P1
Owner: claude
Estimated time: 10 min
Depends on: PR #277 merged (CI green)
Blocks: nothing (unblocks PR #276 review)

## Context

PR #276 (`docs/orch-mcp-cold-start-command`) is docs-only and ready for review,
but its base includes the pre-fix master so CI shows red. After PR #277 merges,
this branch needs a rebase to pick up the fixed Tools.ps1 and go green.

PR #276 is already marked ready for review (done this session). Just needs CI green.

## Scope

- `git rebase master` on branch `docs/orch-mcp-cold-start-command`
- Force-push (rebase on a docs-only branch, no shared work)
- Confirm CI triggers and passes

## Done criteria

- PR #276 CI is green
- No content changes  -  rebase only

## Verify

```powershell
gh pr checks 276
```
