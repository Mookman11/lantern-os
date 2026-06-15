// Viral Pattern Research Engine — pattern miner
// Computes aggregate patterns over the corpus. Two honest, separate views:
//
//   mineEditingPatterns()    — distributions of MEASURED editing features
//                              (cut frequency, hook length, …). Only consumes
//                              rows whose features were actually measured.
//   mineEngagementPatterns() — topic/length ↔ views relationships over rows
//                              that have real public view counts (metadata).
//
// Both return { status:"insufficient_data", have, need } until enough real rows
// exist. Nothing is extrapolated from priors here — priors live in
// research/viral_patterns.json and are kept distinct from measured data.
//
// See docs/creator-v10/viral-pattern-research-engine.md

"use strict";

const corpus = require("./corpus-store");
const { EDITING_FEATURE_KEYS } = require("./corpus-schema");

// Minimum measured rows before a distribution is meaningful enough to report.
// Deliberately conservative — below this the answer is "insufficient_data".
const MIN_MEASURED_FOR_DISTRIBUTION = 30;
const MIN_ROWS_FOR_ENGAGEMENT = 50;

function percentile(sortedAsc, p) {
  if (sortedAsc.length === 0) return null;
  const idx = (sortedAsc.length - 1) * p;
  const lo = Math.floor(idx), hi = Math.ceil(idx);
  if (lo === hi) return sortedAsc[lo];
  return sortedAsc[lo] + (sortedAsc[hi] - sortedAsc[lo]) * (idx - lo);
}
function round(x, n = 2) { return x === null ? null : Number(Number(x).toFixed(n)); }
function mean(a) { return a.length ? a.reduce((s, v) => s + v, 0) / a.length : null; }

/**
 * Distributions (p10/p50/p90/mean/n) for each editing feature, computed only
 * over rows where that feature has a non-null measured value.
 */
function mineEditingPatterns() {
  const rows = corpus.readMeasured();
  if (rows.length < MIN_MEASURED_FOR_DISTRIBUTION) {
    return {
      status: "insufficient_data",
      have: rows.length,
      need: MIN_MEASURED_FOR_DISTRIBUTION,
      note: "Editing-feature distributions need more measured clips. They accrue " +
            "automatically from your own renders/uploads (and any rights-cleared imports).",
    };
  }

  const features = {};
  for (const key of EDITING_FEATURE_KEYS) {
    const vals = rows
      .map((r) => (r.features ? r.features[key] : null))
      .filter((v) => typeof v === "number" && Number.isFinite(v))
      .sort((a, b) => a - b);
    features[key] = vals.length
      ? {
          n: vals.length,
          p10: round(percentile(vals, 0.10)),
          p50: round(percentile(vals, 0.50)),
          p90: round(percentile(vals, 0.90)),
          mean: round(mean(vals)),
        }
      : { n: 0, p10: null, p50: null, p90: null, mean: null };
  }

  return {
    status: "ok",
    sampleSize: rows.length,
    basis: "measured_corpus",
    calibrated: false,
    features,
    computedAt: new Date().toISOString(),
  };
}

function pearson(xs, ys) {
  const n = xs.length;
  if (n < 2) return null;
  const mx = mean(xs), my = mean(ys);
  let num = 0, dx = 0, dy = 0;
  for (let i = 0; i < n; i++) {
    const a = xs[i] - mx, b = ys[i] - my;
    num += a * b; dx += a * a; dy += b * b;
  }
  const den = Math.sqrt(dx * dy);
  return den === 0 ? null : num / den;
}

/**
 * Engagement view: median views per category and the duration↔views
 * correlation, over public reference rows that actually have view counts.
 * This is the part the API-metadata collection (100k+ view Shorts) feeds.
 */
function mineEngagementPatterns() {
  const rows = corpus.readWithViews();
  if (rows.length < MIN_ROWS_FOR_ENGAGEMENT) {
    return {
      status: "insufficient_data",
      have: rows.length,
      need: MIN_ROWS_FOR_ENGAGEMENT,
      note: "Engagement correlations need more public reference rows (collect via the " +
            "YouTube Data API or manual metadata entry).",
    };
  }

  // Median views per category
  const byCategory = {};
  for (const r of rows) {
    const cat = r.category || "other";
    (byCategory[cat] = byCategory[cat] || []).push(r.metadata.views);
  }
  const medianViewsByCategory = {};
  for (const [cat, vals] of Object.entries(byCategory)) {
    const sorted = vals.slice().sort((a, b) => a - b);
    medianViewsByCategory[cat] = { n: sorted.length, medianViews: round(percentile(sorted, 0.5), 0) };
  }

  // duration ↔ views correlation over rows that have both
  const dv = rows.filter((r) => typeof r.metadata.durationSec === "number");
  const durationViewsCorr = dv.length >= 2
    ? round(pearson(dv.map((r) => r.metadata.durationSec), dv.map((r) => r.metadata.views)), 3)
    : null;

  return {
    status: "ok",
    sampleSize: rows.length,
    medianViewsByCategory,
    durationViewsCorr,
    durationViewsN: dv.length,
    note: "Correlation is descriptive of the collected sample, not causal and not calibrated.",
    computedAt: new Date().toISOString(),
  };
}

module.exports = {
  MIN_MEASURED_FOR_DISTRIBUTION, MIN_ROWS_FOR_ENGAGEMENT,
  mineEditingPatterns, mineEngagementPatterns,
};
