const { spawn } = require("child_process");

// Operator notes, conversation log, action triggers
module.exports = async function operatorRoutes(req, res, url, deps) {
  const { sendJson, collectRequestBody, appendJsonlQueued, operatorNotesPath,
    conversationLogPath, path, repoRoot,
    readConversationLog, normalizeConversationEntry, appendConversationEntry,
    runPowerShell, flatRagHousePath, writeFlatRagHouse } = deps;

  if (url.pathname === "/api/operator-notes" && req.method === "POST") {
    try {
      const body = await collectRequestBody(req);
      const input = JSON.parse(body || "{}");
      const text = String(input.text || "").trim().slice(0, 500);
      const priority = ["P0", "P1", "P2"].includes(input.priority) ? input.priority : "P1";
      if (!text) throw new Error("note_text_required");
      const record = { createdAt: new Date().toISOString(), text, priority, done: false };
      await appendJsonlQueued(operatorNotesPath, record);
      sendJson(res, { ok: true, record }, 201);
    } catch (error) {
      sendJson(res, { error: error.message }, 400);
    }
    return true;
  }
  if (url.pathname === "/api/conversations" && req.method === "GET") {
    const limit = Math.max(1, Math.min(200, Number(url.searchParams.get("limit") || 50)));
    sendJson(res, {
      path: path.relative(repoRoot, conversationLogPath),
      conversations: readConversationLog(limit),
    });
    return true;
  }
  if (url.pathname === "/api/conversations" && req.method === "POST") {
    try {
      const body = await collectRequestBody(req);
      const entry = normalizeConversationEntry(JSON.parse(body || "{}"));
      await appendConversationEntry(entry);
      sendJson(res, { ok: true, entry }, 201);
    } catch (error) {
      sendJson(res, { error: error.message }, 400);
    }
    return true;
  }
  if (url.pathname === "/api/actions/run-loop" && req.method === "POST") {
    try {
      const py = process.platform === "win32" ? "python" : "python3";
      const proc = spawn(py, [path.join(repoRoot, "src", "convergence_io_engine.py"), "loop"], {
        cwd: repoRoot,
        timeout: 60000,
      });
      let stdout = "";
      let stderr = "";
      proc.stdout.on("data", (data) => { stdout += data; });
      proc.stderr.on("data", (data) => { stderr += data; });
      const result = await new Promise((resolve, reject) => {
        proc.on("close", (code) => {
          resolve({ ok: code === 0, code, stdout: stdout.slice(0, 2000), stderr: stderr.slice(0, 1000) });
        });
        proc.on("error", (err) => reject(err));
      });
      sendJson(res, result, result.ok ? 200 : 500);
    } catch (err) {
      sendJson(res, { ok: false, error: err.message }, 500);
    }
    return true;
  }
  if (url.pathname === "/api/actions/local-controls" && req.method === "POST") {
    const result = await runPowerShell("scripts/Start-LanternLocalControls.ps1");
    sendJson(res, result, result.code === 0 ? 200 : 500);
    return true;
  }
  if (url.pathname === "/api/actions/flat-rag-ingest" && req.method === "POST") {
    const house = await writeFlatRagHouse();
    sendJson(res, {
      code: 0,
      stdout: `Flat RAG house updated: ${path.relative(repoRoot, flatRagHousePath)}`,
      stderr: "",
      house,
    });
    return true;
  }
};
