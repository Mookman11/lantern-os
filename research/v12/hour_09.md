# V12 Hour 09 — Phase 2: Real Editor Quality (render, priors, memory, nightly loop)

The handoff's point was right: the biggest remaining gap is *render quality* —
making a finished, watchable MP4 that feels like a top creator edited it — not
more scoring. This cycle delivered that, on real measured signals.

## The headline win: real punch-in zoom (Task 6)

`video-export.js` now has `buildZoomFilter()` — a real ffmpeg `zoompan` push-in
(1.0→1.18x over 0.8s, then hold) applied per-segment. `renderSegments` zooms
only the segments flagged `zoom:true` / `role:"peak"` (one energetic punch-in
per edit, not zoom-on-everything, which would feel cheap).

- Verified the filter in isolation: valid 1080×1920 output, correct frame count.
- Verified through `renderSegments`: a 2-segment render zoomed *exactly* the
  peak segment (`zoomedSegments=1`).
- Verified through the FULL pipeline: the standard E2E render now reports
  `zoomCount=1` in editing memory — the punch-in is really in the ffmpeg graph
  of the shipped MP4, not just a flag.

`variant-engine-v10` flags each variant's single strongest beat for zoom, so
every one of the 5 variants lands one dynamic moment.

## Weighted selection formula (Task 3)

Implemented the handoff's exact formula
(`viralScore·.25 + excitement·.20 + sceneEnergy·.15 + suspense·.10 +
faceReaction·.10 + gameplayIntensity·.10 + editingMomentum·.10`) as
`weightedEditScore()` in `score-v10.js`, mapping each term to a REAL existing
viral component. The premise ("current: score = hook + engagement") didn't match
reality — the current scorer is already an 8-component model — so this reuses
those components rather than duplicating them. Components needing absent
detectors (faceReaction without facecam, gameplayIntensity without gaming
signal) are **excluded and the weights renormalized**, never faked. Verified:
no-facecam run excludes faceReaction and renormalizes; facecam run includes it.

## Highlight diversity 2-10 (Task 4)

Already enforced by the V12 fallback (min 2 / max 10) + `antiCollapseSelect`
(multi-peak diversity). Re-verified on an 8-moment clip: all 5 variants land
8 segments (within 2-10); anti-collapse selects 8 with 2 distinct peaks and low
collapse risk. The "never 1 massive moment" rule holds.

## editing-priors.js (Task 2)

`lib/editing-priors.js` computes real priors from CC + first-party + calibration
data: averageCutsPerMinute (median 28.2/min over n=38), targetDurationSec
(median 29s), introHookStrength (median 0.93, n=24). Unmeasurable priors
(zoomFrequency/facecamPosition/captionDensity of *references*, suspenseTiming,
peakSpacing, endingStyle) are honest `insufficient_data` — they need detectors
that don't exist. Refreshed nightly.

## Editing memory (Task 5)

`lib/editing-memory.js` records the real editing stats of every render to
`data/editing-memory/` (cutsPerMinute, subtitlesPerMinute, zoomCount, roles,
viralScore, gameplayCrop). Wired into the export job. Verified it captures real
stats on the actual pipeline render. transitions/hookType are
`insufficient_data` (renderer applies neither named transitions nor hook
classification).

## Nightly loop (Tasks 1, 8)

- `nightly_cc_research.py`: collect CC clips + refresh priors (idempotent).
- `nightly_sigma0_improve.py`: collect → priors → recompute deliverables →
  retrain (gated) → regression E2E → promote vNext ONLY if a model trained AND
  regression passed. Honest: the trainer stays gated on `insufficient_data`
  until owned outcomes exist, so no model is promoted yet — but the loop still
  does real work (priors + regression) every run.

## Task 7 — full pipeline produces a finished, playable MP4

The "most important" task: upload → analyze → highlights → variants → segments
→ render → thumbnail → playback. **Standard E2E: 12/12**, now WITH the punch-in
zoom in the output. The render passes validation (1080×1920, h264, aac, duration
in range — i.e. a standard MP4 the dashboard plays), persists, and is
retrievable after reload. It does not dead-end; it produces a finished Short.

## Honest limits (unchanged, restated)

Kill/headshot/clutch detection, named transitions, kill-replay effects, hook-type
classification, and reference-clip zoom/caption measurement all need detectors
or models that don't exist — marked `insufficient_data`, never faked. The render
is meaningfully more dynamic (real punch-in on the peak), but it is not yet
applying game-event-triggered effects, because those require event detection
that isn't built. The path to that remains the same: real detectors + owned
labeled outcomes, not fabrication.
