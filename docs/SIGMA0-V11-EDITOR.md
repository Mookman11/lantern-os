# Σ₀ V11 Editor Spec

**Status:** Draft, derived from a compressed real-data research loop (see
`research/hour_01.md` through `hour_05.md`). This is **not** the literal
"5,000+5,000 video, 12-hour, hourly-retrain" deliverable originally
requested — that target was not reachable with one YouTube Data API key in
one day (quota economics, see `research/hour_01.md`). What follows is built
from what was actually, honestly collected and measured:

- 1,451 real Shorts metadata records (790 general / 661 gaming), 0 dupes
- 28 real ffmpeg-measured calibration clips (motion/scene/audio), video
  files deleted immediately after feature extraction, never retained
- 28 real official-thumbnail pixel measurements (brightness/contrast/edge/
  colorfulness)
- One trained baseline model (`data/models/xgboost-v10.json`, val_r2=0.199)
- The project's existing production scoring/safe-zone code
  (`scoring-engine-v2.js`, `safe-zone-v2.js`, `caption-engine.js`), which
  already implements several of the rules this spec calls for

Every rule below is tagged **[data]** (grounded in this loop's measurements),
**[existing]** (already implemented in production, reused here), or
**[design]** (Σ₀ anti-collapse principle or design judgment, not yet
empirically validated — flagged for future data collection once quota
resets allow more raw collection).

## Important constraint (carried over verbatim from the handoff)

> Do NOT clone creators. Use the research only as reference patterns, not
> copied styles. Lantern should develop its own editing identity inspired by
> successful structures, stabilized with Σ₀ anti-collapse principles, and
> optimized for long-term creator quality rather than short-term virality
> alone.

Nothing below recommends imitating a specific creator's style, transitions,
or branding. All patterns are statistical/structural (timing, layout,
category effects), not stylistic mimicry.

---

## 1. Final Scoring Formula

**[existing]** Production already implements a multi-term Σ₀-style score in
`apps/lantern-garage/lib/scoring-engine-v2.js`:

```
score = motion·w_motion + sceneChange·w_scene + gameplayPresence·w_gameplay
      + spectralEntropy·w_entropy + (1 - normalizedSpread)·w_spread
      - redundancyPenalty(if entropy near threshold)
      - collapsePenalty(if spectralMetrics.isCollapsed)
```

with a hard validity gate (`gameplayPresence ≥ 0.6`, `spectralEntropy ≥ 0.4`)
that rejects degenerate/redundant segments before scoring — this is the
anti-collapse mechanism already in place, not a new proposal.

**[design]** Proposed addition, not yet implemented or validated: condition
the score on a `content_category` prior (see §6) rather than the current
binary `gameplayPresence` only — Hour 4's data shows engagement effects vary
~2.7x across gaming sub-categories alone, so a single gameplay/no-gameplay
split is coarser than the real signal.

## 2. Editing Rules

**[data]** Duration: this loop's collected dataset's mean Short duration was
~31-33s (gaming 33.1s, general 31.3s) among top-viewed Shorts — both well
under the 60s ceiling already enforced by `ExportValidator`/
`highlight-engine.js`'s `maxHighlightDuration = 60.0`. No change recommended
to the existing 60s ceiling; this is supporting evidence it's already
correctly set, not a reason to lower it.

**[design]** Per the anti-collapse principle: never let one weight dominate
edit decisions for an entire video. Avoid repeating the same transition type,
same hook structure, or same pacing pattern across all segments of one
export — multiple distinct highlight peaks (already a Σ₀ design goal) are
preferred over one over-optimized peak.

**[external]** (Hour 7) Published retention research independently reports
15-30s as highest-retention for quick-payload (setup/surprise/payoff)
content and 45-60s for narrative formats, with the algorithm rewarding
retention *percentage* over raw length.
[Opus](https://www.opus.pro/blog/ideal-youtube-shorts-length-format-retention).
This triangulates with the [data] finding above (our own real top-viewed
sample averaged 31-33s) — independent published research and independently
collected first-party data land in the same range. **Implication:** when
multiple qualifying segments compete for inclusion under the 60s ceiling,
prefer the shorter one if engagement signal is comparable, rather than
defaulting to the longest segment that still fits.

## 3. Hook Rules

**[data]** Hour 1's title hook-word density measure
(`hook_strength_title_proxy`) had **low correlation with engagement_rate**
(mean 0.042, median 0.0 across the full 1,451-record set) and ranked only
3rd of 5 features in Hour 3's trained model (importance 0.126, behind
`is_gaming` and `duration`). **Finding: title hook-wording is a weak signal
in this dataset — do not over-index editing decisions on "hook word density"
without further validation.** This contradicts a common assumption in
the original handoff's hook-research request, and is reported honestly
rather than fabricating a stronger pattern.

**[design]** No real per-frame "fastest hook time" data was collected (would
require frame-level analysis at a scale this loop didn't reach) — mark
`hook_time` as `insufficient_data` in the schema (already done, see Hour 1)
until real frame-level hook-timing analysis is run.

**[external]** (Hour 7) Published Shorts retention research reports 50-60%
of viewer drop-off happens in the first 3 seconds, driven by visual/motion
pattern breaks and mid-action starts — not title wording.
[JoinBrands](https://joinbrands.com/blog/youtube-shorts-best-practices/),
[Virvid](https://virvid.ai/blog/first-3-seconds-hook-faceless-shorts-2026).
This reframes the finding above: `hook_strength_title_proxy` was weak
because it measured the wrong layer (title text) for what actually drives
the hook (opening-frame visual change). **Revised priority for V12:** build
a first-3-seconds motion/scene-change detector reusing
`scoring-engine-v2.js`'s existing `motion`/`sceneChange` inputs, scoped to
just the opening segment, instead of further refining the title-text proxy.

**[existing-but-uncalibrated]** (Hours 10-12) Built and shipped
`detectOpeningHookStrength()` in `highlight-engine.js` per the above —
reuses the engine's real `detectMotion`/`detectSceneChanges` ffmpeg passes,
bounded to the opening window, working code (`node --check` clean, verified
against a real exported video). **Then tested against real
`engagement_rate` for the 28-video calibration sample and found it does
not discriminate**: 26 of 28 videos scored within 0.05 of the formula's
ceiling (`0.983`), because the default `motionThreshold=0.1`/
`sceneThreshold=0.2` over a 3s/10fps window are loose enough that nearly
any real Short trips them. The resulting Pearson r=-0.505 against
engagement_rate is **not a real finding** — it's driven by 2 non-clipped
outliers against 26 identical values, and reporting it as a validated
correlation would overstate noise as signal. Digging into the per-component detail showed `motionFrameCount` and
`sceneChangeCount` are saturated (pinned near max for ~all videos), but
`avgMotion` is real-valued and unsaturated (range 1.56-10.18 across the
sample) — yet correlating `avgMotion` alone against `engagement_rate`
gives **r=0.0024, effectively zero**. Important caveat: the Hour 7 external
research this detector was built to validate against was about *intro
retention %* (a YouTube Studio Analytics metric this project has no OAuth
access to), not `engagement_rate` — so this null result may mean
`engagement_rate` is simply the wrong target for this question, not that
opening motion doesn't matter. **Status: real code, real test, real
negative result on two levels (saturated formula, and unsaturated
component vs. the wrong proxy target) — needs (1) threshold recalibration
and (2) real retention-percentage ground truth before it can inform any
production score.** Do not wire this into `scoreHighlight()` or any
production path until both are addressed (see `research/hour_12.md`).

## 4. Facecam / Safe Zone Rules

**[existing]** `apps/lantern-garage/lib/safe-zone-v2.js` already implements
exactly what the handoff asked for: a measured (not fabricated) facecam/HUD
region detector using a 12×8 grid over downsampled frames, flagging corner
regions with sustained locally-distinct motion (commonly facecam) and static
high-contrast bands (commonly HUD), each with an **auditable confidence
score** (fraction of sampled frames where the region "fired"). It plans a
9:16 crop window that avoids slicing through detected regions and returns
`{ status: "unavailable" }` rather than guessing when ffmpeg can't run. No
new facecam-position rule is proposed here — reuse this module as-is.

**[design]** Goal from the handoff ("gameplay fills the screen, no black
bars") is already the stated design target of the crop-planning step in
`safe-zone-v2.js` — confirmed by reading its 9:16 target-aspect constant,
not re-derived here.

**[external → implemented in Hour 9]** Published safe-zone guidance for
1080×1920 Shorts: avoid the top ~10% (profile/channel UI), keep captions
above the bottom ~20%, center faces in the middle ~60% of frame, and
reserve a ~120px-wide engagement-button strip ~60px from the right edge.
[Kreatli](https://kreatli.com/guides/youtube-shorts-safe-zone). Hour 7
initially mis-scoped this as a crop-planner gap; Hour 9's implementation
corrected that: platform UI overlays the **final output canvas** regardless
of source crop, so it doesn't belong in `planCrop()`'s source-region
scoring. Instead, `safe-zone-v2.js` now exports `PLATFORM_UI_REGIONS`
(top-chrome + right-button-stack, confidence 1, output-canvas-space) and an
`overlapsPlatformUI(rect)` helper for placement decisions (captions, PiP
facecam boxes). **Not yet wired into any caller** — `caption-engine.js`'s
existing `bottom-center` + `safeMargin: 60` default was checked and is
already directionally consistent with this guidance, so no caption bug was
found; full integration (e.g. PiP placement avoiding the button stack) is
V12 future work.

## 5. Gaming Event Detector

**[data]** Category-level engagement effects (Hour 4) are real and usable
today even without a frame-level "kill streak / clutch / funny moment"
classifier: Marvel Rivals (0.0525), Elden Ring (0.0482), and clutch-themed
titles (0.0401) outperformed generic gaming-highlight framing (0.0196-0.0201)
by roughly 2-2.7x in this sample. **Recommendation: treat `content_category`
identity, not just a binary "is this gameplay" flag, as a scoring input** —
see §1.

**[design]** A frame-level kill-streak/clutch/snipe detector (the literal
ask) was not built this loop — it requires either visual gameplay-HUD
parsing or audio-cue detection (kill confirmation sounds, etc.) at a scale
beyond what 28 calibration clips can validate. Flagged as future work, not
guessed at here.

**[external]** (Hour 7) Production gaming-clip tools (Eklipse and similar)
fuse in-game UI cues (kill feed, score spikes, objective captures) with
audio cues (kill-confirmation sounds, caster/crowd reactions), and use
**adaptive clip length keyed to event type** — a no-scope clip runs ~6s,
a multi-stage clutch ~22s — rather than one fixed highlight duration.
[Eklipse](https://blog.eklipse.gg/streaming-tips/how-gameplay-intelligence-works-2.html).
**Design implication for V12:** when a real gaming-event detector is built,
it should output a variable-length segment driven by the detected event's
own start/end (action setup → payoff), not snap to a fixed window — this
refines the *shape* of the future detector even though the detector itself
isn't built yet.

## 6. Thumbnail Selection

**[data]** Real pixel-level thumbnail measurements (Hour 5, n=28, official
CDN thumbnails only) found general-content thumbnails trending brighter,
higher-contrast, and more colorful than gaming thumbnails in this small
sample (e.g., brightness 78.1 vs 73.7) — directional only, not yet a rule
given the sample size.

**[design]** `thumbnail_score()` as requested in the handoff would need
expression/action-frame/motion-blur sub-scores. No face/pose model is
available in this environment, so those sub-scores are explicitly
`insufficient_data` rather than guessed. A real formula, once such a model
is integrated, should combine: brightness/contrast/colorfulness (measurable
today, weight TBD pending more data) + face/expression presence (not yet
available) + motion-blur/action-frame detection (not yet available).
**Do not ship a formula with invented weights for the unmeasured terms.**

## 7. Transition Engine

**[design]** No data this loop. Anti-collapse principle applies directly:
avoid using the same transition for every cut in an export; if the existing
render pipeline (`render-pipeline-v2.js`) has a fixed default transition,
consider varying it per-segment based on the scoring engine's
`spectralSpread`/entropy metrics (already computed) rather than introducing
a new unvalidated rule.

## 8. Caption Placement

**[existing]** `apps/lantern-garage/lib/caption-engine.js` already generates
captions (confirmed working via `scripts/test_creator_pipeline.js`, 3
captions generated in the last E2E run prior to this loop). No new caption-
position rule is proposed; defer to the existing safe-zone output (§4) to
keep captions out of detected facecam/HUD regions, which is already the
intended integration point.

## 9. Retention Strategy

**[design]** Per the Σ₀ anti-collapse principle stated in the original
handoff: never optimize for views/engagement_rate alone. The single trained
model in this loop (Hour 3, val_r2=0.199) should be treated as one weak
signal among several, not a primary editing driver — its own honesty_note
states this directly. Promote diversity across an exported set of clips
(varying category, pacing, hook style) rather than collapsing toward one
high-scoring pattern.

**[existing]** (Hour 13) `src/creator-intelligence/scoring/viral-score-v10.js`
already implements exactly this as a live, tested, honestly-labeled
8-component structural scorer (hook, retention, emotion, surprise, pacing,
rewatch, visualClarity, captionPotential), each with its own confidence and
`basis: "structural_heuristic", calibrated: false`. **Do not build a second,
competing `engagement_prediction × stability × novelty × surprise`
multiplicative formula alongside this** — that would duplicate rather than
improve an already-correct system. The real gap is narrower: see §10.

## 10. Training Pipeline

**[data]** `scripts/research_loop_train.py` is real and reusable:
`MIN_SAMPLES = 200` honesty gate (refuses to train and writes
`{"status": "insufficient_data"}` below that), 80/20 train/val split,
XGBoost regressor, full metrics + feature importances + an explicit
honesty_note written to `data/models/training_report.json` every run. This
pipeline should be re-run whenever more real metadata is collected (next
opportunity: after the daily YouTube API quota resets — today's run
consumed 7,971/8,000 units in under 2 minutes, see `research/hour_01.md`).

**Current model status:** trained, n=1,451, val_r2=0.199, val_mae=0.0124.
`is_gaming` dominates feature importance (0.482) but Hour 4 shows this
conflates distinct sub-category effects — next retrain should add
`content_category` as a feature once per-category sample sizes individually
clear the 200-sample gate.

**[existing, newly connected]** (Hour 13) Discovered a second, separate,
already-built population dataset path —
`src/creator-intelligence/scoring/score-engine.js`, gated at
`MIN_ROWS_FOR_SCORING=500` / `MIN_ROWS_PER_GAME=50` — that had **zero rows**
despite this loop's 1,451-record real collection. Built
`scripts/ingest_youtube_into_creator_intelligence.js` to feed the real
collected data into it correctly (schema-respecting, structural fields left
honestly `null`): 1,451/1,451 rows appended, 0 invalid. Real result:
`viralScore()`/`retentionScore()` and `gameSufficiency()` for fortnite,
minecraft, gta, and cs2 now return real `status:"ok"` for the first time;
cod/roblox/valorant/apex/elden_ring/marvel_rivals remain honestly
`insufficient_data`, each within 1-15 rows of the real threshold. This is
the correct integration point for future structural-feature data, not a
new XGBoost bridge — see `research/hour_13.md`.

---

## What this spec deliberately does NOT claim

- No per-frame hook-timing, camera-movement, zoom-frequency, or beat-timing
  rule is asserted as validated — those fields remain `insufficient_data` in
  every real output file this loop produced.
- No face/expression-based thumbnail rule is asserted — no such model was
  available to validate one honestly.
- No claim that 5,000+5,000 videos were collected — 1,451 unique records
  were, and that number is reported everywhere instead of the original
  target.
- No video content from other creators was retained — the 28-clip
  calibration sample's video files were deleted immediately after feature
  extraction (see `research_loop_calibration.py`'s `finally: out_path.unlink()`).
- No second, competing scoring formula was added alongside the existing
  live `viral-score-v10.js` — see §9/§10 and `research/hour_13.md`.

## Path to a stronger V12

1. Resume metadata collection on subsequent days (quota resets daily) to
   grow past 1,451 records and unlock reliable per-category retraining.
2. Integrate a real face/pose detection model before claiming any
   expression-based thumbnail scoring.
3. Recalibrate `detectOpeningHookStrength()`'s thresholds against the
   28-video ground truth (Hour 12 found it saturates almost every real
   video to ~0.98) before wiring it into any production score.
4. Get real intro-retention-percentage data (YouTube Studio/Analytics API,
   requires channel-owner OAuth not currently available to this project)
   — Hour 12 found `engagement_rate` shows no measurable relationship with
   opening-segment motion, which may mean it's the wrong proxy for
   validating hook hypotheses, not that hooks don't matter.
5. Build frame-level gaming-event (kill/clutch) detection against the
   existing `highlight-engine.js`/`scoring-engine-v2.js` motion+spectral
   pipeline, using adaptive (event-keyed) clip length per Hour 7's Eklipse
   research, rather than a new ad-hoc one.
6. Wire `safe-zone-v2.js`'s new `PLATFORM_UI_REGIONS`/`overlapsPlatformUI()`
   into actual caption/PiP placement decisions (built in Hour 9, not yet
   called from any production path).
7. Re-run `research_loop_train.py` with `content_category` as a feature once
   enough per-category samples exist.
8. ~~Never return zero highlights~~ — done (Hour 13): `job-worker.js`'s
   existing fallback guarantee now uses `buildFallbackHighlights()`'s real
   density-ranked min2/max10 logic instead of its old fixed-window/
   fabricated-0.5-score version. Verified against a synthetic blank/silent
   test clip and the full `test_creator_pipeline.js` suite (12/12).
9. cod/roblox/valorant/apex/elden_ring/marvel_rivals are each within 1-15
   rows of `score-engine.js`'s real 50-row-per-game threshold — the next
   quota-reset day's collection should close these specific gaps first.

---

## 12-hour loop status: complete

This closes the 12-"hour" research loop (`research/hour_01.md` through
`hour_12.md`). Real-world elapsed time was far shorter than 12 wall-clock
hours because the YouTube Data API quota — the loop's main rate limit —
exhausted in under 2 minutes and does not reset until 00:00 UTC, well past
this sitting. Hours 7-12 used that wait productively: external research
(cited), diversity validation, two real shipped code changes
(`safe-zone-v2.js`, `highlight-engine.js`), and a real validation attempt
that produced an honest negative result rather than a padded one. Resuming
this loop on a future quota-reset day (per items 1 and 4 above) is the
clearest path to turning today's `[design]`/`[external]`-tagged sections
into `[data]`-backed ones.
