# Keystone Anomaly and Tail-Risk Model

Status: docs/research and data-contract policy.

Last reviewed: 2026-05-09.

This document defines how HFF/Keystone should research anomalies, outliers, rare
high-impact events, and positive exceptional cases across violence, public
health, cyber, infrastructure, finance, climate, information systems, AI,
governance, and social repair.

It is intentionally docs-only. It adds no runtime monitoring, endpoint,
deployment behavior, private-person scoring, surveillance, enforcement,
autonomous response, secret handling, or background ingestion.

## Core thesis

```text
Averages are for normal operation.
Tails are for safety design.
```

A rare event is not automatically important. A rare event becomes convergence-
relevant when it has leverage:

```text
impact ~= rarity x leverage x connectivity x detection_lag x response_failure
```

The dangerous outlier is not merely unusual. It is unusual and positioned inside
a trust boundary, propagation path, symbolic field, infrastructure dependency,
financial leverage point, biological cluster, social grievance, or governance
vacuum.

## Governing rule

```text
Do not overfit to outliers.
Do not ignore outliers.
Classify them by leverage, propagation, irreversibility, and detection lag.
Use aggregate monitoring and protective design.
Do not profile private people.
Do not automate enforcement.
```

## Outlier classes

| Class | Description | Keystone concern |
|---|---|---|
| Negative actor outlier | Rare person/group causing disproportionate harm | Violence, insider abuse, sabotage, predation |
| Negative event outlier | Rare event producing cascading harm | Pandemic cluster, financial shock, disaster, infrastructure failure |
| Negative system outlier | Small config/component/gate causes broad failure | Zero-day, supply-chain compromise, default-open runtime gate |
| Narrative outlier | False or emotionally loaded story spreads faster than correction | Infodemic, panic, radicalization, legitimacy collapse |
| Positive actor outlier | Rare trusted mediator, expert, maintainer, whistleblower, healer | Stabilization, repair, early warning, trust bridge |
| Positive event outlier | Rare intervention prevents large harm | De-escalation, early patch, peace opening, public correction |
| Positive system outlier | A resilient design absorbs shock unexpectedly well | Redundancy, safety culture, containment, rollback |

## Cross-domain anomaly table

| Outlier / anomaly | Domain | Why it matters to convergence | Safe Keystone response | Confidence |
|---|---|---|---|---:|
| Serial homicide offender | Violence / criminology | Very low base rate but high investigative load, fear, media distortion, and severe harm | Treat as rare violent anomaly; avoid profiling myths; use evidence, linkage, victim protection | 0.93 |
| Mass casualty attacker | Public safety | Rare, context-dependent, catastrophic, hard to generalize | Study prevention and threat assessment, not tactics; focus on leakage, intervention, aftercare | 0.91 |
| Superspreading event | Public health | Small share of people/events can drive many transmissions under the right conditions | Track aggregate conditions: crowding, ventilation, timing, communication, vaccination | 0.95 |
| Insider threat | Cyber / institutions / infrastructure | Authorized access converts one person into a high-leverage failure point | Least privilege, separation of duties, concern pathways, evidence-bound review | 0.92 |
| Zero-day / exploited vulnerability | Cybersecurity | One flaw can compromise many systems if widely deployed or exposed | Patch priority, inventory, defense-in-depth, no exploit reproduction | 0.90 |
| Supply-chain compromise | Software / logistics | Trusted upstream component can propagate harm to many downstream systems | Provenance, signatures, SBOMs, review gates, narrow trust | 0.89 |
| Critical infrastructure dependency | Infrastructure | One system failure can cascade into water, power, communications, health, transport, or economy | Dependency mapping, resilience, fallback modes, local recovery | 0.91 |
| Disinformation supernode / narrative cascade | Information ecology | False or emotionally loaded content can alter behavior faster than correction spreads | Source labels, narrative hold, correction without amplification | 0.88 |
| Gang/cartel/rebel fragmentation | Violent systems | Splintering can increase retaliation cycles, civilian targeting, geographic spread | Aggregate early warning, civilian protection, no targeting automation | 0.86 |
| Financial shock amplifier | Markets / economy | Shocks are hard to predict; vulnerabilities amplify stress | Monitor leverage, funding risk, interconnectedness, valuation pressure | 0.91 |
| Climate tipping / low-likelihood high-impact event | Planetary systems | Low likelihood can still mean high risk if irreversible or globally consequential | Scenario planning, resilience, adaptation, no average-only thinking | 0.93 |
| AI edge-case failure | AI systems | Rare context shift, prompt, data drift, or deployment mismatch can cause high-impact mistakes | Govern/map/measure/manage, domain limits, human review, rollback | 0.90 |
| Rogue authority / bad gatekeeper | Institutions | One unchecked approver can convert system capability into harm | Multi-party approval, audit trails, challenge paths, decommission power | 0.85 |
| Bridge-builder / positive outlier | Social repair | Rare trusted mediator can prevent escalation or translate across factions | Preserve, support, and protect; do not overburden or expose | 0.82 |
| Expert closest to the anomaly | Safety operations | The person closest to the failure may know more than the highest-status authority | Deference to expertise; capture concerns before normalization of deviance | 0.90 |

