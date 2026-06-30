// Verification-as-a-service (#1425). Verify stage — adversarial refute-attempts → verdict.
//   POST /api/verify  { claim, evidence?: string[] }  → { verdict, confidence, votes, sources }
const { verifyClaim } = require("../lib/verify-service");

module.exports = async function verifyRoutes(req, res, url, deps) {
  const { sendJson, collectRequestBody } = deps;

  if (url.pathname === "/api/verify" && req.method === "POST") {
    try {
      const body = JSON.parse((await collectRequestBody(req)) || "{}");
      const claim = String(body.claim || "");
      if (claim.length > 2000) { sendJson(res, { ok: false, error: "claim too long (max 2000 chars)" }, 400); return true; }
      const evidence = Array.isArray(body.evidence) ? body.evidence.slice(0, 20).map((e) => String(e || "").slice(0, 1000)) : [];
      const result = verifyClaim(claim, evidence);
      if (result.status !== "ok") { sendJson(res, { ok: false, ...result }, 400); return true; }
      sendJson(res, { ok: true, ...result, generatedAt: new Date().toISOString() }, 200);
    } catch (err) { sendJson(res, { ok: false, error: err.message }, 400); }
    return true;
  }

  return false;
};
