// Score V10 orchestrator — one call that produces the full V10 scoring bundle
// for an analyzed clip: structural viral score, optional gaming score, retention
// prediction, and editor grade. Every number is computed from real analysis
// signals; nothing is mocked.
//
// Spec: "V10 SCORING ENGINE REDESIGN" Phases 2-4, 8.

"use strict";

const { viralScoreV10 } = require("./viral-score-v10");
const { gamingScoreV10 } = require("./gaming-score-v10");
const { retentionPredictV10 } = require("./retention-predictor-v10");
const { editorGradeV10 } = require("./editor-grade");
// V12 Σ₀ collapse diagnosis (selection-diversity). Required defensively so this
// module still loads if the lantern-garage lib tree is absent.
let collapseRisk = null;
try {
  ({ collapseRisk } = require("../../../apps/lantern-garage/lib/sigma0-v12"));
} catch { /* sigma0-v12 unavailable — collapse diagnosis omitted */ }

/**
 * @param {Object} analysis  HighlightTimeline.toJSON()-shaped: { duration, highlights[] }
 * @param {Object} opts       { gaming, safeZones, cropPlan }
 *   - gaming:    boolean — also compute the gaming-specific score
 *   - safeZones: SafeZoneDetectorV2 region output (for facecam-based reaction)
 *   - cropPlan:  SafeZoneDetectorV2 crop plan (for safe-zone compliance in grade)
 */
function scoreVideoV10(analysis = {}, opts = {}) {
  const viral = viralScoreV10(analysis);
  const retention = retentionPredictV10(viral);
  const grade = editorGradeV10(viral, { cropPlan: opts.cropPlan });

  const result = {
    version: "10.0",
    basis: "structural_heuristic",
    calibrated: false,
    viral,
    retention,
    editorGrade: grade,
    computedAt: new Date().toISOString(),
  };

  // V12: attach the Σ₀ collapse diagnosis of the edit's selected segments, so
  // downstream ranking can prefer diverse (multi-peak) edits over collapsed
  // (single repetitive moment) ones. Real diversity metric, not a virality claim.
  if (collapseRisk && Array.isArray(analysis.highlights)) {
    result.sigma0 = collapseRisk(analysis.highlights);
  }

  if (opts.gaming) {
    result.gaming = gamingScoreV10(viral, { safeZones: opts.safeZones, facecamPresent: opts.facecamPresent });
  }

  // V12 weighted edit score (the handoff's explicit formula). Reuses the REAL
  // viral component scores instead of duplicating the scorer; components that
  // require detectors not present (faceReaction, gameplayIntensity without a
  // facecam/gaming signal) are excluded and the remaining weights renormalized,
  // so the score is honest about what it actually measured rather than faking
  // unavailable inputs.
  result.weightedEditScore = weightedEditScore(viral, result.gaming, opts);

  // Top-level headline numbers for convenience (all traceable to the above).
  result.headline = {
    viralScore: viral.viralScore,
    gamingViralScore: opts.gaming ? result.gaming.gamingViralScore : null,
    predictedCompletionRate: retention.predictedCompletionRate,
    predictedShareRate: retention.predictedShareRate,
    editorGrade: grade.grade,
    confidence: viral.confidence,
  };

  return result;
}

// The handoff's explicit weighted formula, computed from REAL viral components.
// Mapping (handoff term -> real measured component):
//   viralScore        -> viral.viralScore
//   excitement        -> surprise component (multi-signal spike rate)
//   sceneEnergy       -> retention component (scene/cut density)
//   suspense          -> rewatch component (end-payoff / late-surprise buildup)
//   editingMomentum   -> pacing component (cut rhythm)
//   faceReaction      -> emotion component, ONLY when a facecam is present
//   gameplayIntensity -> gaming score, ONLY when gaming scoring ran
// Unavailable components are dropped and weights renormalized — never faked.
const WEIGHTS = {
  viralScore: 0.25, excitement: 0.20, sceneEnergy: 0.15, suspense: 0.10,
  faceReaction: 0.10, gameplayIntensity: 0.10, editingMomentum: 0.10,
};
function weightedEditScore(viral, gaming, opts = {}) {
  const cs = (viral && viral.componentScores) || {};
  const get = (name) => (cs[name] && typeof cs[name].score === "number" ? cs[name].score : null);
  const available = {
    viralScore: typeof viral.viralScore === "number" ? viral.viralScore : null,
    excitement: get("surprise"),
    sceneEnergy: get("retention"),
    suspense: get("rewatch"),
    editingMomentum: get("pacing"),
    // Only real when the supporting detector/signal actually ran:
    faceReaction: opts.facecamPresent ? get("emotion") : null,
    gameplayIntensity: (opts.gaming && gaming && typeof gaming.gamingViralScore === "number") ? gaming.gamingViralScore : null,
  };
  let sum = 0, wsum = 0;
  const used = {}, excluded = [];
  for (const [k, w] of Object.entries(WEIGHTS)) {
    if (available[k] === null) { excluded.push(k); continue; }
    sum += w * available[k]; wsum += w; used[k] = Number(available[k].toFixed(3));
  }
  return {
    score: wsum > 0 ? Number((sum / wsum).toFixed(3)) : 0, // renormalized over available
    components: used,
    excluded, // components needing absent detectors (facecam/gaming) — honestly omitted
    note: "Handoff weighted formula over REAL measured components; unavailable ones excluded + weights renormalized, not faked.",
  };
}

module.exports = { scoreVideoV10, weightedEditScore };
