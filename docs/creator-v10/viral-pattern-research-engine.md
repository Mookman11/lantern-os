# Viral Pattern Research Engine (V10)

A permanent research subsystem that **learns reusable editing patterns, not
specific creators.** It collects high-performing reference videos, extracts
measurable features where it is *allowed* to measure them, stores everything
with explicit provenance, and uses the result to fingerprint and compare the
user's own clips.

Lives in `src/creator-intelligence/research-corpus/`. Gated by the
`viralResearch` feature flag (`LANTERN_CI_VIRAL_RESEARCH=1`). Per-clip
fingerprinting is pure measurement and is always available.

## The honesty constraint (why this is built the way it is)

The editing features at the heart of the spec — `hookLength`, `cutFrequency`,
`captionDensity`, `zoomEvents`, `reactionEvents`, `audioPeaks`, `payoffTime` —
**cannot be obtained from any platform API.** YouTube/TikTok/Instagram APIs
return engagement metadata (views, duration, title, category, publish date).
They do **not** return cut frequency or zoom events; those require analyzing the
actual video frames/audio, i.e. downloading the file.

So the corpus separates two kinds of rows and never conflates them:

| Provenance | Source | What it carries | How |
|---|---|---|---|
| `metadata-only` (`featureProvenance:"null"`) | `youtube_data_api`, `manual_metadata` | views/duration/title/category | Public APIs or manual entry. Editing features stay `null`. No video downloaded. |
| `measured` (`featureProvenance:"measured"`) | `own_render`, `own_upload`, `local_import` | real editing features + fingerprint | ffmpeg analysis of a video Lantern is allowed to open (your own content or rights-cleared imports). Requires a non-empty `analysisRef`. |

The schema validator (`corpus-schema.js`) **rejects at append time** any row
that puts a number in `features` without a `measured` provenance + `analysisRef`,
and forbids metadata-only sources from carrying measured features. This is what
makes a fabricated `zoom_events: 14` for a video we never opened structurally
impossible to store.

## Modules

| File | Responsibility |
|---|---|
| `corpus-schema.js` | Row schema + validators incl. the fabrication guard |
| `corpus-store.js` | Append/read under `data/viral-research/{youtube,tiktok,reels,gaming,own}/`; honest counts split by provenance; `MANIFEST.json` |
| `fingerprint.js` | 6-dim structural fingerprint (0–100) derived from real `viralScoreV10` component scores |
| `pattern-miner.js` | `mineEditingPatterns()` (distributions over measured rows) + `mineEngagementPatterns()` (topic/length↔views over metadata rows); both gate on `insufficient_data` |
| `reference-engine.js` | Nearest-neighbour over fingerprinted exemplars; structural similarity, never "copy this creator" |
| `collect-youtube.js` | YouTube Data API metadata-only collection (needs `YOUTUBE_API_KEY`) + manual import for TikTok/Reels |
| `own-content.js` | Records each analyzed own clip as a measured exemplar (the growing data source) + read-only `analyzeClip` bundle for the dashboard |

## Fingerprint dimensions

Each 0–100, a deterministic transform of measured component scores:

- **hookStrength** — speed of first payoff (`hook` component)
- **payoffStrength** — strength of the late/ending beat (`rewatch`)
- **captionDensity** — caption-able beat density (`captionPotential`)
- **motionIntensity** — pacing + energy (`pacing` + `emotion`)
- **curiosityGap** — multi-signal surprise spikes (`surprise`)
- **loopability** — end-payoff + hook combined

## Data flow

```
Analyze job (own clip)
  → viralScoreV10 (real signals)
  → fingerprint  (always)                       ── persisted to entry.researchV10
  → [flag on] recordOwnClip → measured corpus row (analysisRef = entryId)
  → [flag on] findSimilar → nearest exemplars   ── persisted to entry.researchV10

Collection (optional, flag on)
  POST /api/creator/research/collect  → YouTube Data API → metadata-only rows
  POST /api/creator/research/import   → manual TikTok/Reels metadata row

Dashboard
  entry.html "Viral Research Analysis" → fingerprint bars + similarity / honest empty
  GET /api/creator/research/patterns  → corpus counts + mined patterns
```

## Public API (`src/creator-intelligence/index.js` → `research`)

- `research.fingerprint(analysis)` — always real
- `research.analyzeClip(analysis, opts)` — fingerprint + similar + counts (flag-gated)
- `research.recordOwnClip({entryId, analysis, category})` — flag-gated, idempotent per entryId
- `research.findSimilar(fingerprint, opts)`
- `research.mineEditingPatterns()` / `research.mineEngagementPatterns()`
- `research.collectYouTube(opts)` / `research.importMetadataRow(entry)`
- `research.corpus.counts()` — always honest, even with the flag off

## Sufficiency thresholds

- `MIN_MEASURED_FOR_DISTRIBUTION = 30` — editing-feature distributions
- `MIN_ROWS_FOR_ENGAGEMENT = 50` — topic/length↔views correlations
- reference matching needs ≥1 fingerprinted exemplar; otherwise `insufficient_data`

Below threshold, the API returns `{status:"insufficient_data", have, need}` and
the dashboard shows an honest empty state — never a fabricated number.

## Not yet implemented (honest gaps)

- Zoom/reaction event detection (`zoomEvents`/`reactionEvents` stay `null` on own
  clips until dedicated detectors exist)
- Caption density measurement on raw uploads (no burned captions to read)
- TikTok/Reels bulk collection (no sanctioned API — manual import only)
- Outcome labeling (real post-performance) to move from structural to calibrated
