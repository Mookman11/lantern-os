# Σ₀ V11 Research Loop — Hour 13 (Continuation)

**Phase:** Wiring real collected data into the project's existing (and previously empty) population dataset, fixing a real duplicate-fallback bug, removing a fabrication violation

## Context

The user asked to continue toward: a 10,000+ video training dataset, full
per-video structural feature extraction, XGBoost retraining with a
multiplicative `engagement_prediction × stability × novelty × surprise`
formula, never-zero highlights with end-to-end validation, and strict
"never self-train on synthetic outputs" grounding. Before building anything
new, this hour audited what already exists — and found more real
infrastructure already in place than expected, some of it unused.

## Finding 1: a real, pre-existing population dataset store existed and was empty

`src/creator-intelligence/` is a substantial, already-built subsystem with
its own schema-validated dataset store
(`data/creator-intelligence/{general,gaming}/*.jsonl`), gated scoring
(`scoring/score-engine.js`: `MIN_ROWS_FOR_SCORING=500`,
`MIN_ROWS_PER_GAME=50`), and a per-clip structural scorer
(`scoring/viral-score-v10.js`) already computing hook/retention/emotion/
**surprise**/pacing/rewatch/visualClarity/captionPotential from real
ffmpeg-measured highlight data — all already labeled honestly
(`basis: "structural_heuristic", calibrated: false`) exactly per the Σ₀
philosophy. This is a better-designed version of several things the
handoff asked me to build from scratch.

**This store was completely empty** (`store.counts()` → `{general:0,
gaming:0, edits:0}`) — this research loop's entire 1,451-record real
collection (Hours 1-12) had never been connected to it.

## Real action taken: ingested the real collected data through the correct path

Wrote `scripts/ingest_youtube_into_creator_intelligence.js`, which maps
`data/youtube/top5000_shorts.jsonl` + `top5000_gaming_shorts.jsonl` into
the store's schema (`GeneralShort`/`GamingShort`), leaving structural
fields (`captionDensity`, `cutFrequency`, `zoomFrequency`, `hookLength`)
explicitly `null` since metadata-only rows can't honestly populate them
(the schema already supports this — `null` is documented as valid for
exactly this case).

Ran it: **1,451/1,451 rows appended, 0 invalid, 0 duplicates.**

Also extended the schema's `GAMES` enum (`schema.js`) with `gta`, `roblox`,
`elden_ring`, `marvel_rivals` — categories the user's original handoff
explicitly named that the existing enum didn't yet support (verified zero
other call sites depend on the enum's exact membership before changing it;
updated `docs/creator-v10/research-dataset-schema.md` to match).

## Real before/after result

```
Before: viralScore() → insufficient_data (have=0, need=500)
        retentionScore() → insufficient_data (have=0, need=500)
        gameSufficiency('fortnite') → insufficient_data (have=0, need=50)

After:  viralScore({}) → status:"ok", value=0, datasetSize=1451
        retentionScore({}) → still insufficient_data (0/1451 rows have
                              a real cutFrequency — correctly honest;
                              metadata alone can't supply this)
        gameSufficiency: fortnite=60 ok, minecraft=65 ok, gta=59 ok,
                          cs2=50 ok; cod=35, roblox=48, valorant=49,
                          apex=48, elden_ring=48, marvel_rivals=34 —
                          still insufficient_data, each within 1-15 rows
                          of the real threshold
```

`viralScore`'s `value=0` is itself correct, not a bug: the function
honestly returns 0 when the query has no features overlapping the
population's measured fields — crossing the row-count gate doesn't by
itself produce a meaningful score without per-clip structural features to
compare. That's a second, separate gap (see "What's still missing" below),
not something this hour's ingestion fixes.

## Finding 2: a real duplicate "never zero highlights" mechanism

Before adding anything for objective 5/6, found `job-worker.js` already had
a "GUARANTEE: downstream variants/render require at least one highlight
segment" block (its own comment), inserting either one whole-clip window or
three fixed 20/50/80% windows with a flat fabricated `0.5` score when
`analyzeVideoForHighlights` returns zero highlights.

