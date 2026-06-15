// Viral Pattern Research Engine — reference style engine
// Finds corpus exemplars with the most similar STRUCTURE to a given clip, by
// comparing 6-dimension fingerprints. This is similarity of editing structure
// (pacing, hook, payoff, …) — NOT "copy this creator." It only ever matches
// against rows that carry a real measured fingerprint; if none exist it returns
// insufficient_data rather than inventing matches.
//
// See docs/creator-v10/viral-pattern-research-engine.md

"use strict";

const corpus = require("./corpus-store");
const { FINGERPRINT_KEYS } = require("./corpus-schema");

// Max Euclidean distance in the 6-dim [0,100] space (used to normalize to a
// 0..1 similarity). sqrt(6 * 100^2) ≈ 244.95.
const MAX_DISTANCE = Math.sqrt(FINGERPRINT_KEYS.length) * 100;

function distance(a, b) {
  let sum = 0;
  for (const k of FINGERPRINT_KEYS) {
    const d = (Number(a[k]) || 0) - (Number(b[k]) || 0);
    sum += d * d;
  }
  return Math.sqrt(sum);
}

function isFingerprint(fp) {
  return fp && typeof fp === "object" && FINGERPRINT_KEYS.every((k) => Number.isFinite(fp[k]));
}

/**
 * Find the k corpus exemplars structurally closest to `fingerprint`.
 * @param {object} fingerprint  6-dim fingerprint of the clip being analyzed
 * @param {{k?:number, excludeId?:string}} opts
 * @returns {{status:"ok", matches:[...]}|{status:"insufficient_data", have, need}}
 */
function findSimilar(fingerprint, opts = {}) {
  const k = opts.k || 3;
  if (!isFingerprint(fingerprint)) {
    return { status: "insufficient_data", reason: "no_fingerprint", have: 0, need: 1 };
  }

  const exemplars = corpus.readMeasured().filter(
    (r) => isFingerprint(r.fingerprint) && r.id !== opts.excludeId
  );
  if (exemplars.length === 0) {
    return {
      status: "insufficient_data",
      reason: "no_measured_exemplars",
      have: 0,
      need: 1,
      note: "No clips with measured fingerprints in the corpus yet. Exemplars accrue " +
            "from your own renders/uploads and rights-cleared imports.",
    };
  }

  const scored = exemplars
    .map((r) => {
      const d = distance(fingerprint, r.fingerprint);
      return {
        id: r.id,
        platform: r.platform,
        category: r.category,
        title: r.title,
        source: r.source,
        similarity: Number((1 - d / MAX_DISTANCE).toFixed(3)), // 1 = identical structure
        fingerprint: r.fingerprint,
      };
    })
    .sort((a, b) => b.similarity - a.similarity)
    .slice(0, k);

  return {
    status: "ok",
    corpusSize: exemplars.length,
    matches: scored,
    note: "Structural similarity (pacing/hook/payoff shape), not topical or creator similarity.",
    computedAt: new Date().toISOString(),
  };
}

module.exports = { findSimilar, distance, MAX_DISTANCE };
