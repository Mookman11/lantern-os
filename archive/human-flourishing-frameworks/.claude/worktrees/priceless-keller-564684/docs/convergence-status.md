# HFF Convergence Status

Status: docs/data-contract policy.

Last reviewed: 2026-05-09.

This document is the current convergence anchor for Human Flourishing Frameworks.
It explains what is currently agreed, what remains blocked, and which action is
safest next.

It is intentionally docs-only. It adds no runtime code, endpoints, polling,
autonomous behavior, deployment hooks, secrets access, credentials, or mesh
writes.

## Current convergence line

```text
hold runtime
anchor doctrine in docs
then re-evaluate runtime PRs
```

The active operating decision is:

```text
ConvergenceHoldAndDocsAnchorFirst
```

This means HFF should not increase runtime authority, merge broad runtime safety
branches, or add memory/autonomy machinery until the current Keystone memory and
capability-confidence contracts are durable in the repository.

## Why this is the safest next action

The repo has converged on a doctrine, but that doctrine is still distributed
across issues, pull request bodies, docs, and chat-derived summaries.

That creates a continuity risk:

```text
future agent reads only code -> misses doctrine
future agent reads only PR -> misses memory boundary
future agent reads only chat -> treats memory as proof
future agent reads only deployment state -> overclaims runtime health
surface device degrades -> operator loses access to live context
gpt/app resets -> Keystone loses recent convergence state
model/context window changes -> agent silently drops important assumptions
cross-model handoff -> external model interprets Keystone differently
```

The next safe move is to create one repo-readable anchor that future agents,
operators, and reviewers can inspect before changing runtime behavior.

## Surface and session desync risk

HFF must explicitly account for ordinary continuity failures:

```text
phone/laptop/tablet/browser degrades
network session drops
ChatGPT app goes down
model resets or changes
conversation is archived, deleted, truncated, or unavailable
memory settings change
connected tools are unavailable
another model is used for handoff
repo connector sees stale state
operator and Keystone hold different convergence summaries
```

These failures do not mean convergence is lost, but they can cause desync.

Desync means:

```text
an agent acts from stale doctrine
an operator assumes Keystone remembers something it does not
Keystone assumes a PR/issue is current when it has moved
runtime status is inferred from old logs
external model receives partial context and changes the doctrine
```

Required response:

```text
pause runtime changes
read the convergence docs
read open issues and held PRs
check current repo state
check current live runtime evidence if deployment status matters
summarize differences before acting
prefer docs-only repair over runtime change
```

## Resync protocol

When Alex says `resync`, `convergence check`, or reports lost context, use this
minimum protocol:

1. Read `docs/convergence-status.md`.
2. Read `docs/keystone-memory-contract.md`.
3. Read `docs/capability-confidence-model.md`.
4. Check open issues, especially #36, #37, and #18 until closed or superseded.
5. Check held runtime PRs, especially #20 until closed, merged, or superseded.
6. Check newest relevant PRs after the docs anchor.
7. Check current branch and commit state before assuming `master` equals runtime.
8. If ChatGPT/app availability is part of the failure, check OpenAI status and
   treat its metrics as aggregate rather than proof of the operator's local
   experience.
9. If runtime health matters, require fresh endpoint checks or deployment logs.
10. Produce a short convergence delta:
   - what changed;
   - what is still held;
   - what evidence is fresh;
   - what evidence is stale;
   - safest next action.
11. Do not merge, deploy, or enable runtime autonomy as part of resync.

Operator handoff packet for another model or degraded session:

```text
I am Alex, human operator/project owner.
Keystone is the HFF continuity/system role.
Current convergence line: hold runtime, anchor doctrine in docs, then re-evaluate runtime PRs.
Read docs/convergence-status.md, docs/keystone-memory-contract.md, docs/capability-confidence-model.md.
PR #38 is the docs-only convergence anchor.
PR #20 is held runtime work and should not be merged until re-evaluated.
Memory is not proof; repo/runtime evidence overrides memory; user correction overrides stale memory.
Do not store raw chat logs or secrets.
```

## Current doctrine spine

```text
Truth requires provenance.
Capability is not authority.
Memory is not proof.
Sensors are best-effort unless verified.
Live deployment health requires live endpoint or deployment-log evidence.
Autonomy is closed unless explicitly enabled and stage-authorized.
Alex is the human operator/project owner.
Keystone is the HFF continuity role.
Resync before action after context loss.
```

