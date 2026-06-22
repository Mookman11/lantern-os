// grounding-policy.js — the within→without bridge for the chat.
//
// JS mirror of src/convergence_io/dilation.py (G12-correct) + a chat-level dilation
// estimator. Time-dilation D is a single budget: productively-uncertain messages
// dilate (think more → ground harder); a frozen/degenerate signal collapses D toward
// D_MIN (act / go look now). groundingPolicy(D) turns D into how much EXTERNAL
// grounding to buy (web breadth, corroboration floor, deep mode).
//
// #1012 — mandatory periodic grounding tick: the "calm while wrong" / boiling-frog
// regime (arXiv:2603.08455, cert §4) shows internal proximity monitors stay silent
// during gradual drift. Solution: perform a mandatory external grounding pass on a
// wall-clock cadence regardless of how low collapse-proximity reads. Default 5 min;
// set GROUNDING_TICK_INTERVAL_MS to override. The tick is recorded per-process so
// every warm request contributes; a cold restart resets (acceptable: first reply
// after restart always grounds). Use shouldForceGrounding() before expensive checks
// and recordGroundingTick() after a real grounding pass completes.

const D_MIN = 0.1;
const D_MAX = 5.0;
const D_DEFAULT = 1.0;

const GROUNDING_TICK_MS = parseInt(process.env.GROUNDING_TICK_INTERVAL_MS, 10) || 5 * 60 * 1000;
let _lastGroundingTs = 0;

function shouldForceGrounding() {
  return Date.now() - _lastGroundingTs >= GROUNDING_TICK_MS;
}

function recordGroundingTick() {
  _lastGroundingTs = Date.now();
}

const clamp = (x, lo, hi) => Math.max(lo, Math.min(hi, x));

// Mirror of dilation() including the G12 collapse-proximity sign-fix:
// near collapse (proximity→1) D deflates toward D_MIN instead of inflating.
function dilation(uncertainty, costPressure = 0, confidence = 0.5, collapseProximity = 0) {
  uncertainty = clamp(uncertainty, 0, 1);
  costPressure = clamp(costPressure, 0, 1);
  confidence = clamp(confidence, 0, 1);
  const p = clamp(collapseProximity, 0, 1);
  const raw = (1 + uncertainty) / ((1 + confidence) * (1 + costPressure));
  let d = clamp(raw, D_MIN, D_MAX);
  d = (1 - p) * d + p * D_MIN;
  return clamp(d, D_MIN, D_MAX);
}

// Mirror of grounding_policy(): D → external-grounding budget.
// forcedByTimer: when true (shouldForceGrounding() fired), always fetchExternal at
// base budget even if D would otherwise suppress it — the mandatory tick override.
function groundingPolicy(D, { baseMaxResults = 5, baseMinSources = 2, forcedByTimer = false } = {}) {
  D = clamp(D, D_MIN, D_MAX);
  if (forcedByTimer && D <= 1.0) {
    return { fetchExternal: true, maxResults: baseMaxResults, minSources: baseMinSources, deepMode: false, forcedByTimer: true };
  }
  if (D <= 1.0) {
    return { fetchExternal: D > 0.5, maxResults: baseMaxResults, minSources: baseMinSources, deepMode: false };
  }
  return {
    fetchExternal: true,
    maxResults: Math.round(baseMaxResults * D),
    minSources: baseMinSources + (D >= 3.0 ? 1 : 0),
    deepMode: D >= 3.0,
  };
}

// Estimate chat-level dilation from the message (transparent heuristic — the chat's
// analog of the Σ₀ uncertainty signal). High when the query needs fresh reality, is
// analytical, expresses uncertainty, or is long/multi-part. `collapseProximity` lets a
// post-generation degeneration/repetition signal collapse D (go re-ground).
function chatDilation(message, { confidence = 0.5, collapseProximity = 0 } = {}) {
  const t = String(message || "");
  let u = 0.3;
  if (/\b(latest|current|today|recent|news|price|now|2024|2025|2026|this week|this month)\b/i.test(t)) u += 0.3;
  if (/\b(compare|versus|vs\.?|difference|why|how exactly|trade-?offs?|evaluate|analy[sz]e)\b/i.test(t)) u += 0.2;
  if (/\b(not sure|unsure|maybe|confus|unclear|don'?t know|is it true|verify)\b/i.test(t)) u += 0.2;
  const questions = (t.match(/\?/g) || []).length;
  if (questions >= 2) u += 0.1;
  if (t.length > 280) u += 0.1;
  return dilation(clamp(u, 0, 1), 0, confidence, collapseProximity);
}

module.exports = { dilation, groundingPolicy, chatDilation, shouldForceGrounding, recordGroundingTick, D_MIN, D_MAX, D_DEFAULT };
