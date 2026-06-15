// Viral Pattern Research Engine — structural fingerprint
// Turns the REAL measured component scores from viralScoreV10 into a compact
// 6-dimension structural fingerprint (each 0..100). This is a deterministic
// transform of values that were already measured from the user's own clip — it
// invents nothing. A clip with no detectable structure produces low values, not
// fabricated ones.
//
// Dimensions:
//   hookStrength    — how fast the clip pays off at the start
//   payoffStrength  — strength of the late/ending beat (drives rewatch)
//   captionDensity  — caption-able beat density (proxy until captions measured)
//   motionIntensity — pacing + energy
//   curiosityGap    — multi-signal "surprise" spikes
//   loopability     — end-payoff + hook combined (how cleanly it loops)
//
// See docs/creator-v10/viral-pattern-research-engine.md

"use strict";

const { viralScoreV10, clamp01 } = require("../scoring/viral-score-v10");

function pct(x) { return Math.round(clamp01(x) * 100); }

/**
 * Build a fingerprint from an already-computed viralScoreV10 result.
 * @param {object} viral  output of viralScoreV10()
 * @returns {{hookStrength,payoffStrength,captionDensity,motionIntensity,curiosityGap,loopability}|null}
 */
function fingerprintFromViral(viral) {
  if (!viral || !viral.componentScores) return null;
  const c = viral.componentScores;
  const s = (name) => (c[name] && Number.isFinite(c[name].score) ? c[name].score : 0);

  const hook = s("hook");
  const rewatch = s("rewatch");
  const captionPotential = s("captionPotential");
  const pacing = s("pacing");
  const emotion = s("emotion");
  const surprise = s("surprise");

  return {
    hookStrength: pct(hook),
    payoffStrength: pct(rewatch),
    captionDensity: pct(captionPotential),
    motionIntensity: pct(0.5 * pacing + 0.5 * emotion),
    curiosityGap: pct(surprise),
    loopability: pct(0.6 * rewatch + 0.4 * hook),
  };
}

/**
 * Convenience: compute the fingerprint directly from a HighlightTimeline-shaped
 * analysis ({ duration, highlights[] }). Runs the real viral scorer first.
 * @returns {{fingerprint, viral}}
 */
function fingerprintFromAnalysis(analysis) {
  const viral = viralScoreV10(analysis || {});
  return { fingerprint: fingerprintFromViral(viral), viral };
}

module.exports = { fingerprintFromViral, fingerprintFromAnalysis };
