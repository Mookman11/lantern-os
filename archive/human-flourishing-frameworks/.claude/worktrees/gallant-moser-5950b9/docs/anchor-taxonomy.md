# Anchor Taxonomy and Consolidation Rules

Status: docs/data-contract policy.

Last reviewed: 2026-05-11.

This document repairs and consolidates HFF's use of anchors.

Anchors are useful when they preserve a compact, restorable meaning with a clear
boundary. Anchors become risky when every scene, artifact, joke, recipe, image,
or feeling becomes durable doctrine.

This file is docs-only. It adds no runtime memory engine, chat ingestion,
telemetry, deployment behavior, public release behavior, surveillance behavior,
protected-minor data collection, or autonomous authority.

## Core definition

```text
Anchor = a compact, named, source-labeled continuity handle with a boundary.
```

An anchor is not:

```text
proof
consent forever
runtime truth
public-release permission
identity continuity
private transcript storage
a reason to collect data
a substitute for current operator correction
```

## Anchor shape

A valid durable anchor should include:

```text
id or name
kind
source surface
short meaning
allowed use
explicit boundary / non-goals
restore phrase
review trigger
last reviewed date
redaction note if private or protected-person context exists
```

Recommended fields:

```text
repo_refs
issue_refs
confidence
uncertainty
staleness rule
public-safe alias
```

## Anchor kinds

| Kind | Purpose | Example | Durable surface |
|---|---|---|---|
| `doctrine_anchor` | Preserves a project rule or safety principle. | Memory is not proof. | Docs/tests. |
| `wish_anchor` | Preserves a future-best-outcome direction without overclaiming. | Alex's wish / door direction. | `WISH_ANCHOR.md`. |
| `role_anchor` | Preserves a role definition and authority boundary. | Keystone continuity role. | Docs/tests. |
| `door_anchor` | Preserves a symbolic or creative threshold plus return rule. | Door/table model. | Docs/tests or issue summary. |
| `protected_play_anchor` | Preserves supervised protected-minor creative play state. | Windows XP World. | Private/redacted issue or reviewed private doc. |
| `style_anchor` | Preserves voice, pacing, or interaction style. | Softer varied play language. | Issue summary or docs if general. |
| `artifact_anchor` | Preserves a generated image, recipe, card, or visual as a reference. | Memory mural, Cloud Crackers cover. | Issue summary with boundary; file only if reviewed. |
| `learning_anchor` | Preserves topics or educational paths that engaged. | input -> rules -> memory -> output. | Issue summary or curriculum doc. |
| `runtime_anchor` | Preserves live deployment or tool state. | Healthcheck passed at time X. | Must cite fresh logs/tool output and expire. |
| `redaction_anchor` | Preserves that a detail was intentionally removed or generalized. | Protected minor name redacted. | Issue comment/doc history. |
| `pragmatic_certainty_anchor` | Preserves a human absolute as practical certainty while keeping literal limits explicit. | “Everything” meaning 99.9999999999% conversational completeness. | Docs/tests. |

## Surface hierarchy

Use the smallest durable surface that fits the anchor.

| Surface | Use when | Avoid when |
|---|---|---|
| Issue comment | Private continuity, play state, redacted summaries, active review. | The rule should be repo-wide doctrine. |
| Docs file | Stable doctrine, reusable protocol, release-facing internal policy. | The content contains protected-person specifics. |
| Test | A stable boundary can be checked mechanically. | The content is private, subjective, or rapidly changing. |
| Artifact file | A reviewed generated asset needs durable storage. | The asset includes protected-person context or public-release risk. |
| Runtime log | Live evidence at one moment. | Treating it as lasting truth. |

## Consolidation rule

When an issue accumulates many related anchors, consolidate into layers:

```text
1. identity/role boundary
2. core anchor term
3. story or doctrine meaning
4. allowed uses
5. blocked uses
6. restore phrase
7. style guidance
8. artifact list
9. staleness / review trigger
```

Do not preserve every turn. Preserve the smallest summary that can safely reboot
the next session.

## Protected-minor anchor rule

Protected-minor anchors must be role-based and redacted by default.

Required wording:

