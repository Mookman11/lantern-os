# Claude handoff: dashboard three-view implementation

## Owner

Claude, when available.

## Related issues and commits

- #196 disaster recovery control thread.
- #202 product-safe dashboard view separation and MCP human-agent capability model.
- Merged contract commit: `16e7d1d256b0ab155c1704af562de92e254219f2`.
- Contract file: `docs/dashboard-three-view-contract.md`.

## Current operating mode

Disaster work remains active. Do not treat this as normal backlog until #196 exits disaster.

## Mission

Update the dashboard so it supports three distinct audience views:

1. Public / shareholder view.
2. PM / customer-safe project view.
3. Developer / operator restricted view.

The current dashboard mixes product/project status with raw operator diagnostics. Fix that without weakening live dashboard data freshness, MCP status integrity, or operator access to diagnostics.

## Read first

Before editing, read:

1. `AGENTS.md`
2. `docs/agent-contract.md`
3. `docs/dashboard-three-view-contract.md`
4. #202
5. #196 latest recovery comments

## Files likely involved

- `dashboard/index-v2.html`
- `scripts/Start-Dashboard.ps1`
- `scripts/Get-OrchestratorStatus.ps1`
- optional new files:
  - `dashboard/project.html`
  - `dashboard/public.html`
  - `dashboard/operator.html`
  - `dashboard/dashboard-view-adapter.js`
  - `scripts/Test-DashboardViewRedaction.ps1`

Prefer small commits and avoid whole-file rewrites when possible.

## Required UI behavior

### PM / customer-safe project view

- Queue Status appears above Helpers.
- What Needs Attention appears in the right sidebar.
- Delete or rework the alarming `Right now / 9 / Items need a person` panel.
- Use progress/risk/next-decision language.
- No raw diagnostics.

### Public / shareholder view

- Maximum redaction.
- Focus on milestone progress, delivery health, broad risk, and next public milestone.
- No operational internals.
- Safe status language only:
  - On track
  - Monitoring risk
  - Needs decision
  - External dependency
  - Stabilization in progress

### Developer / operator restricted view

- Raw diagnostics are allowed.
- Must be clearly labeled `Developer / Operator`.
- Must not be the default public route.
- Must be explicitly gated by route or mode.

## Required redaction rules

Product/project mode must not show:

- raw agent names,
- model/provider names,
- local filesystem paths,
- task filenames,
- worktree details,
- changed file lists,
- raw PowerShell errors,
- local endpoint ports,
- internal MCP tool names unless productized.

Public/shareholder mode must not show any of the above, and also must not show:

- Claude,
- Gemini,
- Codex,
- OpenAI,
- provider/model/usage-limit details,
- GitHub issue/PR numbers unless intentionally public,
- queue file paths,
- MCP/local endpoint details.

## Safe role mapping

Map internal helper names to product-safe roles:

- Coordinator
- Automation
- Implementation helper
- Review helper
- Research helper
- Background worker

## Safe blocker mapping

Map raw blockers to product-safe categories:

- Service connection needs review
- Provider capacity unavailable
- Automation runner needs review
- Local workspace needs review
- Tooling configuration needs review

Public/shareholder blocker language should be even broader:

- On track
- Monitoring risk
- Needs decision
- External dependency
- Stabilization in progress

## MCP capability requirement

Represent Alex as a human-agent authority with these capabilities:

- GitHub connector access,
- connector configuration,
- model configuration,
- missing capability decisions,
- local shell when available.

Missing local MCP tooling must be represented as a local surface gap, not global capability absence.

## Suggested implementation order

### Commit 1: redaction adapter

Add a view adapter that converts raw status into public/project/operator presentation models.

Suggested output shape:

```json
{
  "view": "public|project|operator",
  "audience": "shareholder/public|pm/customer|developer/operator",
  "generatedAt": "",
  "headline": "",
  "summary": "",
  "progress": {
    "todo": 0,
    "working": 0,
    "done": 0,
    "blocked": 0,
    "failed": 0
  },
  "risks": [],
  "roles": [],
  "redaction": {
    "level": "maximum|product_safe|operator",
    "allowRawDiagnostics": false
  }
}
```

### Commit 2: dashboard routes / mode selection

Implement one of these patterns:

- `/dashboard/public.html`, `/dashboard/project.html`, `/dashboard/operator.html`, or
- `index-v2.html?mode=public|project|operator`.

Do not make operator mode the default.

### Commit 3: PM/customer layout changes

- Queue Status above Helpers.
- What Needs Attention in right rail.
- Replace `Right now` alarm panel with a next-decision/risk panel.

### Commit 4: public/shareholder page

Create the maximum-redaction view.

It should not expose raw operational internals or internal recovery details.

### Commit 5: tests / validation

Add a no-leak test or validation script.

Suggested forbidden-pattern checks for public/project output:

```text
C:\
/Users/
.ps1
PowerShell
Exception
stack trace
worktree
changed files
claude-main
gemini-lite
codex-main
control-actions
MCP 8787
MCP 8788
localhost
127.0.0.1
tasks/queue/
tasks\\queue\\
```

Additional public/shareholder forbidden patterns:

```text
Claude
Gemini
Codex
OpenAI
provider
model
usage limit
token limit
GitHub issue #
PR #
```

## Validation commands

Run or provide equivalent evidence:

```powershell
cd C:\Users\alexp\Documents\gm-agent-orchestrator

powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\Get-OrchestratorStatus.ps1 -Root "$PWD"
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\Test-DashboardViewRedaction.ps1 -Root "$PWD"
```

If no test script exists yet, add it as part of the PR.

## Acceptance criteria

- PM/customer view shows Queue Status first.
- PM/customer view moves What Needs Attention to the right rail.
- PM/customer view does not leak raw internals.
- Public/shareholder view exists and has maximum redaction.
- Developer/operator view remains available and explicitly restricted.
- Alex/human-agent capability is reflected in dashboard/MCP status model.
- No-leak validation passes.
- Live status freshness remains visible.
- No static fake health is introduced.
- GitHub issue #202 is updated with implementation evidence.

## Stop conditions

Stop and report before proceeding if:

- dashboard status generation fails,
- no-leak validation fails,
- operator mode becomes the default by accident,
- live status freshness is hidden,
- public/project view leaks raw diagnostic fields,
- implementation requires local secrets or connector/model changes,
- local worktree is dirty with unrelated files.

## Safety

Do not wake agents.
Do not move queue/failed tasks.
Do not close #196 or #202.
Do not claim completion until code/config changed, validation passes, audit evidence is written, and GitHub linkage is updated.
