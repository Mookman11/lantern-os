# V12 Hour 04 — Safe-Zone Facecam Placement (Part 5)

## Problem

The handoff: gameplay fills the full 9:16 frame (no black bars, never cropped
to make room); facecam in the top 15-20%, upper-left; if conflict, **resize the
facecam, never crop gameplay**.

## What was built

`planFacecamPlacement(opts)` added to `safe-zone-v2.js`. Given a facecam exists
in the source, it produces an **output-canvas** PiP rectangle:
- anchored upper-left, in the 10-20% top band (just below the platform
  top-chrome line),
- aspect-ratio preserved for the facecam content,
- capped at `FACECAM_MAX_WIDTH = 0.32`; if a wide facecam would exceed the cap
  or band, **the facecam itself is shrunk** — gameplay (the full-frame base
  layer) is never touched.

Wired into `analyzeForCrop`: when a facecam region is actually detected, the
result now includes `facecamPlacement`. It is **never emitted for footage
without a detected facecam** — not fabricated.

## A real bug, caught and fixed

First implementation computed PiP width as `height × CANVAS_ASPECT /
sourceAspect`. That coincidentally looked correct for a square (1:1) facecam
(÷1 = ×1) but produced a too-narrow box (0.10 instead of ~0.32) for a 16:9
facecam. Correct relation: a normalized box (w,h) over a 1080×1920 canvas
displays pixel content `(w·1080)×(h·1920)`, so preserving aspect requires
`w = h · (1920/1080) · sourceAspect` (multiply, not divide). Fixed and verified
the displayed aspect now matches the source for 16:9, 4:3, and 1:1 exactly.

## Verification (real)

| Facecam | Box | Resized | In band | Aspect preserved |
|---|---|---|---|---|
| 16:9 | w=0.316 h=0.10 | no | ✅ | 1.778 == 1.778 |
| 4:3  | w=0.237 h=0.10 | no | ✅ | 1.333 == 1.333 |
| 1:1  | w=0.178 h=0.10 | no | ✅ | 1.001 == 1.000 |
| 21:9 ultrawide | w=0.320 h=0.077 | **yes** | ✅ | 2.333 == 2.333 |

The 21:9 case is the conflict path: it hit the width cap, so it shrank its own
height (0.10 → 0.077) to stay in band and keep aspect — gameplay untouched.

## Honesty boundary

The handoff's "preserve health/ammo/crosshair/minimap/scoreboard" HUD list
requires real per-element HUD detection that is not built (the existing HUD
heuristic only flags static high-contrast top/bottom bands). `planCrop` already
avoids slicing detected facecam/HUD regions; per-element HUD preservation
remains future work, not faked.
