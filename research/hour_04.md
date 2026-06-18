# Σ₀ V11 Research Loop — Hour 4

**Phase:** Sub-category breakdown of Hour 1's collected data (real, no new collection — quota exhausted)

## What happened

Broke down `engagement_rate` (real, from view/like/comment counts — not fabricated)
across the 28 individual search queries used in Hour 1's collection
(`query_source` field), to test Hour 3's finding that `is_gaming` is the
dominant predictor. n≥5 per query shown; all 28 queries had n≥34.

## Real result — query category, sorted by mean engagement_rate

| Category | n | mean | median |
|---|---|---|---|
| marvel rivals shorts | 46 | 0.0525 | 0.0485 |
| elden ring shorts | 48 | 0.0482 | 0.0512 |
| shorts clutch | 45 | 0.0401 | 0.0351 |
| call of duty shorts | 59 | 0.0366 | 0.0348 |
| valorant shorts | 51 | 0.0347 | 0.0299 |
| gta shorts | 59 | 0.0317 | 0.0306 |
| cs2 shorts | 50 | 0.0304 | 0.0334 |
| apex legends shorts | 48 | 0.0290 | 0.0265 |
| fitness shorts | 51 | 0.0280 | 0.0279 |
| cooking shorts | 50 | 0.0261 | 0.0224 |
| minecraft shorts | 77 | 0.0247 | 0.0208 |
| story time shorts | 48 | 0.0247 | 0.0228 |
| fortnite shorts | 62 | 0.0240 | 0.0253 |
| shorts gameplay | 36 | 0.0217 | 0.0133 |
| tiktok style shorts | 54 | 0.0216 | 0.0187 |
| shorts epic moment | 45 | 0.0204 | 0.0180 |
| asmr shorts | 43 | 0.0201 | 0.0185 |
| shorts killstreak | 47 | 0.0201 | 0.0192 |
| animal shorts | 50 | 0.0200 | 0.0141 |
| gaming highlights shorts | 45 | 0.0196 | 0.0134 |
| satisfying shorts | 48 | 0.0195 | 0.0179 |
| life hack shorts | 50 | 0.0193 | 0.0179 |
| roblox shorts | 48 | 0.0190 | 0.0143 |
| viral shorts | 38 | 0.0175 | 0.0122 |
| dance shorts | 49 | 0.0173 | 0.0169 |
| diy shorts | 49 | 0.0163 | 0.0127 |
| shorts funny | 34 | 0.0137 | 0.0134 |
| trending shorts | 77 | 0.0122 | 0.0098 |
| comedy shorts | 42 | 0.0116 | 0.0081 |

## Discoveries

1. **Hour 3's `is_gaming` dominance is real but masks wide spread *within*
   gaming.** Top gaming categories (Marvel Rivals 0.0525, Elden Ring 0.0482)
   outperform the worst gaming categories (Roblox 0.0190, Gaming Highlights
   0.0196) by ~2.7x — the binary `is_gaming` flag is a coarse proxy for what
   is really a per-title/per-game effect.
2. **Newer/trending titles (Marvel Rivals, Elden Ring — both had major
   2024-2025 content drops) outperform older established gaming categories
   (Fortnite, Roblox, Minecraft).** Recency/novelty of the game itself may be
   a real engagement driver — worth testing against upload date once that's
   available, separate from the title/category signal used here.
3. **Generic query terms underperform specific ones almost uniformly**:
   "trending shorts" (0.0122), "viral shorts" (0.0175), "shorts funny"
   (0.0137) all rank near the bottom, while specific game/moment terms
   ("shorts clutch" 0.0401, named games) rank near the top. This suggests
   search-term genericness correlates with *crowded, saturated* result pools
   rather than truly top-tier content — a caution for using broad query
   terms as a proxy for "what performs well" in future collection.
4. This refines the V10 scoring direction: instead of one `gaming_event_score`
   weight, the V11 spec (below) should treat **game/category identity as a
   contextual prior**, not a single boolean — consistent with how a real
   production scorer would condition on content type before applying motion/
   hook/surprise scoring.

## Feature/scoring change proposed this hour

Replace the single `is_gaming: bool` input to the V10 model with a
categorical `content_category` (one-hot or embedding) in any future
retraining — flagged here, not yet implemented (would need ≥200 samples per
category to retrain responsibly per the Hour 3 honesty gate; several
categories above are under that threshold individually).

## Next hour

Quick honest thumbnail-level check: pull official `thumbnail_url` CDN images
for the calibration sample (28 records) and look at brightness/edge-density
as crude composition proxies — no face-detection model is available in this
environment, so anything claiming "expression" or "action frame" detection
beyond pixel-level proxies will be marked `insufficient_data` rather than
guessed.
