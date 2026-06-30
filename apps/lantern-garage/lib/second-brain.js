"use strict";
/**
 * Second brain for everything you read/watch (#1433).
 *
 * Capture articles / videos / notes into a local, grounded, queryable memory of what
 * you've actually consumed, then recall it — including the killer move: "you saved
 * something that may contradict this N days ago." Personal RAG as a consumer habit,
 * local-first (the corpus never leaves the machine).
 *
 * Search/ranking/contradiction logic is pure (no I/O), so it's deterministic + testable.
 */
const fs = require("fs");
const path = require("path");
const crypto = require("crypto");

const DEFAULT_REPO_ROOT = path.resolve(__dirname, "../../..");
const STOP = new Set("the a an and or but of to in on at for with is are was were be been being this that these those it its as by from into about over you your i we they he she them his her their our not no".split(" "));
const NEGATION = /\b(not|no|never|isn'?t|aren'?t|wasn'?t|don'?t|doesn'?t|didn'?t|debunk\w*|myth|false|hoax|contrary|however|but|actually|in fact|disprov\w*|wrong)\b/i;

function tokenize(text) {
  return String(text || "").toLowerCase().split(/[^a-z0-9]+/).filter((t) => t.length >= 3 && !STOP.has(t));
}
function countIn(tokens, term) { let c = 0; for (const t of tokens) if (t === term) c++; return c; }
function uniq(a) { return [...new Set(a)]; }
function recency(a, b) { return (Date.parse(b.capturedAt) || 0) - (Date.parse(a.capturedAt) || 0); }

// A short excerpt of the content around the first query-term hit.
function snippet(item, qTerms, width = 160) {
  const text = String(item.content || item.title || "");
  const lower = text.toLowerCase();
  let at = -1;
  for (const q of qTerms) { const i = lower.indexOf(q); if (i >= 0 && (at < 0 || i < at)) at = i; }
  if (at < 0) return text.slice(0, width).trim();
  const start = Math.max(0, at - width / 3);
  return (start > 0 ? "…" : "") + text.slice(start, start + width).trim() + (start + width < text.length ? "…" : "");
}

// TF relevance over title (×3) / tags (×2) / content (×1), recency as the tiebreak.
function search(items, query, { limit = 20 } = {}) {
  const qTerms = uniq(tokenize(query));
  const list = items || [];
  if (!qTerms.length) return list.slice().sort(recency).slice(0, limit).map((item) => ({ item, score: 0, snippet: snippet(item, []) }));
  return list.map((item) => {
    const title = tokenize(item.title), tags = (item.tags || []).flatMap(tokenize), content = tokenize(item.content);
    let score = 0, hit = 0;
    for (const q of qTerms) {
      const s = countIn(title, q) * 3 + countIn(tags, q) * 2 + countIn(content, q);
      if (s > 0) hit++;
      score += s;
    }
    return { item, score, coverage: hit / qTerms.length };
  }).filter((x) => x.score > 0)
    .sort((a, b) => (b.coverage - a.coverage) || (b.score - a.score) || recency(a.item, b.item))
    .slice(0, limit)
    .map((x) => ({ item: x.item, score: x.score, coverage: Math.round(x.coverage * 100) / 100, snippet: snippet(x.item, qTerms) }));
}

// Items that overlap a passage's terms (excluding one id) — "you've read about this".
function findRelated(items, text, { excludeId, limit = 5 } = {}) {
  return search((items || []).filter((i) => i.id !== excludeId), text, { limit });
}

// The differentiator: items that share the topic AND carry a negation/contradiction cue
// relative to the claim. Heuristic and surfaced honestly as "may contradict", with how
// long ago you saved it.
function findContradictions(items, claim, nowMs) {
  const topic = uniq(tokenize(claim));
  if (!topic.length) return [];
  const now = nowMs != null ? nowMs : Date.now();
  const out = [];
  for (const item of items || []) {
    const text = `${item.title || ""} ${item.content || ""}`;
    const itemTerms = new Set(tokenize(text));
    const shared = topic.filter((t) => itemTerms.has(t)).length;
    if (shared >= Math.min(2, topic.length) && NEGATION.test(text)) {
      const ageDays = Math.max(0, Math.round((now - (Date.parse(item.capturedAt) || now)) / 86400000));
      out.push({ id: item.id, title: item.title, url: item.url, ageDays, sharedTerms: shared, snippet: snippet(item, topic) });
    }
  }
  return out.sort((a, b) => b.sharedTerms - a.sharedTerms);
}

// ── thin JSONL persistence (local-only) ─────────────────────────────────────────
function _file(root) { return path.join(root || DEFAULT_REPO_ROOT, "data", "second-brain", "items.jsonl"); }
function readItems(root) {
  try {
    return fs.readFileSync(_file(root), "utf8").split("\n").filter((l) => l.trim())
      .map((l) => { try { return JSON.parse(l); } catch { return null; } }).filter(Boolean);
  } catch { return []; }
}
function captureItem(root, input, nowIso) {
  const title = String(input.title || "").trim();
  const content = String(input.content || "").trim();
  if (!title && !content) throw new Error("a title or content is required");
  const item = {
    id: `brain:${crypto.randomUUID()}`,
    title: (title || content.slice(0, 80)).slice(0, 280),
    url: String(input.url || "").slice(0, 600),
    type: ["article", "video", "pdf", "note"].includes(input.type) ? input.type : "note",
    content: content.slice(0, 20000),
    tags: uniq((Array.isArray(input.tags) ? input.tags : []).map((t) => String(t).trim().toLowerCase()).filter(Boolean)),
    capturedAt: nowIso,
  };
  const f = _file(root); fs.mkdirSync(path.dirname(f), { recursive: true });
  fs.appendFileSync(f, JSON.stringify(item) + "\n");
  return item;
}

module.exports = { tokenize, search, findRelated, findContradictions, readItems, captureItem };
