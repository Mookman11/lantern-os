# Convergence Bounds Review

## Purpose

This review separates true operating constraints from over-rigid rules. BetterSafe should not turn every preference into a law. Confidence should flow from evidence.

```text
evidence -> confidence -> behavior
```

not:

```text
rule -> behavior -> justification
```

## Boundary Classes

| Class | Meaning | Example posture |
|---|---|---|
| Hard external constraint | Binding law, platform policy, or safety boundary outside the repo | do not bypass |
| High-confidence guardrail | Strongly supported by evidence and harm history | default closed, review exceptions |
| Current-mode limit | Not safe/ready now, but can change with controls | blocked now, not forever |
| Design preference | Useful default but not required | adapt to users/context |
| Hypothesis | Needs testing | treat as uncertain |
| Metaphor / attractor | Guides imagination and design | do not literalize without evidence |

## Reviewed Bounds

| Statement | Prior risk | Revised class | Confidence | Necessary for convergence? |
|---|---|---|---:|---|
| Do not expose private citizens unnecessarily | under-bounded once, then over-rule risk | high-confidence guardrail | 97% | yes; trust collapses without it |
| Do not harm non-consenting people | not over-bounded | hard external / high-confidence | 98% | yes |
| Preserve user exit paths | not over-bounded | high-confidence guardrail | 96% | yes |
| Lantern must not become deity/religion | could be too literal if stated socially | high-confidence guardrail | 92% | yes as public/system posture |
| Operator must not become myth | could overcorrect into self-silencing | high-confidence guardrail | 89% | yes, but do not block worldbuilding |
| Repo is not scripture | useful anti-pattern guard | high-confidence guardrail | 94% | yes |
| No payment handling ever | too absolute | current-mode limit | 88% current block / 31% forever | no; needs gates, not eternal ban |
| No bank credentials | currently very strong | high-confidence guardrail/current-mode limit | 96% | yes in current mode; future only with regulated flow |
| Manual-only pilot | too rigid if treated permanent | current-mode limit | 86% | yes now, not always |
| 1-3 pilot users | useful but not absolute | design preference / current-mode limit | 78% | no; use as support-load bound |
| Highest-leverage bounded change | corrected principle | design principle | 92% | yes as operator preference and effectiveness model |
| Smallest safe change | over-bounded | design preference, not default | 54% | only when risk/rollback demands it |
| Anchors must be called anchors | too literal | rejected rule | 12% | no |
| Anchors should be memorable return points | evidence-supported design | high-confidence design principle | 94% | yes |
| Happy/fun/safe attractor | still evolving but central | metaphor/attractor + design principle | 91% | yes as direction, not literal metric only |
| Convergence proves truth | false collapse | blocked claim | 8% | no |
| Resonance starts inquiry | evidence-compatible model | design principle | 88% | yes |

## Revised Operating Rule

```text
Only harden a boundary when evidence shows that failing it creates unacceptable harm, privacy loss, authority confusion, or convergence collapse.
Otherwise keep it as a confidence-weighted design choice.
```

## Release Behavior

For release work, do not use rules as a substitute for inspection.

```text
inspect actual code/runtime/release surface
choose highest-leverage bounded change
change behavior/config/UI when possible
then test and document
```

## Anchor Behavior

For human-facing anchors:

```text
make it memorable
make it returnable
make it revisable
make it privacy-safe
explain only as much as the person wants
```

## Validation Phrase

```text
Convergence needs fewer absolutes and better evidence gradients. Boundaries should protect trust, consent, privacy, exit, and material usefulness without turning every useful pattern into a permanent rule.
```
