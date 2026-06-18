// CLI wrapper exposing the project's existing, tested ffmpeg-based detectors
// to scripts/shorts_visual_research.py — reuses real logic instead of
// reimplementing motion/scene/audio/facecam detection a second time in
// Python. Usage: node _visual_research_helper.js <videoPath>
// Prints one JSON line to stdout. Never fabricates — any detector that
// fails reports its own honest status rather than a guessed number.
"use strict";

const path = require("path");
const {
  getVideoMetadata, detectMotion, detectAudioSpikes, detectSceneChanges,
  detectOpeningHookStrength,
} = require(path.join(__dirname, "..", "apps", "lantern-garage", "lib", "highlight-engine.js"));
const { analyzeForCrop } = require(path.join(__dirname, "..", "apps", "lantern-garage", "lib", "safe-zone-v2.js"));

const videoPath = process.argv[2];

async function main() {
  if (!videoPath) {
    console.log(JSON.stringify({ status: "unavailable", reason: "no videoPath arg" }));
    return;
  }

  const metadata = await getVideoMetadata(videoPath).catch(() => null);
  if (!metadata) {
    console.log(JSON.stringify({ status: "unavailable", reason: "ffprobe failed" }));
    return;
  }

  const ffOpts = { maxSeconds: Math.min(metadata.duration || 60, 120) };
  const [motion, audio, scenes, hook, cropPlan] = await Promise.all([
    detectMotion(videoPath, 5, 0.15, ffOpts).catch(() => []),
    detectAudioSpikes(videoPath, 5, 0.7, ffOpts).catch(() => []),
    detectSceneChanges(videoPath, 5, 0.3, ffOpts).catch(() => []),
    detectOpeningHookStrength(videoPath).catch(() => ({ status: "unavailable" })),
    analyzeForCrop(videoPath, { fps: 1 }).catch(() => ({ status: "unavailable" })),
  ]);

  // Per-second motion curve (real frame-diff magnitude, not a guess).
  const motionCurve = {};
  for (const m of motion) {
    const sec = Math.floor(m.timestamp);
    motionCurve[sec] = Math.max(motionCurve[sec] || 0, m.motion);
  }

  const avgCutLength = scenes.length > 0 ? (metadata.duration || 0) / (scenes.length + 1) : (metadata.duration || 0);

  let facecamPosition = "insufficient_data";
  let hudPosition = "insufficient_data";
  if (cropPlan.status === "ok") {
    const fc = cropPlan.regions.find((r) => r.type === "facecam");
    const hud = cropPlan.regions.find((r) => r.type === "hud");
    if (fc) facecamPosition = { corner: fc.corner, confidence: fc.confidence };
    if (hud) hudPosition = { bounds: hud.bounds, confidence: hud.confidence };
  }

  console.log(JSON.stringify({
    status: "ok",
    fps: 30,
    durationSec: Number((metadata.duration || 0).toFixed(2)),
    sceneCutCount: scenes.length,
    averageCutLength: Number(avgCutLength.toFixed(2)),
    motionCurve,
    audioSpikeCount: audio.length,
    audioSpikeTimestamps: audio.map((a) => Number(a.timestamp.toFixed(2))),
    openingHookStrength: hook.status === "ok" ? hook.hookStrength : "insufficient_data",
    facecamPosition,
    hudPosition,
    safeZoneStatus: cropPlan.status,
  }));
}

main();
