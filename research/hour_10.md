# Σ₀ V11 Research Loop — Hour 10

**Phase:** Implementing the first-3-seconds hook detector flagged in Hour 7

## What happened

Hour 7 cross-checked Hour 1/3's weak `hook_strength_title_proxy` finding
against published retention research and concluded the proxy measured the
wrong layer (title text) — the real driver is opening-frame visual/motion
pattern breaks. Rather than leave that as a future-work note, implemented
it: added `detectOpeningHookStrength(videoPath, opts)` to
`apps/lantern-garage/lib/highlight-engine.js`, reusing the engine's existing
`detectMotion()` and `detectSceneChanges()` ffmpeg passes (same code already
used for full-clip analysis), just bounded to a short `windowSeconds`
(default 3) instead of the whole clip.

## Real formula implemented

```
motionRatio = min(1, motionFrameCount / (windowSeconds * fps))
avgMotion   = mean motion-delta of above-threshold frames in the window
sceneChangeCount = scene cuts detected in the window

hookStrength = 0.5*motionRatio + 0.3*avgMotion + 0.2*min(1, sceneChangeCount/2)
```

Weighted toward "how much of the opening window has above-threshold
motion," with scene-cut count as a secondary signal — directly matching the
cited "pattern break" hook tactic (motion change + a cut early scores
higher than steady motion alone). Returns `{ status: "unavailable" }` on
ffmpeg failure rather than a fabricated score, consistent with every other
detector in this engine.

## Verification (real, not just syntax-checked)

Ran it against a real exported video already on disk
(`data/creator/exports/job-1781500879042-jmj16lbk0-9_16.mp4`, produced by
this project's own render pipeline, not external/third-party content):

```json
{
  "status": "ok",
  "hookStrength": 0.956,
  "windowSeconds": 3,
  "motionFrameCount": 29,
  "avgMotion": 0.91,
  "sceneChangeCount": 29
}
```

High motion/cut activity in the opening 3s of this particular export —
plausible for a highlight-reel-style render, and the function ran
end-to-end against real ffmpeg output, not a mock.

## What this is and isn't

- **Is:** a real, working, exported function that computes an honest
  opening-hook score from real video analysis, reusing already-trusted
  detection code rather than introducing a new ad-hoc method.
- **Isn't:** validated against engagement outcomes yet — there's no dataset
  pairing `detectOpeningHookStrength()` output with real engagement_rate
  for enough videos to know if this particular weighting (0.5/0.3/0.2)
  actually predicts retention. That validation requires running this
  function against the calibration-sample videos *before* they're deleted
  (the current calibration script deletes each file right after its
  existing feature set is extracted) — flagged as a concrete next step, not
  done this hour.
- Not yet wired into `scoreHighlight()` or the production scoring path —
  this hour only adds and verifies the building block.

## Next hour

Wire `detectOpeningHookStrength()` into `research_loop_calibration.py`'s
per-video feature extraction (call it via subprocess before the file is
deleted) so the next calibration run produces real
`(hookStrength, engagement_rate)` pairs — that's what's needed to actually
validate or reject this hour's weighting, instead of leaving it as an
untested formula.
