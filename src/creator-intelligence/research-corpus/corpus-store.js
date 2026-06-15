// Viral Pattern Research Engine — corpus store
// Reads/appends rows under data/viral-research/ and reports HONEST counts split
// by provenance. A fresh install has zero rows; every count reflects rows that
// physically exist on disk. Nothing is seeded or faked.
//
// Buckets mirror the user's requested layout:
//   youtube/ tiktok/ reels/ gaming/   — public references (metadata-only unless
//                                        a row is from a rights-cleared import)
//   own/                              — Lantern's own generated/uploaded clips
//                                        (the measured, growing data source)
//
// See docs/creator-v10/viral-pattern-research-engine.md

"use strict";

const fs = require("fs");
const path = require("path");
const { validateCorpusRow } = require("./corpus-schema");

// repoRoot = three levels up: src/creator-intelligence/research-corpus -> root
const REPO_ROOT = path.resolve(__dirname, "..", "..", "..");
const DATA_DIR = path.join(REPO_ROOT, "data", "viral-research");
const MANIFEST_PATH = path.join(DATA_DIR, "MANIFEST.json");

const BUCKETS = ["youtube", "tiktok", "reels", "gaming", "own"];

function bucketDir(bucket) { return path.join(DATA_DIR, bucket); }
function bucketFile(bucket) { return path.join(bucketDir(bucket), `${bucket}.jsonl`); }

function ensureDir(dir) { if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true }); }

/**
 * Route a row to a bucket. Own-content sources always go to "own". Otherwise
 * gaming-category references go to "gaming"; the rest go by platform.
 */
function routeBucket(row) {
  if (row.source === "own_render" || row.source === "own_upload") return "own";
  if (row.category === "gaming") return "gaming";
  if (row.platform === "youtube") return "youtube";
  if (row.platform === "tiktok") return "tiktok";
  if (row.platform === "instagram") return "reels";
  return "youtube";
}

function readBucket(bucket) {
  const file = bucketFile(bucket);
  if (!fs.existsSync(file)) return [];
  const rows = [];
  for (const line of fs.readFileSync(file, "utf8").split("\n")) {
    if (!line.trim()) continue;
    try { rows.push(JSON.parse(line)); } catch { /* skip malformed — never count it */ }
  }
  return rows;
}

/** All rows across every bucket. */
function readAll() {
  const out = [];
  for (const b of BUCKETS) out.push(...readBucket(b));
  return out;
}

/** Rows that carry genuinely measured editing features (have a fingerprint). */
function readMeasured() {
  return readAll().filter((r) => r.featureProvenance === "measured" && r.fingerprint);
}

/** Rows that have public engagement metadata (a real view count). */
function readWithViews() {
  return readAll().filter((r) => r.metadata && typeof r.metadata.views === "number");
}

/**
 * Honest counts: total + per-bucket + split by provenance. This is the source
 * of truth the miner/reference engine consume for sufficiency.
 */
function counts() {
  const perBucket = {};
  let total = 0, measured = 0, metadataOnly = 0;
  for (const b of BUCKETS) {
    const rows = readBucket(b);
    perBucket[b] = rows.length;
    total += rows.length;
    for (const r of rows) {
      if (r.featureProvenance === "measured") measured++;
      else metadataOnly++;
    }
  }
  return { total, measured, metadataOnly, perBucket };
}

function appendRow(row) {
  const { valid, errors } = validateCorpusRow(row);
  if (!valid) throw new Error(`invalid corpus row: ${errors.join("; ")}`);
  const bucket = routeBucket(row);
  ensureDir(bucketDir(bucket));
  fs.appendFileSync(bucketFile(bucket), JSON.stringify(row) + "\n", "utf8");
  refreshManifest();
  return { bucket };
}

/** True if a row with this id already exists (dedupe collected references). */
function hasId(id) {
  if (!id) return false;
  return readAll().some((r) => r.id === id);
}

/**
 * Rewrite MANIFEST.json with real counts + provenance split + a ToS note. The
 * manifest is the auditable provenance record; counts here always match disk.
 */
function refreshManifest() {
  ensureDir(DATA_DIR);
  const c = counts();
  const manifest = {
    counts: c,
    updatedAt: new Date().toISOString(),
    provenanceNote:
      "measured = editing features were measured from a video Lantern was allowed " +
      "to analyze (own content or rights-cleared import). metadataOnly = public " +
      "reference with engagement metadata only; its editing features are null " +
      "because the video was never downloaded or analyzed.",
    collectionPolicy:
      "Public references store metadata (views/duration/title/category) only, via " +
      "official APIs or manual entry. No third-party copyrighted video is downloaded " +
      "or pixel-analyzed.",
  };
  fs.writeFileSync(MANIFEST_PATH, JSON.stringify(manifest, null, 2), "utf8");
  return manifest;
}

module.exports = {
  DATA_DIR, MANIFEST_PATH, BUCKETS,
  counts, readAll, readBucket, readMeasured, readWithViews,
  appendRow, hasId, routeBucket, refreshManifest,
};
