// Emits the joined first-party labeled training set as JSON, so the Python
// trainer reuses dataset-store's join authority instead of re-implementing it.
// Usage: node _firstparty_join_helper.js [labelKey]   (default engagement_rate)
"use strict";
const path = require("path");
const store = require(path.join(__dirname, "..", "src", "creator-intelligence", "dataset", "dataset-store"));
const labelKey = process.argv[2] || "engagement_rate";
console.log(JSON.stringify({ labelKey, rows: store.joinLabeledFirstParty(labelKey) }));
