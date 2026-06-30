// Second brain API (#1433). Local-only personal RAG over what you've read/watched.
//   GET  /api/brain                 → { items (recent), count }
//   GET  /api/brain/search?q=…      → { results }
//   POST /api/brain                 { title, url, type, content, tags } → item + contradictions it surfaces
const sb = require("../lib/second-brain");

module.exports = async function brainRoutes(req, res, url, deps) {
  const { sendJson, collectRequestBody, repoRoot } = deps;

  if (url.pathname === "/api/brain/search" && req.method === "GET") {
    const items = sb.readItems(repoRoot);
    const q = url.searchParams.get("q") || "";
    sendJson(res, { ok: true, query: q, results: sb.search(items, q), contradictions: sb.findContradictions(items, q) }, 200);
    return true;
  }

  if (url.pathname === "/api/brain" && req.method === "GET") {
    const items = sb.readItems(repoRoot);
    sendJson(res, { ok: true, count: items.length, items: items.slice(-30).reverse() }, 200);
    return true;
  }

  if (url.pathname === "/api/brain" && req.method === "POST") {
    try {
      const body = JSON.parse((await collectRequestBody(req)) || "{}");
      const existing = sb.readItems(repoRoot);
      const item = sb.captureItem(repoRoot, body, new Date().toISOString());
      // On capture, surface anything already saved that may contradict the new item.
      const contradictions = sb.findContradictions(existing, `${item.title} ${item.content}`);
      sendJson(res, { ok: true, item, contradictions }, 201);
    } catch (err) { sendJson(res, { ok: false, error: err.message }, 400); }
    return true;
  }

  return false;
};
