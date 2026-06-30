// Negotiation & life-admin co-pilot API (#1432). Local-only.
//   GET  /api/admin                 → { cases (with nextAction), stats }
//   POST /api/admin                 { type, counterparty, account, summary, desiredOutcome, policyClause, name } → case + draft
//   POST /api/admin/draft           { ...case, polish? } → { draft } (optional local-LLM tone polish)
//   POST /api/admin/:id/status      { status, outcome } → updated case
const http = require("http");
const ac = require("../lib/admin-copilot");

// Optional: ask the local Ollama model to tighten the tone. Falls back to the scaffold.
function polishDraft(scaffold) {
  return new Promise((resolve) => {
    const base = process.env.OLLAMA_BASE_URL || "http://127.0.0.1:11434";
    const model = process.env.OLLAMA_MODEL || "qwen2.5-coder:14b-instruct-q5_k_m";
    const prompt = "Rewrite this dispute email to be firm, concise, and professional — keep every fact, the deadline, "
      + "the citation slot, and the escalation. Return ONLY the email body, no preamble.\n\n" + scaffold.body;
    const payload = JSON.stringify({ model, stream: false, messages: [{ role: "user", content: prompt }], options: { temperature: 0.3, num_predict: 600 } });
    const u = new URL(base);
    const req = http.request({ hostname: u.hostname, port: u.port || 11434, path: "/api/chat", method: "POST",
      headers: { "Content-Type": "application/json", "Content-Length": Buffer.byteLength(payload) } }, (res) => {
      let data = ""; res.on("data", (c) => { data += c; });
      res.on("end", () => { try { const t = JSON.parse(data).message?.content; resolve(t && t.length > 60 ? { ...scaffold, body: t.trim(), polished: true } : scaffold); } catch { resolve(scaffold); } });
    });
    req.on("error", () => resolve(scaffold));
    req.setTimeout(40000, () => { req.destroy(); resolve(scaffold); });
    req.write(payload); req.end();
  });
}

module.exports = async function adminCopilotRoutes(req, res, url, deps) {
  const { sendJson, collectRequestBody, repoRoot } = deps;

  if (url.pathname === "/api/admin" && req.method === "GET") {
    const cases = ac.readCases(repoRoot).map((c) => ({ ...c, nextAction: ac.nextAction(c) }));
    sendJson(res, { ok: true, cases: cases.reverse(), stats: ac.caseStats(cases) }, 200);
    return true;
  }

  if (url.pathname === "/api/admin" && req.method === "POST") {
    try {
      const body = JSON.parse((await collectRequestBody(req)) || "{}");
      const c = ac.createCase(repoRoot, body, new Date().toISOString());
      sendJson(res, { ok: true, case: c, draft: ac.draftEmail(c) }, 201);
    } catch (err) { sendJson(res, { ok: false, error: err.message }, 400); }
    return true;
  }

  if (url.pathname === "/api/admin/draft" && req.method === "POST") {
    try {
      const body = JSON.parse((await collectRequestBody(req)) || "{}");
      const scaffold = ac.draftEmail(body);
      const draft = body.polish ? await polishDraft(scaffold) : scaffold;
      sendJson(res, { ok: true, draft }, 200);
    } catch (err) { sendJson(res, { ok: false, error: err.message }, 400); }
    return true;
  }

  const m = url.pathname.match(/^\/api\/admin\/([^/]+)\/status$/);
  if (m && req.method === "POST") {
    try {
      const body = JSON.parse((await collectRequestBody(req)) || "{}");
      const c = ac.updateStatus(repoRoot, decodeURIComponent(m[1]), body.status, body.outcome, new Date().toISOString());
      if (!c) { sendJson(res, { ok: false, error: "case_not_found" }, 404); return true; }
      sendJson(res, { ok: true, case: c }, 200);
    } catch (err) { sendJson(res, { ok: false, error: err.message }, 400); }
    return true;
  }

  return false;
};
