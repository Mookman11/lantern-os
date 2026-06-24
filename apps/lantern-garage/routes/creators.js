// Creator profile intake and retrieval
module.exports = async function creatorsRoutes(req, res, url, deps) {
  const { sendJson, collectRequestBody, path, repoRoot, fs } = deps;

  const creatorsDir = path.join(repoRoot, "data", "creators");

  function ensureDir() {
    if (!fs.existsSync(creatorsDir)) fs.mkdirSync(creatorsDir, { recursive: true });
  }

  // GET /api/creators — list all creator slugs (#1119: sort alphabetically)
  if (url.pathname === "/api/creators" && req.method === "GET") {
    ensureDir();
    const files = fs.readdirSync(creatorsDir).filter(f => f.endsWith(".json"));
    const slugs = files.map(f => f.replace(".json", "")).sort();
    sendJson(res, { creators: slugs });
    return true;
  }

  // GET /api/creators/:slug — load a creator profile
  if (url.pathname.startsWith("/api/creators/") && req.method === "GET") {
    const rawSlug = url.pathname.slice("/api/creators/".length);
    // #1107: reject instead of silently sanitizing — the caller should send a valid slug
    if (!rawSlug || !/^[a-z0-9-]+$/.test(rawSlug)) {
      sendJson(res, { error: "Invalid slug — use lowercase letters, numbers, and hyphens only" }, 400);
      return true;
    }
    const filePath = path.join(creatorsDir, `${rawSlug}.json`);
    if (!fs.existsSync(filePath)) {
      sendJson(res, { error: "Creator not found" }, 404);
      return true;
    }
    // #1118: guard JSON.parse — a corrupted profile must not 500 the server
    let data;
    try {
      data = JSON.parse(fs.readFileSync(filePath, "utf8"));
    } catch (e) {
      sendJson(res, { error: "Creator profile is corrupted and cannot be read" }, 500);
      return true;
    }
    sendJson(res, { creator: data });
    return true;
  }

  // POST /api/creators — save or update a creator profile
  if (url.pathname === "/api/creators" && req.method === "POST") {
    try {
      const raw = await collectRequestBody(req);
      const body = JSON.parse(raw);
      if (!body.slug || !/^[a-z0-9-]+$/.test(body.slug)) {
        sendJson(res, { error: "Invalid or missing slug (lowercase letters, numbers, hyphens only)" }, 400);
        return true;
      }
      ensureDir();
      const filePath = path.join(creatorsDir, `${body.slug}.json`);
      const record = { ...body, ingestedAt: new Date().toISOString() };
      fs.writeFileSync(filePath, JSON.stringify(record, null, 2), "utf8");
      sendJson(res, { saved: true, slug: body.slug, creator: record });
    } catch (err) {
      sendJson(res, { error: err.message }, 400);
    }
    return true;
  }

  return false;
};
