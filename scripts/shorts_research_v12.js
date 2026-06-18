#!/usr/bin/env node
// Shorts Research V12 — `npm run shorts-research-v12`
//
// Recomputes the editing-rule and Σ₀ deliverables from data ALREADY ON DISK:
//   - data/youtube/features_v11.jsonl       (1,451 real collected metadata rows)
//   - data/youtube/calibration_features.jsonl (real ffmpeg-measured sample)
//   - data/shorts_research/*.json            (first-party + sample visual features)
//
// SCOPE (honest, deliberate): this harness does NOT bulk-download thousands of
// third-party videos. That acquisition was declined across this project's
// research cycle (see research/hour_01.md, hour_13.md, hour_14.md) on ToS/
// copyright grounds, and deletion-after-extraction does not change the
// acquisition risk. The "fetch fresh metadata" step is a no-op when the daily
// YouTube API quota is exhausted; this command is built to be re-runnable any
// day and to recompute from whatever real data exists, marking anything it
// cannot measure as insufficient_data rather than inventing it.
//
// Writes deliverables:
//   data/models/creator-profiles.json   (from editor-v12.js)
//   data/models/hook-weights.json
//   data/models/editing-rules.json
//   data/models/sigma0-training.json
"use strict";

const fs = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "..");
const YT_DIR = path.join(ROOT, "data", "youtube");
const RESEARCH_DIR = path.join(ROOT, "data", "shorts_research");
const MODELS_DIR = path.join(ROOT, "data", "models");

const { CREATOR_PROFILES, DEFAULT_PROFILE } = require("../apps/lantern-garage/lib/editor-v12");

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

function median(nums) {
  const a = nums.filter((x) => typeof x === "number" && Number.isFinite(x)).sort((x, y) => x - y);
  if (!a.length) return null;
  const mid = Math.floor(a.length / 2);
  return a.length % 2 ? a[mid] : (a[mid - 1] + a[mid]) / 2;
}
function mean(nums) {
  const a = nums.filter((x) => typeof x === "number" && Number.isFinite(x));
  return a.length ? a.reduce((s, x) => s + x, 0) / a.length : null;
}
const INSUFFICIENT = "insufficient_data";

