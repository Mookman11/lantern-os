# Σ₀ V12 Research Loop — Hour 14

**Phase:** Visual Research Engine — Phase 1 (Video Observer) built and run on real data

## Scope decision (stated up front, not buried)

The V12 handoff asked for visual analysis of 5,000 general + 5,000 gaming
YouTube Shorts + TikTok gaming clips. Built the full requested pipeline
architecture, but ran it on:
- **All 10 of Lantern's own real rendered exports** with linked entries
  (`data/creator/entries/*/renders/*.mp4`) — first-party content, no scale
  limit, no ToS question.
- **5 real third-party Shorts** (3 succeeded, 2 were no-longer-available) —
  reusing the same small-curated-sample convention already established in
  Hours 1-13 (28-40 videos), not a new escalation toward thousands.
- **No TikTok.** No official public data API exists for it, and its
  anti-scraping enforcement is stricter than YouTube's — even less
  defensible at this scale than the YouTube case already declined twice
  this session.

Bulk downloading thousands of videos across two platforms to build this
dataset remains out of scope for the reasons already given in
`research/hour_01.md` and `research/hour_13.md`: deleting the file after
feature extraction reduces redistribution risk, not acquisition risk —
downloading the content at all, automated, at thousands-per-platform scale,
in violation of platform ToS, is the act in question, independent of
retention.

## What was built (Phase 1 — Video Observer)

- `scripts/_visual_research_helper.js` — Node CLI wrapper exposing
  `highlight-engine.js`'s `detectMotion`/`detectAudioSpikes`/
  `detectSceneChanges`/`detectOpeningHookStrength` and `safe-zone-v2.js`'s
  `analyzeForCrop` as one JSON call. Reuses existing tested detectors
  rather than reimplementing motion/facecam detection a second time in
  Python.
- `scripts/shorts_visual_research.py` — orchestrator producing the
  requested schema (`data/shorts_research/<video_id>.json`): `fps`,
  `average_cut_length`, `hook_duration`, `motion_curve`, `facecam_position`,
  `hud_position`, `emotional_peaks`, `engagement`, real where measurable.
  `zoom_frequency`, `subtitle_style` are explicitly `insufficient_data` —
  **no zoom/crop-change detector exists in this codebase yet, and no OCR
  engine is installed in this environment** (checked: no `pytesseract`,
  no `easyocr`, no `tesseract` binary). Neither was faked.
  `caption_density` is real for Lantern's own renders (captions are known
  exactly from `caption-engine.js` output) and `insufficient_data` for
  third-party clips (would require OCR on the source video).
- `scripts/run_visual_research_batch.py` — batch runner over Lantern's own
  entries.

**14 real records produced** in `data/shorts_research/`: 10 first-party +
3 third-party (1 from an earlier single test + the 3-of-5 demo batch).

## Real findings

1. **Facecam detection produced genuine, varying results on real
   third-party content**: top_right (0.642 confidence), bottom_left
   (0.501), top_left (0.301) — three different corners, three different
   confidences, not a constant. Lantern's own first-party renders mostly
   show `insufficient_data` for facecam (correct: the test fixture is
   gameplay-only footage with no webcam overlay — an honest negative, not
   a detector failure).
2. **`hook_duration` (via `detectOpeningHookStrength`) saturates at ~0.983
   again on this new, independent small sample** — same finding as Hour 12,
   now reproduced on different videos. This strengthens (not just repeats)
   the conclusion that the detector needs threshold recalibration before
   use; it's not an artifact of the original 28-video sample specifically.
3. **Real caption density varies meaningfully across Lantern's own
   renders**: 44.0 captions/min for three short, caption-dense exports vs.
   6.08 captions/min for others — real signal about Lantern's own current
   output variety, not a third-party finding.
4. HUD detection returned `insufficient_data` for all 14 — the existing
   `safe-zone-v2.js` HUD-band heuristic (static high-contrast top/bottom
   band) didn't fire on any of this sample. Could mean none of these clips
   have a strong static HUD, or the heuristic's thresholds are tuned for a
   different visual style. Flagged as observational, not diagnosed further
   (n=14 too small either way).

## Phases 2-6 — honest status, not built further this hour

- **Phase 2 (hook formula):** the user's requested formula
  (`motion + audio_change + scene_change + subtitle_intensity +
  face_presence`) can't be fully assembled — `subtitle_intensity` requires
  the same missing OCR step. `detectOpeningHookStrength()` already
  combines motion + scene_change (see Hour 10) and is known-saturated
  (this hour reconfirms). Not recalibrated this hour — still the right
  next step, now backed by two independent samples instead of one.
- **Phase 3 (gaming highlight timing — "6 sec kill, 8 sec replay" etc.):**
  not attempted. This requires either many more real labeled gaming clips
  or manual annotation; n=2 real gaming clips this hour is far too small
  for even an observational pattern, let alone a detector.
- **Phase 4 (Safe Zone V3):** no change made to `safe-zone-v2.js` this
  hour. The real facecam-corner variation found above (3 different corners
  in 3 clips) argues against hardcoding a single "facecam goes here" rule
  — the existing per-video measured detection (already built) is more
  honest than a fixed V3 layout would be.
- **Phase 5 (XGBoost `predicted_short_score`):** not trained. 14 records
  is far below even the project's own conservative `MIN_SAMPLES=200` /
  `MIN_ROWS_FOR_SCORING=500` gates already established this session
  (`research_loop_train.py`, `score-engine.js`). Training on n=14 would be
  the exact fabrication this loop exists to avoid.
- **Phase 6 (style embedding / "Lantern Style"):** not built as a trained
  embedding — no dataset remotely close to supporting one exists yet. The
  qualitative direction (combine real measured structure + Σ₀ stability +
  measured safe zones + originality, per the user's own framing) is
  already reflected in how `viral-score-v10.js` is designed (see
  `research/hour_13.md`) and doesn't need a new artifact to restate.

## Files this hour

`scripts/_visual_research_helper.js`, `scripts/shorts_visual_research.py`,
`scripts/run_visual_research_batch.py` (new, real, run).
`data/shorts_research/*.json` (14 new real records). Nothing committed.
