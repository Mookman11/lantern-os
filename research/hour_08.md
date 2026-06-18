# Σ₀ V11 Research Loop — Hour 8

**Phase:** Anti-collapse diversity analysis of the real collected dataset

## Why this hour

The original handoff's anti-collapse principle says: never optimize
views-only, avoid single-attractor collapse, promote diversity/novelty.
Before writing diversity rules into the V11 spec as `[design]` judgment
calls, this hour checks how diverse the *real collected dataset itself* is
— if the "top-viewed Shorts" pool used for all prior hours' analysis is
itself collapsed onto a few channels/phrases, that would bias every
downstream finding (Hours 1-7) toward those sources' patterns specifically,
which the original handoff explicitly said to avoid ("learn patterns, not
clone creators").

## Real measurements (n=1,451, all from Hour 1's collection)

**Channel concentration:**
- 986 unique channels across 1,451 videos
- Top channel (`Ethobot`) appears 19 times — **1.31% of the dataset**
- Next four: jacobweeby (15), Minku Tinku (14), Paintellectual PriyA (12),
  Little Remy Food (11)
- No single channel exceeds ~1.3% share — **the dataset is not collapsed
  onto a handful of creators.** This directly supports the "reference
  patterns, not copied styles" constraint: any pattern found in Hours 1-7
  reflects a spread across ~986 distinct channels, not a few dominant ones.

**View concentration:**
- Top 10% of videos by views hold 48.7% of total views in the dataset — a
  real, expected power-law skew (a small number of breakout Shorts vastly
  outview the median). This is normal for view-count data and not itself a
  collapse risk, but it does mean **engagement_rate-based training (Hour 3)
  is more robust to this skew than a raw-views-based target would have
  been**, since engagement_rate is a ratio, not an absolute count.

**Title vocabulary:**
- 11,945 total title tokens, 3,497 unique (vocabulary not dominated by
  one phrase — "shorts" itself is the top token at 1,070 occurrences,
  expected since it's in most titles by construction of the search queries)
- Top bigrams are mostly query-category names themselves ("minecraft
  shorts", "apex legends", "elden ring", "marvel rivals", "gta 5") —
  meaning title content closely tracks the category, not a single viral
  phrase repeated across categories.

## Discoveries

1. **No collapse risk found in the collection itself** — channel diversity
   (986 unique, max 1.3% share) and title vocabulary diversity (3,497
   unique tokens) both indicate the dataset spans a genuinely broad creator
   base rather than a few accounts dominating the "top viewed" results.
   This is a real, checkable precondition for trusting Hours 1-7's findings
   as cross-creator patterns rather than a few creators' idiosyncrasies.
2. View-count power-law skew (top 10% = 48.7% of total views) is exactly
   why `engagement_rate` (ratio) was the right Hour 3 training target
   instead of raw views — confirms that earlier design choice was sound,
   with real supporting evidence rather than assumption.
3. No new diversity *rule* is added to the V11 spec this hour — this was a
   validation check on existing data, not a new editing rule. Recorded here
   for the record since it directly evidences the handoff's "don't clone
   creators" constraint being respected in the collection methodology
   itself, not just in how results get used.

## Next hour

Implement the concrete, scoped safe-zone fix identified in Hour 7's
external-research cross-check: add fixed top-10%/right-edge-button
exclusion constants to `apps/lantern-garage/lib/safe-zone-v2.js`'s crop
planner, alongside its existing measured facecam/HUD detection.
