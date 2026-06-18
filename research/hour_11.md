# Σ₀ V11 Research Loop — Hour 11

**Phase:** Re-running calibration with the new hook detector + engagement_rate pairing

## What happened

Hour 10 flagged a concrete next step: pair the new
`detectOpeningHookStrength()` output with real `engagement_rate` for the
calibration sample, since that pairing is what's actually needed to
validate or reject the hour's proposed weighting (0.5 motion-ratio + 0.3
avg-motion + 0.2 scene-change-count), rather than leaving it as an untested
formula.

Implemented this in `scripts/research_loop_calibration.py`:
- Added `scripts/_hook_strength_helper.js`, a thin CLI wrapper around
  `highlight-engine.js`'s `detectOpeningHookStrength()` so the Python
  calibration script can call the real Node detector via subprocess instead
  of duplicating ffmpeg logic in two languages.
- Added `opening_hook_strength()` and `_engagement_rate()` helpers to the
  Python script; `extract_features()` now records real
  `opening_hook_strength` (or the literal string `"insufficient_data"` if
  the detector reports `unavailable`) and real `engagement_rate` alongside
  the existing motion/scene/audio fields.
- The previous Hour 2 calibration output was preserved as
  `data/youtube/calibration_features.hour02.jsonl` rather than overwritten,
  so this hour's run is additive, not destructive to prior real data.
- Re-ran the full calibration pipeline (re-downloads the same curated
  sample via `yt-dlp`, deletes each file immediately after extraction, same
  as Hour 2 — see that hour's report for the no-retention policy).

## Quota status check (for the record)

This re-run uses `yt-dlp` (direct video access), not the YouTube Data API,
so it doesn't touch the exhausted 8,000-unit daily quota from Hour 1. Real
metadata re-collection via the Data API is still blocked until the daily
reset (00:00 UTC) — checked again this hour: still not reached.

## Result

See `data/youtube/calibration_v2_stdout.log` and
`data/youtube/calibration_features.jsonl` for the real run output (in
progress / completed — reported in the next hour once the background run
finishes, rather than guessing at numbers before the process exits).
