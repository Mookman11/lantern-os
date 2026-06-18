// Sigma0 V12 — collapse-risk measurement + anti-collapse multi-peak selection.
//
// This is the SELECTION-DIVERSITY half of Σ₀ for the editor. It deliberately
// does NOT re-implement the viral scorer (src/creator-intelligence/scoring/
// viral-score-v10.js already scores hook/retention/emotion/surprise/pacing/
// rewatch and is the single scoring authority). Instead it answers a different
// question the scorer doesn't: "is this EDIT collapsing onto one repetitive
// moment, or does it carry multiple distinct peaks?" — the anti-collapse
// principle established across research/hour_08.md and hour_13.md (never
// optimize one signal; promote diversity / multiple peaks).
//
// HONESTY BOUNDARY: collapse risk is computed from REAL measured segment
// properties (score distribution, tag diversity, temporal spread). It is a
// structural diversity metric, not a trained model and not a virality claim.

"use strict";

function round3(x) { return Number(Number(x).toFixed(3)); }
function segDur(h) { return Math.max(0, (h.end || 0) - (h.start || 0)); }

// Gini-like concentration of an array of non-negative weights: 0 = perfectly
// even, ~1 = one element holds everything. Used for "does one segment dominate?"
function concentration(weights) {
  const w = weights.filter((x) => x > 0).sort((a, b) => a - b);
  const n = w.length;
  if (n <= 1) return n === 1 ? 1 : 0; // a single segment IS maximally concentrated
  const total = w.reduce((s, x) => s + x, 0);
  if (total === 0) return 0;
  let cum = 0, gini = 0;
  for (let i = 0; i < n; i++) {
    cum += w[i];
    gini += cum / total;
  }
  // Convert the running-sum form to the standard Gini in [0,1].
  return round3(clamp01((n + 1 - 2 * gini / 1) / n));
}

function clamp01(x) { return Math.max(0, Math.min(1, Number.isFinite(x) ? x : 0)); }

// Count distinct local peaks in a chronological score series: a segment whose
// score is >= both neighbors (and above a floor) is a peak. More peaks = less
// collapse.
function countPeaks(chronological) {
  if (chronological.length === 0) return 0;
  if (chronological.length <= 2) return chronological.filter((h) => (h.score || 0) > 0.2).length;
  let peaks = 0;
  for (let i = 0; i < chronological.length; i++) {
    const cur = chronological[i].score || 0;
    const prev = i > 0 ? chronological[i - 1].score || 0 : -Infinity;
    const next = i < chronological.length - 1 ? chronological[i + 1].score || 0 : -Infinity;
    if (cur > 0.2 && cur >= prev && cur >= next) peaks++;
  }
  return peaks;
}

// Tag-set diversity: fraction of distinct tag signatures among segments.
function tagDiversity(highlights) {
  if (highlights.length === 0) return 0;
  const sigs = new Set(highlights.map((h) => (h.tags || []).slice().sort().join("|")));
  return round3(sigs.size / highlights.length);
}

/**
 * Collapse risk of a SELECTION of segments, in [0,1]. 0 = diverse/healthy,
 * 1 = collapsed onto one repetitive pattern. Blends three real measures:
 *   - score concentration (one segment dominating)
 *   - low tag diversity (every segment the same kind of moment)
 *   - single-peak structure (no distinct second peak to sustain interest)
 */
function collapseRisk(highlights) {
  const hs = (highlights || []).filter((h) => segDur(h) > 0);
  if (hs.length === 0) return { risk: 1, reason: "no segments", peaks: 0, tagDiversity: 0, concentration: 1 };
  if (hs.length === 1) return { risk: 1, reason: "single segment — cannot carry multiple peaks", peaks: 1, tagDiversity: tagDiversity(hs), concentration: 1 };

  const conc = concentration(hs.map((h) => h.score || 0));
  const div = tagDiversity(hs);
  const chronological = [...hs].sort((a, b) => (a.start || 0) - (b.start || 0));
  const peaks = countPeaks(chronological);
  const peakPenalty = peaks >= 2 ? 0 : 1; // having <2 distinct peaks is itself a collapse signal

  // Weighted blend: concentration and single-peak structure are the strongest
  // collapse signals; low tag diversity is supporting.
  const risk = clamp01(0.4 * conc + 0.35 * peakPenalty + 0.25 * (1 - div));

  return {
    risk: round3(risk),
    peaks,
    tagDiversity: div,
    concentration: conc,
    reason: risk > 0.6 ? "high collapse risk — edit concentrates on one repetitive moment"
      : risk > 0.35 ? "moderate collapse risk"
      : "healthy diversity — multiple distinct peaks",
  };
}

/**
 * Anti-collapse multi-peak selection. Greedily pick segments that MAXIMIZE
 * marginal diversity (new tag signatures, temporal spread, score spread) rather
 * than just taking the top-N by score — so the final edit carries several
 * distinct peaks instead of clones of one moment.
 *
 * @param {Array} highlights  scored segments (source coords)
 * @param {Object} opts { targetSec=22, maxSec=55, minPeaks=2 }
 * @returns {{ selected: Array, collapse: Object }}
 */
function antiCollapseSelect(highlights, opts = {}) {
  const targetSec = opts.targetSec || 22;
  const maxSec = opts.maxSec || 55;
  const pool = (highlights || []).filter((h) => segDur(h) > 0).sort((a, b) => (b.score || 0) - (a.score || 0));
  if (pool.length === 0) return { selected: [], collapse: collapseRisk([]) };

  const selected = [];
  const usedSigs = new Set();
  let total = 0;

  // Always seed with the single strongest moment (the anchor peak).
  const seed = pool.shift();
  selected.push(seed);
  usedSigs.add((seed.tags || []).slice().sort().join("|"));
  total += segDur(seed);

  // Then greedily add the candidate with the best diversity-adjusted value:
  // its own score, boosted if it brings a NEW tag signature and if it is
  // temporally far from already-selected segments.
  while (pool.length && total < targetSec) {
    let best = null, bestVal = -Infinity, bestIdx = -1;
    for (let i = 0; i < pool.length; i++) {
      const c = pool[i];
      const sig = (c.tags || []).slice().sort().join("|");
      const novelty = usedSigs.has(sig) ? 0 : 0.25;              // reward a new kind of moment
      const minGap = Math.min(...selected.map((s) => Math.abs((c.start || 0) - (s.start || 0))));
      const spread = clamp01(minGap / 10) * 0.15;                 // reward temporal distance (cap ~10s)
      const val = (c.score || 0) + novelty + spread;
      if (val > bestVal) { bestVal = val; best = c; bestIdx = i; }
    }
    if (!best) break;
    if (total + segDur(best) > maxSec) break;
    selected.push(best);
    usedSigs.add((best.tags || []).slice().sort().join("|"));
    total += segDur(best);
    pool.splice(bestIdx, 1);
  }

  // Return in chronological order (a watchable sequence), with the collapse
  // diagnosis of the final selection.
  const ordered = [...selected].sort((a, b) => (a.start || 0) - (b.start || 0));
  return { selected: ordered, collapse: collapseRisk(ordered) };
}

module.exports = { collapseRisk, antiCollapseSelect, concentration, countPeaks, tagDiversity };
