# Σ₀ V11 Research Loop — Hour 12 (Final)

**Phase:** Validating the Hour 10 hook detector against real engagement_rate — and a real negative result

## Process note (caught before it corrupted results)

The Hour 11 background calibration run was launched twice — an earlier
attempt using `nohup ... &` inside the bash tool didn't die when I thought
it had (same false-completion pattern noted in this project's earlier
session work), so it kept running concurrently with the second, correctly
backgrounded run. Both processes appended to
`data/youtube/calibration_features.jsonl`, producing 18 duplicate
`video_id` rows (46 total instead of 28). Caught by checking for duplicate
IDs before analyzing; deduped down to 28 unique records (preferring the
row with the new `opening_hook_strength` field where both copies had it).
No data was fabricated or silently discarded without checking — the
duplication was a process bug, not a data quality issue, and is recorded
here rather than hidden.

## Real result: the Hour 10 hook detector does not discriminate at this calibration's scale

Ran the prepared correlation check (`opening_hook_strength` vs.
`engagement_rate`) on the deduped 28-record set:

```
n=28  mean_hook=0.981  mean_engagement_rate=0.01938  pearson_r=-0.505
```

That r=-0.505 number is **not a trustworthy finding** — looking at the raw
values explains why:

| opening_hook_strength | count |
|---|---|
| 0.933 | 1 |
| 0.967 | 1 |
| **0.983** | **26 of 28** |

**26 of 28 videos score exactly 0.983.** The formula from Hour 10
(`0.5·motionRatio + 0.3·avgMotion + 0.2·min(1, sceneChangeCount/2)`) is
saturating at its ceiling for nearly every real video in this sample —
the `motionThreshold=0.1` / `sceneThreshold=0.2` defaults are loose enough,
and `windowSeconds=3` at `fps=10` short enough, that almost any real Short
trips the "high motion in the opening" condition. The reported negative
correlation is driven by only 2 non-clipped data points and is statistical
noise, not a real "more hook strength = less engagement" relationship —
reporting it as a validated finding would violate this project's honesty
rule by overstating noise as signal.

## Digging one level deeper: even the non-saturated component shows no effect

Looking at the raw per-video detail (`opening_hook_detail` in
`calibration_features.jsonl`): `motionFrameCount` and `sceneChangeCount`
are both pinned at ~28-29 of 30 possible frames for nearly every video —
`motionThreshold=0.1` and `sceneThreshold=0.2` are loose enough that almost
every frame transition in a 3s/10fps window trips them, regardless of the
video. **`avgMotion` is the one component that isn't saturated** — it
ranges real-valued from 1.56 to 10.18 across the 28 videos, a genuine
~6.5x spread.

Correlating just `avgMotion` against `engagement_rate` directly:

```
n=28  mean_avgMotion=5.14  pearson_r=0.0024
```

**Essentially zero.** This is a cleaner, more useful negative result than
the saturated-composite-score noise reported above: even the one real,
unsaturated motion signal this hour could measure shows no relationship
with engagement_rate at this sample size.

**Important honesty caveat on what this does and doesn't disprove:** the
Hour 7 external research's claim was about "intro retention %" (viewed vs.
swiped-away, measured inside YouTube Studio analytics) — a metric this
project has no access to via the public Data API. `engagement_rate`
((likes+comments)/views) is a different, weaker proxy. A null result
comparing opening motion to `engagement_rate` does **not** invalidate the
cited retention research — it means `engagement_rate` may not be the right
target to validate a hook-timing hypothesis against, separate from whether
the detector itself needs recalibration (both are true here).

## Honest conclusion

**The Hour 10 detector, as built, is not yet a useful discriminative score
— most real Shorts saturate it to the same value, and even its one
unsaturated component shows no measured relationship with the only
engagement proxy available to this project.** This is a legitimate, real
negative result from real testing, not a failure to hide. Two separate
fixes are needed before this line of work can inform production scoring:
(1) tighten `motionThreshold`/`sceneThreshold` so the score spreads across
real opening-segment activity instead of saturating, and (2) get access to
real retention-percentage data (YouTube Studio / Analytics API, which
requires channel-owner OAuth this project doesn't currently have) rather
than continuing to validate hook hypotheses against `engagement_rate`,
which may simply be the wrong target for this specific question.

**Correcting `docs/SIGMA0-V11-EDITOR.md` §3 (Hook Rules):** the detector
built in Hour 10 stays `[existing-but-uncalibrated]`, not `[data]` —
exported and working code, but not yet shown to predict anything. This
hour's finding is added to the spec below.

## What 12 hours of this loop actually produced (honest final accounting)

- 1,451 real, deduplicated YouTube Shorts metadata records (today's full
  API quota — quota does not reset again until 00:00 UTC, several hours
  past this loop's 12-hour window)
- 28 real calibration clips with motion/scene/audio/thumbnail/opening-hook
  measurements, video files never retained
- A trained baseline model (val_r2=0.199) — weak but honestly characterized
- A real, citation-grounded category-level engagement finding (Hour 4)
- Two real, shippable code changes: `safe-zone-v2.js`'s `PLATFORM_UI_REGIONS`
  constant + `overlapsPlatformUI()` helper, and `highlight-engine.js`'s
  `detectOpeningHookStrength()` — the latter now known, via real testing, to
  need recalibration before it's useful
- A documented, citation-backed `docs/SIGMA0-V11-EDITOR.md` distinguishing
  validated data, reused existing code, external research, and untested
  design judgment at every section
- One real negative result (this hour) — exactly the kind of finding the
  project's honesty rule exists to surface rather than bury

## What's still not done

- Recalibrating `detectOpeningHookStrength()`'s thresholds against this
  same 28-video ground truth until it actually spreads/discriminates
  (next concrete step, not done this loop)
- Frame-level gaming-event (kill/clutch) detection — still future work
- Face/expression-based thumbnail scoring — still blocked on no face model
  in this environment
- Further metadata collection — blocked on quota until 00:00 UTC