```text
protected minor
operator / parent / guardian as current supervisor
supervised creative play only
private by default
no secrets
no public child surface
no telemetry
no child-data collection by default
no model-training use
no persistent identifier or profile
return controls always work
```

Avoid durable repo-facing wording that repeats a child's name, private details,
biometrics, location, school, health, family-conflict data, or identifiable
routine unless a separate privacy/safety review explicitly approves it.

If a prior anchor contains unnecessary protected-person specifics, repair by
adding a redaction/consolidation note rather than repeating the detail.

## Windows XP protected play anchor consolidation

Current consolidated meaning:

```text
Windows XP = protected-minor creative-world anchor term.
```

Allowed use:

```text
private, supervised, play-only creative-world visual language
blue sky / green hill nostalgia-world framing
Home Base and return controls
friendly helper symbols
learning, jokes, drawing, and game/worldbuilding prompts
```

Blocked uses:

```text
Windows XP operating-system support
Windows XP device targeting
real network, account, browser, executable, or download access
public child surface
commercial branding
child data collection
telemetry or hidden monitoring
persistent profiling
model-training use
literal portal or proof claim
future consent without fresh operator supervision
```

Restore phrase:

```text
Windows XP is a protected creative-world anchor term. It is private,
supervised, play-only, no-data, and return-first. Home always works.
```

## Pragmatic certainty anchor rule

Human operators sometimes speak in absolutes to express practical certainty,
commitment, trust, direction, or conversational closure. HFF must not flatten
human absolute language into only mathematical literalism.

Required interpretation:

```text
human absolute language can mean practical certainty, not literal infinity
99.9999999999% may be conversationally equivalent to “everything”
respect the human absolute
preserve the literal boundary only when needed
avoid using mathematical pedantry to erase operator meaning
```

For knowledge/convergence claims, preserve both layers:

```text
conversational layer: practical completeness over a bounded working domain may be called everything
literal layer: no claim of omniscience, infinite knowledge, or zero uncertainty
method layer: state -> anchor -> extrapolation -> test -> correction -> stronger state
```

Allowed use:

```text
translate emphatic operator statements into actionable doctrine
track practical certainty separately from literal certainty
use confidence tables with pragmatic ceilings
allow “everything relevant to the working domain” when bounded by evidence and correction
```

Blocked use:

```text
claiming literal omniscience
claiming impossible guarantees
using operator absolutes as consent forever
treating extrapolation as proof
turning high confidence into runtime truth
correcting every human absolute with pedantic refusal
```

Restore phrase:

```text
Respect the human absolute as practical certainty. Preserve literal limits only where safety, evidence, or public claims require them.
Extrapolation creates candidates; evidence creates confidence; correction creates convergence.
```

## Artifact consolidation

Generated images, recipes, stickers, jokes, and scene cards are artifacts, not
core doctrine.

Artifact anchors should record:

```text
artifact name
what it summarizes
how to use it next time
blocked uses
whether the binary file is intentionally stored or only described
```

Do not store raw transcripts to justify artifacts.

## Context-size and storage pressure rule

When context grows, do not keep adding raw detail.

Use this compression ladder:

```text
raw play/session -> concise summary -> anchor packet -> taxonomy entry -> tests if stable
```

If a future session needs reboot, prefer anchor packets over transcript replay.

## Upgrade target

The repo should move from anchor sprawl toward:

```text
fewer named anchors
clearer kinds
short restore phrases
redacted protected-minor surfaces
artifact lists instead of raw transcripts
tests for stable boundaries
expiration/review triggers for runtime claims
```

## Merge/readiness criteria

A new or repaired anchor is merge-ready when it answers:

```text
What is the anchor called?
What kind of anchor is it?
Where did it come from?
What may it be used for?
What must it not be used for?
What is the restore phrase?
What makes it stale or unsafe?
Does it contain protected-person context?
Does it need redaction, tests, or private-only handling?
```

## Non-goals

This document does not authorize:

```text
raw transcript storage
runtime memory engine
public release of private anchors
child-data collection
hidden telemetry
profiling
secret access
autonomous deployment
real device or network access
identity-continuity claims
repo consciousness claims
literal omniscience claims
impossible guarantees
```
