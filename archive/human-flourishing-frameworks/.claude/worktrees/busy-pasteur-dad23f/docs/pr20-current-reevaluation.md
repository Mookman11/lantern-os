# PR #20 Current Re-evaluation

Status: docs-only re-evaluation note.

Last reviewed: 2026-05-09.

This note records the current state of PR #20 after the Keystone convergence
docs, public-copy fixes, Render smoke scripts, and handoff memory landed on
`master`.

It adds no runtime code, endpoint, workflow trigger, deployment behavior,
secret handling, live polling, mesh write behavior, or autonomous authority.

## Current live GitHub state

Checked with `gh` on 2026-05-09:

```text
PR: #20 Add bio-threat registry and runtime safety gates
state: closed as superseded
closed_at: 2026-05-09T16:28:44Z
previous_stage: draft
head: codex/read-only-bio-threat-source-registry
base: master
only open repo issue: #18 dual-use engine risk
```

## Current master checkpoint

Checked from `C:\tmp\human-flourishing-frameworks-scan`:

```text
master and origin/master are aligned at dc3e7696cfeec786700286523bff86b91cd7d19d
docs/convergence-status.md is present
docs/keystone-memory-contract.md is present
docs/capability-confidence-model.md is present
docs/release-smoke-evidence-protocol.md is present
scripts/validate_public_site.ps1 is present
scripts/check_nodes_api.cmd is present
```

Fresh Render smoke evidence from this session:

```text
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\validate_public_site.ps1 -BaseUrl "https://human-flourishing-frameworks.onrender.com"
result: PASS
LASTEXITCODE=0
```

Fresh adoption evidence from this session:

```text
GET /api/adoption/stats:
  total_nodes: 0
  active_last_hour: 0
  verified_nodes: 0

GET /api/adoption/nodes:
  []
```

## Important branch-risk finding

PR #20 is stale relative to current `master`.

The PR branch was created before many docs, scripts, tests, and public-surface
fixes landed. A direct merge of the PR branch into current `master` would not be
a narrow runtime-gate merge. It would also remove or overwrite important
already-landed safety and convergence artifacts.

Observed with:

```text
git diff --name-status HEAD refs/remotes/pr/20
```

High-risk examples from that comparison:

```text
D .github/workflows/container-smoke.yml
D .github/workflows/public-site-smoke.yml
D docs/capability-confidence-model.md
D docs/convergence-status.md
D docs/keystone-memory-contract.md
D docs/keystone-next-chat-handoff.md
D docs/keystone-public-copy-incident-memory.md
D docs/release-smoke-evidence-protocol.md
D scripts/check_nodes_api.cmd
D scripts/validate_container_smoke.ps1
D scripts/validate_public_site.ps1
```

This means PR #20 must not be merged as-is even if tests are green.

## Remaining useful material in PR #20

PR #20 still contains useful candidate material, but it needs to be split or
rebuilt from fresh `master`:

```text
bio-threat source registry contract and tests
autonomous executor default-off gate and tests
mesh sync default-closed gate and tests
false-narrative copy guard
world-model shape regression test
CI unittest workflow changes
Railway/dependency cleanup
README/release-checklist wording
```

Several low-risk successor slices have already landed on `master` separately.
The remaining runtime and deployment-adjacent material should be reintroduced
only through fresh, narrow branches.

## Decision

Current decision:

```text
PR #20 is closed as superseded
do not reopen or merge PR #20 as-is
do not use PR #20 branch state as the source of truth for current master
use PR #20 only as historical inventory for scoped successor branches
```

Safest next action:

```text
create successor branches from current master, one scope at a time
start with the smallest remaining non-runtime guardrail or test
avoid deployment/config changes until live surface evidence is explicitly needed
keep issue #18 open as the dual-use governance boundary
```

## Successor order

Recommended order from current `master`:

```text
1. false-narrative copy guard, if master lacks the exact regression coverage
2. bio-threat source registry docs/data/tests only, no polling/dashboard/response
3. world-model shape regression test, if still relevant and isolated
4. autonomous executor default-off gate
5. mesh sync default-closed gate
6. CI workflow changes after shell-injection review
7. deployment/dependency cleanup only with surface-specific evidence
```

## Hard stops

Stop for Alex review if a successor branch:

```text
deletes landed Keystone/convergence docs
deletes Render smoke scripts or workflows
enables live polling by default
enables autonomous executor behavior by default
enables mesh writes by default
adds operational bio-threat detail
changes deployment behavior
changes CI shell execution using untrusted input
claims live health without fresh endpoint or deployment-log evidence
```

## Confidence

| Claim | Confidence |
|---|---:|
| PR #20 must not merge as-is | 0.99 |
| PR #20 is stale relative to current master | 0.98 |
| PR #20 remains useful as inventory | 0.82 |
| Successor branches should start from current master | 0.97 |
| Issue #18 should remain open during successor work | 0.94 |
