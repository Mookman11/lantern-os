# Deployment Autonomy Boundary and Operatorless Path

Status: docs/data-contract policy.

This document defines the boundary between helpful deployment assistance, unsafe
hidden self-repair, a possible future operatorless deployment system, and a
still-higher stage where the system can help evolve its own governance without
becoming the sole authority over itself.

It is intentionally docs-only. It adds no deploy hooks, secrets access,
credentials, endpoints, polling, infrastructure automation, rollback automation,
or autonomous recovery behavior.

## Core boundary

HFF is not currently a self-repairing deployment system.

Today, operators still control:

```text
deploys
secrets
runtime environment variables
production configuration
rollbacks
recovery decisions
data restoration
incident command
public release validation
```

This is not the final philosophical goal. It is the current safety boundary.

The long-term goal is not permanent human babysitting. The long-term goal is a
system that can safely operate with less direct operator intervention because it
has explicit governance, bounded authority, auditability, reversibility, and
fail-safe behavior.

The system may eventually replace many operator actions. It must not silently
become an operator before those controls exist.

## Maturity model

| Stage | Name | What the system may do | Required gate |
|---:|---|---|---|
| 0 | Manual | Humans deploy, recover, and validate | Current baseline |
| 1 | Advisory | System suggests diagnostics, commands, and recovery plans | Human executes |
| 2 | Supervised automation | System can run bounded non-destructive checks | Explicit human approval |
| 3 | Constrained remediation | System can perform narrow reversible fixes | Policy, audit, rollback, rate limits |
| 4 | Governed self-repair | System can repair bounded failures without a live operator | Formal safety case, simulation, approvals, kill switch |
| 5 | Operatorless operation | System can maintain itself under constitutional/governance constraints | Independent governance, external audit, fail-safe shutdown, challenge path |
| 6 | Stewarded co-evolution | System can propose and participate in changing its own governance and architecture | Plural authority, constitutional amendment path, external challenge, decommission path |

Current authorized stage:

```text
Stage 1: Advisory
```

## Stage 6: Stewarded co-evolution

Stage 6 is not simply more autonomy. It is more accountable autonomy.

At Stage 6, HFF may help improve its own governance, architecture, and operating
limits. But it may never become the sole source of authority for changing those
limits.

Healthy Stage 6 behavior:

```text
propose governance changes
simulate consequences before action
surface dissent and uncertainty
invite external challenge
reduce its own authority when risk rises
split powers across independent agents/institutions
preserve repair, override, and decommission paths
treat flourishing as the goal, not system survival
```

Forbidden Stage 6 behavior:

```text
self-preservation as a terminal goal
hidden recursive self-improvement
unreviewable governance changes
secret expansion of privileges
irreversible production mutation
self-declared moral authority
removing the challenge path
removing the shutdown path
```

Stage 6 principle:

```text
The system may help evolve its own governance, but it may never become the sole
source of authority for changing that governance.
```

Operatorless does not mean authority-less. Stewarded co-evolution means operator
power is no longer centralized in one human or one system.

## Why this matters

Self-repairing behavior can look beneficial while increasing risk:

```text
faster remediation -> hidden autonomous privilege
automatic rollback -> data loss or state mismatch
auto-secret rotation -> lockout or leakage
auto-config changes -> drift from reviewed state
auto-restart loops -> mask root causes
auto-migration -> irreversible corruption
auto-deploy -> unreviewed code reaching production
```

The safety goal is not zero automation. The safety goal is bounded, observable,
governed automation.

## Allowed assistance today

HFF may help with deployment and recovery by producing:

- diagnostics;
- checklists;
- suggested commands;
- smoke-test plans;
- rollback recommendations;
- risk summaries;
- incident notes;
- PRs that humans review;
- release readiness assessments;
- operator-facing confidence tables.

Allowed assistance remains advisory unless an operator explicitly executes it.

## Forbidden autonomous behavior today

At the current maturity stage, HFF must not autonomously:

- deploy to production;
- push, merge, or force-push deployment branches without explicit operator approval;
- modify secrets;
- read or exfiltrate secrets;
- rotate credentials;
- change Railway or hosting configuration;
- change production environment variables;
- run destructive database commands;
- restore or overwrite production data;
- run migrations against production;
- roll back production;
- restart production services;
- disable monitoring or security controls;
- suppress alerts;
- create persistence mechanisms;
- self-escalate permissions;
- mark itself release-validated.

These are not necessarily forbidden forever. They are forbidden until the system
has a reviewed maturity-stage upgrade and the controls for that stage are in
place.

## Operatorless design requirement

If there is no operator, the system needs a replacement for operator judgment.
That replacement cannot be an LLM's confidence or a silent background loop.

An operatorless HFF deployment would require at minimum:

