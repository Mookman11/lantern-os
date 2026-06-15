// Creator Intelligence — public API surface
// Single entry point for the V10 subsystem. Population-dependent calls
// short-circuit to insufficient_data when the subsystem flag is off or the
// dataset is empty. Per-video and export-validation calls work regardless.
//
// See docs/creator-v10/creator-intelligence-architecture.md

"use strict";

const flags = require("./dataset/feature-flags");
const datasetStore = require("./dataset/dataset-store");
const scoreEngine = require("./scoring/score-engine");
const { validateExport, DEFAULTS: EXPORT_DEFAULTS } = require("./scoring/export-validator");
const reverseEngineer = require("./analysis/reverse-engineer");
const learningStore = require("./training/learning-store");
const recommend = require("./recommendations/recommend");
const { scoreVideoV10 } = require("./scoring/score-v10");
const { generateVariantsV10 } = require("./scoring/variant-engine-v10");

// Viral Pattern Research Engine
const researchCorpus = require("./research-corpus/corpus-store");
const { mineEditingPatterns, mineEngagementPatterns } = require("./research-corpus/pattern-miner");
const { fingerprintFromAnalysis } = require("./research-corpus/fingerprint");
const { findSimilar } = require("./research-corpus/reference-engine");
const { recordOwnClip, analyzeClip } = require("./research-corpus/own-content");
const { collectYouTube, importMetadataRow } = require("./research-corpus/collect-youtube");

function subsystemEnabled(env) {
  return flags.isEnabled("creatorIntelligence", env);
}

function disabledResult(reason = "subsystem_disabled") {
  return { status: "insufficient_data", reason, have: 0, need: null };
}

module.exports = {
  // Flags
  flags: (env) => flags.resolveFlags(env),
  isEnabled: flags.isEnabled,

  // Dataset (counts always honest, even when subsystem disabled)
  dataset: {
    counts: () => datasetStore.counts(),
    gamingCountsByGame: () => datasetStore.gamingCountsByGame(),
    appendGeneral: (row) => datasetStore.appendGeneral(row),
    appendGaming: (row) => datasetStore.appendGaming(row),
    refreshManifest: () => datasetStore.refreshManifest(),
  },

  // Analysis (gated by researchReport + dataset sufficiency)
  analysis: {
    reverseEngineer: (opts, env) =>
      flags.isEnabled("researchReport", env)
        ? reverseEngineer.reverseEngineer(opts)
        : disabledResult("researchReport_flag_off"),
  },

  // Scoring (gated by subsystem + dataset sufficiency)
  scoring: {
    viralScore: (features, opts, env) =>
      subsystemEnabled(env) ? scoreEngine.viralScore(features, opts) : disabledResult(),
    retentionScore: (features, opts, env) =>
      subsystemEnabled(env) ? scoreEngine.retentionScore(features, opts) : disabledResult(),
    gameSufficiency: (game) => scoreEngine.gameSufficiency(game),
  },

  // V10 per-clip structural scoring (always real — computed from the user's own
  // analyzed video; never population claims). Returns viral/gaming/retention/grade.
  scoreVideoV10: (analysis, opts) => scoreVideoV10(analysis, opts),

  // V10 multi-variant generator (5 ranked strategy variants, real cut-lists).
  generateVariantsV10: (analysis, opts) => generateVariantsV10(analysis, opts),

  // Continuous learning (first-party data — always allowed)
  training: learningStore,

  // Recommendations (per-video always real; population path honest)
  recommendations: {
    forVideo: (analysis) => recommend.forVideo(analysis),
  },

  // Viral Pattern Research Engine — learns reusable editing PATTERNS, never
  // clones creators. Per-clip fingerprint/similarity is always real (measured
  // from the user's own analyzed clip). Population mining + collection are gated
  // by the viralResearch flag and honestly return insufficient_data when empty.
  research: {
    // Always real: structural fingerprint of the user's own clip.
    fingerprint: (analysis) => fingerprintFromAnalysis(analysis || {}),
    // Read-only bundle (fingerprint + nearest exemplars + corpus counts).
    analyzeClip: (analysis, opts, env) =>
      flags.isEnabled("viralResearch", env)
        ? analyzeClip(analysis, opts)
        : disabledResult("viralResearch_flag_off"),
    // Continuous-learning: record an analyzed own clip as a measured exemplar.
    recordOwnClip: (args, env) =>
      flags.isEnabled("viralResearch", env)
        ? recordOwnClip(args)
        : { status: "skipped", reason: "viralResearch_flag_off" },
    findSimilar: (fingerprint, opts) => findSimilar(fingerprint, opts),
    // Corpus counts are always honest, even when the flag is off.
    corpus: {
      counts: () => researchCorpus.counts(),
      refreshManifest: () => researchCorpus.refreshManifest(),
    },
    // Pattern mining over real rows (insufficient_data until enough exist).
    mineEditingPatterns: (env) =>
      flags.isEnabled("viralResearch", env) ? mineEditingPatterns() : disabledResult("viralResearch_flag_off"),
    mineEngagementPatterns: (env) =>
      flags.isEnabled("viralResearch", env) ? mineEngagementPatterns() : disabledResult("viralResearch_flag_off"),
    // Public reference collection (metadata only; needs YOUTUBE_API_KEY).
    collectYouTube: (opts, env) =>
      flags.isEnabled("viralResearch", env)
        ? collectYouTube(opts)
        : Promise.resolve(disabledResult("viralResearch_flag_off")),
    importMetadataRow: (entry, env) =>
      flags.isEnabled("viralResearch", env)
        ? importMetadataRow(entry)
        : { status: "skipped", reason: "viralResearch_flag_off" },
  },

  // Export validation (real ffprobe; flag on by default)
  validateExport: (outputPath, options, env) => {
    if (!flags.isEnabled("exportValidator", env)) {
      return Promise.resolve({
        ok: true,
        checks: [{ name: "validator", ok: true, actual: "skipped (flag off)" }],
        blockedReasons: [],
        skipped: true,
        probedAt: new Date().toISOString(),
      });
    }
    return validateExport(outputPath, options);
  },
  EXPORT_DEFAULTS,
};