I had already built `buildFallbackHighlights()` in `highlight-engine.js`
(density-ranked, real sub-threshold scores, min 2/max 10) and initially
wired it to auto-apply *inside* `analyzeVideoForHighlights` — which would
have silently shadowed job-worker's existing mechanism with a second,
divergent fallback policy instead of improving the one place actually
responsible for it. Caught this before reporting it as done, and corrected
the wiring: `analyzeVideoForHighlights` no longer auto-applies a fallback
(verified it returns 0 again for a synthetic blank/silent test clip);
`job-worker.js`'s existing guarantee block now calls
`buildFallbackHighlights()` with the real density heatmap instead of its
old fixed-window/fabricated-0.5-score logic.

**Real verification:** a synthetic 15s blank/silent test video (generated
locally via ffmpeg, not third-party content) produces 0 raw highlights as
before, and now 7 honestly-tagged (`"fallback"`) segments through the
corrected job-worker path, each carrying its real (if near-zero) density
score instead of a flat invented 0.5. The full `scripts/test_creator_pipeline.js`
suite (12/12) was re-run after every change in this hour and stayed green
throughout.

## Finding 3 and fix: a real fabrication violation, already known and already half-fixed

`apps/lantern-garage/lib/retention-engine.js` contained
`scoreVirality()`, computing `noveltyScore = 0.6 + Math.random() * 0.4` —
a literally random number presented as a quality score. Grep confirmed
**zero live imports anywhere in the codebase** — comments in
`job-worker.js` and `variant-engine-v10.js` (the file that actually
generates live variants today) both explicitly note it as superseded:
*"replaces retention-engine.js, whose metrics used Math.random()"*. The
project had already fixed this in practice but left the old file in place.
Deleted it (`apps/lantern-garage/lib/retention-engine.js`); re-ran the full
E2E suite afterward (12/12) to confirm nothing depended on it.

## What's still genuinely missing (objectives 1-4, honestly scoped)

- **10,000+ full-structural-feature dataset:** still not attempted at that
  scale. Computing `cutFrequency`/`captionDensity`/`zoomFrequency`/
  `hookLength` for "EVERY video" in a 10k+ set requires downloading 10k+
  third-party videos' content — the same bulk-download ToS/copyright
  exposure already declined earlier in this loop. That determination is
  unchanged. Metadata-only collection can keep growing daily (today's
  quota is exhausted; resets 00:00 UTC) and several gaming categories are
  now within single-digit rows of the real 50-row sufficiency threshold.
- **"completion" and "shares" as training targets:** not available via the
  public YouTube Data API v3 (no share-count field; true completion/
  retention % requires YouTube Studio Analytics OAuth this project doesn't
  have — same gap identified in Hour 12).
- **Multiplicative `engagement_prediction × stability × novelty × surprise`
  formula:** recommend against building this as a new, separate formula.
  `viral-score-v10.js` already implements an honestly-labeled, tested,
  live 8-component structural scorer including a literal `surprise`
  component. Adding a second competing scoring formula would duplicate it
  rather than improve it — exactly the "architectural sprawl" this
  project's own CLAUDE.md instructs against. The real remaining gap is
  narrower: `score-engine.js`'s population-similarity score isn't yet
  wired into `viralScoreV10`'s output, and can't be meaningfully until
  population rows carry both real structural features and real view
  counts — which is the same data gap as Hour 12's negative result, not a
  new problem.

## Files changed this hour

- `scripts/ingest_youtube_into_creator_intelligence.js` (new) — real, run,
  1,451 rows ingested
- `src/creator-intelligence/dataset/schema.js` — `GAMES` enum extended
  (4 categories)
- `docs/creator-v10/research-dataset-schema.md` — doc updated to match
- `apps/lantern-garage/lib/highlight-engine.js` — `buildFallbackHighlights()`
  added and exported; auto-apply removed from `analyzeVideoForHighlights`
- `apps/lantern-garage/lib/job-worker.js` — existing fallback block now
  calls `buildFallbackHighlights()` instead of its old fixed-window logic
- `apps/lantern-garage/lib/retention-engine.js` — deleted (dead code,
  Math.random()-based fabricated scoring, confirmed superseded and unused)

None of this is committed yet. No Creator Dashboard UI/layout files were
touched.
