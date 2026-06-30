"use strict";
/**
 * Personal AI that remembers your life across months (#1429, Remember stage).
 *
 * Durable personal facts — your kid's shoe size, the landlord's name, the argument in March —
 * stored locally and recalled by question months later. Cloud assistants forget when the
 * context window rolls; this keeps the fact forever. These facts do NOT decay (the whole
 * point) — separate from the forgetting-curve memory.
 *
 * extractFact (sentence → {subject, attribute, value}), categorize, and recall (question →
 * best matching facts) are pure/deterministic; persistence is append-only JSONL.
 */
const fs = require("fs");
const path = require("path");
const crypto = require("crypto");

const DEFAULT_REPO_ROOT = path.resolve(__dirname, "../../..");
const STOP = new Set("the a an is are was were be of to in on at my your his her their our its what whats who whos when where which that this do does did i you tell me remember know".split(" "));

const CATEGORIES = [
  { name: "people", re: /\b(name|brother|sister|mom|dad|mother|father|kid|son|daughter|wife|husband|friend|landlord|boss|doctor|neighbor|partner)\b/i },
  { name: "dates", re: /\b(birthday|anniversary|due date|appointment|deadline|march|april|may|june|july|august|january|february|october|november|december|\d{4})\b/i },
  { name: "places", re: /\b(address|street|city|live|lives|home|office|restaurant|gym|school)\b/i },
  { name: "preferences", re: /\b(size|favorite|favourite|allergic|allergy|likes?|loves?|hates?|prefers?|order|coffee)\b/i },
  { name: "events", re: /\b(argument|fight|met|trip|vacation|wedding|moved|started|quit|happened)\b/i },
];

function terms(s) {
  return String(s || "").toLowerCase().replace(/[^a-z0-9 ]+/g, " ").split(/\s+/).filter((w) => w.length > 1 && !STOP.has(w));
}

function categorize(text) {
  for (const c of CATEGORIES) if (c.re.test(text)) return c.name;
  return "other";
}

// Best-effort parse of a natural sentence into {subject, attribute, value}.
// Handles "my kid's shoe size is 7", "the landlord's name is Dana", "Mom's birthday is March 3".
function extractFact(text) {
  const t = String(text || "").trim().replace(/\.$/, "");
  if (!t) return null;
  // possessive: "<subject>'s <attribute> is <value>"
  let m = t.match(/^(.*?)'s\s+(.+?)\s+(?:is|are|was|=|:)\s+(.+)$/i);
  if (m) return { subject: m[1].trim(), attribute: m[2].trim(), value: m[3].trim() };
  // "<subject> <attribute> is <value>"  (e.g. "landlord name is Dana")
  m = t.match(/^(.+?)\s+(?:is|are|was|=|:)\s+(.+)$/i);
  if (m) return { subject: m[1].trim(), attribute: m[1].trim(), value: m[2].trim() };
  // fallback: store the whole thing as a value with no structured subject
  return { subject: "", attribute: t, value: t };
}

function monthsAgo(savedAt, nowMs) {
  const t = Date.parse(savedAt);
  if (!t) return null;
  return Math.max(0, Math.round(((nowMs != null ? nowMs : Date.now()) - t) / (30 * 86400000)));
}

// Recall: score every fact against a question by term overlap (subject + attribute + value),
// return the best matches with a "remembered N months ago" longevity. cite-or-abstain: if
// nothing overlaps, return status:"no_memory" rather than guessing.
function recall(facts, query, opts = {}) {
  const q = new Set(terms(query));
  if (!q.size) return { status: "insufficient_data", matches: [] };
  const now = opts.nowMs != null ? opts.nowMs : Date.now();
  const scored = (facts || []).map((f) => {
    const hay = new Set(terms(`${f.subject} ${f.attribute} ${f.value}`));
    let hits = 0; for (const w of q) if (hay.has(w)) hits++;
    // subject/attribute hits matter more than value hits for "what is X's Y" questions
    const subjAttr = new Set(terms(`${f.subject} ${f.attribute}`));
    let keyHits = 0; for (const w of q) if (subjAttr.has(w)) keyHits++;
    const score = hits + keyHits * 0.5;
    return { fact: f, score, monthsAgo: monthsAgo(f.savedAt, now) };
  }).filter((x) => x.score > 0).sort((a, b) => b.score - a.score);

  if (!scored.length) return { status: "no_memory", matches: [], answer: "I don't have a memory of that yet." };
  const top = scored.slice(0, opts.limit || 3);
  const best = top[0];
  const since = best.monthsAgo == null ? "" : best.monthsAgo === 0 ? " (you told me this recently)" : ` (you told me ${best.monthsAgo} month${best.monthsAgo === 1 ? "" : "s"} ago)`;
  return {
    status: "ok",
    answer: `${best.fact.value}${since}`,
    matches: top.map((x) => ({ ...x.fact, score: Math.round(x.score * 100) / 100, monthsAgo: x.monthsAgo })),
  };
}

// ── append-only JSONL persistence ───────────────────────────────────────────────
function _file(root) { return path.join(root || DEFAULT_REPO_ROOT, "data", "life-memory", "facts.jsonl"); }
function readFacts(root) {
  try {
    return fs.readFileSync(_file(root), "utf8").split("\n").filter((l) => l.trim())
      .map((l) => { try { return JSON.parse(l); } catch { return null; } }).filter(Boolean);
  } catch { return []; }
}
function addFact(root, input, nowIso) {
  let subject = input.subject, attribute = input.attribute, value = input.value;
  if ((!attribute || !value) && input.text) {
    const ex = extractFact(input.text);
    if (ex) { subject = subject || ex.subject; attribute = attribute || ex.attribute; value = value || ex.value; }
  }
  value = String(value || "").trim();
  if (!value) throw new Error("nothing to remember (provide text or value)");
  const fact = {
    id: `mem:${crypto.randomUUID()}`,
    subject: String(subject || "").slice(0, 160).trim(),
    attribute: String(attribute || "").slice(0, 200).trim(),
    value: value.slice(0, 600),
    category: categorize(`${subject} ${attribute} ${value} ${input.text || ""}`),
    savedAt: nowIso,
  };
  const f = _file(root); fs.mkdirSync(path.dirname(f), { recursive: true });
  fs.appendFileSync(f, JSON.stringify(fact) + "\n");
  return fact;
}

module.exports = { CATEGORIES, terms, categorize, extractFact, recall, readFacts, addFact, monthsAgo };
