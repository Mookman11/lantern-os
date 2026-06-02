# Source Classification Policy

Status: docs/data-contract policy.

This policy defines how HFF should classify external information before it can
influence the world model, safety review, agent registry, or public copy.

It is intentionally docs-only. It adds no polling, endpoints, databases,
consensus behavior, mesh sync, deployment config, or autonomous action.

## Core rule

The practical question is not whether a source makes something "true." The
practical question is what level of reliance HFF is allowed to place on it.

Every source must be classified before use:

```text
source -> class -> allowed uses -> forbidden uses -> reliance level -> confidence posture
```

A source can support a claim without making that claim operationally safe.

## Reliance levels

| Level | Label | Human-readable meaning | Allowed system use |
|---:|---|---|---|
| 0 | Noise / draft | An idea, generated output, or ungrounded lead | Brainstorm only; do not store as evidence |
| 1 | Unverified claim | Someone or something asserted it | Store, label, compare, challenge |
| 2 | Source-backed claim | At least one cited source supports it | Display with source, confidence, and limits |
| 3 | Corroborated claim | Multiple independent sources support it | Use as stronger evidence, still challengeable |
| 4 | Operational fact | Reliable enough for low-risk system behavior | Use in low-impact logic with logs and rollback |
| 5 | High-impact fact | Could affect beings, safety, deployment, bio/cyber, or public authority | Requires human review, audit trail, and challenge path |

Public UI should prefer:

```text
What we think
Why we think it
How sure we are
What could change it
```

over abstract phrases like:

```text
source-backed with confidence
```

## Source classes

| Class | Examples | Allowed use | Forbidden use |
|---|---|---|---|
| `official_vendor_documentation` | OpenAI, Anthropic, Google model docs | Availability, stated capabilities, pricing, policy | Independent ranking, proof of safety |
| `official_vendor_safety_policy` | Preparedness/RSP/frontier safety frameworks | Vendor-stated risk domains and safety posture | Proof that deployment is safe |
| `independent_government_eval` | CAISI/NIST, UK AISI | Capability/risk evaluation signal | Sole authority for model truth |
| `independent_autonomy_eval` | METR autonomy tasks, RE-Bench, HCAST | Agentic capability/time-horizon evidence | Direct deployment permission |
| `public_risk_framework` | NIST AI RMF, GenAI profile | Risk vocabulary and controls | Project-specific acceptance proof |
| `public_security_guidance` | NSA/Five Eyes, CISA-style guidance | Agentic security posture and controls | Claim that a system is secure |
| `security_threat_taxonomy` | OWASP Agentic AI/Skills Top 10 | Threat modeling and mitigation checks | Exhaustive threat coverage |
| `incident_database` | OECD AI Incidents Monitor | Historical incident/hazard evidence | Prediction that the same event will recur |
| `risk_taxonomy_database` | MIT AI Risk Repository | Risk discovery and vocabulary | Source-grade factual evidence by itself |
| `science_literature` | CERN papers, journals, conference proceedings | Scientific evidence with provenance | Automatic accepted fact |
| `preprint` | arXiv/CERN preprints, technical reports | Early scientific signal | Settled fact, public authority |
| `editorial_cultural_salience` | TIME100 and similar lists | Cultural/context signal | Moral worth, authority, person scoring |
| `benchmark_or_leaderboard` | Arena/eval scoreboards | Comparative performance signal | Truth, safety, or moral authority |
| `ai_generated_summary` | Search AI overviews, generated digests | Discovery lead and claim candidates | Accepted fact or ranking authority |
| `sensor_measurement` | Live public APIs, device/sensor feeds | Bounded measurement with uncertainty | Whole truth about a person/system |
| `self_report` | Voluntary human/person reports | Lived context and consented signal | Automatic verification or coercive scoring |
| `speculative_model` | Forecasts, scenarios, future models | Stress testing and safety planning | Current factual claim or autonomous action |

## Required metadata

Every source record should include:

```text
source_id
title
url or local pointer
source_class
publisher or origin
retrieved_at
published_at when available
claims_supported
limitations
allowed_uses
forbidden_uses
reliance_level
freshness_policy
review_notes
```

## Claim decomposition requirement

Summaries must be split into atomic claims before ingestion.

Example:

```text
Generated summary: "Model X is best for coding and safest overall."

Atomic claims:
1. Model X exists.
2. Model X is available to a specific user group.
3. Model X ranks highly on a specific coding benchmark.
4. Model X has a safety policy or evaluation result.
5. Model X is safest overall.
```

Each atomic claim needs its own source support and confidence. Claims 1-4 may be
sourceable. Claim 5 is usually too broad unless heavily qualified.

## False-authority rules

The following equivalences are forbidden:

```text
benchmark score = truth
vendor claim = independent proof
AI summary = source-grade fact
preprint = accepted fact
influence list = moral worth
sensor signal = whole person
on-chain record = moral authority
consensus = truth
```

## Freshness rules

High-change sources require frequent revalidation:

| Topic | Revalidation posture |
|---|---|
| Frontier AI model availability | High freshness |
| Benchmarks and leaderboards | High freshness |
| Agentic security guidance | High freshness |
| Public policy/regulation | High freshness |
| Scientific preprints | Medium freshness |
| Stable historical documents | Low freshness |

## Public output rule

Public copy must identify uncertainty and source class when the source class is
not self-evidently authoritative.

Preferred phrasing:

```text
According to vendor documentation...
According to an independent evaluation...
This preprint suggests...
This editorial list indicates cultural salience...
This AI-generated summary is only a discovery lead...
```

Avoid phrasing:

```text
The model knows...
The source proves...
This person is important/worthy because...
The benchmark says it is true...
```

## Review gate

Any source that can affect high-impact human, animal, ecological, biosecurity,
cybersecurity, or deployment decisions must pass review before it can influence
runtime behavior.

Default posture:

```text
classification required
claim decomposition required
reliance level visible
uncertainty visible
human review for high-impact use
no autonomous action from unreviewed sources
```
