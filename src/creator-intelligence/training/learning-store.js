// Creator Intelligence — continuous learning store
// Appends first-party EditEvents (edits, generated/selected variants, exports)
// to data/creator-intelligence/edits/. This is the operator's OWN data, always
// legitimate to keep. `outcome` stays null until real performance data exists.
//
// See docs/creator-v10/research-dataset-schema.md (EditEvent)

"use strict";

const store = require("../dataset/dataset-store");

function nowIso() {
  return new Date().toISOString();
}

function makeId(prefix) {
  return `${prefix}-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
}

/**
 * Record that an edit happened.
 * @param {string} entryId  links to data/creator/entries/<id>
 * @param {Object} features measured features of the edit
 */
function recordEdit(entryId, features = {}) {
  return store.appendEdit({
    id: makeId("edit"), entryId, createdAt: nowIso(),
    kind: "edit", features, choice: null, outcome: null,
  });
}

function recordVariantGenerated(entryId, variantId, features = {}) {
  return store.appendEdit({
    id: makeId("vargen"), entryId, createdAt: nowIso(),
    kind: "variant_generated", features, choice: variantId, outcome: null,
  });
}

function recordVariantSelected(entryId, variantId, features = {}) {
  return store.appendEdit({
    id: makeId("varsel"), entryId, createdAt: nowIso(),
    kind: "variant_selected", features, choice: variantId, outcome: null,
  });
}

function recordExport(entryId, features = {}) {
  return store.appendEdit({
    id: makeId("export"), entryId, createdAt: nowIso(),
    kind: "export", features, choice: null, outcome: null,
  });
}

/**
 * Capture the real Σ₀ feature vector of an edit that was just rendered, so it
 * can later be joined to its real published-performance outcome. This is the
 * FEATURE half of the first-party flywheel. `features` should be the measurable
 * editing decisions of the rendered Short (durations, segment count, story-arc
 * presence, collapse risk, viral component scores) — all real, none invented.
 */
function recordRenderedFeatures(entryId, renderId, features = {}) {
  return store.appendEdit({
    id: makeId("export"), entryId, createdAt: nowIso(),
    kind: "export", features: { renderId, ...features }, choice: renderId, outcome: null,
  });
}

/**
 * Record a REAL performance outcome for a Short the operator published. This is
 * the LABEL half of the flywheel — the only legitimate source of outcome-labeled
 * training data (the operator's own content). Metrics must be real numbers the
 * operator owns (their channel analytics / a figure they report); nothing here
 * is fabricated or scraped.
 * @param {string} entryId   the rendered entry this outcome belongs to
 * @param {Object} metrics   { views, likes, comments, avgViewDurationSec, ... }
 * @param {Object} opts      { source="self_reported", renderId }
 */
function recordOutcome(entryId, metrics = {}, opts = {}) {
  return store.appendOutcome({
    id: makeId("outcome"),
    entryId,
    renderId: opts.renderId || null,
    source: opts.source || "self_reported",
    recordedAt: nowIso(),
    metrics,
  });
}

module.exports = {
  recordEdit, recordVariantGenerated, recordVariantSelected, recordExport,
  recordRenderedFeatures, recordOutcome,
};
