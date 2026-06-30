// Job-hunt tracker API (#1431). Local-only; recruiting funnel + per-app next actions.
//   GET  /api/jobs                 → { apps (with nextAction), funnel }
//   POST /api/jobs                 { company, role, source, stage, notes } → app
//   POST /api/jobs/:id             { stage?, outcome? } → updated app
const jh = require("../lib/job-hunt");

module.exports = async function jobsRoutes(req, res, url, deps) {
  const { sendJson, collectRequestBody, repoRoot } = deps;

  if (url.pathname === "/api/jobs" && req.method === "GET") {
    const apps = jh.readApps(repoRoot);
    const withNext = apps.map((a) => ({ ...a, nextAction: jh.nextAction(a) }))
      .sort((a, b) => (Date.parse(b.lastUpdate) || 0) - (Date.parse(a.lastUpdate) || 0));
    sendJson(res, { ok: true, apps: withNext, funnel: jh.funnelStats(apps) }, 200);
    return true;
  }

  if (url.pathname === "/api/jobs" && req.method === "POST") {
    try {
      const app = jh.addApp(repoRoot, JSON.parse((await collectRequestBody(req)) || "{}"), new Date().toISOString());
      sendJson(res, { ok: true, app }, 201);
    } catch (err) { sendJson(res, { ok: false, error: err.message }, 400); }
    return true;
  }

  const m = url.pathname.match(/^\/api\/jobs\/([^/]+)$/);
  if (m && req.method === "POST") {
    try {
      const app = jh.updateApp(repoRoot, decodeURIComponent(m[1]), JSON.parse((await collectRequestBody(req)) || "{}"), new Date().toISOString());
      if (!app) { sendJson(res, { ok: false, error: "app_not_found" }, 404); return true; }
      sendJson(res, { ok: true, app }, 200);
    } catch (err) { sendJson(res, { ok: false, error: err.message }, 400); }
    return true;
  }

  return false;
};
