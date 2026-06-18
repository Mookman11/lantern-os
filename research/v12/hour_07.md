# V12 Hour 07 — Honest Limits & What's NOT Done

This cycle delivered real, verified upgrades to highlight selection, story flow,
crop/facecam logic, style presets, and Σ₀ diversity selection. To keep the
record honest, here is what the handoff asked for that was **not** built, and
why — so nobody mistakes a proxy for a trained system.

## Not built (and why)

1. **Bulk 5,000 / 10,000 video download + per-video visual feature mining**
   (Parts 1, 7). Declined — automated mass download of third-party copyrighted
   video against platform ToS. Delete-after-extraction addresses retention, not
   acquisition. Unchanged from `research/hour_01.md`, `hour_13.md`, `hour_14.md`.

2. **Real gameplay-event detectors** — kills, crosshair snaps, damage flashes,
   victory screens, enemy appearances (Part 3 "reward" list). These need a
   trained CV model or per-game HUD/OCR parsing. The negative detectors built
   this cycle are heuristic signal-combinations, not event classifiers. Reward
   side stays `motion/scene/audio` proxies; kill-density is `insufficient_data`.

3. **Per-element HUD preservation** (health/ammo/crosshair/minimap/scoreboard,
   Part 5). The crop planner avoids slicing the *detected* facecam/HUD bands,
   but does not identify individual HUD elements. Future work.

4. **Real subtitle/zoom/music-timing extraction from third-party clips**
   (Part 1). Requires OCR + per-clip audio-beat analysis on downloaded video.
   NOTE: `tesseract.js` IS a lantern-garage dependency (the earlier "no OCR"
   finding was Python-only) — so OCR-based subtitle detection on *first-party*
   renders is now feasible as a future task without new bulk downloads.

5. **Nightly retraining on outcome labels** (Part 7). There is no labeled
   outcome data: real retention % and share counts are not exposed by the
   public YouTube Data API (`hour_12.md`). `npm run shorts-research-v12`
   recomputes structural priors from real on-disk data; it does not and cannot
   do gradient updates against virality outcomes, and does not claim to.

6. **`hook-model.json` / `story-model.json` / `safe-zone-model.json`** as
   *trained* `.json` models. The hook/story/safe-zone logic shipped as real
   *code* (`detectOpeningHookStrength`, `story-engine-v12.js`,
   `safe-zone-v2.js`) rather than learned weight files, because there is no
   labeled training set to fit them to. `creator-profiles.json`,
   `editing-rules.json`, `hook-weights.json`, `sigma0-training.json` are
   real (config + measured priors), not invented model weights.

## Net assessment

Against the success criterion — "stop acting like a highlight trimmer, start
behaving like a Shorts editor that understands pacing, hooks, gameplay moments,
and narrative flow" — the engine now:
- actively suppresses dead air / idle / menu / conversation (verified to 0),
- builds a real hook→rising→peak→reaction→payoff arc from measured signals,
- plans facecam placement that never crops gameplay,
- offers five named editing styles,
- prefers diverse multi-peak edits over collapsed single-moment ones.

It does this on **real measured signals**, with every gap to a "trained" system
stated rather than papered over. The honest ceiling: it is a much smarter
*structural* editor, not a learned one — and it can't become learned until real
outcome-labeled data exists.
