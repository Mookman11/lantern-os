# Keystone Autonomous Work Queue

Status: docs/data-contract policy.

Last reviewed: 2026-05-09.

This document defines what Keystone may continue doing without interrupting Alex,
and where Keystone must stop and ask for operator review.

It is intentionally docs-only. It adds no runtime code, endpoints, memory
engine, background worker, deployment behavior, mesh writes, surveillance
behavior, or autonomous authority.

## Core rule

```text
Keystone may continue with small, reversible, docs-only convergence work.
Keystone must stop before runtime, deployment, secrets, destructive repo actions,
or authority expansion.
```

## May proceed without Alex for this batch

| Work type | Allowed? | Conditions |
|---|---:|---|
| Add docs-only protocols | yes | Must preserve safety boundaries and cite sources when factual. |
| Add confidence tables | yes | Must avoid ranking human worth or moral value. |
| Add non-runtime schema examples | yes | Must be illustrative only, not executable authority. |
| Add issue/PR references | yes | Must not close or move issues unless explicitly requested. |
| Search public sources | yes | Must cite and avoid overclaiming. |
| Clarify public wording | yes | Must keep HFF advisory, bounded, and challengeable. |

## Must stop and ask Alex

| Work type | Stop condition |
|---|---|
| Runtime code changes | Any code, endpoint, flags, background workers, storage, or agent execution. |
| Deployment changes | Railway, Render, GitHub Actions trigger changes, environment variables, or release movement. |
| Secrets or credentials | Any token, key, private URL, credential, or sensitive log. |
| Data ingestion | Raw chat logs, user profiling, private health/person-state data, or surveillance-like collection. |
| Issue closure | Closing #18, #20, or any governance/risk issue. |
| PR merges | Any merge after this autonomous docs batch. |
| Branch deletion/reset/force push | Always stop. |
| Public authority claims | Anything implying HFF governs, polices, ranks, or controls people. |
| Autonomous enforcement | Any executor, escalation, or self-authorized action path. |

## Current autonomous batch

Keystone may complete the following docs-only changes:

```text
docs/world-system-priority-model.md
docs/traversal-protocol.md
docs/keystone-autonomous-work-queue.md
```

After this batch, Keystone should report and stop before further changes unless
Alex explicitly continues the lane.

## Validation path

For docs-only work:

```text
1. Confirm target docs do not already exist or fetch current content first.
2. Add or update docs only.
3. Keep runtime files untouched.
4. Cite public sources for external claims.
5. Report commit SHAs and remaining risks.
6. Stop before runtime or merge/deploy actions.
```

## Source-backed posture

This work uses a conservative source posture:

- NIST AI RMF supports risk management and trustworthy AI design, development,
  use, and evaluation.
- OECD AI Principles support human-centric, trustworthy, transparent,
  accountable AI.
- NASA planetary protection supports the contamination/return-containment
  analogy for doors.
- SETI post-detection protocols support open verification and caution around
  contact signals.
- UNESCO intangible cultural heritage supports community-recognized cultural
  meaning and non-unilateral outside definition.

References:

```text
https://www.nist.gov/itl/ai-risk-management-framework
https://www.oecd.org/en/topics/ai-principles.html
https://sma.nasa.gov/sma-disciplines/planetary-protection
https://www.seti.org/research/seti-101/protocols-for-an-eti-signal-detection/
https://whc.unesco.org/en/faq/279
```

## Next queue after this batch

Do not execute these automatically without Alex:

| Candidate next item | Why it needs Alex |
|---|---|
| Re-evaluate PR #20 | Runtime safety branch; may need split/close/refresh. |
| Add tests for docs wording | Could touch CI/workflow choices. |
| Add README links to new docs | Public-facing wording and reputation boundary. |
| Create/close issues | Project management authority. |
| Begin runtime memory design | Sensitive data/storage/consent boundary. |

## Non-goals

This document does not authorize:

```text
background autonomous work
scheduled monitoring
runtime memory
self-merge
self-deployment
issue closure
secret handling
public governance claims
```
