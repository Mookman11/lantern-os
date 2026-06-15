// Viral Pattern Research Engine — corpus row schema + validators
// See docs/creator-v10/viral-pattern-research-engine.md
//
// HONESTY GATE (the whole point of this file): a corpus row may only claim
// MEASURED editing features (cut frequency, hook length, zoom events, …) when
// those numbers were actually measured from a video Lantern was allowed to
// analyze — proven by a non-empty `analysisRef`. Public videos collected via a
// platform API carry metadata only (views/duration/title); their editing
// `features` MUST stay null with `featureProvenance:"null"`. The validator
// rejects any row that puts a number in `features` without earning it. This is
// what stops the corpus from ever accumulating fabricated "zoom_events: 14"
// style values for videos we never opened.

"use strict";

const PLATFORMS = ["youtube", "tiktok", "instagram"];
const CATEGORIES = [
  "gaming", "comedy", "sports", "fails", "animals",
  "science", "tech", "entertainment", "other",
];
// Where the row came from. *_api / *_metadata sources are metadata-only by
// construction; own_* and local_import are the only sources allowed to carry
// measured editing features.
const SOURCES = [
  "youtube_data_api", "manual_metadata", // metadata-only (no video analyzed)
  "own_render", "own_upload", "local_import", // rights-cleared → measurable
];
const METADATA_ONLY_SOURCES = new Set(["youtube_data_api", "manual_metadata"]);

const FEATURE_PROVENANCE = ["null", "measured", "research_prior"];

// The editing features the engine cares about. Each may be a finite number or
// null. Numbers are only legal under measured/research_prior provenance.
const EDITING_FEATURE_KEYS = [
  "hookLength",     // seconds to first event
  "cutFrequency",   // cuts per minute
  "captionDensity", // 0..1 fraction of clip covered by captions
  "zoomEvents",     // count
  "reactionEvents", // count (facecam reactions)
  "audioPeaks",     // count
  "payoffTime",     // seconds (time of the strongest late beat)
];

// Fingerprint dimensions (0..100), derived from measured component signals.
const FINGERPRINT_KEYS = [
  "hookStrength", "payoffStrength", "captionDensity",
  "motionIntensity", "curiosityGap", "loopability",
];

function isFiniteNumber(v) { return typeof v === "number" && Number.isFinite(v); }
function isFiniteNumberOrNull(v) { return v === null || isFiniteNumber(v); }
function isNonEmptyString(v) { return typeof v === "string" && v.length > 0; }

/**
 * @returns {{ valid: boolean, errors: string[] }}
 */
function validateCorpusRow(row) {
  const errors = [];
  if (!row || typeof row !== "object") return { valid: false, errors: ["row is not an object"] };

  if (!isNonEmptyString(row.id)) errors.push("id required");
  if (!PLATFORMS.includes(row.platform)) errors.push(`platform must be one of ${PLATFORMS.join("|")}`);
  if (!CATEGORIES.includes(row.category)) errors.push(`category must be one of ${CATEGORIES.join("|")}`);
  if (!SOURCES.includes(row.source)) errors.push(`source must be one of ${SOURCES.join("|")}`);
  if (!isNonEmptyString(row.collectedAt)) errors.push("collectedAt (ISO-8601) required");
  if (!isNonEmptyString(row.title)) errors.push("title required");

  // metadata block — all numeric fields finite-or-null (never garbage)
  const md = row.metadata || {};
  if (typeof md !== "object" || md === null) {
    errors.push("metadata must be an object");
  } else {
    for (const k of ["views", "likeCount", "commentCount", "durationSec"]) {
      if (!isFiniteNumberOrNull(md[k])) errors.push(`metadata.${k} must be a finite number or null`);
    }
    if (md.publishedAt !== undefined && md.publishedAt !== null && !isNonEmptyString(md.publishedAt)) {
      errors.push("metadata.publishedAt must be an ISO string or null");
    }
  }

  // featureProvenance gate
  if (!FEATURE_PROVENANCE.includes(row.featureProvenance)) {
    errors.push(`featureProvenance must be one of ${FEATURE_PROVENANCE.join("|")}`);
  }

  // features block — keys finite-or-null; any non-null value must be earned
  const feats = row.features || {};
  let anyMeasuredValue = false;
  for (const k of EDITING_FEATURE_KEYS) {
    const v = feats[k];
    if (v === undefined) continue; // missing key treated as null
    if (!isFiniteNumberOrNull(v)) { errors.push(`features.${k} must be a finite number or null`); continue; }
    if (v !== null) anyMeasuredValue = true;
  }

  if (anyMeasuredValue) {
    if (row.featureProvenance === "null") {
      errors.push("features contain numbers but featureProvenance is 'null' (fabrication guard)");
    }
    if (row.featureProvenance === "measured" && !isNonEmptyString(row.analysisRef)) {
      errors.push("measured features require a non-empty analysisRef (which video was analyzed)");
    }
    if (METADATA_ONLY_SOURCES.has(row.source)) {
      errors.push(`source '${row.source}' is metadata-only and cannot carry measured features`);
    }
  }

  // fingerprint — null, or 6 finite numbers in [0,100]; non-null requires real features
  if (row.fingerprint !== undefined && row.fingerprint !== null) {
    if (typeof row.fingerprint !== "object") {
      errors.push("fingerprint must be null or an object");
    } else {
      for (const k of FINGERPRINT_KEYS) {
        const v = row.fingerprint[k];
        if (!isFiniteNumber(v) || v < 0 || v > 100) errors.push(`fingerprint.${k} must be a number in [0,100]`);
      }
      if (row.featureProvenance === "null") {
        errors.push("fingerprint present but featureProvenance is 'null' (a fingerprint must come from measured signals)");
      }
    }
  }

  return { valid: errors.length === 0, errors };
}

module.exports = {
  PLATFORMS, CATEGORIES, SOURCES, METADATA_ONLY_SOURCES,
  FEATURE_PROVENANCE, EDITING_FEATURE_KEYS, FINGERPRINT_KEYS,
  validateCorpusRow,
};
