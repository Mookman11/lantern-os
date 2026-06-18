// Editing Memory V12 (data/editing-memory/ per the handoff).
//
// Records the REAL editing stats of every render so the system has a memory of
// what it actually produced. This is owned first-party data (Lantern's own
// output), so it is always legitimate to keep. It complements the flywheel's
// learning-store (which captures features for outcome-joining) by keeping a
// human-readable per-render log.
//
// HONESTY: only real stats are recorded. cutsPerMinute, segment count,
// zoomCount, gameplayCrop, facecamPlacement, and viralScore are known exactly
// at render time. subtitlesPerMinute is real when captions are supplied;
// transitions/hookType are marked insufficient_data because the renderer does
// not apply named transitions or classify hook types (no such stage exists).

"use strict";

const fs = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "..", "..", "..");
const MEM_DIR = path.join(ROOT, "data", "editing-memory");
const INDEX_FILE = path.join(MEM_DIR, "index.jsonl");
const INSUFFICIENT = "insufficient_data";

function r3(x) { return typeof x === "number" && Number.isFinite(x) ? Number(x.toFixed(3)) : null; }

/**
 * Build + persist an editing-memory record for one render.
 * @param {Object} o {
 *   entryId, renderId, durationSec, segments[] (with score/role/zoom),
 *   captionCount, viralScore, cropMode, facecamPlacement, zoomedSegments
 * }
 * @returns the record written.
 */
function recordEditingMemory(o = {}) {
  const segs = Array.isArray(o.segments) ? o.segments : [];
  const dur = Number(o.durationSec) || segs.reduce((a, s) => a + Math.max(0, (s.end || 0) - (s.start || 0)), 0);
  const cuts = segs.length; // each segment boundary is a cut in the final edit
  const minutes = dur > 0 ? dur / 60 : null;

  const rec = {
    entryId: o.entryId || null,
    renderId: o.renderId || null,
    recordedAt: new Date().toISOString(),
    durationSec: r3(dur),
    segmentCount: segs.length,
    cutsPerMinute: minutes ? r3(cuts / minutes) : null,
    subtitlesPerMinute: (typeof o.captionCount === "number" && minutes) ? r3(o.captionCount / minutes) : INSUFFICIENT,
    zoomCount: typeof o.zoomedSegments === "number" ? o.zoomedSegments : segs.filter((s) => s.zoom || s.role === "peak").length,
    transitions: INSUFFICIENT + " (renderer concatenates; no named transitions applied)",
    hookType: INSUFFICIENT + " (no hook-type classifier)",
    gameplayCrop: o.cropMode || "crop (full-frame 9:16)",
    facecamPlacement: o.facecamPlacement || INSUFFICIENT,
    viralScore: r3(o.viralScore),
    roles: segs.map((s) => s.role || (s.zoom ? "zoom" : "segment")),
  };

  fs.mkdirSync(MEM_DIR, { recursive: true });
  if (rec.renderId) {
    fs.writeFileSync(path.join(MEM_DIR, `${rec.renderId}.json`), JSON.stringify(rec, null, 2));
  }
  fs.appendFileSync(INDEX_FILE, JSON.stringify(rec) + "\n");
  return rec;
}

/** Read the full editing-memory index (for analysis / nightly priors). */
function readEditingMemory() {
  if (!fs.existsSync(INDEX_FILE)) return [];
  return fs.readFileSync(INDEX_FILE, "utf8").split("\n").map((l) => l.trim()).filter(Boolean)
    .map((l) => { try { return JSON.parse(l); } catch { return null; } }).filter(Boolean);
}

module.exports = { recordEditingMemory, readEditingMemory, MEM_DIR };
