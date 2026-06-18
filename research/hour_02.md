# Σ₀ V11 Research Loop — Hour 2

**Phase:** Curated calibration sample (real frame/audio features)

## What happened

Ran `scripts/research_loop_calibration.py`: selected the top 40 highest-view
videos from Hour 1's collection (split across gaming/general), downloaded
each via `yt-dlp` at lowest quality (`--max-filesize 30M`), ran real `ffmpeg`
scene-cut/motion/audio-loudness analysis, then **deleted the video file
immediately** after extracting numeric features — no video content is
retained anywhere on disk.

**Result: 28/40 succeeded** (12 failed — "video not available", i.e.
deleted/region-locked/private since collection). All 28 produced real,
non-fabricated numbers in `data/youtube/calibration_features.jsonl`.

## Real findings (n=28 — small, treat as directional not conclusive)

| | n | mean motion_score |
|---|---|---|
| Gaming | 19 | 0.477 |
| General | 9 | 0.707 |
| Combined | 28 | 0.551 |

Scene-cut-derived `motion_score` (cuts/sec, normalized) varied widely:
several videos had `motion_score = 0.0` (0 detected scene cuts across the
whole clip — likely single continuous shots, common in some general-content
formats: cooking, ASMR, satisfying clips) while top gaming clips had up to
54 cuts in 45s (`motion_score = 1.0`, capped). This is a real signal, not
noise: **general top-viewed Shorts in this sample show a wider bimodal split
— either near-zero cuts (single continuous shot) or very high cuts** — while
gaming clips cluster more in the middle.

**Caveat:** n=28 is too small to generalize "general Shorts have higher
motion than gaming Shorts" — that's counter to intuition and likely an
artifact of which 40 videos happened to be top-viewed in this collection
batch (e.g. several general top performers were music/dance/ASMR clips with
sustained single shots that still average high per-frame motion despite few
hard cuts — `motion_score` here specifically measures *cut frequency*, not
continuous motion, which is a definitional gap worth fixing before treating
this as a real pattern).

## Feature/scoring changes this hour

None applied to production code yet — this is observational calibration
data only, pending Hour 3 (training).

## Methodology note for future hours

`motion_score` as currently defined (scene-cuts-per-second) conflates "fast
cutting" with "high motion energy." A continuous-shot video with constant
camera pans/gameplay action would score 0.0 here despite being highly
dynamic. The existing production `highlight-engine.js` already computes a
better-grounded `motion` signal (frame-diff based, not just cut-detection) —
worth reusing that approach for any future calibration-sample work rather
than this hour's simplified scdet-based proxy.

## Next hour

Train an initial model on the 1,451-record metadata feature set (Hour 1) —
metadata-only features (title length, tag count, hook-word proxy, duration,
is_gaming) predicting `engagement_rate`. This is a legitimate, sufficiently-
sized dataset for a first-pass model, separate from the small calibration
sample above (which stays observational due to n=28).