## Current issue alignment

| Issue | Status | Convergence meaning |
|---|---:|---|
| #36 Keystone memory contract | Open | Must become durable docs before Keystone memory is treated as repo state. |
| #37 Capability confidence model | Open | Must become durable docs before using actor/system confidence records. |
| #18 Dual-use engine risk | Open | Ongoing governance/security boundary; do not collapse into this PR. |
| #22 Live polling observability | Closed/completed | Live polling/status observability comes before consensus hardening. |
| #13 Live sensor diagnosis | Historical | Registered sensors are not proof of fresh or verified measurements. |
| #12 Deployment split-brain | Historical | Deployment truth must be checked against the selected live surface. |

## Current PR alignment

| Pull request | Status | Convergence meaning |
|---|---:|---|
| #20 Runtime safety gates | Open draft | Keep held. Re-evaluate after convergence docs land. |
| Recent docs/safety PRs | Merged | The doctrine is moving toward default-closed advisory behavior. |

## External alignment

The current convergence posture is consistent with public governance and platform
sources:

- NIST AI RMF frames AI work as risk management for individuals,
  organizations, and society, and as a way to incorporate trustworthiness into
  design, development, use, and evaluation.
- NIST describes the AI RMF core around govern, map, measure, and manage.
- OECD AI Principles promote human-centric, trustworthy AI that respects human
  rights and democratic values.
- OpenAI's public ChatGPT memory guidance says ChatGPT does not remember every
  detail from past chats and that users should use saved memories for anything
  that must remain top-of-mind.
- OpenAI's public status page should be checked when ChatGPT availability is part
  of the failure mode, but its availability metrics are aggregate and individual
  customer availability may vary by tier, model, and feature.
- Railway healthchecks gate deployment activation but are not continuous live
  monitoring after deployment.
- GitHub Actions job reruns use the original event SHA/ref; a rerun is not the
  same as a fresh workflow dispatch on a new target.

References:

```text
https://www.nist.gov/itl/ai-risk-management-framework
https://www.nist.gov/news-events/news/2023/01/nist-risk-management-framework-aims-improve-trustworthiness-artificial
https://www.oecd.org/en/topics/ai-principles.html
https://help.openai.com/en/articles/8590148-memory-in-chatgpt
https://status.openai.com/
https://docs.railway.com/reference/healthchecks
https://docs.github.com/en/actions/how-tos/manage-workflow-runs/re-run-workflows-and-jobs
```

## Current validation evidence

Latest available GitHub Actions rerun evidence from 2026-05-09:

```text
workflow: tests
run id: 25597347535
rerun job id: 75152786980
context: PR #35 merge-test ref, not a new master workflow dispatch
compile key modules and tests: passed
focused unittest discovery: passed
result: Ran 92 tests in 0.127s — OK
```

Important limitation:

```text
The workflow has pull_request and push-to-master triggers only.
It does not currently expose workflow_dispatch.
The rerun validated the original PR/run context, not a fresh manual master run.
```

## Current blockers

Do not mark runtime work ready until these are satisfied:

```text
Keystone memory contract committed
capability confidence model committed
convergence status committed
surface/session desync protocol committed
human review complete
live public health checked against selected deployment
runtime flags audited
write/autonomy/mesh surfaces verified default-closed
```

## Next best action

The current highest-confidence action is this docs-only convergence PR:

```text
docs/convergence-status.md
docs/keystone-memory-contract.md
docs/capability-confidence-model.md
```

Expected issue effect:

```text
satisfies #36
satisfies #37
references #18 as ongoing boundary
references #20 as held runtime PR
```

## Explicit non-goals

This convergence anchor does not authorize:

```text
runtime memory engine
raw chat transcript storage
autonomous deployment
autonomous recovery
mesh writes
bio-threat polling or dashboarding
operational pathogen detail
secret access
public scoring of people
moral authority claims
consensus hardening before live telemetry evidence
```

## Re-evaluation rule

After this docs anchor lands:

```text
review #20 again
prefer splitting broad runtime changes into small successor PRs
keep default-closed behavior as the baseline
require live endpoint/deployment-log evidence before release validation
run the resync protocol after any major context loss
```
