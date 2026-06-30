// Adaptive-compute coder budget estimator (#1423). Reason stage.
//   POST /api/adaptive-compute/analyze  { code }  → per-line depth + compute-saved meter
const ac = require("../lib/adaptive-compute");

module.exports = async function adaptiveComputeRoutes(req, res, url, deps) {
  const { sendJson, collectRequestBody } = deps;

  if (url.pathname === "/api/adaptive-compute/analyze" && req.method === "POST") {
    try {
      const body = JSON.parse((await collectRequestBody(req)) || "{}");
      const code = String(body.code || "");
      if (code.length > 20000) { sendJson(res, { ok: false, error: "code too large (max 20k chars)" }, 400); return true; }
      sendJson(res, { ok: true, analysis: ac.analyzeCode(code) }, 200);
    } catch (err) { sendJson(res, { ok: false, error: err.message }, 400); }
    return true;
  }

  return false;
};
