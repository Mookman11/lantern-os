# Σ₀ V11 Research Loop — Hour 5

**Phase:** Thumbnail composition signal (real pixel data, official thumbnail CDN only)

## What happened

Pulled the official YouTube thumbnail image (`https://i.ytimg.com/vi/<id>/hqdefault.jpg`
— the same CDN URL YouTube serves on every watch/search page, not a
downloaded video frame) for all 28 calibration-sample videos. Computed
real, non-fabricated pixel statistics with Pillow:

- `brightness` — mean grayscale luminance
- `contrast` — grayscale stddev
- `edge_density` — mean response of an edge-detect filter (proxy for visual
  busyness/detail)
- `colorfulness` — mean RGB channel stddev

No face-detection or expression-classification model is available in this
environment (`cv2`/`face_recognition` not installed) — anything claiming to
detect "expression," "action frame," or "motion blur" specifically would
have to be guessed, so those fields are **not computed** here rather than
faked. This is a deliberate scope-narrowing, consistent with the honesty
rule used in every prior hour.

## Real result (n=28, all succeeded)

| Metric | Gaming (n=19) | General (n=9) |
|---|---|---|
| brightness | 73.7 | 78.1 |
| contrast | 58.9 | 66.1 |
| edge_density | 13.9 | 16.1 |
| colorfulness | 60.7 | 66.6 |

Output: `data/youtube/thumbnail_features.jsonl`.

## Discoveries

1. General-content thumbnails in this small sample are consistently
   brighter, higher-contrast, busier (edge density), and more colorful than
   gaming thumbnails — gaming thumbnails trend darker/flatter. Plausible
   real-world explanation: many gaming thumbnails are raw in-game screenshots
   (often dim, indoor/night settings, HUD overlays reduce edge variety),
   while general-content thumbnails are more often staged/lit specifically
   for the thumbnail.
2. **n=28 (19/9 split) is too small to treat this as a rule.** This is a
   directional observation only, consistent with this loop's pattern of
   flagging small-sample findings as hypotheses, not facts.
3. No expression/action-frame signal could be honestly computed without a
   face/pose model — the V11 spec's "thumbnail_score()" (see final
   deliverable) will mark those sub-scores `insufficient_data` until such a
   model is actually integrated, rather than presenting a guessed formula as
   validated.

## Next hour

Synthesize Hours 1-5 into editing/layout/hook-rule recommendations for the
final `docs/SIGMA0-V11-EDITOR.md` deliverable, being explicit throughout
about which rules are grounded in this loop's real data (category effects,
duration/tag/title patterns, motion-score caveats, thumbnail composition
direction) versus which remain design-judgment carried over from the
existing V10 system (`highlight-engine.js`) and the Σ₀ anti-collapse
principles in the original handoff, pending more data to validate them
empirically.
