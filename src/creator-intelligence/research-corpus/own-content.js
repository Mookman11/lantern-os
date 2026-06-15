// Viral Pattern Research Engine — own-content learning loop
// The honest, growing data source: every clip Lantern analyzes is the user's
// own content (full rights), so its editing features are genuinely MEASURED and
// can enter the corpus with featureProvenance:"measured" + analysisRef=entryId.
// Over time this is what fills the measured distributions and the exemplar pool.
//
// See docs/creator-v10/viral-pattern-research-engine.md  (Phase 8)

"use strict";

const corpus = require("./corpus-store");
const { fingerprintFromAnalysis } = require("./fingerprint");
const { findSimilar } = require("./reference-engine");

/**
 * Measure the editing features we can honestly derive from a real highlight
 * timeline. Features we cannot measure (caption density on a raw upload, zoom
 * and reaction events without dedicated detectors) stay null — never guessed.
 */
function measureEditingFeatures(analysis, signals) {
  const highlights = Array.isArray(analysis.highlights) ? analysis.highlights : [];
  const durationSec = Math.max(0, Number(analysis.duration) ||
    (highlights.length ? Math.max(...highlights.map((h) => h.end || 0)) : 0));

  const audioPeaks = highlights.filter((h) => Array.isArray(h.tags) && h.tags.includes("audio")).length;

  // strongest beat in the last 20% → its start time is the payoff time
  const lateThreshold = 0.8 * durationSec;
  const late = highlights.filter((h) => h.start >= lateThreshold);
  const payoffTime = late.length
    ? late.reduce((best, h) => ((h.score || 0) > (best.score || 0) ? h : best), late[0]).start
    : null;

  return {
    hookLength: signals && Number.isFinite(signals.timeToFirstEventSec) ? Number(signals.timeToFirstEventSec.toFixed(2)) : null,
    cutFrequency: signals && Number.isFinite(signals.cutsPerMin) ? Number(signals.cutsPerMin.toFixed(2)) : null,
    captionDensity: null,   // not measurable on a raw upload (no burned captions to read)
    zoomEvents: null,       // no zoom detector yet
    reactionEvents: null,   // requires facecam reaction detection
    audioPeaks,
    payoffTime: payoffTime !== null ? Number(payoffTime.toFixed(2)) : null,
  };
}

/**
 * Record an analyzed own clip into the corpus as a measured exemplar.
 * Idempotent per entryId (re-analysis updates nothing; a duplicate id is skipped).
 * @param {{entryId:string, analysis:object, category?:string, platform?:string, title?:string, source?:string}} args
 * @returns {{status:"ok", id, bucket, fingerprint}|{status:"skipped", reason}}
 */
function recordOwnClip(args = {}) {
  const { entryId, analysis } = args;
  if (!entryId || !analysis) return { status: "skipped", reason: "entryId_and_analysis_required" };

  const id = `own_${entryId}`;
  if (corpus.hasId(id)) return { status: "skipped", reason: "already_recorded", id };

  const { fingerprint, viral } = fingerprintFromAnalysis(analysis);
  if (!fingerprint) return { status: "skipped", reason: "no_fingerprint" };

  const features = measureEditingFeatures(analysis, viral.signals);
  const durationSec = Number.isFinite(Number(analysis.duration)) ? Number(analysis.duration) : null;

  const { bucket } = corpus.appendRow({
    id,
    platform: args.platform || "youtube",     // intended publish platform (metadata only)
    category: args.category || "gaming",
    source: args.source || "own_upload",
    collectedAt: new Date().toISOString(),
    title: args.title || `Own clip ${entryId}`,
    creator: "self",
    url: null,
    metadata: { views: null, likeCount: null, commentCount: null, durationSec, publishedAt: null },
    features,
    fingerprint,
    featureProvenance: "measured",
    analysisRef: entryId,
    notes: "own content — measured from real highlight analysis",
  });

  return { status: "ok", id, bucket, fingerprint };
}

/**
 * Read-only research bundle for a clip: its fingerprint + nearest exemplars +
 * current corpus size. Used by the dashboard. Writes nothing.
 * @param {object} analysis  HighlightTimeline-shaped
 * @param {{excludeId?:string, k?:number}} opts
 */
function analyzeClip(analysis, opts = {}) {
  const { fingerprint } = fingerprintFromAnalysis(analysis || {});
  const similar = findSimilar(fingerprint, { k: opts.k || 3, excludeId: opts.excludeId });
  return {
    fingerprint,
    similar,
    corpus: corpus.counts(),
    computedAt: new Date().toISOString(),
  };
}

module.exports = { recordOwnClip, analyzeClip, measureEditingFeatures };
