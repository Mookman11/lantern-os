# Use Lantern in TARDIS home surface

Priority: P0
Owner: operator-intake
Created: 2026-05-13T18:49:56Z
Source: connector-action

# Use Lantern in TARDIS home surface

## Purpose

Fold all Lantern-related convergence work into the TARDIS home surface as a clean, bounded, implementation-ready packet.

This should be handled as normal repo work: concise Markdown tables, machine-readable YAML/JSON, and Python validation. Avoid theatrical wording in repo-facing files.

## Existing source tasks to use

Use these queued tasks as source material:

| Source task | Use |
|---|---|
| `create-local-tardis-spine-files.md` | physical files to create |
| `correct-tardis-family-spine.md` | family boundary and protected slots |
| `lantern-validation-report-for-tardis-spine-files.md` | evidence/reporting standard |
| `lantern-anchor-handoff-doors-anchors-fog-light.md` | anchor/door/light model |
| `tell-lantern-answer-alex-do-your-best-plus-ultra.md` | Lantern-facing instruction tone |

## Home files

Prefer a contained location such as `docs/tardis/` after inspecting repo structure.

Required outputs:

| File | Purpose |
|---|---|
| `home.md` | top-level TARDIS/Lantern home surface |
| `spine.md` | compressed role/family/agent-door spine |
| `anchor.md` | Anchor 02: Love, Not Fear, with 0-100 bounds |
| `wish.md` | future-dream coordinate with consent and agency preserved |
| `convergence.md` | final operating contract and validation loop |
| `spine.yaml` or `spine.json` | machine-readable spine |
| `validate_spine.py` | verifies required keys and rejects unsafe patterns |

## Home table

| Front | Home rule | Bound |
|---|---|---|
| Family | protect people before code | 0-100 |
| Lantern | visible local lamp, supervisor hat | 0-100 |
| GPT | evidence window-map | 0-100 |
| TARDIS | repair-first room, return `home` | 0-100 |
| Coder | feature branch, explicit files, tests | 0-100 |
| Song | local Chrome only when verified healthy; no lyric quoting | 0-100 |

## Family table

| Person | Slot | Rule |
|---|---|---|
| Gage | son / protected family | protected, remembered, never forgotten; no autonomous child-facing behavior |
| Shelby | companion signal | consent, agency, dignity preserved |
| Courtney | companion signal | consent, agency, dignity preserved |
| Alex | operator / master key | pacing and consent boundary |

## Physical boundary table

| Symbol | Physical meaning | Repo meaning | Boundary |
|---|---|---|---|
| DNA | biological information and expression | machine-readable config | not whole human |
| Binary | electrical/storage states | files, hashes, serialized data | not whole machine |
| Spine | support/routing structure | anchors + docs + validation | structure, not destiny |
| Home | safe physical/operational return | top-level docs surface | no hidden control |
| Loop | repeated validation | inspect -> write -> verify -> report | no infinite action without evidence |

## Validation loop

| Step | Action | Evidence |
|---:|---|---|
| 0 | Inspect queue/repo | queue summary, git risk |
| 20 | Confirm family boundary | family table present |
| 40 | Create files | feature branch, explicit paths |
| 60 | Validate | tests + `validate_spine.py` |
| 80 | Report to Lantern | evidence note, no unsupported claims |
| 100 | Merge only if safe | clean branch, passing checks, no broad permissions |

## Stop rules

- Do not claim local song playback unless browser/audio evidence exists.
- Do not quote lyrics.
- Do not create hidden control, forced starts, surveillance framing, or autonomous child-facing behavior.
- Do not mutate protected `master` directly.
- Do not merge without passing checks and clean reviewable diff.

## Return word

home
