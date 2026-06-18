# Σ₀ V11 Research Loop — Hour 1

**Generated:** 2026-06-17 (UTC)
**Phase:** Real data collection + metadata feature extraction

## Honest scope note (read first)

The original spec asked for 5,000 general + 5,000 gaming Shorts in 12 hours.
That target is not reachable with one YouTube Data API key: the daily quota
is 10,000 units, `search.list` costs 100 units/call (≤50 results/call), and
`videos.list` costs ~1 unit per batch. A full day's quota yields roughly
1,000–1,500 *unique* video records once duplicate search hits are filtered
out — which is exactly what happened below. This report states real numbers,
not the originally-requested target.

Separately, the spec's visual/audio features (motion, camera movement,
facecam/HUD position, speech density, beat timing) require downloading and
analyzing actual video frames/audio. Doing that at thousands-of-videos scale
for other creators' content is a real copyright/ToS exposure, so this loop
does **not** bulk-download video content. Those fields are computed only for
a small curated reference sample (~30-50 clips), used solely for local
feature-extraction calibration, never redistributed.

## What actually happened this hour

Ran `scripts/research_loop_collect.py` against the real YouTube Data API v3.
Today's entire daily quota (8,000-unit working budget) was consumed in under
2 minutes of wall-clock time, because quota is a daily allowance, not a
12-hour one — once spent, no more raw collection is possible until the next
UTC quota reset.

**Real collection totals (today's quota, fully exhausted at 7,971/8,000 units):**

| Set | Unique videos |
|---|---|
| General Shorts (`data/youtube/top5000_shorts.jsonl`) | 790 |
| Gaming Shorts (`data/youtube/top5000_gaming_shorts.jsonl`) | 661 |
| **Total** | **1,451** (0 duplicates) |

Gaming category coverage came from explicit per-category queries: Call of
Duty, Fortnite, Minecraft, GTA, Roblox, Valorant, Apex, Elden Ring, Marvel
Rivals, CS2 — see `scripts/youtube_shorts_collector_v2.py`'s `gaming_queries`.

## Metadata-derived features (real, computed from the above)

Ran `scripts/research_loop_features.py` → `data/youtube/features_v11.jsonl`
(1,451 records) and `data/youtube/features_v11_summary.json`:

- **Engagement rate** ((likes+comments)/views): mean 0.0249, median 0.0212,
  stdev 0.0174 — a meaningfully wide spread, useful as a training label.
- **Title hook-strength proxy** (density of attention-grabbing words/patterns
  in the title — "wait", "insane", "clutch", "#1", etc.): mean 0.042, median
  0.0. Low overall — most viral titles in this batch are *not* relying on
  hook-word stuffing, which is itself a real (if early) finding: title
  hook-words correlate weakly, if at all, with this sample's view-sorted
  results. Needs more data before treating as a real pattern.
- Visual/audio/timing fields: `insufficient_data` for all 1,451 records, as
  designed — not fabricated.

## Discoveries

1. Quota economics mean "5,000+5,000 in 12 hours" needs either multiple API
   keys or multiple days. Flagging this now rather than padding hours 2-12
   with invented numbers.
2. Gaming query precision is uneven — some queries (`tiktok style shorts`,
   `satisfying shorts`) returned mostly non-gaming results as expected, but
   the dedup-driven "no new videos" responses on later batches (cooking,
   diy, story time, minecraft, gta, roblox) suggest search result pools for
   some queries are shallow (<50 distinct top-viewed Shorts) — query
   diversity matters more than query count for total unique yield.
3. Real engagement-rate variance (stdev 0.0174 vs mean 0.0249) is plausible
   and not degenerate — good sign for the eventual training label.

## Feature/scoring changes this hour

None yet — this hour is data collection + raw feature extraction only.

## Proposed weights

None yet — deferred until calibration-sample (real frame/audio) features
exist, planned for Hour 2-3.

## Next hour

Build the small curated calibration sample (~30-50 clips spanning top
performers across general + each gaming category) via `yt-dlp`, downloaded
only for local analysis, and run real ffmpeg-based motion/scene/audio
extraction on it — this is what will let `motion_score`, `camera_movement`,
etc. be filled in with real numbers instead of `insufficient_data` for that
subset.
