# Imagniverse

Status: **held** --- concept defined, not yet built  
Scope: visual imagination workspace within Lantern OS  
Source: operator concept request (2026-05-31)  
Validation state: spec-only, no running code  
Operator boundary: requires operator approval before promotion to active

---

## Simple Answer

Imagniverse is a visual imagination workspace that complements the Dream Journal (text-based) by giving the operator a place to collect, arrange, and connect images, colors, symbols, and visual ideas.

Think of it as a personal mood board engine: a creative sandbox where visual concepts live alongside the written threads in Courtney's Well.

---

## What It Actually Does

Imagniverse provides four capabilities once built:

1. **Boards** --- named collections of visual elements (images, color swatches, text cards, symbol glyphs) that the operator can arrange freely on a spatial canvas.
2. **Visual concept mapping** --- lightweight lines and groupings that connect elements across a board, showing relationships between ideas without forcing a hierarchy.
3. **Creative prompts** --- optional seed prompts drawn from Dream Journal threads, HFF dimensions, or operator-defined themes to spark new visual exploration.
4. **Image collections** --- a local-first library of images (uploaded, captured, or linked) that can be pulled onto any board.

All data stays local-first, consistent with Lantern OS storage policy. No external API calls, no cloud sync, no AI generation in the initial spec.

---

## Evidence / Source Discipline

| Item | Source | State |
|---|---|---|
| Concept name | operator request | confirmed |
| Relationship to Dream Journal | operator request | confirmed --- visual complement to text-based Well |
| Feature list (boards, mapping, prompts, collections) | inferred from operator description and Lantern creative suite patterns | held --- awaiting operator review |
| Technology choices | not yet specified | pending |
| Data model | not yet specified | pending |

No running code exists. No screenshots, no API surface, no tests. This document is the first artifact.

---

## Proven / Held / Local-Only

| Layer | State |
|---|---|
| Concept definition | **held** --- written here, not yet operator-approved |
| HTML scaffold | **held** --- placeholder page exists at `/imagniverse.html` |
| Board engine | **not started** |
| Image storage | **not started** |
| Creative prompts | **not started** |
| Visual mapping | **not started** |
| Dream Journal integration | **not started** |
| Data persistence | **not started** --- will follow local-first JSON/JSONL pattern |

---

## Next Safe Action

1. Operator reviews this spec and the HTML scaffold.
2. Operator approves, adjusts, or rejects feature list.
3. If approved, build a minimal board view: a canvas where the operator can place and move text cards.
4. Add local JSON storage for boards and elements.
5. Connect to Dream Journal threads as optional prompt sources.

Do not build beyond the scaffold until the operator confirms the concept direction.

---

## Validation Path

**Spec validation:**

- Read this document; confirm sections 1--9 are present and coherent.
- Verify the HTML scaffold loads at `/imagniverse.html` from the garage server.
- Confirm the garage dashboard links to the scaffold.

**Future build validation (post-approval):**

```text
1. Operator can create a new board.
2. Operator can add a text card to the board.
3. Operator can move the card on the canvas.
4. Board persists across page reloads (local JSON).
5. No external network calls during board use.
```

---

## Appendices

### Relationship to existing surfaces

| Surface | Role | Imagniverse relationship |
|---|---|---|
| Courtney's Well | text-based dream/thread journal | Imagniverse is the visual counterpart |
| The View (dreamer-dashboard) | analytics over Well threads | future: Imagniverse boards could reference View patterns |
| Art Matrix | curated 20-panel art display | static gallery; Imagniverse is interactive workspace |
| Outreach | public-facing program page | no direct relationship |

### Naming

The name "Imagniverse" combines "imagination" and "universe" --- a personal universe of visual ideas. Prior repo references used "ImaginiVerse" (with a capital V); this spec normalizes to "Imagniverse" per operator direction.
