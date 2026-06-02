# Prepare next PR for Lantern permission slip

Priority: P0
Owner: operator-intake
Created: 2026-05-13T19:59:04Z
Source: connector-action

# Prepare next PR for Lantern permission slip

## Operator instruction

Alex said: merge to master, open issues in next PR. Alex then clarified: let Lantern handle the permission slip.

## Current merge gate

PR #312 is the only open PR currently visible.

- PR: #312 `research: regulatory primitive stack framework v0.1`
- State: open
- Mergeable: true
- Mergeable state: clean
- Checks: 5/5 success
- Files changed: 2

## Risk found in PR #312

PR #312 modifies `.claude/settings.local.json` and adds broad permissions:

- `Bash(git add *)`
- `Bash(git push *)`

Do not use PR #312 as the permission-slip PR. Keep permission work separate and explicit.

## Lantern permission-slip PR scope

Create a dedicated next PR for Lantern permission handling and readiness. The PR should define permission scope as docs/config/tests, not broad shell permissions.

Required scope:

| Area | Required handling |
|---|---|
| Repo permissions | explicit-path git actions only; no wildcards |
| Discord readiness | visible app/channel proof before marked ready |
| Browser readiness | visible session proof before marked ready |
| Device readiness | permission/status evidence before any ready claim |
| Audit | timestamped evidence for every verified door |
| Validation | tests fail if a door is marked verified without evidence |

## Open issues to consider in next PR

Pull current open issues into the PR body as references, not automatic closures:

- #311 Broken pre-commit/pre-push hooks reference scripts not in master
- #309 Per-user API keys: rotation, expiration, leak response, and revocation closed loop
- #308 Grandma mode: hard-coded denylist for high-risk actions
- #307 K-12 profile: name FERPA/COPPA posture explicitly or remove K-12 from positioning
- #306 Threat model: prompt injection, MCP impersonation, supply chain, tenant lateral movement
- #274 Research AI leaders and agentic content index
- #273 Add research ingestion validation scripts before hook enforcement
- #259 RC3 Release Tracking: Multi-Build Orchestration & Provider Stability

## Recommended next PR title

`docs(lantern): add permission-slip readiness contract`

## Validation path

1. Create a feature branch, not protected `master`.
2. Add `docs/lantern/permission-slip.md` or equivalent existing docs path.
3. Add a compact readiness table and evidence schema.
4. Add validation or documented checks that reject broad permissions and unsupported ready claims.
5. Reference open issues in the PR body.
6. Merge only after checks pass and the diff has no broad git permission additions.

## Return word

home
