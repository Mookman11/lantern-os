"use strict";
/**
 * Family / shared memory vault (#1437) — "the family's brain".
 *
 * A local, owned, multi-user grounded memory: recipes, allergies, the WiFi saga,
 * password-rotation reminders. The distinct piece is per-entry visibility — everyone /
 * private / shared-with-specific-members — so the household shares what it wants and keeps
 * the rest private, all on one machine.
 *
 * Access control + search are pure (no I/O), so the "who can see what" logic is fully
 * testable. Thin JSONL persistence underneath.
 */
const fs = require("fs");
const path = require("path");
const crypto = require("crypto");

const DEFAULT_REPO_ROOT = path.resolve(__dirname, "../../..");
const CATEGORIES = ["recipe", "allergy", "wifi", "password", "contact", "household", "other"];
const STOP = new Set("the a an and or of to in on at for with is are was this that it as by from".split(" "));

function tokenize(text) { return String(text || "").toLowerCase().split(/[^a-z0-9]+/).filter((t) => t.length >= 3 && !STOP.has(t)); }

// Who can see an entry. everyone → all members; private → author only; an array of member
// ids → the author plus those members.
function canView(entry, viewerId) {
  if (!entry) return false;
  const v = entry.visibility;
  if (v == null || v === "everyone") return true;
  if (v === "private") return entry.author === viewerId;
  if (Array.isArray(v)) return entry.author === viewerId || v.includes(viewerId);
  return entry.author === viewerId;
}

function visibleTo(entries, viewerId) {
  return (entries || []).filter((e) => canView(e, viewerId))
    .slice().sort((a, b) => (Date.parse(b.createdAt) || 0) - (Date.parse(a.createdAt) || 0));
}

// Search WITHIN what the viewer is allowed to see — access control is applied first, so a
// search can never leak a private entry.
function search(entries, query, viewerId) {
  const visible = visibleTo(entries, viewerId);
  const q = [...new Set(tokenize(query))];
  if (!q.length) return visible;
  return visible.map((e) => {
    const hay = tokenize(`${e.title} ${e.content} ${(e.tags || []).join(" ")} ${e.category}`);
    let score = 0; for (const term of q) score += hay.filter((h) => h === term).length;
    return { e, score };
  }).filter((x) => x.score > 0).sort((a, b) => b.score - a.score).map((x) => x.e);
}

function vaultStats(entries, viewerId) {
  const visible = visibleTo(entries, viewerId);
  const byCat = {};
  for (const e of visible) byCat[e.category || "other"] = (byCat[e.category || "other"] || 0) + 1;
  const members = [...new Set((entries || []).map((e) => e.author).filter(Boolean))].sort();
  return {
    visibleCount: visible.length,
    totalCount: (entries || []).length,
    privateHidden: (entries || []).length - visible.length,
    byCategory: Object.entries(byCat).map(([category, count]) => ({ category, count })).sort((a, b) => b.count - a.count),
    members,
    status: (entries || []).length ? "ok" : "insufficient_data",
  };
}

// ── thin JSONL persistence (local-only) ─────────────────────────────────────────
function _file(root) { return path.join(root || DEFAULT_REPO_ROOT, "data", "family-vault", "entries.jsonl"); }
function readEntries(root) {
  try {
    return fs.readFileSync(_file(root), "utf8").split("\n").filter((l) => l.trim())
      .map((l) => { try { return JSON.parse(l); } catch { return null; } }).filter(Boolean);
  } catch { return []; }
}
function addEntry(root, input, nowIso) {
  const title = String(input.title || "").trim();
  const content = String(input.content || "").trim();
  if (!title) throw new Error("title is required");
  const author = String(input.author || "").trim() || "household";
  let visibility = input.visibility;
  if (visibility !== "everyone" && visibility !== "private" && !Array.isArray(visibility)) visibility = "everyone";
  if (Array.isArray(visibility)) visibility = [...new Set(visibility.map((m) => String(m).trim()).filter(Boolean))];
  const entry = {
    id: `vault:${crypto.randomUUID()}`,
    title: title.slice(0, 200),
    content: content.slice(0, 5000),
    category: CATEGORIES.includes(input.category) ? input.category : "other",
    author, visibility,
    tags: [...new Set((Array.isArray(input.tags) ? input.tags : []).map((t) => String(t).trim().toLowerCase()).filter(Boolean))],
    createdAt: nowIso,
  };
  const f = _file(root); fs.mkdirSync(path.dirname(f), { recursive: true });
  fs.appendFileSync(f, JSON.stringify(entry) + "\n");
  return entry;
}

module.exports = { CATEGORIES, tokenize, canView, visibleTo, search, vaultStats, readEntries, addEntry };