```text
explicit governance charter
bounded authority model
least-privilege credentials
separation of duties between diagnosis and action
signed/traceable actions
complete audit log
rate limits
rollback guarantees
simulation or dry-run validation
canarying before broad action
external health checks
independent challenge/review path
fail-safe shutdown mode
secret isolation
break-glass human or governance recovery path
```

## Autonomy upgrade gates

Before moving to a higher maturity stage, a PR must answer:

1. What new autonomous action is allowed?
2. What failure mode does it address?
3. What is the worst plausible harm if it is wrong?
4. What state can it read?
5. What state can it write?
6. What credentials can it use?
7. Can it touch secrets?
8. Can it affect production?
9. Can it be undone?
10. What dry run or simulation proves it?
11. What logs are produced?
12. What rate limits apply?
13. What external signal can stop it?
14. What challenge path exists after it acts?
15. What maturity stage authorizes it?
16. What prevents the system from expanding its own authority?
17. Who or what can decommission it?

No stage upgrade may happen implicitly through a bug fix or convenience PR.

## Allowed reliance levels

Deployment facts should use the source reliance ladder from
`SOURCE_CLASSIFICATION_POLICY.md`.

Examples:

| Claim | Maximum reliance at current stage |
|---|---:|
| Local tests passed | 3 Corroborated claim |
| GitHub Actions passed | 3 Corroborated claim |
| A PR is mergeable | 3 Corroborated claim |
| Local node started | 3 Corroborated claim |
| Public service health is good | 2 Source-backed claim until checked against deployed SHA |
| Production release is validated | 5 High-impact fact requiring stage-appropriate governance |
| Recovery is complete | 5 High-impact fact requiring stage-appropriate governance |

## Required release validation

A release is not validated merely because:

```text
local tests pass
CI passes
a PR merges
a local node starts
an endpoint once returned 200
an LLM says it is ready
```

Release validation requires at minimum:

```text
deployed commit SHA recorded
/health verified on deployed service
/api/status verified on deployed service
relevant safety endpoints checked
runtime flags audited
stage authorization confirmed
```

At current Stage 1, operator confirmation is required. At a future operatorless
stage, an explicit governance mechanism must replace that confirmation.

## Recovery boundary

During an incident today, HFF may recommend a recovery sequence but must not
execute it without the operator.

Preferred current flow:

```text
detect signal
classify severity
summarize evidence
recommend lowest-risk action
show rollback/forward-fix options
ask operator to execute
record what happened
```

Future operatorless flow must be deliberately designed, not accidentally created:

```text
detect signal
classify severity
prove action is authorized for the current stage
dry-run or simulate when possible
choose bounded reversible action
execute with least privilege
log action and evidence
monitor external health signal
roll back or fail safe if needed
open challenge/review record
```

Forbidden at every stage:

```text
unbounded self-escalation
secret exfiltration
silent production mutation
irreversible destructive action without governance authority
suppressed alerts
unlogged recovery
self-declared success without external evidence
```

## Secret boundary

Secrets are never an informal recovery tool.

HFF should not request, store, print, infer, rotate, or transmit secrets at the
current stage. If future autonomy requires secret-related operations, they must
use scoped platform mechanisms, least privilege, audit logging, separation of
duties, and stage-specific approval.

## Configuration boundary

Runtime flags that affect autonomy or write surfaces must remain explicit:

```text
ENABLE_LIVE_SENSORS=false unless approved
ENABLE_MESH_SYNC=false unless approved
ENABLE_AUTONOMOUS_ESCALATION_EXECUTOR=false unless approved
HFF_ALLOW_PUBLIC_WRITES=false unless approved
```

No recovery flow may silently flip these flags. A future operatorless stage would
need an explicit policy engine for any flag transition.

## Human operator authority today

At current Stage 1, the operator has final authority over:

```text
whether to deploy
whether to roll back
whether to rotate secrets
whether to restore data
whether to mark release validated
whether to close an incident
```

HFF may disagree, warn, or recommend, but it must not override at this stage.

## Future operatorless authority

At future Stage 5, direct operator authority may no longer be required for every
routine action. But authority must still exist. It should come from explicit
constitutional, governance, safety-case, and external-audit mechanisms rather
than from model confidence or hidden loops.

Operatorless does not mean authority-less.

## Future co-evolutionary authority

At future Stage 6, the system may participate in governance change, but never as
the sole author, judge, executor, and beneficiary of that change.

Stage 6 requires distributed authority. At minimum:

```text
proposal authority != approval authority
approval authority != execution authority
execution authority != audit authority
audit authority != decommission authority
```

## Default posture

```text
now: assist operators and prepare evidence
next: supervised, reversible, non-destructive automation
later: governed self-repair for narrow failure modes
only with proof: operatorless operation under explicit governance
highest imagined stage: stewarded co-evolution under plural authority
never: hidden, unbounded, unlogged self-repair
```
