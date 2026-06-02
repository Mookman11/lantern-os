# Keystone Public-Copy Incident Memory

Status: durable incident memory and capability-improvement record.

Last reviewed: 2026-05-09.

This is a consent-aware summary of the public dashboard copy incident, not a raw
chat transcript. It intentionally excludes secrets, private logs, raw exports,
credentials, and unrelated personal content.

## Incident

The public dashboard for HFF exposed false or unsafe authority language:

```text
ALGORITHMIC GOVERNANCE
No human board
Escalations are irreversible after a 24-hour lock
```

This contradicted current Keystone/HFF doctrine:

```text
Capability is not authority.
Memory is not proof.
A deployment status is not live content proof.
Agents are advisory/demo/research workflows unless explicitly and lawfully authorized.
Escalations are review records unless an operator authorizes action.
```

## Impact

The copy implied:

```text
autonomous governance authority;
absence of human review;
irreversible escalation;
public authority without authorization;
production certainty beyond evidence.
```

This was a public trust and convergence failure, even if the underlying runtime
was not actually exercising that authority.

## What happened

Sequence summary:

```text
1. Alex identified the live Render page as unsafe.
2. Keystone initially tried entrypoint-level guards (`safe_app.py`, Dockerfile, WSGI, Procfile).
3. Alex's local validation showed Render still exposed stale/unsafe wording.
4. Evidence showed Render and Railway were separate public surfaces.
5. Source cleanup in `app.py` became the primary fix.
6. Alex pushed `e61eb081d86244ef53fd64d7b84ef3802d3a5265`, removing the remaining source phrase.
7. PR #40 and PR #41 were not merged as PRs because they were draft/outdated/non-mergeable.
8. Their safe docs-only content was landed directly on `master` and those PRs were closed as superseded.
9. PR #20 remained open/draft because it contains runtime/autonomy/bio-threat behavior and is unsafe to merge under unresolved live-state uncertainty.
```

## Capability assessment

Keystone can currently do well:

```text
inspect GitHub repo state;
read PRs/issues/commits;
create small docs/tests/source-copy commits;
close superseded draft PRs;
use operator local validation as stronger evidence than inference;
keep runtime/autonomy gates held;
turn chat memory into consent-aware repo summaries.
```

Keystone cannot currently do directly:

```text
SSH into Alex's machine;
use Alex's personal Render dashboard;
force Render redeploy without credentials/hooks;
prove Render live content when this environment cannot fetch the URL;
assume Railway success means Render success;
merge high-risk runtime PRs safely while live public state is unsettled;
store raw chat logs as durable memory without filtering.
```

## Keystone errors in this incident

```text
1. Overweighted GitHub/Railway deployment status relative to Alex's live Render validation.
2. Treated entrypoint wrappers as closer to convergence than direct source cleanup.
3. Moved one leg at a time, increasing split-surface risk.
4. Repeated plan language during connector/MCP transitions, creating script-like behavior.
5. Did not distinguish quickly enough among source truth, deployment status, live HTML, and user validation.
6. Added a PowerShell validator with a `$Retries:` interpolation bug.
7. Did not immediately account for Render being under Alex's personal account and separate from Railway.
8. Initially tried an opaque `sitecustomize.py` style path, which was rejected as too risky.
```

## Improved operating rules

```text
Live user validation beats deployment inference.
Source cleanup beats wrapper cleanup.
One public-copy incident must be handled as a bundle: source, startup paths, tests, deploy target, live validation, and outreach.
Do not claim convergence from a push, status context, or healthcheck alone.
Separate Render, Railway, local Docker, and GitHub master as distinct surfaces.
Do not commit raw chat logs; commit consent-aware incident memory.
Do not merge runtime/autonomy/bio-threat work during an unresolved public trust incident.
```

## Time-boxed convergence target

Goal: reach a defensible convergence checkpoint before Alex sleeps.

The checkpoint is not full system completion. It is:

```text
public unsafe copy absent from intended public URL;
source and docs memory committed;
unsafe runtime PRs held;
outreach-after-validation protocol prepared;
next risks and blockers clearly named.
```

Suggested cadence:

| Timebox | Target | Evidence |
|---|---|---|
| T+0 to T+15 min | Source and repo memory aligned | `app.py` source clean; incident doc committed |
| T+15 to T+30 min | Public URL rechecked | `validate_public_site.ps1` result captured for Render and/or Railway |
| T+30 to T+45 min | Deploy target resolved | Render dashboard/manual deploy status or Railway logs/status known |
| T+45 to T+60 min | Outreach packet prepared | Operator-reviewed factual message ready, not sent by Keystone |
| Sleep checkpoint | Handoff safe | One paragraph: what passed, what failed, what must not be merged overnight |

## Post-validation outreach protocol

Outreach is appropriate only after the intended public URL is fixed or the stale
surface is clearly disabled/redirected.

Outreach must be factual, short, non-alarming, and operator-sent.

Do not send model-authored outreach to officials or external parties without
operator review.

Minimum outreach packet:

```text
Subject: HFF public dashboard copy corrected

A public dashboard section previously used inaccurate authority wording that
could imply autonomous governance, no human review, and irreversible escalation.
That wording was wrong. The project is experimental/advisory software, not a
human board, regulator, court, enforcement system, or autonomous authority.

Corrected wording now describes experimental advisory agents and states that
escalations are review records only unless explicitly authorized by an operator.

Validation evidence:
- source commit: e61eb081d86244ef53fd64d7b84ef3802d3a5265
- public URL checked: <url>
- checked at: <timestamp>
- result: <pass/fail/partial>

Follow-up:
We are preserving an incident record, tightening release smoke evidence, and
holding runtime/autonomy changes until live surfaces are verified.
```

## Merge boundary

Allowed under this incident:

```text
docs-only memory;
copy/source fixes;
regression tests;
validation scripts;
closing superseded draft docs PRs;
post-validation outreach templates.
```

Blocked under this incident:

```text
PR #20 runtime/autonomy/bio-threat merge;
autonomous executor enablement;
mesh write expansion;
public claims of validated runtime safety without endpoint evidence;
raw chat transcript commit;
model-sent outreach to external people;
weaponized or coercive response.
```

## Current PR consensus

As of this note:

```text
PR #40: closed as superseded by direct docs-only commit.
PR #41: closed as superseded by direct docs-only commits.
PR #20: remains open/draft and must not be merged until live public state, runtime gates, and operator review are satisfied.
```

## Confidence table

| Claim | Confidence |
|---|---:|
| The original public copy was unsafe and misleading | 0.99 |
| Alex's local Render validation is stronger evidence than Railway status | 0.98 |
| Source cleanup in `app.py` is necessary for convergence | 0.96 |
| Entrypoint wrappers alone are insufficient convergence | 0.95 |
| PR #20 should remain held during this incident | 0.97 |
| Consent-aware summary memory is safer than raw chat-log commits | 0.99 |
| Outreach should wait for validation or disabling of stale surface | 0.93 |