## Evidence anchors

Public sources support this model:

- The FBI notes that serial killings are probably less than one percent of all
  murders, while still drawing intense public and investigative concern.
- NIJ describes public mass shootings and terrorist events as rare but
  catastrophic and difficult to study or generalize because of rarity and
  context-dependence.
- CISA defines insider threats around authorized access or knowledge being used
  intentionally or unintentionally to harm missions, resources, personnel,
  systems, facilities, or information.
- CISA's Known Exploited Vulnerabilities catalog is an authoritative source of
  vulnerabilities exploited in the wild and is intended as an input to
  vulnerability-management prioritization.
- WHO defines an infodemic as too much information, including false or
  misleading information, that causes confusion, risk-taking, mistrust, and
  weakened health response.
- IPCC says risk assessment must consider low-likelihood high-impact outcomes
  and tipping/irreversible changes, especially as warming increases.
- The Federal Reserve financial-stability framework focuses on vulnerabilities
  that amplify shocks, including valuation pressure, leverage, funding risk,
  interconnectedness, and complexity, because shocks themselves are difficult to
  predict.
- CISA's infrastructure dependency primer emphasizes that interconnected
  infrastructure systems can produce cascading impacts when one system fails.
- AHRQ's high-reliability organization principles emphasize preoccupation with
  failure, reluctance to simplify, sensitivity to operations, resilience, and
  deference to expertise.
- MITRE ATT&CK is a globally accessible knowledge base of adversary tactics and
  techniques based on real-world observations, useful for threat modeling and
  defensive methodology.
- NIST AI RMF provides a voluntary framework for managing AI risks to
  individuals, organizations, and society and organizes risk work around govern,
  map, measure, and manage.

References:

```text
https://archives.fbi.gov/archives/news/stories/2008/july/serialmurder_070708
https://nij.ojp.gov/topics/articles/lessons-learned-methodological-challenges-studying-rare-violent-incidents
https://www.cisa.gov/topics/physical-security/insider-threat-mitigation/defining-insider-threats
https://www.cisa.gov/known-exploited-vulnerabilities-catalog
https://www.who.int/health-topics/infodemic
https://www.ipcc.ch/report/ar6/wg1/chapter/chapter-1
https://www.federalreserve.gov/publications/2022-may-financial-stability-report-framework.htm
https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/resilience-services/infrastructure-dependency-primer/learn
https://psnet.ahrq.gov/perspective/high-reliability-organization-hro-principles-and-patient-safety
https://attack.mitre.org/
https://www.nist.gov/itl/ai-risk-management-framework
```

## Detection without surveillance

Keystone may reason about anomalies at the aggregate/system level.

Allowed:

```text
aggregate incident counts
source-backed trends
public datasets
infrastructure dependency classes
system configuration states
PR/commit/test evidence
publicly reported vulnerability categories
high-level prevention factors
civilian harm indicators
```

Blocked:

