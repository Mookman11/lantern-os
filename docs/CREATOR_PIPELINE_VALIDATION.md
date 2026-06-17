# Creator Dashboard Pipeline — End-to-End Validation

**Date:** 2026-06-15
**Harness:** `scripts/test_creator_pipeline.js` — drives the **real** backend
(`entry-store` + `JobQueue` + `JobWorker` + `creator-intelligence`), not mocks.
**Result:** **12/12 backend checks passed.**

Run it yourself:

```bash
node scripts/test_creator_pipeline.js
# auto-generates tests/assets/test-video.mp4 (30s) on first run
# writes data/creator/pipeline-test-summary.json
```

---

## Results

| # | Stage | Status | Evidence |
|---|-------|--------|----------|
| 1 | Upload → project entry | ✅ | `createEntry` returns id + filePath + createdAt |
| 2 | Thumbnail from frame | ✅ | `thumbnail.jpg` (~290KB) generated via ffmpeg |
| 3 | Analysis completes to 100% | ✅ | analyze job `status=complete`, `progress=100` |
| 4 | Σ₀ / V10 metrics valid | ✅ | `viralScore=0.736`, `confidence=0.742`, `gamingViralScore=1` — no 0/null/NaN |
| 5 | Highlights generated | ✅ | 5 highlights (real ffmpeg motion/audio/scene detection) |
| 6 | Variants A–E have segments | ✅ | 5 variants, segment counts `[5,5,5,5,5]` |
| 7 | Safe zones detected | ✅ | `status=ok`, regions found, `safezone-overlay.jpg` rendered |
| 8 | Captions generated | ✅ | caption job `count=11` |
| 9 | Render → real mp4 >1MB | ✅ | 7.78MB mp4, passes `ExportValidator` |
| 10 | Render is 1080×1920 | ✅ | ffprobe: `1080,1920` |
| 11 | Persistence after reload | ✅ | title, filePath, thumbnail, analysis, variants, captions, renderRecords all survive |
| 12 | Render lands in project | ✅ | `entries/<id>/renders/<job>-9_16.mp4` recorded as a renderRecord |

The pipeline runs the full chain unattended:

```
createEntry → thumbnail → analyze (Σ₀ scoring) → highlights → variants(+segments)
→ safe zones → captions → render → 1080×1920 mp4 → persisted render record
```

---

## Bugs found and fixed during validation

The first run failed 4/12. All four were real integration breaks where a job
handler called a function that did not exist — code paths that had silently
regressed and were never exercised end-to-end. Fixed:

1. **`entry-store` missing 3 functions.** `job-worker` called
   `addAnalysisRun`, `recordAnalysisError`, `clearAnalysisError`; none were
   defined/exported. The analyze job's audit trail and error-state handling
   threw (caught as non-fatal, so they failed silently). **Added** all three.

2. **Caption job fully broken.** `job-worker` imported `generateVTT`,
   `generateSRT`, `generateJSON` from `caption-engine`, but those functions —
   though defined — were not in `module.exports`. The caption job threw
   `generateVTT is not a function`. **Exported** them.

3. **Safe-zone overlay missing.** The safezones job required
   `renderSafeZoneOverlay` from `safe-zone-v2`, which did not exist. **Implemented**
   it (ffmpeg `drawbox` over normalized region bounds → `safezone-overlay.jpg`).

4. **Render blocked on short variants.** `ExportValidator` requires ≥15s, but a
   short source produced a 13.8s variant → render blocked → no segments persisted.
   **Added** a duration top-up: when the assembled cut-list is under 15s and the
   source has the footage, the export job extends the segments to meet the floor.
   (If the source itself is <15s, it is left unchanged — you genuinely cannot make
   a 15s Short from a 10s clip.)

---

## Σ₀ / V10 metric mapping (honesty note)

The handoff asked for `motion / entropy / hook / collapseRisk / gamingScore`.
The production scorer (`src/creator-intelligence`) does not expose those exact
names; it returns structurally-grounded, confidence-weighted signals. The test
asserts against the **real** fields:

| Handoff name | Real field |
|---|---|
| hook | `viral.componentScores.hookSpeed.score` |
| (scene/motion proxy) | `viral.componentScores.sceneDensity.score`, `audioEnergy.score` |
| overall | `viral.viralScore` + `viral.confidence` |
| gamingScore | `gaming.gamingViralScore` |

These are derived from the real ffmpeg analysis and carry an honest `confidence`
(and `insufficient_data` when structure is absent) rather than fabricated numbers.

---

## Scope — what this validates and what it does not

**Validated (backend, real code, no mocks):** every stage in the table above,
including persistence across a fresh `getEntry` reload from disk.

**Not performed in this pass — live browser click-through (step 12 of the
handoff).** I exercised the real **backend handlers** the UI buttons call, which
is more deterministic than driving pixels, but I did **not** automate Chrome /
Opera GX clicking Upload/Analyze/Render/etc. The HTTP routes that back those
buttons exist (`/api/creator/analyze|variants|captions|safe-zones|export`,
`/api/creator-entries/*`, `/api/dreamer/upload`) and the handlers behind them are
the same code this test drives. A live UI smoke test is a reasonable follow-up.

**Test-data caveat:** the asset is a 30s clip, which is short enough to trigger
the duration top-up (item 4). On a real long upload, variants reach the ~35s
target naturally (e.g. a 17-min source produced 329 highlights and a 36s variant
in earlier runs), so the top-up does not engage.

---

## Reproduction artifacts

- Test driver: `scripts/test_creator_pipeline.js`
- Machine-readable summary: `data/creator/pipeline-test-summary.json` (gitignored)
- Generated fixture: `tests/assets/test-video.mp4` (gitignored, regenerated on run)
