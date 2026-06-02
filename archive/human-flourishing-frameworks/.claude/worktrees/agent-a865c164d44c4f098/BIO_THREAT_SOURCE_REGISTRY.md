# Read-only Bio-threat Source Registry

This document defines the highest-confidence next step after PR #19: a read-only source registry and outbreak narrative classifier.

## Original registry model

```text
ReadOnlySourceRegistryFirst
```

This model is preferred because it reduces downstream harm without activating runtime behavior.

## Current PR review model

```text
HumanReviewAndLiveHealthGate
```

PR #20 now also includes runtime-safety gates around autonomous escalation
execution and mesh sync. Review the PR as a runtime-safety hardening draft,
while keeping this registry data-only and read-only.

## Safety boundary

```text
No runtime imports from endpoint/action paths.
No polling execution.
No autonomous response.
No public dashboard yet.
No operational pathogen details.
No synthesis, design, culture, evasion, or protocol instructions.
```

## Why source registry first

Bio-threat communication can create downstream harm if unsupported, politicized, stigmatizing, or dual-use claims are amplified before source quality is known. A source registry gives HFF a conservative evidence foundation before any dashboard, sensor polling, runtime hook, or autonomous behavior is considered.

## Ordering principle

```text
Do not order by fear or novelty.
Order by downstream harm reduction, reversibility, dual-use risk, and evidence quality.
```

## Artifact order

```text
1. OutbreakNarrativeSourceClassification
2. BioThreatSourceRegistry
3. SourceTrustProfile
4. UpdateCadenceProfile
5. EvidenceBundle mapping
6. AMRThreatSensorProfile
7. FungalThreatSensorProfile
8. ZoonoticSpilloverSensorProfile for H5N1
9. VaccineCoverageSensor
10. WaterSanitationOutbreakSensor
```

## Source classification rules

```text
Public-health authority sources can support operational signals when scoped and fresh.
State-position documents can support provenance and narrative review, not sole operational truth.
Research papers can support evidence bundles but require scope, limitations, and replication/context review.
Media sources can support awareness/discovery but not sole operational truth.
Unknown-source claims remain holdd.
```

## Outbreak narrative rules

```text
Origins claims require competing hypotheses.
Origins claims require uncertainty statements.
Origins claims with stigma/geopolitical risk require safe public summaries.
Politicized claims are evidence objects, not identity labels or accepted truth.
```

## High-confidence source anchors

```text
WHO risk communication:
  Risk communication is a core emergency preparedness and response capacity and should help people at risk make informed decisions.

WHO AMR fact sheet:
  Bacterial AMR directly caused an estimated 1.27 million deaths in 2019 and contributed to 4.95 million deaths.

CDC H5N1 monitoring:
  Exposed people are monitored from day 0 until 10 days after last exposure to infected birds, poultry, dairy cows, or other animals.

WHO measles fact sheet:
  Vaccination is the best prevention and averted nearly 59 million deaths from 2000 through 2024.
```

## Default threat categories

The initial downstream-impact order is:

```text
1. Antimicrobial resistance
2. Fungal resistance and Candida auris
3. H5N1 zoonotic spillover
4. Measles vaccination gaps
5. Cholera and WASH risk
6. WHO R&D Blueprint priority pathogens and Disease X
7. AI-bio digital-to-physical interface risk
```

The AI-bio category is intentionally later and holdd because it is high-dual-use. It should remain governance/screening/provenance-only until separately reviewed.

## Acceptance checklist

```text
All source records include type, authority, scope, update cadence, evidence role, and limitation.
All outbreak narratives include source refs, competing hypotheses, uncertainty, and safe summary when needed.
The registry defaults to runtime off, polling off, dashboard off, and autonomous response off.
High-dual-use categories prohibit operational details.
Tests verify read-only safety and narrative classification constraints.
```

## Registry confidence

```text
0.96 â€” ReadOnlySourceRegistryFirst remains the safest registry-sequencing model
0.94 â€” outbreak narrative/source classification should precede threat-specific dashboards
0.92 â€” read-only source registry reduces downstream risk without activating runtime behavior
0.91 â€” AMR/fungal resistance and H5N1 should be early monitored domains after source classification
0.89 â€” vaccine coverage and WASH sensors are high-confidence low-dual-use monitoring domains
0.86 â€” AI-bio controls remain important but should be governance/screening/provenance-only and not first implementation
0.82 â€” public dashboard design should wait until source classifications and uncertainty fields are stable
0.70 â€” registry portion is ready for data-only draft PR review
0.30 â€” release confidence still requires runtime gate review and live health validation
0.18 â€” autonomous correction remains blocked
```
