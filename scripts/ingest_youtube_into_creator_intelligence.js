// Ingests this research loop's real, collected YouTube Shorts metadata
// (data/youtube/top5000_shorts.jsonl + top5000_gaming_shorts.jsonl, see
// research/hour_01.md) into the Creator Intelligence dataset store
// (data/creator-intelligence/{general,gaming}/), which is the project's
// existing, schema-validated, sufficiency-gated population dataset used by
// src/creator-intelligence/scoring/score-engine.js. That store was empty
// before this script ran — this research loop's collection had not been
// wired into it. Structural fields not measurable from metadata alone
// (captionDensity, cutFrequency, zoomFrequency, hookLength) are left null,
// never guessed — see docs/creator-v10/research-dataset-schema.md.
"use strict";

const fs = require("fs");
const path = require("path");
const store = require("../src/creator-intelligence/dataset/dataset-store");

const ROOT = path.resolve(__dirname, "..");
const SOURCES = [
  { file: path.join(ROOT, "data", "youtube", "top5000_shorts.jsonl"), gaming: false },
  { file: path.join(ROOT, "data", "youtube", "top5000_gaming_shorts.jsonl"), gaming: true },
];

// Real category → schema GAMES enum, only where the mapping is unambiguous.
// Anything not listed (generic terms like "shorts clutch", "shorts gameplay")
// honestly maps to "other" rather than guessing a specific title.
const QUERY_TO_GAME = {
  "call of duty shorts": "cod",
  "fortnite shorts": "fortnite",
  "minecraft shorts": "minecraft",
  "gta shorts": "gta",
  "roblox shorts": "roblox",
  "valorant shorts": "valorant",
  "apex legends shorts": "apex",
  "elden ring shorts": "elden_ring",
  "marvel rivals shorts": "marvel_rivals",
  "cs2 shorts": "cs2",
};

function loadJsonl(file) {
  if (!fs.existsSync(file)) return [];
  return fs.readFileSync(file, "utf8").split("\n")
    .map((l) => l.trim()).filter(Boolean)
    .map((l) => JSON.parse(l));
}

function toGeneralShort(r) {
  return {
    id: `youtube_${r.video_id}`,
    platform: "youtube",
    source: r.source || "youtube_api_real",
    collectedAt: r.timestamp,
    title: r.title,
    duration: typeof r.duration === "number" ? r.duration : null,
    viewCount: typeof r.views === "number" ? r.views : null,
    likeCount: typeof r.likes === "number" ? r.likes : null,
    commentCount: typeof r.comments === "number" ? r.comments : null,
    captionDensity: null,
    cutFrequency: null,
    zoomFrequency: null,
    hookLength: null,
  };
}

function main() {
  const existingIds = new Set([
    ...store.readAll("general").map((r) => r.id),
    ...store.readAll("gaming").map((r) => r.id),
  ]);

  let appended = 0, skippedDupe = 0, skippedInvalid = 0;
  const invalidSamples = [];

  for (const { file, gaming } of SOURCES) {
    const rows = loadJsonl(file);
    for (const r of rows) {
      const base = toGeneralShort(r);
      if (existingIds.has(base.id)) { skippedDupe++; continue; }

      try {
        if (gaming) {
          const game = QUERY_TO_GAME[r.query_source] || "other";
          store.appendGaming({ ...base, game });
        } else {
          store.appendGeneral(base);
        }
        existingIds.add(base.id);
        appended++;
      } catch (e) {
        skippedInvalid++;
        if (invalidSamples.length < 5) invalidSamples.push({ id: base.id, error: e.message });
      }
    }
  }

  const counts = store.counts();
  const byGame = store.gamingCountsByGame();
  console.log(JSON.stringify({ appended, skippedDupe, skippedInvalid, invalidSamples, counts, byGame }, null, 2));
}

main();
