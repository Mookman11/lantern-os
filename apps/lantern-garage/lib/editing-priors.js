// Editing Priors V12 (lib/editing_priors.js per the handoff).
//
// Learns editing PRIORS from real on-disk reference data (CC-licensed clips +
// first-party render observations) and exposes them for the editor to consult.
// Updated by the nightly orchestrator.
//
// HONESTY BOUNDARY: a prior is only emitted when it is actually measurable from
// the data. Cut frequency, scene-cut counts, durations, and opening-hook
// strength ARE measured (real ffmpeg observations). Zoom frequency, facecam
// position aggregates, and per-element layout are NOT measurable without
// detectors that don't exist, so they are returned as the literal string
// "insufficient_data" — never guessed. This module reads data; it never
// downloads or fabricates anything.

"use strict";

const fs = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "..", "..", "..");
const CC_FILE = path.join(ROOT, "data", "shorts", "cc", "features_cc.jsonl");
const RESEARCH_DIR = path.join(ROOT, "data", "shorts_research");
const YT_DIR = path.join(ROOT, "data", "youtube");
const OUT_FILE = path.join(ROOT, "data", "models", "editing-priors.json");

const INSUFFICIENT = "insufficient_data";

function readJsonl(file) {
  if (!fs.existsSync(file)) return [];
  return fs.readFileSync(file, "utf8").split("\n").map((l) => l.trim()).filter(Boolean)
    .map((l) => { try { return JSON.parse(l); } catch { return null; } }).filter(Boolean);
}
function readJsonDir(dir) {
  if (!fs.existsSync(dir)) return [];
  return fs.readdirSync(dir).filter((f) => f.endsWith(".json"))
    .map((f) => { try { return JSON.parse(fs.readFileSync(path.join(dir, f), "utf8")); } catch { return null; } })
    .filter(Boolean);
}
function num(a) { return a.filter((x) => typeof x === "number" && Number.isFinite(x)); }
function median(a) { const s = num(a).sort((x, y) => x - y); if (!s.length) return null; const m = s.length >> 1; return s.length % 2 ? s[m] : (s[m - 1] + s[m]) / 2; }
function mean(a) { const s = num(a); return s.length ? s.reduce((x, y) => x + y, 0) / s.length : null; }
function r3(x) { return x == null ? null : Number(Number(x).toFixed(3)); }

/**
 * Compute editing priors from whatever real reference data exists on disk.
 * @returns the priors object (also describes provenance + which are measured).
 */
function computeEditingPriors() {
  const cc = readJsonl(CC_FILE).map((r) => r.features).filter((f) => f && f.status === "ok");
  const firstParty = readJsonDir(RESEARCH_DIR).filter((r) => r.status === "ok");
  const calibration = readJsonl(path.join(YT_DIR, "calibration_features.jsonl"));
  const metaDurations = readJsonl(path.join(YT_DIR, "features_v11.jsonl")).map((f) => f.duration);

  // Real cut-rate: cuts/minute from CC + calibration (scene cuts over duration).
  const cutsPerMin = [];
  for (const c of cc) {
    if (typeof c.sceneCutCount === "number" && c.durationSec > 0) cutsPerMin.push(c.sceneCutCount / (c.durationSec / 60));
  }
  for (const c of calibration) {
    if (typeof c.scene_cut_count === "number" && c.duration_actual > 0) cutsPerMin.push(c.scene_cut_count / (c.duration_actual / 60));
  }

  // Real opening-hook strength (intro intensity proxy) from any observer record.
  const hooks = [
    ...cc.map((c) => c.openingHookStrength),
    ...firstParty.map((f) => f.hook_duration),
  ];

  return {
    generatedAt: new Date().toISOString(),
    sampleSizes: { ccClips: cc.length, firstPartyRenders: firstParty.length, calibration: calibration.length },

    // ── Measured priors (real) ──────────────────────────────────────────
    averageCutsPerMinute: cutsPerMin.length ? { median: r3(median(cutsPerMin)), mean: r3(mean(cutsPerMin)), n: cutsPerMin.length } : INSUFFICIENT,
    targetDurationSec: metaDurations.length ? { median: r3(median(metaDurations)), mean: r3(mean(metaDurations)) } : INSUFFICIENT,
    introHookStrength: num(hooks).length ? { median: r3(median(hooks)), mean: r3(mean(hooks)), n: num(hooks).length,
      caveat: "detectOpeningHookStrength saturates (~0.98); describes detector behavior, not validated hook quality (hour_12.md)" } : INSUFFICIENT,

    // ── Not measurable without detectors that don't exist (honest) ──────
    zoomFrequency: INSUFFICIENT + " (no zoom detector for reference clips; render applies punch-in, but we don't measure others' zooms)",
    facecamPosition: INSUFFICIENT + " (per-clip facecam heuristic exists, but no reliable aggregate over references)",
    captionDensity: INSUFFICIENT + " (only known for first-party renders, not reference clips — no OCR on references)",
    suspenseTiming: INSUFFICIENT + " (needs per-segment arc timing across many labeled refs)",
    peakSpacing: INSUFFICIENT + " (needs multi-peak timing labels not present in references)",
    endingStyle: INSUFFICIENT + " (needs ending-classification not built)",
    gameplayCrop: "full-frame 9:16 (renderer fills frame; safe-zone-v2 avoids slicing detected regions)",

    honestyNote:
      "Priors are emitted only where real measurement exists (cut rate, duration, intro hook). Everything " +
      "requiring an absent detector is insufficient_data, never guessed. Reference data is CC-licensed + " +
      "first-party only.",
  };
}

/** Compute and persist priors (called by the nightly orchestrator). */
function updateEditingPriors() {
  const priors = computeEditingPriors();
  fs.mkdirSync(path.dirname(OUT_FILE), { recursive: true });
  fs.writeFileSync(OUT_FILE, JSON.stringify(priors, null, 2));
  return priors;
}

module.exports = { computeEditingPriors, updateEditingPriors, OUT_FILE };
