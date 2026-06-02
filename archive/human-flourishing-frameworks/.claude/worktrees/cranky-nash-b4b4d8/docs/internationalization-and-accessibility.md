# Internationalization and Accessibility Posture

Status: public-readiness guardrail artifact.

## Purpose

HFF is not fully internationalized yet. This document defines the posture for
translation, plain-language summaries, accessibility, and jurisdiction-sensitive
claims so public-facing HFF material can become more globally useful without
claiming public authority.

## Current status

| Area | Status | Boundary |
|---|---|---|
| Language coverage | English-first | Do not imply global accessibility yet. |
| Plain-language summaries | Partial | Technical docs need shorter summaries. |
| Accessibility | Partial | Public UI/docs should be reviewed for screen readers, contrast, headings, and keyboard use. |
| Legal/medical/financial portability | Not established | HFF is not legal, medical, financial, or governance authority in any jurisdiction. |
| Cultural portability | Partial | Metrics and weights are value-laden and should be challengeable. |
| Translations | Not authoritative by default | Reviewed source text remains controlling unless a translation is explicitly reviewed. |

## Public-language rules

| Rule | Requirement |
|---|---|
| State scope plainly | Say what HFF does and does not do. |
| Avoid authority inflation | Do not imply HFF is a government, regulator, court, medical authority, or moral oracle. |
| Preserve uncertainty | Measurements, model outputs, and confidence estimates must show uncertainty and source class. |
| Use plain summaries | Important pages should include a non-technical summary before detailed claims. |
| Avoid culture ranking | Flourishing metrics must not rank people, cultures, nations, or moral worth. |
| Preserve challenge paths | Public claims should be correctable, reviewable, and source-backed. |

## Translation posture

Translations may help people understand the project, but they can introduce
meaning drift.

| Translation state | Meaning |
|---|---|
| Machine translated | Helpful draft only; not authoritative. |
| Human reviewed | Better public copy, still challengeable. |
| Legally reviewed | Needed before any jurisdiction-specific legal/policy reliance. |
| Source-of-truth translation | Only if explicitly designated and maintained. |

## Accessibility baseline

Public pages should aim for:

- semantic headings;
- descriptive links;
- high contrast;
- keyboard navigation;
- no meaning conveyed by color alone;
- concise tables with headings;
- readable mobile layout;
- captions or text alternatives for media;
- plain-language summaries for dense technical sections.

## Jurisdiction boundary

HFF may discuss laws, norms, and adaptive governance patterns. It must not claim
that its rules are law, that future people must obey current artifacts, or that a
public dashboard creates governance legitimacy.

## Sensor-language boundary

Use the public surface policy vocabulary:

```text
person -> bounded signal pathway -> optional device surface -> policy-controlled record
```

Avoid:

```text
person = sensor
sensor = proof
consent once = consent forever
public signal = public person
```

## Pass condition

A future public-facing page passes this posture if a non-technical reader can
understand:

1. what HFF is;
2. what HFF is not;
3. what evidence supports a claim;
4. what uncertainty remains;
5. who has authority to act;
6. how to challenge or correct the claim.
