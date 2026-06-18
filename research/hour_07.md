# Σ₀ V11 Research Loop — Hour 7

**Phase:** External research (published industry data), triangulated against this loop's first-party measurements

## Why this hour is different

Hours 1-6 exhausted today's YouTube Data API quota (7,971/8,000 units used
at ~13:00 UTC; resets at 00:00 UTC — roughly 11 hours from this hour's
start). No new first-party metadata is collectible until then. Rather than
pad time with restated analysis of the same 1,451-record dataset, this hour
does real, citable web research into published Shorts editing/retention
findings, then checks each claim against our own Hour 1-5 numbers instead
of accepting it uncritically. Quota-reset collection is scheduled to resume
automatically later in this 12-hour window (see "Next" below).

All findings here are tagged **[external]** (third-party published claim,
cited) to keep them clearly distinct from **[data]** (this project's own
measurement) and **[design]** (unvalidated judgment call) used in
`docs/SIGMA0-V11-EDITOR.md`.

## Hook timing

**[external]** Industry sources report 50-60% of Shorts viewer drop-off
happens in the first 3 seconds, with a target "intro retention" (viewed vs.
swiped away) of 70-75%+ for healthy distribution. Recommended hook tactics:
pattern breaks (unusual framing/motion/contradiction), starting mid-action
(no slow intros/greetings), and "curiosity gap" framing.
[JoinBrands](https://joinbrands.com/blog/youtube-shorts-best-practices/),
[Shortimize](https://www.shortimize.com/blog/youtube-shorts-retention-rate),
[Virvid](https://virvid.ai/blog/first-3-seconds-hook-faceless-shorts-2026)

**Cross-check against [data]:** Hour 1/3's `hook_strength_title_proxy`
(title-text hook-word density) showed weak correlation with engagement_rate
in our 1,451-record sample. This is not a contradiction — the external
research above is about the **first 3 seconds of video content** (motion/
framing/pacing), not title wording. Our proxy measured the wrong layer
(title text) for what the cited research says actually drives retention
(visual hook in the opening frames). **Revision to the V11 spec:** the Hook
Rules section should stop treating title hook-words as the primary hook
signal and instead prioritize a real first-3-seconds visual-motion-change
detector — which is exactly what's still listed as not-yet-built in §3 of
the spec. This external research sharpens *why* that gap matters, it
doesn't replace the work needed to close it.

## Length / pacing

**[external]** 15-30s clips show the highest retention (often 80%+) for
quick-payload content (setup/surprise/payoff); 45-60s suits narrative
formats. The algorithm rewards retention *percentage* over raw length — a
30s clip at 85% watch-through beats a 60s clip at 50%.
[Opus](https://www.opus.pro/blog/ideal-youtube-shorts-length-format-retention),
[Toptal](https://www.toptal.com/creator/post/youtube-shorts-length)

**Cross-check against [data]:** Hour 1's real collected dataset had mean
duration 31.3s (general) / 33.1s (gaming) among top-viewed Shorts — sitting
almost exactly inside the cited 25-35s "breakout" range. This is a genuine
triangulation: independently-collected real view-sorted data lines up with
published retention research. **No change to the existing 60s ceiling is
warranted** (already correctly set, per Hour 2's report) — but this is
support for *favoring* shorter highlights within that ceiling when several
qualifying segments compete for inclusion, not a hard new rule.

## Gaming highlight detection

**[external]** Production highlight-clipping tools (Eklipse and similar)
use multi-signal detection: in-game UI cues (kill feed, score spikes,
objective captures) combined with audio cues (kill-confirmation sounds,
caster/crowd reactions). Clip length is adaptive to the moment type (a
no-scope ≈ 6s, a multi-stage clutch ≈ 22s) rather than fixed.
[Eklipse](https://blog.eklipse.gg/streaming-tips/how-gameplay-intelligence-works-2.html),
[Eklipse FAQ](https://eklipse.gg/help/how-can-i-automatically-clip-the-most-exciting-highlights-from-fast-paced-esports-matches/)

**Relevance to §5 (Gaming Event Detector) of the V11 spec:** this confirms
the right approach is audio-cue + on-screen-UI-cue fusion, not a single
visual-only classifier — and that **adaptive clip length keyed to event
type** (not a fixed highlight duration) is the production-grade pattern.
This is still flagged as future work (no such detector was built this
loop), but the design direction is now grounded in how real, deployed
systems do it rather than guessed from scratch.

## Facecam / safe zone layout

**[external]** Recommended Shorts safe zone: avoid top ~10% (profile/UI),
keep titles/captions above bottom ~20%, keep faces centered in the middle
~60% of frame; engagement-button cluster occupies a ~120px-wide strip ~60px
from the right edge on a 1080×1920 canvas.
[Kreatli](https://kreatli.com/guides/youtube-shorts-safe-zone),
[Kreatli Hub](https://kreatli.com/guides/safe-zone-guide)

**Cross-check against [existing]:** `apps/lantern-garage/lib/safe-zone-v2.js`
already does measured facecam/HUD detection plus 9:16 crop planning, but
its grid-cell approach doesn't currently encode an explicit "avoid top 10% /
right-edge button strip" constant the way the cited guide does. **Concrete,
low-risk improvement identified:** add the published right-edge button-zone
and top-10% exclusion as additional fixed-region constraints in the crop
planner, alongside its existing measured facecam/HUD detection — this is a
real, scoped code change (not yet made) rather than a speculative one.

## Discoveries this hour

1. Two independent triangulations were found: our duration data matches
   published retention-optimal ranges, and the existing safe-zone module's
   gap (no explicit right-edge-button exclusion) is now a concretely
   scoped, citable fix rather than a vague todo.
2. The original hook-strength proxy (title text) was measuring the wrong
   layer — published research is about opening-frame visual/motion hooks,
   not titles. This is a real correction to the V11 spec's framing, not
   just new information layered on top.
3. Adaptive (event-type-keyed) clip length, not fixed duration, is the
   production-grade pattern for gaming highlight detection — worth carrying
   into any future highlight-engine work.

## Next

Quota resets at 00:00 UTC (~11h from this hour). A wake-up is scheduled
near that time to attempt a second real collection batch (more unique
videos, ideally pushing the per-category sample sizes in Hour 4's table
toward the 200-sample retraining threshold), followed by a retrain and an
hour report covering the result. Between now and then, remaining hours
continue external-research-grounded analysis and start scoping the
right-edge safe-zone fix identified above.
