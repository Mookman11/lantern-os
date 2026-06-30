// Family / shared memory vault API (#1437). Local-only, multi-user with per-entry visibility.
//   GET  /api/vault?member=X[&q=…]   → { entries (visible to member), stats }
//   POST /api/vault                  { title, content, category, author, visibility, tags } → entry
const fv = require("../lib/family-vault");

module.exports = async function vaultRoutes(req, res, url, deps) {
  const { sendJson, collectRequestBody, repoRoot } = deps;

  if (url.pathname === "/api/vault" && req.method === "GET") {
    const entries = fv.readEntries(repoRoot);
    const member = url.searchParams.get("member") || "household";
    const q = url.searchParams.get("q") || "";
    const visible = q ? fv.search(entries, q, member) : fv.visibleTo(entries, member);
    sendJson(res, { ok: true, member, entries: visible, stats: fv.vaultStats(entries, member) }, 200);
    return true;
  }

  if (url.pathname === "/api/vault" && req.method === "POST") {
    try {
      const entry = fv.addEntry(repoRoot, JSON.parse((await collectRequestBody(req)) || "{}"), new Date().toISOString());
      sendJson(res, { ok: true, entry }, 201);
    } catch (err) { sendJson(res, { ok: false, error: err.message }, 400); }
    return true;
  }

  return false;
};
