# V12 Hour 03 — Story Arc Engine (Part 4)

## Problem

The handoff: don't just stitch highlights — build a narrative
HOOK → RISING ACTION → PEAK → REACTION → PAYOFF and render it as one story.

## What was built

`apps/lantern-garage/lib/story-engine-v12.js` — `buildStoryArc(highlights)`
assigns narrative roles from **real measured properties** of segments the
highlight engine already produced, then orders them as a deliberate arc:

- **PEAK** = the single most intense real moment (score × multi-signal boost).
- **HOOK** = a strong moment to open on, preferring one that occurs at/before
  the peak (opens hot without spending the peak immediately).
- **REACTION** = the best **audio-tagged** moment occurring **after** the peak
  (a shout/celebration following the big play). Real signal only.
- **PAYOFF** = a strong **late** moment to close on.
- **RISING ACTION** = remaining strong moments, chronological, bridging
  hook → peak so tension builds.

## Honesty boundary

- There is no emotion model and no trained narrative classifier. A "reaction"
  slot is filled by a real post-peak audio segment; **if none exists the slot
  is omitted, not invented** (verified). Same for every role.
- Segments flagged by the V12 negative detectors (idle/menu/static/conversation)
  are excluded from role assignment — dead air never gets a narrative role.
- Output stays in the exact shape the render pipeline consumes
  (start/end/duration/score/tags) plus a non-breaking `role` annotation.

## Wiring

Replaced the legacy chronological `story_arc` strategy in
`variant-engine-v10.js` with this engine (defensive `require`, falls back to
the old behavior if the module is ever absent). The `role` annotation now flows
through to each variant's segment list.

## Verification (real)

- 6-segment clip incl. an idle segment → arc came out
  `hook → rising → peak → reaction → payoff`, peak = highest score, reaction =
  the post-peak audio segment, idle segment **excluded**.
- Edge cases: all-negative → empty arc (no fabrication); single segment → used
  as peak; no post-peak audio → reaction = null (not invented).
- Through the full variant engine: all 5 variants still build, story_arc
  variant carries role-annotated segments, idle stays excluded.
