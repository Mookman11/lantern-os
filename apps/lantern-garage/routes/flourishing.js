const http = require("http");
const { spawn } = require("child_process");
const path = require("path");

// Human Flourishing Frameworks — proxy route
// Spawns the HFF Flask app as a child process if available, then proxies requests.

const HFF_PORT = Number(process.env.HFF_PORT || 5100);
const HFF_DIR = path.resolve(__dirname, "..", "..", "..", "integrations", "human-flourishing-frameworks");
let hffProcess = null;
let hffReady = false;

function killHff() {
  if (hffProcess && !hffProcess.killed) {
    hffProcess.kill("SIGTERM");
  }
}
process.on("SIGTERM", killHff);
process.on("SIGINT", killHff);

function startHff(repoRoot) {
  if (hffProcess) return;
  const appPy = path.join(HFF_DIR, "app.py");
  const fs = require("fs");
  if (!fs.existsSync(appPy)) {
    console.log("[HFF] app.py not found, skipping child-process spawn");
    return;
  }
  const pythonExe = process.platform === "win32" ? "python" : "python3";
  hffProcess = spawn(pythonExe, [appPy], {
    cwd: HFF_DIR,
    env: { ...process.env, PORT: String(HFF_PORT), FLASK_ENV: "production" },
    stdio: "inherit",
  });
  hffProcess.on("error", (err) => {
    console.error(`[HFF] Failed to start: ${err.message}`);
    hffProcess = null;
  });
  hffProcess.on("exit", (code) => {
    console.log(`[HFF] exited with code ${code}`);
    hffProcess = null;
    hffReady = false;
  });
  // Quick health probe
  setTimeout(() => {
    http.get(`http://127.0.0.1:${HFF_PORT}/api/world/status`, (r) => {
      hffReady = r.statusCode === 200;
      if (hffReady) console.log(`[HFF] Ready on port ${HFF_PORT}`);
    }).on("error", () => {
      console.log(`[HFF] Health probe failed on port ${HFF_PORT}`);
    });
  }, 3000);
}

function proxyRequest(req, res, targetPath) {
  return new Promise((resolve) => {
    const options = {
      hostname: "127.0.0.1",
      port: HFF_PORT,
      path: targetPath,
      method: req.method,
      headers: { ...req.headers, host: `127.0.0.1:${HFF_PORT}` },
    };
    const proxyReq = http.request(options, (proxyRes) => {
      res.writeHead(proxyRes.statusCode, proxyRes.headers);
      proxyRes.pipe(res, { end: true });
    });
    proxyReq.on("error", (err) => {
      res.writeHead(502, { "Content-Type": "application/json" });
      res.end(JSON.stringify({ ok: false, error: `HFF unreachable: ${err.message}` }));
      resolve();
    });
    req.pipe(proxyReq, { end: true });
  });
}

module.exports = async function flourishingRoutes(req, res, url, deps) {
  const { repoRoot } = deps;

  // Auto-start HFF on first request (idempotent)
  if (!hffProcess && process.env.HFF_AUTO_START !== "0") {
    startHff(repoRoot);
  }

  // Proxy /api/flourishing/* → HFF /api/*
  if (url.pathname.startsWith("/api/flourishing/")) {
    const targetPath = url.pathname.replace("/api/flourishing", "/api") + url.search;
    await proxyRequest(req, res, targetPath);
    return true;
  }

  // Serve HFF dashboard at /flourishing
  if (url.pathname === "/flourishing" || url.pathname === "/flourishing/") {
    await proxyRequest(req, res, "/" + url.search);
    return true;
  }

  // Proxy /flourishing/static/* → HFF /static/*
  if (url.pathname.startsWith("/flourishing/")) {
    const targetPath = url.pathname.replace("/flourishing", "") + url.search;
    await proxyRequest(req, res, targetPath);
    return true;
  }

  return false;
};
