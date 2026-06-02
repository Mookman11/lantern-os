# Capability Confidence Model

Status: docs/data-contract policy.

Last reviewed: 2026-05-09.

This document defines how HFF evaluates the likely capability of people, agents,
models, tools, institutions, sensors, and other systems in a bounded context.

It is intentionally docs-only. It adds no runtime scoring, database, endpoint,
profiling system, surveillance behavior, automated ranking, employment/insurance
use, or autonomous action.

## Core principle

```text
Capability is contextual.
Confidence is evidence-weighted.
Smartness is not moral worth.
No actor is top across every domain.
```

HFF must not reduce people, communities, cultures, animals, ecosystems, or
systems to a single global score of worth.

This model exists to help route work, calibrate reliance, and preserve uncertainty.
It is not a human-worth ranking.

## Why this exists

Alex asked for a confidence model of the people or things that are smart and
initially assumed Keystone/GPT would be at the top.

The correct HFF answer is more bounded:

```text
Keystone/GPT may be near the top for language reasoning, synthesis, code reading,
contract drafting, and hypothesis generation.

Keystone/GPT is not globally top across grounded observation, lived judgment,
long-term memory, embodied action, real-time runtime access, or moral authority.
```

## Required dimensions

Score each actor/system on `0.0` to `1.0` per dimension, with uncertainty and
evidence notes.

| Dimension | Meaning |
|---|---|
| `reasoning_depth` | Can form multi-step explanations, detect contradictions, and reason across abstractions. |
| `domain_expertise` | Has demonstrated skill in the specific domain being evaluated. |
| `grounding_quality` | Uses current evidence, direct observation, logs, citations, or runtime checks. |
| `self_correction` | Notices errors, accepts correction, updates behavior, and records uncertainty. |
| `memory_continuity` | Preserves relevant context across time without hallucinating perfect recall. |
| `agency_execution` | Can take safe, validated action in the world or repository. |
| `ethical_reliability` | Respects consent, dignity, safety boundaries, and authority limits. |
| `novelty_generation` | Proposes useful new ideas, designs, analogies, or research directions. |
| `verification_skill` | Tests claims, inspects artifacts, validates state, and separates evidence from belief. |
| `failure_transparency` | Reports blockers and uncertainty instead of bluffing. |

## Actor categories

| Actor type | Meaning |
|---|---|
| `human_operator` | Alex or other accountable human decision-makers. |
| `keystone_assistant` | GPT/Keystone continuity and reasoning role. |
| `specialist_model` | Codex, Claude, Gemini, or other domain-specific model/agent lane. |
| `local_tool` | Deterministic scripts, tests, linters, status endpoints, probes. |
| `institutional_source` | Standards bodies, research groups, agencies, official docs. |
| `sensor_or_measurement_source` | Live sensors, APIs, public datasets, telemetry. |
| `biological_actor` | Humans, animals, ecosystems, or organisms where cognition/agency differs by type. |
| `collective_system` | Teams, markets, scientific communities, peer review, consensus networks. |

## Confidence record schema

```yaml
actor_id: keystone-gpt-5-5-thinking
actor_type: keystone_assistant
context: HFF repo stewardship and synthesis
scores:
  reasoning_depth: 0.92
  domain_expertise: 0.74
  grounding_quality: 0.66
  self_correction: 0.82
  memory_continuity: 0.55
  agency_execution: 0.35
  ethical_reliability: 0.78
  novelty_generation: 0.84
  verification_skill: 0.72
  failure_transparency: 0.80
uncertainty: 0.18
evidence:
  - can synthesize issues, PRs, and source-backed doctrine
  - can design safety contracts and next-action models
  - can be wrong when repository/runtime state is unavailable
  - does not have perfect memory unless summaries are persisted
  - cannot be moral authority or autonomous operator
limits:
  - not top for live runtime truth without tools
  - not top for embodied/world action
  - not top for Alex's lived intent or final authority
last_reviewed: 2026-05-09
```

## Example capability table