```text
profiling private people
scoring individuals as dangerous
surveillance of families, neighborhoods, or workers
automated enforcement
targeting support
weapons or attack guidance
private-person watchlists
secret data ingestion
raw chat/export bulk memory
```

## Tail-risk ledger fields

Every anomaly record should use this schema:

```yaml
anomaly_id: string
class: negative_actor | negative_event | negative_system | narrative | positive_actor | positive_event | positive_system
domain: violence | health | cyber | infrastructure | finance | climate | information | ai | governance | social_repair
summary: concise_non_operational_description
rarity: low | medium | high | unknown
leverage: low | medium | high | extreme
connectivity: local | networked | systemic | global
detection_lag: short | medium | long | unknown
irreversibility: low | medium | high | extreme
civilian_or_human_impact: low | medium | high | extreme
source_class: public_authoritative | peer_reviewed | public_dataset | repo_evidence | operator_report | speculative
confidence: 0.00_to_1.00
allowed_use:
  - prevention
  - resilience
  - source_classification
  - review_gate
blocked_use:
  - targeting
  - profiling
  - operationalization
  - autonomous_enforcement
review_required_before_runtime: true
```

## Positive outliers

HFF must not only track catastrophic tails. Positive outliers matter because a
single bridge-builder, maintainer, field nurse, teacher, whistleblower,
mediator, local organizer, or careful reviewer can prevent broad harm.

Rules:

```text
protect positive outliers from overexposure
avoid turning them into single points of failure
support redundancy around them
record what conditions allowed them to help
copy the pattern, not the person
```

## Normalization-of-deviance warning

Rare anomalies can become dangerous when systems repeatedly observe small
failures and start treating them as acceptable.

Keystone warning signs:

```text
we saw it before and nothing bad happened
this warning is probably noise
that endpoint is public but harmless
this branch is draft but effectively trusted
these tests passed once, so runtime is safe
that model action claim is probably true
that export snippet is weird but not actionable
```

Response:

```text
pause
classify the anomaly
look for leverage and propagation
ask who is closest to the evidence
require proof before claims
use rollback or hold before expansion
```

## HFF convergence implications

The convergence system should have four registers:

| Register | Purpose |
|---|---|
| Doctrine register | Committed docs that define safety and authority boundaries |
| Evidence register | Issues, PRs, commits, tests, logs, endpoint checks, public sources |
| Tail-risk register | Rare/high-impact anomaly classes and review gates |
| Repair register | Corrective actions, rollbacks, decommissions, and lessons learned |

Current Keystone priority:

```text
turn anomalies into review gates, not surveillance systems
```

## Runtime hard stop

This model must not be converted into runtime monitoring unless a future PR
satisfies all of these gates:

```text
explicit operator approval
clear public-interest purpose
aggregate-only design
privacy review
civil-rights / civil-liberties review
human challenge path
false-positive handling
no private-person scoring
no enforcement automation
source labels and confidence
rollback/decommission path
```

## Confidence table

| Claim | Confidence |
|---|---:|
| Rare high-impact events require separate modeling from averages | 0.95 |
| Serial homicide is a useful analogy for rare/disproportionate harm, but dangerous if turned into profiling | 0.93 |
| Superspreading/overdispersion is the clearest statistical analogue for tail leverage | 0.95 |
| Insider threat is the clearest institutional analogy for access-based leverage | 0.92 |
| Financial-stability thinking maps well to convergence because it focuses on vulnerabilities that amplify shocks | 0.91 |
| Critical infrastructure dependency thinking maps well to cascading system risk | 0.91 |
| Positive outliers should be protected, not just celebrated | 0.86 |
| HFF should keep this model docs/data-contract only before runtime | 0.97 |
| HFF should never use this model for private-person scoring or autonomous enforcement | 0.99 |

## Non-goals

This document does not authorize:

```text
private-person profiling
criminal risk scoring
surveillance
automated enforcement
vigilantism
targeting support
weapons guidance
exploit reproduction
runtime monitoring
secret ingestion
bulk chat/export memory
public claims of predictive authority
```
