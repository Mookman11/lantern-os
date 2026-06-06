/**
 * cloud-server.js — Railway / Render / cloud deploy entry point
 *
 * Thin wrapper over server.js that enforces cloud defaults:
 *   PORT env var → binds 0.0.0.0 (Railway sets this automatically)
 *   LANTERN_REPO_ROOT env var → override for cloud filesystem layout
 *
 * Cloud runtime adds:
 *   - Security headers on every response (X-Content-Type-Options,
 *     Referrer-Policy, X-Frame-Options, Permissions-Policy)
 *   - Write-method bounds on sensitive endpoints
 *   - Explicit AWS action-holding for local-only routes
 */

const http = require("http");
const fs = require("fs");
const path = require("path");

// Load .env.local then .env from repo root (two levels up from apps/lantern-garage/)
const candidateEnvFiles = [
  path.resolve(__dirname, "..", "..", ".env.local"),
  path.resolve(__dirname, "..", "..", ".env"),
];
for (const envPath of candidateEnvFiles) {
  if (!fs.existsSync(envPath)) continue;
  fs.readFileSync(envPath, "utf8").split("\n").forEach((line) => {
    const m = line.match(/^([A-Z0-9_]+)\s*=\s*(.*)$/);
    if (m && !process.env[m[1]]) process.env[m[1]] = m[2].replace(/^['"]/g, "").replace(/['"]$/g, "");
  });
}

const { sendJson, sendFile, sendHtml, collectRequestBody } = require("./lib/http-utils");
const { readJson, readJsonl, appendJsonlQueued } = require("./lib/file-queue");
const { getStatus, getReadiness, getMiningLabStatus, getActionCapabilities, getOperatorFeedbackMemory, getAccessModel, getCloudMirrorStatus } = require("./lib/status");
const { readConversationLog, normalizeConversationEntry, appendConversationEntry, appendExternalRagItem, readOperatorQueue } = require("./lib/conversation-store");
const { buildFlatRagHouse, writeFlatRagHouse } = require("./lib/rag-house");
const { runPowerShell } = require("./lib/powershell");
const { renderMarkdownDocument } = require("./lib/markdown-render");
const { normalizeDreamerUser, dreamerNotebookPath, appendDreamerEntry, readDreamerNotebook, readRecentDreams } = require("./lib/dreamer-store");
const { dreamChatReply, AGENT_PERSONAS, DREAM_DOORS, selectAgent } = require("./lib/dream-chat");
const { unifiedAgentGreet, unifiedAgentHealth, unifiedAgentInspect } = require("./lib/unified-agent");
const { handleStreamChat } = require("./lib/stream-chat");

const repoRoot = path.resolve(__dirname, "..", "..");
const publicRoot = path.join(__dirname, "public");
const port = Number(process.env.PORT || "8080"); // Railway injects PORT; default 8080 for other clouds
const host = "0.0.0.0";
const conversationLogPath = path.join(repoRoot, "data", "conversations", "garage-conversations.jsonl");
const flatRagHousePath = path.join(repoRoot, "data", "rag-house", "flat-rag-house-latest.json");
const flatRagHouseManifestPath = path.join(repoRoot, "manifests", "FLAT-RAG-HOUSE-LATEST.md");
const operatorNotesPath = path.join(repoRoot, "data", "operator-notes", "notes.jsonl");
const cloudMirrorsPath = path.join(repoRoot, "manifests", "cloud-mirrors.json");
const cloudMirrorUrls = process.env.LANTERN_CLOUD_MIRROR_URLS || "";
const maxConversationTextLength = 4000;
const maxDreamerTextLength = 2000;

// Shared dependency bundle passed to every route module
const deps = {
  fs, path,
  sendJson, sendFile, sendHtml, collectRequestBody,
  readJson, readJsonl, appendJsonlQueued,
  getStatus, getReadiness, getMiningLabStatus, getActionCapabilities,
  getOperatorFeedbackMemory, getAccessModel, getCloudMirrorStatus,
  readConversationLog, normalizeConversationEntry, appendConversationEntry,
  appendExternalRagItem, readOperatorQueue,
  buildFlatRagHouse, writeFlatRagHouse,
  runPowerShell, renderMarkdownDocument,
  normalizeDreamerUser, dreamerNotebookPath, appendDreamerEntry,
  readDreamerNotebook, readRecentDreams,
  dreamChatReply, AGENT_PERSONAS, DREAM_DOORS, selectAgent,
  unifiedAgentGreet, unifiedAgentHealth, unifiedAgentInspect,
  handleStreamChat,
  repoRoot, publicRoot,
  conversationLogPath, flatRagHousePath, flatRagHouseManifestPath,
  operatorNotesPath, cloudMirrorsPath, cloudMirrorUrls,
  maxConversationTextLength, maxDreamerTextLength,
  "__dirname": __dirname,
};

const routes = [
  require("./routes/status"),
  require("./routes/rag"),
  require("./routes/operator"),
  require("./routes/files"),
  require("./routes/dreamer"),
  require("./routes/dream"),
  require("./routes/keystone"),
  require("./routes/surfaces"),
];

async function route(req, res) {
  const url = new URL(req.url, `http://${req.headers.host}`);

  // Browser hardening headers on every cloud response
  res.setHeader("X-Content-Type-Options", "nosniff");
  res.setHeader("Referrer-Policy", "no-referrer");
  res.setHeader("X-Frame-Options", "DENY");
  res.setHeader("Permissions-Policy", "camera=(), microphone=(), geolocation=()");

  // Cloud write-method bounds: block POST on sensitive endpoints
  if (url.pathname === "/api/chat" && req.method === "POST") {
    return sendJson(res, { error: "cloud_read_only_method_not_allowed", message: "Action held in AWS cloud mode." }, 403);
  }
  if (url.pathname === "/api/command" && req.method === "POST") {
    return sendJson(res, { error: "cloud_read_only_method_not_allowed", message: "Action held in AWS cloud mode." }, 403);
  }
  if (url.pathname.startsWith("/api/actions/") && req.method === "POST") {
    return sendJson(res, { error: "cloud_read_only_method_not_allowed", message: "local orchestrator queue is not exposed on AWS cloud mode" }, 403);
  }

  // Cloud health endpoint
  if (url.pathname === "/health") {
    return sendJson(res, { status: "ok", mode: "cloud", port, host });
  }

  // Cloud outreach endpoint
  if (url.pathname === "/outreach") {
    return sendFile(res, path.join(publicRoot, "outreach.html"));
  }

  if (req.method === "OPTIONS") {
    res.writeHead(204, {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type",
      "Cache-Control": "no-store",
      "X-Content-Type-Options": "nosniff",
      "Referrer-Policy": "no-referrer",
      "X-Frame-Options": "DENY",
      "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
    });
    res.end();
    return;
  }

  for (const handler of routes) {
    const handled = await handler(req, res, url, deps);
    if (handled) return;
  }
}

const server = http.createServer((req, res) => {
  route(req, res).catch((error) => {
    if (res.headersSent) {
      console.error("Route error after response sent:", error.message);
      return;
    }
    sendJson(res, { error: error.message }, 500);
  });
});

server.on("error", (error) => {
  if (error.code === "EADDRINUSE") {
    console.error(`Lantern Garage cloud port ${port} is already in use.`);
    process.exitCode = 1;
    return;
  }
  throw error;
});

server.listen(port, host, () => {
  console.log(`Lantern Garage cloud app listening on ${host}:${port}`);
});
