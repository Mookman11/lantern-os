"use strict";
// collapse-canary.js — live chat n-gram repetition monitor (#1010).
//
// The Σ₀ decode canary (src/sigma0/decode_canary.py) operates on token-id logits
// and can't be wired directly into the Node.js SSE path. This module is the JS
// chat-level equivalent: it tracks self-repeat / n-gram echo in the streamed reply
// text, computes sigma0_proximity (0=healthy, 1=total loop-collapse), and fires a
// logged canary event when the reply starts looping.
//
// "Per-reply, not per-token": observe(text) is called once the full reply is
// assembled, so it works with every streaming provider without tapping mid-stream.
// The signal is logged; the serving path is never blocked.
//
// Acceptance (#1010): a forced repeating reply raises proximity + emits a logged
// canary_* event; healthy replies are unaffected.

const path = require("path");

const CANARY_LOG_PATH = path.resolve(__dirname, "../../data/convergence/canary-events.jsonl");
const DEFAULT_NGRAM = 3;
const PROXIMITY_THRESHOLD = 0.35; // >= 35% repeated trigrams → rising collapse

// ── Pure: word-level n-gram counter ─────────────────────────────────────────
function extractNgrams(text, n = DEFAULT_NGRAM) {
  const words = String(text || "").toLowerCase().split(/\s+/).filter(Boolean);
  if (words.length < n) return { total: 0, repeated: 0, proximity: 0 };
  const counts = new Map();
  for (let i = 0; i <= words.length - n; i++) {
    const gram = words.slice(i, i + n).join(" ");
    counts.set(gram, (counts.get(gram) || 0) + 1);
  }
  const total = counts.size + (words.length - n); // approx total positions
  let repeated = 0;
  for (const cnt of counts.values()) {
    if (cnt > 1) repeated += cnt - 1;
  }
  const proximity = total > 0 ? Math.min(1, repeated / Math.max(1, words.length - n + 1)) : 0;
  return { total: words.length - n + 1, repeated, proximity };
}

// ── Pure: echo detection — did the last 1/3 of the reply appear earlier? ────
function detectEcho(text) {
  const words = String(text || "").toLowerCase().split(/\s+/).filter(Boolean);
  if (words.length < 18) return 0;
  const tailLen = Math.floor(words.length / 3);
  const tail = words.slice(-tailLen).join(" ");
  const head = words.slice(0, words.length - tailLen).join(" ");
  // Count how many 5-grams from the tail appeared in the head
  const tailGrams = [];
  const tailWords = tail.split(/\s+/);
  for (let i = 0; i <= tailWords.length - 5; i++) tailGrams.push(tailWords.slice(i, i + 5).join(" "));
  if (!tailGrams.length) return 0;
  const matched = tailGrams.filter((g) => head.includes(g)).length;
  return matched / tailGrams.length;
}

// ── Core: compute sigma0_proximity for a completed reply ────────────────────
function computeProximity(text) {
  const { proximity: repeatProx } = extractNgrams(text, DEFAULT_NGRAM);
  const echoScore = detectEcho(text);
  // Weighted combination: trigram repeat dominates, echo is secondary signal
  return Math.min(1, repeatProx * 0.7 + echoScore * 0.3);
}

// ── I/O: log a canary event best-effort (never throws) ──────────────────────
function logCanaryEvent(event) {
  try {
    const { appendJsonlQueued } = require("./file-queue");
    appendJsonlQueued(CANARY_LOG_PATH, {
      ts: new Date().toISOString(),
      ...event,
    }).catch(() => {});
  } catch { /* never block the response */ }
}

// ── Main API: observe a completed reply ─────────────────────────────────────
// Returns { proximity, echo, canary_fired, action }.
// When proximity >= PROXIMITY_THRESHOLD, logs a canary_collapse event.
function observe(text, { agent = "keystone", provider = "unknown", surface = "dream-chat" } = {}) {
  if (!text || text.length < 50) {
    return { proximity: 0, echo: 0, canary_fired: false, action: null };
  }
  const proximity = computeProximity(text);
  const echo = detectEcho(text);
  const canary_fired = proximity >= PROXIMITY_THRESHOLD;

  if (canary_fired) {
    logCanaryEvent({
      type: "canary_collapse",
      proximity,
      echo,
      agent,
      provider,
      surface,
      text_length: text.length,
      action: "logged",
    });
  }

  return { proximity, echo, canary_fired, action: canary_fired ? "logged" : null };
}

module.exports = {
  computeProximity,
  extractNgrams,
  detectEcho,
  observe,
  PROXIMITY_THRESHOLD,
  CANARY_LOG_PATH,
};
