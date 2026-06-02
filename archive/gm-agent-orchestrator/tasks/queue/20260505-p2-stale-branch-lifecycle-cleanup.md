# Task: Stale branch lifecycle audit and cleanup (#259 Phase 3.2)

Priority: P2
Owner: claude
Estimated time: 1 hour
Depends on: CI green
Blocks: nothing (housekeeping, but stale branches cause routing confusion)

## Context

RC3 tracker #259 Phase 3.2. The repo has accumulated branches from agent sessions
that are either merged, abandoned, or superseded. These create noise in `git branch -a`
output and can mislead routing when the slot-bindings check branch state.

Current known stale branches (from `git branch -a` output this session):
- `claude/magical-napier-b89d19`  -  worktree branch, appears unrelated to any open PR
- `claude/nervous-goldstine-a1aabe`  -  same
- `claude/vigilant-cannon-4ff2cf`  -  same
- `feat/crash-cart-mvp`  -  old feature, check if merged or needs closure
- `feat/mcp-overview-truthful`  -  closed/merged
- `fix/owner-aware-queue-scoring`  -  merged
- `governance-pr-standards-and-enforcement`  -  check status
- `fix/dispatch-remove-headless-param`  -  check status
- `feature/mcp-guarded-git-pr-tools`  -  check status
- `feature/operator-guardrails-dispatch-guard`  -  check status

## Scope

**This task is read-only investigation + documentation first, then cleanup.**

### Step 1: Audit (read-only)

Run `scripts/Get-StaleBranchStatus.ps1` (already exists) and review output.
For each branch: is there an open PR? Is it merged? Is it active worktree?

### Step 2: Document results

Write findings to `reports/audit/$(Get-Date -Format yyyyMMdd)-stale-branch-audit.md`:
- Columns: branch, PR#, status (merged/open/no-PR/worktree), recommended action

### Step 3: Cleanup (only clearly safe branches)

For branches with merged PRs and no active worktree:
```powershell
git push origin --delete <branch>
```
Do NOT delete: active worktree branches (`claude/*`), open-PR branches, or anything uncertain.

### Step 4: PR for branch deletion records

Commit the audit report. Branch deletions don't need a commit  -  they're remote ops.

## Done criteria

- Audit report written at `reports/audit/<date>-stale-branch-audit.md`.
- At minimum 3 confirmed-merged branches deleted from remote.
- No active worktree or open-PR branch deleted.
- Branch pushed, PR open for the audit report commit.

## Reference

- Existing script: `scripts/Get-StaleBranchStatus.ps1`
- Existing test: `tests/Test-StaleBranchStatusContract.ps1`
- Branch lifecycle policy: `docs/agent-contract.md` (per-agent branch completion rule)
