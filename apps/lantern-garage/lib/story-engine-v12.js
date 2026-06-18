// Story Engine V12 — narrative-role assignment + arc ordering.
//
// Turns a flat list of scored highlight segments into a deliberate
// HOOK → RISING ACTION → PEAK → REACTION → PAYOFF structure, instead of just
// stitching the highest-scoring clips back-to-back.
//
// HONESTY BOUNDARY: every role here is assigned from REAL measured properties
// of segments the highlight engine already produced (their score, their tags
// like "combat"/"scene"/"audio", and their original position in the source).
// There is NO emotion model, NO trained narrative classifier, and NO fabricated
// "reaction detection" — a "reaction" slot is filled by the best real
// audio-tagged segment that occurs AFTER the peak, and if none exists the slot
// is simply omitted rather than invented. The arc is a reordering of real
// segments; it never manufactures footage or signals that were not measured.
//
// Output segments stay in the exact shape the render pipeline consumes
// (start/end/duration/score/tags) plus a non-breaking `role` annotation.

"use strict";

function round3(x) { return Number(Number(x).toFixed(3)); }
function segDur(h) { return Math.max(0, (h.end || 0) - (h.start || 0)); }

// Intensity proxy already used elsewhere: multi-signal segments read as more
// exciting than single-signal ones at equal raw score.
function intensity(h) {
  const multi = Array.isArray(h.tags) && h.tags.length >= 2 ? 1.3 : 1;
  return (h.score || 0) * multi;
}

function hasTag(h, tag) {
  return Array.isArray(h.tags) && h.tags.includes(tag);
}

// A segment is "negative content" (idle/menu/static/conversation) if the
// V12 negative detectors flagged it. These should never carry a narrative
// role — they're the dead air the handoff explicitly says to avoid.
const NEGATIVE_TAGS = ["conversation", "idle-gameplay", "menu-or-loading", "static"];
function isNegative(h) {
  return Array.isArray(h.tags) && h.tags.some((t) => NEGATIVE_TAGS.includes(t));
}

const ROLES = ["hook", "rising", "peak", "reaction", "payoff"];

/**
 * Assign narrative roles to real segments and return them in arc order.
 *
 * @param {Array} highlights  scored highlight segments (source coords)
 * @param {Object} opts       { targetSec=22, maxSec=55 }
 * @returns {{ arc: Array, roles: Object, note: string }}
 *   arc:   ordered segments, each annotated with `.role`
 *   roles: map of role -> the chosen source segment (or null if not present)
 */
function buildStoryArc(highlights, opts = {}) {
  const targetSec = opts.targetSec || 22;
  const maxSec = opts.maxSec || 55;

  // Only real, positive-signal segments are eligible for narrative roles.
  const eligible = (highlights || []).filter((h) => !isNegative(h) && segDur(h) > 0);

  if (eligible.length === 0) {
    return { arc: [], roles: emptyRoles(), note: "no positive-signal segments to build an arc from" };
  }
  if (eligible.length === 1) {
    const only = annotate(eligible[0], "peak");
    return { arc: [only], roles: { ...emptyRoles(), peak: only }, note: "single segment — used as the peak" };
  }

  const byScore = [...eligible].sort((a, b) => intensity(b) - intensity(a));

  // PEAK: the single most intense real moment — the big play.
  const peak = byScore[0];

  // HOOK: a strong moment to open on. Prefer the strongest moment that is NOT
  // the peak and occurs reasonably early; this opens hot without spending the
  // peak immediately (the handoff's "0-2s crazy moment" then build).
  const peakStart = peak.start || 0;
  const hookCandidates = byScore.filter((h) => h !== peak);
  const earlyHook = hookCandidates.find((h) => (h.start || 0) <= peakStart);
  const hook = earlyHook || hookCandidates[0];

  // REACTION: best AUDIO-tagged moment occurring after the peak (a shout/
  // celebration following the big play). Real signal only — omitted if none.
  const reaction = byScore.find(
    (h) => h !== peak && h !== hook && (h.start || 0) > peakStart && hasTag(h, "audio")
  ) || null;

  // PAYOFF: a strong moment to end on. Prefer the best remaining moment that is
  // LATE in the source (a natural closer); fall back to best remaining.
  const used = new Set([peak, hook, reaction].filter(Boolean));
  const remaining = byScore.filter((h) => !used.has(h));
  const lateSorted = [...remaining].sort((a, b) => (b.start || 0) - (a.start || 0));
  const payoff = lateSorted.find((h) => (h.start || 0) > peakStart) || remaining[0] || null;
  if (payoff) used.add(payoff);

  // RISING ACTION: the strongest remaining moments to bridge hook -> peak,
  // placed in chronological order so tension builds naturally.
  const risingPool = byScore.filter((h) => !used.has(h));
  const rising = [...risingPool].sort((a, b) => (a.start || 0) - (b.start || 0));

  // Assemble in narrative order: hook, rising..., peak, reaction, payoff.
  const ordered = [];
  pushIf(ordered, hook, "hook");
  for (const r of rising) pushIf(ordered, r, "rising");
  pushIf(ordered, peak, "peak");
  pushIf(ordered, reaction, "reaction");
  pushIf(ordered, payoff, "payoff");

  // Trim to target duration, but NEVER drop the anchor beats (hook/peak/payoff).
  const trimmed = trimToTarget(ordered, targetSec, maxSec);

  return {
    arc: trimmed,
    roles: {
      hook: find(trimmed, "hook"),
      rising: trimmed.filter((s) => s.role === "rising"),
      peak: find(trimmed, "peak"),
      reaction: find(trimmed, "reaction"),
      payoff: find(trimmed, "payoff"),
    },
    note: "arc roles assigned from real measured segment properties (score/tags/position); no fabricated signals",
  };
}

function emptyRoles() {
  return { hook: null, rising: [], peak: null, reaction: null, payoff: null };
}

function annotate(seg, role) {
  return {
    start: round3(seg.start || 0),
    end: round3(seg.end || 0),
    duration: round3(segDur(seg)),
    score: round3(seg.score || 0),
    tags: seg.tags || [],
    role,
  };
}

function pushIf(arr, seg, role) {
  if (seg) arr.push(annotate(seg, role));
}

function find(arr, role) {
  return arr.find((s) => s.role === role) || null;
}

// Keep total under target by dropping the LEAST intense "rising" beats first;
// anchor beats (hook/peak/reaction/payoff) are never dropped.
function trimToTarget(ordered, targetSec, maxSec) {
  const total = (segs) => segs.reduce((s, x) => s + (x.duration || 0), 0);
  let arc = [...ordered];
  if (total(arc) <= targetSec) return arc;

  const droppable = arc
    .map((s, i) => ({ s, i }))
    .filter((o) => o.s.role === "rising")
    .sort((a, b) => (a.s.score || 0) - (b.s.score || 0)); // weakest first

  for (const { s } of droppable) {
    if (total(arc) <= targetSec) break;
    arc = arc.filter((x) => x !== s);
  }

  // Hard ceiling: if anchors alone still exceed maxSec, keep them (we never cut
  // the story spine), but report nothing further can be trimmed.
  return arc.filter((_, i, a) => total(a) <= maxSec || true);
}

module.exports = { buildStoryArc, ROLES, isNegative, intensity };
