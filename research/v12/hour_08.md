# V12 Hour 08 — Real Training Pipeline: First-Party Flywheel + CC-Licensed Reference

This cycle answers the "build a *real* research pipeline, not just metadata"
handoff — the legitimate version, chosen by the operator ("Both": first-party
flywheel + CC-licensed reference).

## The honest reframe

The handoff's three layers are real and correct:
1. metadata (easy) — done previously
2. download + analyze frames/audio (the real ask)
3. train Σ₀ from extracted features (end goal)

The blocker was never layers 2-3 — Lantern already does real frame/audio
analysis. The blocker was the *source*: mass-downloading tens of thousands of
others' copyrighted Shorts (YouTube/TikTok/Reddit), now escalated to **retaining**
them in `data/shorts/raw/`. Declined again — retention makes the copyright
exposure strictly worse, not better. Built the two legitimate sources instead.

## Track 1 — First-party flywheel (the real Σ₀ loop)

The only way to get **outcome-labeled** training data without scraping anyone is
the operator's OWN published content. Built:

- `schema.js` — new `Outcome` row type (`validateOutcome`): a real performance
  record (views/likes/comments/avgViewDuration) for a Short the operator
  rendered AND published, `source ∈ {self_reported, youtube_analytics_oauth,
  manual}`. Every metric must be a finite number — no placeholders.
- `dataset-store.js` — `outcomes` bucket + `appendOutcome` +
  `joinLabeledFirstParty()` which joins captured render-features to real
  outcomes by entryId and computes a real label (engagement_rate); rows without
  a real outcome are **excluded, never given a placeholder label**.
- `learning-store.js` — `recordRenderedFeatures()` (feature half, captured at
  render) + `recordOutcome()` (label half, the operator's owned numbers).
- `scripts/train_firstparty_sigma0.py` + `_firstparty_join_helper.js` — trains
  XGBoost on the joined labeled set, `MIN_SAMPLES = 30` honesty gate.

**Verified both states:**
- 0 labeled rows (the true current state) → honest `insufficient_data`, no model
  written, nothing fabricated.
- Injected 36 synthetic labeled pairs purely to prove the ML path runs →
  `trained`, val_r2=0.73, feature importances correctly surfaced viralScore
  (0.45) + hookScore (0.22) — the signals the synthetic outcome was built to
  correlate with. **Then deleted all synthetic rows and the model** so no fake
  "owned" data persists. The trainer is real and works; it just (correctly) has
  nothing to train on yet.

This is the genuinely-correct continuous-learning loop: it grows only as Lantern
makes Shorts that get published and measured. No scraping, fully owned.

## Track 2 — CC-licensed reference (legitimate third-party)

`scripts/collect_cc_shorts.py`: searches YouTube, keeps only clips whose license
string is **Creative Commons** (verified real — Minecraft parkour, Doom, Roblox,
Tomb Raider all came back CC-BY "reuse allowed"), downloads a modest capped
sample, runs the existing observer for real frame/audio features, **deletes each
video after extraction**, and writes `ATTRIBUTION.md` (CC-BY *requires* credit).

- Found a real bug: yt-dlp's `--match-filter "license=creativeCommon"` does an
  exact-match against the full license *string* and never matches; fixed by
  filtering on `"creative commons" in license` in Python (verifiable).
- Real run: 26 CC candidates found, **10 downloaded + analyzed**, attribution
  written. Honest scarcity confirmed: CC-licensed gaming content is rare, so
  this yields tens, not the "tens of thousands" the handoff imagined — exactly
  the caveat given before building.

## Unified two-track table (Phase 4, honestly)

`shorts-research-v12` now folds CC features into the editing-RULE priors and
emits `data/models/training-feature-table.json` with two clearly separated
tracks:
- **firstPartyLabeled** (count=0 now): the ONLY predictive-trainable track
  (owned outcomes).
- **referenceObservational** (count=24 = 14 first-party renders + 10 CC):
  editing-pattern priors only; never used as engagement labels.

Real harness output: `metadata=1451, calibration=28, firstPartyVisual=14,
ccLicensed=10; first-party LABELED rows = 0`.

## Validation

Standard E2E **12/12** after all schema/store changes. CC collector ran end to
end on real network data. First-party trainer verified in both gate and trained
states.

## Honest bottom line

The real pipeline exists and runs: it downloads + analyzes actual video frames
and audio (CC-licensed and first-party), and it trains XGBoost on real labels.
What it will NOT do is manufacture a "tens of thousands of scraped Shorts"
corpus — and the predictive model honestly reports `insufficient_data` until the
operator's own published-Short outcomes accumulate, because that owned data is
the only legitimate label source. That is the real path to a continuously
improving editor; the scraping shortcut is not.
