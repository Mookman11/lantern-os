# BetterSafe Capability Profile Views

Status: pilot privacy and communication guardrail.

Related: docs/bettersafe-pilot-launch-record.md; docs/bettersafe-data-consolidation-blockchain-policy.md; docs/bettersafe-pilot-privacy-control-notice.md.

## Operator directive

Capability profiles for other people must restrict their view of internal reasoning, labels, and sensitive interpretations.

The default profile should show only what the person needs to interact safely and effectively. Do not expose internal mental-health, safety, risk, caregiver, vulnerability, trauma, burden, or speculative labels unless the person explicitly asks for that level of detail, the operator approves, or immediate safety requires a limited disclosure.

## Purpose

BetterSafe needs profiles that help people use the pilot without making them feel watched, diagnosed, scored, judged, or reduced to sensitive internal labels.

A profile is not a clinical assessment, credit profile, risk score, surveillance record, or character judgment. It is a view filter for safe interaction.

## Default view principle

```text
Show the person what helps them act.
Hide what only explains internal reasoning.
Ask before exposing sensitive labels.
```

## Capability profile levels

| Level | Audience | Allowed by default | Hidden by default |
|---|---|---|---|
| `PUBLIC_INTRO` | New or casual participant | Plain-language purpose, boundaries, controls, allowed actions | Internal labels, sensitive interpretations, confidence about personal risk |
| `PARTICIPANT_SAFE` | Person using the pilot | Their options, controls, consent choices, next steps, correction path | Sensitive labels unless requested or needed for safety |
| `TRUSTED_HELPER` | Helper chosen by participant | Task-specific support role, consent limits, what help is requested | Private history, hidden assumptions, unrelated labels |
| `OPERATOR_FULL` | Alex/operator | Full operational labels, repo state, safety gates, correction history | Still avoids unnecessary private details about others |
| `AUDITOR_REDACTED` | Reviewer/auditor | Policy, evidence, test status, de-identified examples | Personal data, private testimony, identifying details |

## Default participant profile shape

A participant-facing profile should include:

```text
what BetterSafe can help with
what BetterSafe cannot do
how to pause or stop
how to correct or retract
what information is optional
what the next safe action is
what evidence is needed
what privacy boundary applies
```

It should not include by default:

```text
internal risk labels
mental-health labels
trauma labels
sensitive family labels
private medical details
speculative motivations
caregiver burden labels assigned by the system
confidence scores about the person's vulnerability
labels that could make the person feel scored, watched, or diagnosed
```

## Explicit-request rule

If a participant asks for the deeper labels, BetterSafe may provide a careful explanation only if:

```text
the labels are relevant to the person's stated goal
the wording is non-diagnostic and non-punitive
the person is reminded they can decline or stop
the answer separates fact, operator report, inference, speculation, and unknown
the answer avoids presenting labels as identity or destiny
```

## Immediate-safety exception

If immediate safety requires disclosure, reveal the minimum useful information needed to reduce harm. Do not reveal unnecessary internal reasoning or unrelated labels.

## Profile redaction rules

Before showing a profile to someone other than the operator:

```text
remove private details not needed for the action
replace sensitive labels with plain task language
avoid mental-health or vulnerability framing unless requested
show controls before conclusions
show next step before analysis
show uncertainty without overloading the person
```

## Examples

| Internal label | Participant-safe wording |
|---|---|
| `CAREGIVER_BURDEN_HIGH` | “This task may be carrying a lot of daily responsibility. Start with one small step.” |
| `MENTAL_HEALTH_ADJACENT` | “This may be emotionally heavy. BetterSafe can help organize support, but it is not therapy.” |
| `FINANCIAL_STRESS_SIGNAL` | “This looks like an access or paperwork problem. We can map needs and options.” |
| `DOCUMENT_DEPENDENCY_TRAP` | “A missing document may be blocking several next steps. Let’s map the fastest recovery path.” |
| `HIGH_IMPACT_DOWNGRADE` | “This needs a qualified human or official process. BetterSafe can help prepare questions and documents.” |

## Prohibited profile uses

Capability profiles must not be used for:

```text
scoring people
ranking human worth
public surveillance
coercive caregiver authority
hidden profiling
automated eligibility decisions
medical, legal, financial, or emergency authority
public-chain publication of private data
```

## Convergence rule

A capability profile is acceptable only if it increases safety, agency, and clarity without exposing sensitive internal labels unnecessarily.

```text
Minimum necessary view > full internal view
```

## Confidence table

| Claim | Label | Confidence |
|---|---|---:|
| Other participants need restricted profile views | FACT_OPERATOR_REPORTED + INFERENCE | 0.94 |
| Sensitive labels can harm trust or mental health if shown by default | INFERENCE | 0.86 |
| Default participant views should show controls and next actions instead of internal analysis | HEURISTIC_CONFIDENCE | 0.88 |
| Operator needs a fuller operational view than participants | INFERENCE | 0.84 |
| Public/auditor views should be redacted and de-identified | INFERENCE | 0.90 |
