// Creator Intelligence — dataset store
// Reads/appends rows under data/creator-intelligence/ and reports HONEST counts.
// A fresh install has zero rows; every count returned here reflects rows that
// physically exist on disk. Nothing is seeded or faked.
//
// See docs/creator-v10/research-dataset-schema.md

"use strict";

const fs = require("fs");
const path = require("path");
const {
  validateGeneralShort, validateGamingShort, validateEditEvent, validateOutcome,
} = require("./schema");

// repoRoot = three levels up: src/creator-intelligence/dataset -> repo root
const REPO_ROOT = path.resolve(__dirname, "..", "..", "..");
const DATA_DIR = path.join(REPO_ROOT, "data", "creator-intelligence");
const MANIFEST_PATH = path.join(DATA_DIR, "MANIFEST.json");

const BUCKETS = {
  general: { dir: path.join(DATA_DIR, "general"), file: "general.jsonl", validate: validateGeneralShort },
  gaming: { dir: path.join(DATA_DIR, "gaming"), file: "gaming.jsonl", validate: validateGamingShort },
  edits: { dir: path.join(DATA_DIR, "edits"), file: "edits.jsonl", validate: validateEditEvent },
  outcomes: { dir: path.join(DATA_DIR, "outcomes"), file: "outcomes.jsonl", validate: validateOutcome },
};

function ensureDir(dir) {
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
}

/**
 * Count non-empty lines across all *.jsonl files in a bucket directory.
 * Returns 0 honestly when nothing exists.
 */
function countBucket(bucketName) {
  const bucket = BUCKETS[bucketName];
  if (!bucket || !fs.existsSync(bucket.dir)) return 0;
  let count = 0;
  for (const name of fs.readdirSync(bucket.dir)) {
    if (!name.endsWith(".jsonl")) continue;
    const raw = fs.readFileSync(path.join(bucket.dir, name), "utf8");
    for (const line of raw.split("\n")) {
      if (line.trim().length > 0) count++;
    }
  }
  return count;
}

/**
 * Real counts for every bucket. This is the source of truth for "how much
 * data exists" and what the sufficiency guards consume.
 * @returns {{ general:number, gaming:number, edits:number }}
 */
function counts() {
  return {
    general: countBucket("general"),
    gaming: countBucket("gaming"),
    edits: countBucket("edits"),
    outcomes: countBucket("outcomes"),
  };
}

/**
 * Per-game counts within the gaming bucket (for MIN_ROWS_PER_GAME checks).
 * @returns {Object<string, number>}
 */
function gamingCountsByGame() {
  const bucket = BUCKETS.gaming;
  const byGame = {};
  if (!fs.existsSync(bucket.dir)) return byGame;
  for (const name of fs.readdirSync(bucket.dir)) {
    if (!name.endsWith(".jsonl")) continue;
    const raw = fs.readFileSync(path.join(bucket.dir, name), "utf8");
    for (const line of raw.split("\n")) {
      if (!line.trim()) continue;
      try {
        const game = JSON.parse(line).game || "other";
        byGame[game] = (byGame[game] || 0) + 1;
      } catch { /* skip malformed line — do not count it */ }
    }
  }
  return byGame;
}

function appendRow(bucketName, row) {
  const bucket = BUCKETS[bucketName];
  if (!bucket) throw new Error(`unknown bucket: ${bucketName}`);
  const { valid, errors } = bucket.validate(row);
  if (!valid) {
    throw new Error(`invalid ${bucketName} row: ${errors.join("; ")}`);
  }
  ensureDir(bucket.dir);
  fs.appendFileSync(path.join(bucket.dir, bucket.file), JSON.stringify(row) + "\n", "utf8");
  refreshManifest();
  return true;
}

const appendGeneral = (row) => appendRow("general", row);
const appendGaming = (row) => appendRow("gaming", row);
const appendEdit = (row) => appendRow("edits", row);
const appendOutcome = (row) => appendRow("outcomes", row);

/**
 * Join captured edit-export features to their real outcome labels by entryId
 * (and renderId when present). Returns only rows that have BOTH a feature
 * vector and a real outcome — i.e. the legitimately labeled first-party
 * training set. Never fabricates a label for an unlabeled edit.
 * @returns {Array<{entryId, renderId, features, metrics, source, label}>}
 */
function joinLabeledFirstParty(labelKey = "engagement_rate") {
  const exports = readAll("edits").filter((e) => e.kind === "export" && e.features);
  const outcomes = readAll("outcomes");
  const byEntry = new Map();
  for (const o of outcomes) {
    // Latest outcome per entry wins (most recent real measurement).
    const key = o.entryId || o.renderId;
    if (!key) continue;
    const prev = byEntry.get(key);
    if (!prev || (o.recordedAt || "") > (prev.recordedAt || "")) byEntry.set(key, o);
  }
  const joined = [];
  for (const e of exports) {
    const key = e.entryId || (e.features && e.features.renderId);
    const o = key ? byEntry.get(key) : null;
    if (!o) continue; // unlabeled edit — excluded, never given a placeholder label
    const label = computeLabel(o.metrics, labelKey);
    if (label === null) continue;
    joined.push({ entryId: e.entryId, renderId: o.renderId || null, features: e.features, metrics: o.metrics, source: o.source, label });
  }
  return joined;
}

// Derive a real training label from real metrics. engagement_rate =
// (likes+comments)/views; never invented if views are missing/zero.
function computeLabel(metrics, labelKey) {
  if (!metrics) return null;
  if (labelKey === "engagement_rate") {
    const v = metrics.views, l = metrics.likes || 0, c = metrics.comments || 0;
    return typeof v === "number" && v > 0 ? (l + c) / v : null;
  }
  const direct = metrics[labelKey];
  return typeof direct === "number" && Number.isFinite(direct) ? direct : null;
}

/**
 * Read all rows from a bucket (used by analysis/scoring). For large datasets
 * this should be streamed; kept simple here and acceptable at current scale.
 */
function readAll(bucketName) {
  const bucket = BUCKETS[bucketName];
  if (!bucket || !fs.existsSync(bucket.dir)) return [];
  const rows = [];
  for (const name of fs.readdirSync(bucket.dir)) {
    if (!name.endsWith(".jsonl")) continue;
    const raw = fs.readFileSync(path.join(bucket.dir, name), "utf8");
    for (const line of raw.split("\n")) {
      if (!line.trim()) continue;
      try { rows.push(JSON.parse(line)); } catch { /* skip malformed */ }
    }
  }
  return rows;
}

/**
 * Rewrite MANIFEST.json with real counts + a timestamp. The manifest is the
 * auditable record of provenance; counts here always match disk.
 */
function refreshManifest() {
  ensureDir(DATA_DIR);
  let existing = { sources: [] };
  if (fs.existsSync(MANIFEST_PATH)) {
    try { existing = JSON.parse(fs.readFileSync(MANIFEST_PATH, "utf8")); } catch { /* reset */ }
  }
  const manifest = {
    ...existing,
    counts: counts(),
    gamingByGame: gamingCountsByGame(),
    updatedAt: new Date().toISOString(),
    note: "Counts reflect rows physically present on disk. Empty = insufficient data.",
  };
  fs.writeFileSync(MANIFEST_PATH, JSON.stringify(manifest, null, 2), "utf8");
  return manifest;
}

module.exports = {
  DATA_DIR, MANIFEST_PATH,
  counts, gamingCountsByGame, readAll,
  appendGeneral, appendGaming, appendEdit, appendOutcome,
  joinLabeledFirstParty,
  refreshManifest,
};
