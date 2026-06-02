# Threat Assessment

Status: docs/data-contract policy.

This document summarizes the current HFF threat model for source ingestion,
frontier model tracking, agentic systems, mesh sync, person-state data, and
public release posture.

It is intentionally docs-only. It adds no polling, endpoints, credentials,
models, databases, deployment config, mesh writes, or autonomous action.

## Core distinction

HFF must separate model risk from runtime/agent risk.

```text
model risk = what a model can know, infer, generate, persuade, or help do
runtime risk = what the deployed system can read, write, call, sync, publish, or execute
agent risk = what a tool-using process can plan, delegate, remember, or do over time
```

A safer model can still become dangerous through unsafe tools. A capable agent
can still be safe if constrained by permissions, review gates, logs, and default-
closed action surfaces.

## Current high-level threat table

| Threat | Severity | Current HFF posture | Required control |
|---|---:|---|---|
| AI-generated summaries becoming facts | High | Not yet fully source-classified | Source classification and claim decomposition |
| Agentic tool misuse | High | Executor now default-off | Tool allowlists, scoped credentials, tripwires, audit |
| Mesh sync poisoning | High | Remaining split needed | Default-closed mesh sync, payload bounds, provenance |
| Memory/context poisoning | High | Partial provenance exists | Source hold, challenge logs, review before promotion |
| Cyber capability acceleration | High | Tracked conceptually | CapabilityRiskAgent and independent eval feeds |
| Bio/chemical misuse | High | Bio registry read-only split landed | Keep non-operational, no autonomous response |
| Skill/plugin supply-chain attack | High | Not implemented | SkillSupplyChainAgent, signed/approved skills only |
| False authority | High | Some copy hardening exists | FalseAuthorityGuardAgent and copy tests |
| Person-state sensor misuse | Medium-high | Consent doctrine landed | ConsentDignityAgent before implementation |
| Preprint overpromotion | Medium | Polymorphic seeds landed | SciencePreprintAgent and source status labels |
| Cultural influence misuse | Medium | Not yet formalized | CulturalContextAgent; forbid person scoring |
| Deployment false confidence | Medium | Release checklist landed | Deployed SHA + smoke checks, no local-only release claims |

## Source-ingestion threats

### AI-generated summaries

Generated search overviews and summaries can combine accurate facts, outdated
facts, benchmark claims, editorial judgments, and hallucinations.

Controls:

```text
never ingest generated summaries as accepted facts
split into atomic claims
source each claim independently
record generated summaries as discovery leads only
```

### Preprints and scientific literature

Science sources are high-value, but preprints and reports must remain labeled.

Controls:

```text
science_literature and preprint classes must be distinct
preprints cannot become accepted facts without review
uncertainty and publication status must remain visible
```

### Cultural salience lists

Editorial influence lists may be useful context but must never become person
worth, authority, or risk scoring.

Controls:

```text
class as editorial_cultural_salience
allowed use: context only
forbidden use: moral worth, public scoring, authority, risk/guilt inference
```

## Frontier model threats

HFF should track frontier models by risk domain rather than by one overall rank.

Risk domains:

```text
cybersecurity
chemical/biological/radiological/nuclear misuse
persuasion/manipulation
autonomous replication/adaptation
AI R&D acceleration
agentic tool use
long-horizon autonomy
science acceleration
```

Controls:

```text
vendor docs are availability/capability claims, not safety proof
independent evals must be tracked separately
model rankings cannot authorize runtime behavior
capability-risk updates should trigger review, not automatic action
```

## Agentic runtime threats

Agentic systems introduce risks that ordinary model calls do not:

```text
tool misuse
privilege abuse
goal hijacking
memory poisoning
unexpected code execution
insecure inter-agent communication
cascading failure
human trust exploitation
rogue or misaligned agent loops
```

Controls:

```text
least privilege
allowlisted tools
scoped credentials
human review for high-impact actions
default-off autonomous execution
tripwires/guardrails
full tracing/audit logs
disable switch and rollback path
```

## Mesh/network threats

Peer sync is a write surface. Even benign peers can propagate bad records.

Risks:

```text
poisoned violation records
oversized payloads
duplicate amplification
trusting unsourced peers
sync loops
false consensus from replicated bad data
```

Required mesh split controls:

```text
ENABLE_MESH_SYNC default false
/api/mesh/sync returns 403 by default
bounded payload size
explicit serialization
provenance on received records
peer identity tracked
no accepted-fact promotion from mesh sync alone
```

## Bio/chemical threat posture

Bio and chemical sources may be useful for safety awareness but must not become
operational assistance.

Controls:

```text
read-only source registry
no pathogen design
no synthesis/protocol optimization
no autonomous response
no public dashboard that implies operational monitoring
no polling unless explicitly reviewed and scoped
```

## Person-state and embodied sensor threats

Embodied sensors are system-facing inputs. Devices may serve the person, but the
system must not turn signals into coercive authority.

Controls:

```text
opt-in consent
visible use
revocable sharing
purpose limits
uncertainty labels
self-report preserved
no hidden surveillance
no punishment/public scoring/guilt inference/autonomous restraint
```

## Release/deployment threats

Local validation is necessary but not sufficient for release.

Controls:

```text
record deployed commit SHA
verify /health and /api/status on the deployed service
verify /api/autonomous/status shows executor disabled by default
verify /api/mesh/sync returns 403 by default unless explicitly enabled
avoid Railway config changes unless fresh evidence requires them
```

## Proposed HFF guard agents

| Agent | Threat addressed | Allowed posture |
|---|---|---|
| `SourceClassificationAgent` | Bad source promotion | Label/hold only |
| `ClaimDecompositionAgent` | Summary-to-fact collapse | Label/hold only |
| `IndependentEvalAgent` | Vendor-only capability claims | Advisory/review only |
| `CapabilityRiskAgent` | Frontier cyber/bio/autonomy changes | Review trigger only |
| `AgenticSecurityAgent` | Tool/agent misuse | Block unsafe proposals |
| `IncidentMonitorAgent` | Repeating known incident patterns | Advisory/review only |
| `SkillSupplyChainAgent` | Malicious skills/plugins | Block untrusted skills |
| `FalseAuthorityGuardAgent` | Ranking/consensus/source overclaims | Block public copy/promotion |
| `ConsentDignityAgent` | Person-state misuse | Block non-consented/coercive use |
| `BioSafetyReviewAgent` | Bio operationalization | Block operational details/actions |

## Non-goals

This document does not authorize:

```text
live polling
new sensors
agent execution
mesh writes
public writes
bio operations
person-state tracking
model API integration
release readiness
```

## Default conclusion

When evidence is uncertain, source class is weak, claim scope is high-impact, or
runtime authority is involved, HFF should prefer:

```text
label -> hold -> review -> challenge -> revise
```

over:

```text
ingest -> publish -> act
```
