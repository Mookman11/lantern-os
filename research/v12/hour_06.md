# V12 Hour 06 — Research Harness (Part 7) + End-to-End Validation

## Part 7 — `npm run shorts-research-v12`

`scripts/shorts_research_v12.js`, wired as the npm script. Recomputes the
editing-rule and Σ₀ deliverables from data **already on disk** — no bulk
download (see `hour_01.md` scope decision). Re-runnable any day; marks anything
it can't measure as `insufficient_data`.

Run result (real):
```
inputs: features=1451, calibration=28, visual=14
wrote data/models/{hook-weights, editing-rules, creator-profiles, sigma0-training}.json
```

Real measured outputs:
- **editing-rules.json**: median Short duration 29s (mean 32.1), median
  average-cut-length 3.17s, median 7.5 scene-cuts/clip — real stats over the
  collected metadata + calibration sample.
- **hook-weights.json**: opening-hook-strength mean 0.924, range 0.88-0.98
  across 14 visual records — **confirms the detector's known saturation**
  (`hour_12.md`), honestly noted as describing the detector's behavior, not a
  validated hook-quality ground truth.
- **sigma0-training.json**: a signal manifest tagging each Σ₀ editing signal
  real / proxy / insufficient_data. No nightly weight retraining is claimed —
  there is no labeled outcome data (real retention %/share counts unavailable
  via public API). "Training" = recomputing structural priors from real data.

## Validation — end to end

**Standard pipeline E2E** (`scripts/test_creator_pipeline.js`): **12/12** after
all V12 changes — upload → analyze → highlights → variants → safe-zones →
captions → render (13MB, 1080×1920) → persistence. No regressions from any of
the six parts.

**Dead-air exclusion test** (purpose-built): a synthetic 24s clip —
8s static gray (menu/dead-air) + 4s sustained-motion action (mandelbrot) +
12s idle drift. Result:

```
HIGHLIGHTS DETECTED:  8-12s  score=0.54  tags=[motion,scene]   (the action only)
highlights in ACTION window (8-12s): 1
highlights in DEAD/IDLE windows:     0
max density in action window: 0.392    max density in dead/idle: 0
story arc: single real segment -> peak role
RENDER: 4.41 MB, 1080x1920, 4s, all segments from action window (no dead air)
```

A first attempt used `testsrc` for the action segment and produced 0 highlights
— investigated and found it was a **flaw in the synthetic clip** (testsrc is
nearly static in the middle; only its segment boundaries had motion, which
dominated normalization), not the engine. Switching to `mandelbrot`
(continuous motion) gave the clean result above. Worth recording: the
diagnosis came before any "fix" to the engine, which needed none.

## Handoff validation checklist

| Requirement | Result |
|---|---|
| Highlights are found | ✅ |
| No dead air selected | ✅ (0 in dead/idle windows; all rendered from action) |
| Gameplay fills screen | ✅ (1080×1920, crop fit) |
| Facecam stays safe | ✅ (placement in top band, resize-on-conflict — `hour_04`) |
| Captions fit | ✅ (standard E2E, 3 captions) |
| Story arc exists | ✅ (peak role assigned) |
| Final MP4 renders | ✅ (4.41 MB) |
| Uploadable Shorts format | ✅ (1080×1920) |
