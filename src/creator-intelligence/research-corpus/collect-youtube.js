// Viral Pattern Research Engine — public reference collection (metadata only)
//
// Pulls PUBLIC engagement metadata (views, duration, title, category, publish
// date) for high-view Shorts via the official YouTube Data API v3, and offers a
// manual-entry path for TikTok/Reels (which have no sanctioned bulk metadata
// API). It NEVER downloads or pixel-analyzes the videos — editing features stay
// null with featureProvenance:"null". This is the ToS-respecting way to learn
// topic/length ↔ views relationships from 100k+ view references.
//
// Requires YOUTUBE_API_KEY in the environment. With no key it returns a clear
// insufficient_data result instead of faking anything.
//
// See docs/creator-v10/viral-pattern-research-engine.md

"use strict";

const https = require("https");
const corpus = require("./corpus-store");

// YouTube numeric categoryId → our category enum (approximate; unknown→other).
const YT_CATEGORY_MAP = {
  "20": "gaming", "23": "comedy", "17": "sports", "15": "animals",
  "28": "science", "24": "entertainment", "1": "entertainment", "10": "entertainment",
};

function httpsGetJson(url) {
  return new Promise((resolve, reject) => {
    https.get(url, (res) => {
      let data = "";
      res.on("data", (c) => (data += c));
      res.on("end", () => {
        try {
          const json = JSON.parse(data);
          if (res.statusCode >= 400) {
            reject(new Error(`YouTube API ${res.statusCode}: ${json.error ? json.error.message : data.slice(0, 200)}`));
          } else resolve(json);
        } catch (e) { reject(new Error(`bad JSON from YouTube API: ${e.message}`)); }
      });
    }).on("error", reject);
  });
}

/** Parse ISO-8601 duration (PT#H#M#S) to seconds. */
function parseISODuration(iso) {
  const m = /^PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?$/.exec(iso || "");
  if (!m) return null;
  return (Number(m[1] || 0) * 3600) + (Number(m[2] || 0) * 60) + Number(m[3] || 0);
}

/**
 * Collect high-view YouTube Shorts metadata for a query.
 * @param {{query:string, minViews?:number, maxResults?:number, maxDurationSec?:number, category?:string}} opts
 * @returns {Promise<{status:"ok"|"insufficient_data"|"error", collected?, skipped?, ...}>}
 */
async function collectYouTube(opts = {}) {
  const apiKey = process.env.YOUTUBE_API_KEY;
  if (!apiKey) {
    return { status: "insufficient_data", reason: "no_youtube_api_key",
      note: "Set YOUTUBE_API_KEY to collect public reference metadata. No data was invented." };
  }
  const query = opts.query;
  if (!query || typeof query !== "string") {
    return { status: "error", reason: "query_required" };
  }
  const minViews = Number.isFinite(opts.minViews) ? opts.minViews : 100000;
  const maxResults = Math.min(50, Math.max(1, opts.maxResults || 25));
  const maxDurationSec = Number.isFinite(opts.maxDurationSec) ? opts.maxDurationSec : 180;

  // 1) search for short videos ordered by view count
  const searchUrl = "https://www.googleapis.com/youtube/v3/search?part=snippet" +
    `&q=${encodeURIComponent(query)}&type=video&videoDuration=short&order=viewCount` +
    `&maxResults=${maxResults}&key=${apiKey}`;
  const search = await httpsGetJson(searchUrl);
  const ids = (search.items || []).map((it) => it.id && it.id.videoId).filter(Boolean);
  if (ids.length === 0) return { status: "ok", collected: 0, skipped: 0, note: "no results" };

  // 2) fetch statistics + contentDetails for those ids
  const videosUrl = "https://www.googleapis.com/youtube/v3/videos?part=statistics,contentDetails,snippet" +
    `&id=${ids.join(",")}&key=${apiKey}`;
  const videos = await httpsGetJson(videosUrl);

  let collected = 0, skipped = 0;
  const errors = [];
  for (const v of videos.items || []) {
    try {
      const views = Number(v.statistics && v.statistics.viewCount);
      const durationSec = parseISODuration(v.contentDetails && v.contentDetails.duration);
      if (!Number.isFinite(views) || views < minViews) { skipped++; continue; }
      if (durationSec !== null && durationSec > maxDurationSec) { skipped++; continue; }
      if (corpus.hasId(`yt_${v.id}`)) { skipped++; continue; }

      const sn = v.snippet || {};
      const category = opts.category || YT_CATEGORY_MAP[sn.categoryId] || "other";
      corpus.appendRow({
        id: `yt_${v.id}`,
        platform: "youtube",
        category,
        source: "youtube_data_api",
        collectedAt: new Date().toISOString(),
        title: sn.title || `YouTube ${v.id}`,
        creator: sn.channelTitle || null,
        url: `https://www.youtube.com/watch?v=${v.id}`,
        metadata: {
          views,
          likeCount: Number.isFinite(Number(v.statistics.likeCount)) ? Number(v.statistics.likeCount) : null,
          commentCount: Number.isFinite(Number(v.statistics.commentCount)) ? Number(v.statistics.commentCount) : null,
          durationSec,
          publishedAt: sn.publishedAt || null,
        },
        features: {}, // metadata-only — editing features were NOT measured
        fingerprint: null,
        featureProvenance: "null",
        analysisRef: null,
        notes: `collected via youtube_data_api for query "${query}"`,
      });
      collected++;
    } catch (e) { errors.push(e.message); }
  }

  return { status: "ok", collected, skipped, query, minViews, errors: errors.slice(0, 5) };
}

/**
 * Manually record a public reference's metadata (for TikTok/Reels, which have
 * no sanctioned bulk metadata API). Editing features stay null.
 * @param {{platform:string, url:string, title:string, views:number, durationSec?:number, category?:string, creator?:string}} entry
 */
function importMetadataRow(entry = {}) {
  const id = entry.id || `man_${entry.platform || "x"}_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
  corpus.appendRow({
    id,
    platform: entry.platform,
    category: entry.category || "other",
    source: "manual_metadata",
    collectedAt: new Date().toISOString(),
    title: entry.title,
    creator: entry.creator || null,
    url: entry.url || null,
    metadata: {
      views: Number.isFinite(Number(entry.views)) ? Number(entry.views) : null,
      likeCount: null,
      commentCount: null,
      durationSec: Number.isFinite(Number(entry.durationSec)) ? Number(entry.durationSec) : null,
      publishedAt: entry.publishedAt || null,
    },
    features: {},
    fingerprint: null,
    featureProvenance: "null",
    analysisRef: null,
    notes: "manual metadata entry",
  });
  return { status: "ok", id };
}

module.exports = { collectYouTube, importMetadataRow, parseISODuration };
