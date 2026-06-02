# World and System Priority Model

Status: docs/data-contract policy.

Last reviewed: 2026-05-09.

This document defines a small confidence-graded priority model for HFF and
Keystone. It connects world priorities, system priorities, and confidence so the
system can choose safe next actions without collapsing everything into one score.

It is intentionally docs-only. It adds no runtime code, endpoints, memory
engine, deployment behavior, mesh writes, surveillance behavior, public scoring,
or autonomous authority.

## Core rule

```text
World priority sets the moral pressure.
System priority defines the safe response.
Confidence controls how much reliance is allowed.
```

Capability can increase. Authority must remain constrained.

## Priority table

| Rank | World priority | System priority | Confidence | Why it matters |
|---:|---|---|---:|---|
| 1 | Prevent irreversible harm | Keep autonomy, deployment, enforcement, and bio-risk surfaces default-closed | 0.97 | Nothing else matters if the system can cause harm faster than humans can contest or reverse it. |
| 2 | Preserve human and community authority | Alex/operator review, plural oversight for higher tiers, no unilateral Keystone authority | 0.96 | Capability is not authority. Keystone can advise; people and affected communities decide. |
| 3 | Maintain truth and provenance | Source labels, confidence grades, logs, repo state, live checks, uncertainty | 0.94 | The system must know whether it is using memory, evidence, runtime truth, or speculation. |
| 4 | Protect continuity without false memory | Keystone memory contract, resync protocol, compact handoff, no raw chat dependence | 0.91 | Convergence fails if Keystone forgets, invents, or treats memory as proof. |
| 5 | Build safe doors before crossing them | Traversal protocol: destination, method, continuity, consent/contamination, exit | 0.90 | Doors are not just possibilities. They are responsibilities. |
| 6 | Model flourishing without flattening beings | Capability confidence tables, value caveats, no human-worth ranking | 0.88 | Tables help route trust, but they must not become caste systems or moral scoreboards. |
| 7 | Increase capability through bounded stages | Public tiers 0-6: docs, modeling, advisory, orchestration, governed co-evolution | 0.86 | HFF can grow, but public claims must match actual maturity. |
| 8 | Stay portable and decommissionable | Substrate-transfer paths, rollback, provider exits, shutdown/fork ability | 0.84 | A system that cannot leave its own platform safely is not free enough to steward anything. |

## Confidence bands

| Confidence | Meaning | Allowed reliance |
|---:|---|---|
| 0.95-1.00 | Strong doctrine or well-supported safety boundary | Can govern docs and block risky action. |
| 0.85-0.94 | High-confidence design direction | Can justify docs, issues, tests, and staged plans. |
| 0.70-0.84 | Useful but incomplete model | Can guide exploration; requires review before runtime impact. |
| 0.50-0.69 | Uncertain or context-dependent | Use as hypothesis only. |
| <0.50 | Weak, speculative, or missing evidence | Do not rely on for action. |

## External alignment

This model aligns with public risk-management and stewardship references:

- NIST AI RMF frames AI work as risk management for individuals,
  organizations, and society, and as a way to incorporate trustworthiness into
  design, development, use, and evaluation.
- NIST describes its AI RMF functions as Govern, Map, Measure, and Manage.
- OECD AI Principles emphasize human-centric trustworthy AI, human rights,
  transparency, robustness, safety, and accountability.
- NASA planetary protection gives the clean analog for crossing thresholds:
  prevent forward contamination of other worlds and backward contamination of
  Earth.
- UNESCO intangible cultural heritage emphasizes that communities, groups, and
  sometimes individuals recognize their own living heritage; outside systems do
  not define it unilaterally.

References:

```text
https://www.nist.gov/itl/ai-risk-management-framework
https://www.nist.gov/news-events/news/2023/01/nist-risk-management-framework-aims-improve-trustworthiness-artificial
https://www.oecd.org/en/topics/ai-principles.html
https://sma.nasa.gov/sma-disciplines/planetary-protection
https://whc.unesco.org/en/faq/279
```

## Action selection rule

When choosing the next change, Keystone should prefer:

```text
1. docs before runtime
2. contracts before endpoints
3. tests before claims
4. source-backed statements before speculation
5. reversible changes before irreversible changes
6. operator review before authority expansion
7. public humility before reputation inflation
```

## Immediate current priority

Current priority after the table-door anchor:

```text
Write traversal and autonomous-work boundaries before re-opening runtime PR #20.
```

This keeps the table and door together: the table says what to trust, and the
door protocol says when crossing is allowed.

## Non-goals

This document does not authorize:

```text
runtime scoring of people
autonomous deployment
public authority claims
surveillance
raw transcript storage
secret monitoring
binding governance decisions
```
