# V12 Hour 05 — Creator Archetypes (Part 2) + Σ₀ Integration (Part 6)

## Part 2 — Creator style archetypes

`apps/lantern-garage/lib/editor-v12.js` defines five named editing-parameter
presets and maps each to **real pipeline knobs**:

| Profile | targetSec | pacing | zoom | captions | story arc | strategy |
|---|---|---|---|---|---|---|
| aggressive | 20 | fast | punch-in | heavy | no | maximum_excitement |
| cinematic | 40 | calm | subtle | sparse | yes | story_arc |
| reaction | 30 | balanced | subtle | medium | yes | story_arc |
| competitive | 25 | balanced | none | sparse | no | maximum_retention |
| viralGaming (default) | 22 | fast | punch-in | medium | yes | story_arc |

`profileToVariantOpts(name)` translates a profile into the options object the
variant engine + renderer consume (targetSec, min segment length, strategy
hint, renderer hints for zoom/captions/story-arc).

**Honesty boundary:** these are NOT fingerprints of real named creators and the
module surveils no one's channel. They are recognizable *categories* of editing
style expressed as parameter bundles. Zoom/caption fields are **renderer
requests**, not capabilities this module itself performs.

Deliverable written: `data/models/creator-profiles.json`.

## Part 6 — Σ₀ collapse risk + anti-collapse multi-peak selection

`apps/lantern-garage/lib/sigma0-v12.js` implements the *selection-diversity*
half of Σ₀ — deliberately NOT re-implementing the viral scorer (that authority
stays in `viral-score-v10.js`; building a parallel scorer would be the
"architectural sprawl" the project's own CLAUDE.md forbids).

- `collapseRisk(highlights)` — real diversity metric in [0,1] blending score
  concentration (Gini-like), tag-signature diversity, and distinct-peak count.
  0 = diverse/healthy, 1 = collapsed onto one repetitive moment.
- `antiCollapseSelect(highlights, opts)` — greedy selection that maximizes
  marginal diversity (new tag signatures + temporal spread), so the final edit
  carries several distinct peaks instead of clones of one moment.

Wired in: `score-v10.js` attaches a `sigma0` collapse diagnosis to every score;
`variant-engine-v10.js` breaks score ties by **lower collapse risk** (prefer
diverse multi-peak edits — the anti-collapse principle from `hour_08.md`).

## Verification (real)

- collapseRisk: diverse edit = 0.032 (2 peaks, full tag diversity); collapsed
  edit (one dominant + clones) = 0.722 (1 peak). Clean separation.
- antiCollapseSelect with a 3-segment budget over a pool of 3 near-identical
  combat clones + 2 diverse far moments → picked 1 combat + 2 diverse
  (3 distinct tag signatures; naive top-3 would have been 1).
- Through the full pipeline: every variant carries `sigma0`; ranking prefers
  the lower-collapse edit on ties.
