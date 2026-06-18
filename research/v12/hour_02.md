# V12 Hour 02 — Negative Content Detectors (Part 3)

## Problem

The handoff: Lantern sometimes selects dead air, conversations, menus, loading
screens. Never do this. Apply a hard `score *= 0.15` penalty to such regions.

## What was built

Four heuristic detectors in `highlight-engine.js`, applied inside
`mergeDetections` before a frame's density forms a highlight candidate:

| Detector | Fires when (from real measured signals) |
|---|---|
| `detectConversation` | loud + sustained (low transient) audio + static scene + modest motion |
| `detectIdleGameplay` | nonzero motion but no combat, no scene change, **sustained ≥ 2.5s** |
| `detectMenuOrLoadingScreen` | near-zero scene change + no audio transient, **sustained ≥ 1.5s** |
| `detectStaticFrames` | motion + scene + audio all near zero, **sustained ≥ 1.5s** |

A hit multiplies that frame's density by `NEGATIVE_CONTENT_PENALTY = 0.15`
(exactly the handoff's value). Crucially, idle/menu/static require the pattern
to **hold over real consecutive seconds** (tracked via streak timers that reset
on any real time gap) — so a momentary lull right before a kill is not punished,
only genuinely sustained dead air is.

## Honesty boundary

These are NOT visual classifiers. There is no OCR, no menu template matching,
no kill-feed parsing. They are combinations of the same three measured signals
(motion / scene-change / audio) the engine already computes. They will have
false positives/negatives; they are a coarse filter, not a guarantee. The
handoff's "reward kills / crosshair snaps / damage flashes / victory screens"
asks for real CV event detection that is explicitly **not built** (would need a
trained model) — those remain `insufficient_data`, not faked.

## Verification (real)

Unit tests on each detector (sustain thresholds enforced):
- conversation true on talking, false on real action
- idle true only after ≥2.5s sustain, false at 1s
- menu/static true only after sustain, false on real scene change / any real signal

End-to-end on a synthetic 24s clip (8s static + 4s action + 12s idle):
```
per-second density during sustained idle:  0.08 -> 0.012  (= 0.08 x 0.15)
```
The 0.15 penalty engages exactly when the idle streak crosses 2.5s. Full
dead-air exclusion is shown in `hour_06.md` (validation).
