// Self-distillation flywheel observability API (#1421).
//   GET /api/flywheel[?target=0.7&windowHours=168] → { flywheel }
const fw = require("../lib/distillation-flywheel");

module.exports = async function flywheelRoutes(req, res, url, deps) {
  const { sendJson, repoRoot } = deps;

  if (url.pathname === "/api/flywheel" && req.method === "GET") {
    try {
      const target = parseFloat(url.searchParams.get("target") || "0.7");
      const windowHours = parseInt(url.searchParams.get("windowHours") || "168", 10) || 168;
      const flywheel = fw.flywheelStats(fw.readLeaderboard(repoRoot), fw.readDecisions(repoRoot),
        { target: Number.isFinite(target) ? target : 0.7, windowMs: windowHours * 3_600_000 });
      sendJson(res, { ok: true, flywheel }, 200);
    } catch (err) {
      sendJson(res, { ok: false, error: err.message }, 500);
    }
    return true;
  }

  return false;
};
