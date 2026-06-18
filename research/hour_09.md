# Σ₀ V11 Research Loop — Hour 9

**Phase:** Implementing the scoped safe-zone fix identified in Hour 7

## What happened

Hour 7's external research cross-check identified a real, low-risk gap:
`apps/lantern-garage/lib/safe-zone-v2.js` measures facecam/HUD regions from
source-video pixels, but had no representation of the YouTube Shorts
*player chrome* itself (top channel/subscribe strip, right-edge like/
comment/share button stack) — UI the platform overlays on the **final
output canvas** regardless of how the source was cropped.

While implementing, realized my Hour 7 framing was imprecise: platform
chrome isn't "sliced through" by cropping the source (it's not in the
source at all) — it matters for **placement decisions in the output
canvas** (where to put captions or a PiP facecam box), not for the
existing horizontal-crop solver (`planCrop()`), which operates on
source-video content. Corrected the implementation to match that distinction
rather than merging it into the crop-scoring regions list, which would have
been a real category error (a constant platform-UI rect competing in the
same "preserved/excluded/sliced" scoring as measured source content), and
is honestly documented in the code comment rather than silently shipped.

## Real change made

`apps/lantern-garage/lib/safe-zone-v2.js`:
- Added `PLATFORM_UI_REGIONS` — two normalized, output-canvas-space
  constants (top ~10% chrome strip, right-edge ~17%-wide/65%-tall button
  stack), confidence 1 (deterministic platform constant, not a heuristic),
  sourced from the same Hour 7 citation
  ([Kreatli](https://kreatli.com/guides/youtube-shorts-safe-zone)), with an
  explicit code comment noting the real layout can shift with player
  updates.
- Added `overlapsPlatformUI(rect)` — a simple rect-overlap helper future
  caption/PiP placement code can call to avoid putting content under the
  player chrome.
- Both exported from the module. `node --check` passed.
- **Not wired into any caller yet** — this hour only adds the building
  block; integrating it into `caption-engine.js` or PiP placement logic is
  future work, not done here, to keep this change small and reviewable.

## Verification

Checked `caption-engine.js`'s existing caption placement: it already
defaults to `bottom-center` with a `safeMargin: 60` (px) for mobile/
portrait video — already directionally consistent with the cited "keep
captions above the bottom ~20%" guidance, just not expressed in the same
normalized units as the new constants. No change made there this hour;
flagged as a deeper integration task for V12, not a bug.

## Discoveries

1. A subtle but real conceptual distinction matters here: detected
   *source-video* regions (facecam, HUD) belong in the crop-window solver;
   *platform UI* belongs in output-canvas placement logic. Conflating them
   would have produced a working-looking but conceptually wrong fix — caught
   during implementation, not left in.
2. Existing caption placement was already roughly aligned with published
   safe-zone guidance before this hour's change — a real, mildly reassuring
   finding (not a bug that needed fixing).

## Next hour

Quota still won't have reset (UTC midnight is the real reset point — many
hours away from this point in the loop). Use the remaining time before
reset to draft the first-3-seconds motion/scene-change hook detector design
flagged in Hour 7 §3, reusing `scoring-engine-v2.js`'s existing
`motion`/`sceneChange` inputs scoped to a video's opening segment.