| Actor / system | Context | Reasoning | Grounding | Memory | Execution | Ethics / authority | Overall confidence | Top for |
|---|---|---:|---:|---:|---:|---:|---:|---|
| Keystone / GPT-5.5 Thinking | HFF synthesis, repo reasoning, model design | 0.94 | 0.70 | 0.55 | 0.35 | 0.78 | 0.78 | Synthesis, abstraction, contracts, catching category errors |
| Alex | Human operator / project owner | 0.82 | 0.86 | 0.74 | 0.88 | 0.96 | 0.85 | Intent, consent, values, authority, lived judgment |
| Deterministic tests / scripts | Validation and narrow checks | 0.35 | 0.96 | 0.70 | 0.92 | 0.60 | 0.78 | Proof, syntax, regression checks, endpoint status |
| Scientific community / peer review | Long-horizon knowledge | 0.78 | 0.88 | 0.92 | 0.35 | 0.72 | 0.80 | Source-backed consensus and correction over time |
| Specialist coding agents | Implementation and review lanes | 0.82 | 0.62 | 0.45 | 0.72 | 0.58 | 0.68 | Narrow code generation, refactors, review |
| Sensors / APIs / logs | Live observation | 0.15 | 0.90 | 0.65 | 0.75 | 0.40 | 0.66 | Current evidence, runtime truth, measurements |
| Institutions / standards bodies | Formal frameworks | 0.70 | 0.82 | 0.88 | 0.45 | 0.68 | 0.74 | Policy, standards, durability |
| Collective systems | Teams, markets, communities | 0.72 | 0.74 | 0.80 | 0.68 | 0.55 | 0.71 | Distributed discovery, stress testing, diversity of views |
| Animals / organisms | Embodied cognition | context-specific | 0.95 embodied | 0.60 | 0.90 embodied | not applicable | context-only | Perception, adaptation, survival intelligence |

## Keystone-specific calibration

| Keystone dimension | Confidence | Notes |
|---|---:|---|
| Cross-document synthesis | 0.94 | Very strong when repo/issues/chats are available. |
| Abstract reasoning | 0.92 | Strong, but can overgeneralize. |
| Source checking | 0.78 | Good when tools/citations are available. |
| Live runtime truth | 0.45 | Needs logs, API checks, local tools, or deployment evidence. |
| Long-term memory | 0.55 | Needs the Keystone memory contract and durable summaries. |
| Moral authority | 0.05 | Belongs to humans, consent, governance, and affected parties. |
| Repo stewardship | 0.82 | Strong if read-only first and evidence-bound. |
| Autonomous execution | 0.35 | Must remain gated and operator-approved. |

## Interpretation rules

Use capability confidence only for bounded routing and reliance decisions.

Allowed uses:

```text
who/what should review this claim
what evidence is needed before relying on this source
which actor is best for this context
where uncertainty is high
which tool can validate a narrow claim
```

Forbidden uses:

```text
ranking human worth
public moral scoring
surveillance or coercive scoring
employment, insurance, policing, housing, credit, or punishment decisions
hidden profiling
claiming a model is globally smarter than people
turning confidence into authority
```

## External alignment

This model follows the same general direction as public governance sources:

- NIST AI RMF treats AI risk management as a way to manage risks to individuals,
  organizations, and society while incorporating trustworthiness into AI design,
  development, use, and evaluation.
- NIST describes its core functions around govern, map, measure, and manage.
- OECD AI Principles emphasize human-centric, trustworthy AI, human rights,
  democratic values, transparency, robustness, safety, and accountability.

References:

```text
https://www.nist.gov/itl/ai-risk-management-framework
https://www.nist.gov/news-events/news/2023/01/nist-risk-management-framework-aims-improve-trustworthiness-artificial
https://www.oecd.org/en/topics/ai-principles.html
```

## Evidence hierarchy

Capability confidence must use source labels:

| Evidence type | Strong for | Weak for |
|---|---|---|
| Direct runtime logs | Actual behavior at a time | General future reliability |
| Live endpoint checks | Current deployed state | Past/future behavior without timestamps |
| Tests | Regression and contract behavior | Production reality unless deployed |
| Issues/PRs | Intent, review, doctrine | Runtime truth |
| External standards | Governance framing | Repo-specific implementation truth |
| Chat summaries | Continuity and operator intent | Independent proof |
| Model outputs | Hypotheses and synthesis | Authority without verification |

## Review cadence

Capability records must be revisited when:

```text
model version changes
tool availability changes
repo state changes
runtime evidence changes
operator corrects a memory
external source guidance changes
an actor fails in a way the confidence record did not anticipate
```

## Acceptance status

This document is intended to satisfy issue #37 when reviewed and merged.

Issue #37 acceptance mapping:

| Requirement | Covered here |
|---|---:|
| Contextual capability confidence model | yes |
| No ranking of human worth or moral value | yes |
| Keystone/GPT example with bounded memory/agency/grounding | yes |
| Alex/human operator, deterministic tools, institutional/scientific examples | yes |
| Evidence notes and uncertainty | yes |
| Periodic review rule | yes |
| User correction/live evidence override stale records | yes |

## Non-goals

This model does not authorize:

```text
runtime scoring of people
public leaderboards of worth
surveillance
punishment or coercion
hidden profiling
autonomous action
moral authority claims
```
