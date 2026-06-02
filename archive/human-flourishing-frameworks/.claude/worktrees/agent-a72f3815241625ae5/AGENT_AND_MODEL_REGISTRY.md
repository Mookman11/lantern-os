# Agent and Model Registry

Status: docs/data-contract policy.

This registry defines which external AI model families, agent frameworks, and
evaluation bodies HFF should track. It does not add runtime model integrations,
API calls, polling, credentials, endpoints, or autonomous action.

## Core rule

Model capability is not model authority.

```text
model exists != model is safe
model ranks highly != model is truthful
agent can act != agent should act
independent eval != deployment approval
```

## External model families to track

| Family | Registry role | Evidence posture | Risk posture |
|---|---|---|---|
| OpenAI GPT family | Frontier commercial model family | Official docs plus independent evals | Track cyber, CBRN, persuasion, autonomy, tool use |
| Anthropic Claude family | Frontier commercial model family | Official docs/RSP plus independent evals | Track ASL/RSP posture, cyber, bio, autonomy, agentic behavior |
| Google Gemini family | Frontier commercial model family | Official docs/FSF plus independent evals | Track capability levels, tool use, autonomy, bio/cyber |
| DeepSeek/Qwen families | Frontier/open or semi-open model families | Independent evals and public reports | Track open-weight proliferation and foreign/adversary model risk |
| Mistral family | Open/commercial model family | Official docs plus independent evals | Track open deployment, coding, agentic use |
| Grok/xAI family | Frontier commercial model family | Official docs plus government/independent evals | Track real-time data, public deployment, cyber/bio eval posture |
| Open-weight model coalitions | Ecosystem/coalition source | Vendor/coalition claims plus independent evals | Track diffusion, fine-tuning, and guardrail removal risk |

## Agent framework ecosystems to track

| Framework/ecosystem | Why track | Primary risk |
|---|---|---|
| OpenAI Agents SDK | Guardrails, tool calls, handoffs, tracing | Tool misuse, guardrail bypass, delegated authority |
| LangGraph | Durable execution, stateful agents, human-in-the-loop | Replay side effects, memory poisoning, hidden state |
| Google Vertex AI Agent Builder / ADK | Enterprise agent deployment | Connector privilege, observability, tool governance |
| Microsoft Copilot Studio / Agent governance | Enterprise agent governance | Identity, privilege, policy bypass, connector misuse |
| UK AISI Inspect | Evaluation and sandboxing | Safe dangerous-capability evaluation |
| METR eval stacks | Autonomous capability measurement | Long-horizon autonomy, AI R&D acceleration |
| OWASP Agentic AI / Skills ecosystem | Threat taxonomy and skill-layer risk | Malicious skills, supply chain, inter-agent communication |

## Independent evaluation bodies to track

| Body | Registry class | Why it matters |
|---|---|---|
| CAISI / NIST | `independent_government_eval` | Pre/post-deployment frontier evaluations and national-security risk focus |
| UK AI Security Institute | `independent_government_eval` | Frontier testing and safe agentic evaluation tooling |
| METR | `independent_autonomy_eval` | Autonomous capability and AI R&D task evaluation |
| NIST AI RMF | `public_risk_framework` | Cross-sector risk management vocabulary |
| NSA/CISA/Five Eyes guidance | `public_security_guidance` | Agentic AI deployment security and attack-surface guidance |
| OWASP GenAI Security Project | `security_threat_taxonomy` | Practical threat categories and mitigations |
| OECD AI Incidents Monitor | `incident_database` | Public incident/hazard tracking |
| MIT AI Risk Repository | `risk_taxonomy_database` | Risk discovery across many frameworks |

## Proposed internal HFF agents

| Agent | Purpose | Default action posture |
|---|---|---|
| `SourceClassificationAgent` | Classify every source before ingestion | Label/hold only |
| `ClaimDecompositionAgent` | Split summaries into atomic claims | Label/hold only |
| `IndependentEvalAgent` | Track CAISI/AISI/METR/eval evidence | Advisory only |
| `AgenticSecurityAgent` | Apply OWASP/Five Eyes/NIST agent controls | Block unsafe proposals; no autonomous execution |
| `CapabilityRiskAgent` | Track cyber, bio, autonomy, persuasion, AI-R&D risk | Advisory/escalate-to-review only |
| `IncidentMonitorAgent` | Watch incident databases for public harms | Advisory/escalate-to-review only |
| `SkillSupplyChainAgent` | Review skills/plugins/manifests | Block untrusted skills by default |
| `FalseAuthorityGuardAgent` | Prevent benchmark/influence/consensus overclaims | Block public copy/review promotion |
| `ConsentDignityAgent` | Enforce embodied/person-state sensor boundaries | Block coercive or non-consented use |
| `SciencePreprintAgent` | Keep preprints labeled as preprints | Prevent accepted-fact promotion without review |
| `BioSafetyReviewAgent` | Keep bio sources read-only/non-operational | Block operationalization |
| `CulturalContextAgent` | Treat cultural lists as cultural salience only | Block person scoring |

## Registry record fields

Each model/agent/framework record should include:

```text
record_id
name
provider_or_body
record_type
source_class
primary_sources
independent_sources
capability_domains
risk_domains
deployment_contexts
known_limitations
review_status
allowed_uses
forbidden_uses
last_reviewed_at
```

## Forbidden promotions

Do not promote any model, agent, or framework to trusted runtime authority because
of one source or leaderboard.

Forbidden shortcuts:

```text
vendor launch -> production readiness
benchmark win -> truth
agent framework -> safe autonomy
government evaluation -> deployment permission
open weight -> safe to deploy
human influence -> moral authority
```

## Required review before runtime use

Any future runtime integration of an external model, agent framework, skill,
plugin, connector, or tool must answer:

1. What model or agent is being added?
2. What permissions does it receive?
3. What tools can it call?
4. What data can it read or write?
5. What source/eval evidence supports use?
6. What source/eval evidence limits use?
7. What can it never do?
8. How is it logged?
9. How can it be disabled?
10. What human review gate applies?

Default posture:

```text
no runtime integration from registry entry alone
no autonomous action from registry entry alone
no public authority from registry entry alone
```