function main() {
  fs.mkdirSync(MODELS_DIR, { recursive: true });
  const now = new Date().toISOString();

  const features = readJsonl(path.join(YT_DIR, "features_v11.jsonl"));
  const calibration = readJsonl(path.join(YT_DIR, "calibration_features.jsonl"));
  const visual = readJsonDir(RESEARCH_DIR).filter((r) => r.status === "ok");

  // ── hook-weights.json ──────────────────────────────────────────────────
  // Real opening-hook-strength stats from any visual records that have them.
  const hookVals = visual.map((v) => v.hook_duration).filter((x) => typeof x === "number");
  const hookWeights = {
    generatedAt: now,
    source: "data/shorts_research/*.json (opening_hook_strength via highlight-engine detectOpeningHookStrength)",
    sampleSize: hookVals.length,
    openingHookStrength: hookVals.length
      ? { mean: round(mean(hookVals)), median: round(median(hookVals)), min: round(Math.min(...hookVals)), max: round(Math.max(...hookVals)) }
      : INSUFFICIENT,
    honestyNote:
      "detectOpeningHookStrength is known to saturate (~0.98) on most clips and is NOT yet recalibrated " +
      "(see research/hour_12.md). These weights describe the current detector's behavior, not a validated " +
      "hook-quality ground truth. Title-text hook density was shown to correlate weakly with engagement.",
  };
  write("hook-weights.json", hookWeights);

  // ── editing-rules.json ─────────────────────────────────────────────────
  // Real duration/cut stats from the calibration sample + the collected set.
  const durations = features.map((f) => f.duration).filter((x) => typeof x === "number");
  const cutLens = calibration.map((c) => c.average_scene_length).filter((x) => typeof x === "number");
  const sceneCuts = calibration.map((c) => c.scene_cut_count).filter((x) => typeof x === "number");
  const editingRules = {
    generatedAt: now,
    sources: {
      durations: "data/youtube/features_v11.jsonl (n=" + durations.length + ")",
      cutting: "data/youtube/calibration_features.jsonl (n=" + calibration.length + ")",
    },
    targetDurationSec: durations.length ? { median: round(median(durations)), mean: round(mean(durations)) } : INSUFFICIENT,
    averageCutLengthSec: cutLens.length ? { median: round(median(cutLens)), mean: round(mean(cutLens)) } : INSUFFICIENT,
    sceneCutsPerClip: sceneCuts.length ? { median: round(median(sceneCuts)), mean: round(mean(sceneCuts)) } : INSUFFICIENT,
    negativeContentPenalty: 0.15,
    negativeDetectors: ["detectConversation", "detectIdleGameplay", "detectMenuOrLoadingScreen", "detectStaticFrames"],
    honestyNote:
      "Duration/cut stats are real measurements over collected metadata + the small calibration sample. " +
      "They describe what top-viewed Shorts in the sample look like; they are guidance priors, not a trained policy.",
  };
  write("editing-rules.json", editingRules);

  // ── creator-profiles.json (re-export from editor-v12) ──────────────────
  write("creator-profiles.json", {
    profiles: CREATOR_PROFILES, default: DEFAULT_PROFILE, generatedAt: now,
    note: "Named editing-parameter presets, not real-creator fingerprints. Source: apps/lantern-garage/lib/editor-v12.js",
  });

  // ── sigma0-training.json ───────────────────────────────────────────────
  // The Σ₀ signal manifest the editor scores on, with which are real vs pending.
  const sigma0Training = {
    generatedAt: now,
    signals: {
      motion: "real (highlight-engine detectMotion, frame-diff)",
      sceneChanges: "real (highlight-engine detectSceneChanges, histogram diff)",
      audioIntensity: "real (highlight-engine detectAudioSpikes)",
      hookStrength: "real-but-uncalibrated (detectOpeningHookStrength; saturates — see hour_12.md)",
      surprise: "real (viral-score-v10 surprise component: multi-signal spike rate)",
      emotion: "proxy (audio energy; no trained emotion model)",
      retention: "structural proxy (viral-score-v10 retention component)",
      storyArc: "real (story-engine-v12 role assignment from measured properties)",
      collapseRisk: "real (sigma0-v12 selection-diversity metric)",
      killDensity: INSUFFICIENT + " (no kill-feed OCR / event detector built)",
    },
    antiCollapse: {
      method: "sigma0-v12 antiCollapseSelect — multi-peak diversity-maximizing selection",
      rankingRule: "variant-engine-v10 breaks score ties by LOWER collapse risk (prefer diverse multi-peak edits)",
    },
    honestyNote:
      "This manifest lists which Σ₀ editing signals are real measurements vs proxies vs not-yet-built. " +
      "No nightly weight retraining is claimed: there is no labeled outcome data (real retention %/share counts " +
      "are not available via the public API — see hour_12.md). 'Training' here means recomputing structural " +
      "priors from real on-disk data, not gradient updates on outcome labels.",
  };
  write("sigma0-training.json", sigma0Training);

  console.log("\nshorts-research-v12 complete. Deliverables written to data/models/:");
  console.log("  creator-profiles.json, hook-weights.json, editing-rules.json, sigma0-training.json");
  console.log(`  inputs: features=${features.length}, calibration=${calibration.length}, visual=${visual.length}`);
}

function round(x) { return x == null ? null : Number(Number(x).toFixed(4)); }
function write(name, obj) {
  fs.writeFileSync(path.join(MODELS_DIR, name), JSON.stringify(obj, null, 2));
  console.log("  wrote data/models/" + name);
}

main();
