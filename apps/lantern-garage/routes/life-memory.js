// Life-memory API (#1429). Remember stage — durable personal facts + recall.
//   GET  /api/life-memory                → { facts, byCategory }
//   POST /api/life-memory                { text } or { subject, attribute, value } → fact
//   POST /api/life-memory/recall         { query } → { answer, matches }
const lm = require("../lib/life-memory");

module.exports = async function lifeMemoryRoutes(req, res, url, deps) {
  const { sendJson, collectRequestBody, repoRoot } = deps;

  if (url.pathname === "/api/life-memory" && req.method === "GET") {
    const facts = lm.readFacts(repoRoot).sort((a, b) => (Date.parse(b.savedAt) || 0) - (Date.parse(a.savedAt) || 0));
    const byCategory = {};
    for (const f of facts) (byCategory[f.category] = byCategory[f.category] || []).push(f);
    sendJson(res, { ok: true, facts, byCategory, total: facts.length }, 200);
    return true;
  }

  if (url.pathname === "/api/life-memory" && req.method === "POST") {
    try {
      const fact = lm.addFact(repoRoot, JSON.parse((await collectRequestBody(req)) || "{}"), new Date().toISOString());
      sendJson(res, { ok: true, fact }, 201);
    } catch (err) { sendJson(res, { ok: false, error: err.message }, 400); }
    return true;
  }

  if (url.pathname === "/api/life-memory/recall" && req.method === "POST") {
    try {
      const body = JSON.parse((await collectRequestBody(req)) || "{}");
      const result = lm.recall(lm.readFacts(repoRoot), String(body.query || ""));
      sendJson(res, { ok: true, ...result }, 200);
    } catch (err) { sendJson(res, { ok: false, error: err.message }, 400); }
    return true;
  }

  return false;
};
