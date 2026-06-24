"use strict";
/**
 * tool-runner.js — one canonical tool registry for the local Σ₀ Ouro coder in chat.
 * ADR-0008: capabilities are Tools in this registry — advertised == executed == trainable.
 *
 * CONSISTENCY RULE (how Claude Code / OpenAI / any tool-calling LLM works): a tool is
 * defined ONCE — name + input_schema + executor + policy — and that single definition
 * both (a) renders the prompt preamble and (b) dispatches execution. The names here are
 * the EXACT names the adapter was trained on (harvested Claude Code sessions: Read, LS,
 * Glob, Grep, Bash, PowerShell, Write, Edit), so advertised == emitted == executed.
 * No name canonicalization, no input-key aliasing, no per-tool mappers — those were
 * patches over a vocabulary mismatch (an invented read_file/list_dir set). Removed.
 *
 * The only adapter we keep is parseToolCall(): the local model emits a <tool_call> as
 * free text rather than a native tool_use block, so the proxy parses it (with light
 * JSON repair). That's the equivalent of the API layer parsing model output — not a hack.
 *
 * POLICY (per-tool, enforced uniformly):
 *   read     (Read/LS/Glob/Grep)        — execute, repo-sandboxed.
 *   shell    (Bash/PowerShell)          — execute via the SHARED allowlist + safe-exec
 *                                          (lib/command-allowlist + lib/safe-exec); OPERATOR only.
 *   mutating (Write/Edit)               — execute, repo-sandboxed; OPERATOR only.
 * The master on/off switch (CHAT_TOOL_EXEC) is enforced by the caller (stream-chat).
 */
const fs = require("fs");
const path = require("path");
const https = require("https");
const http = require("http");
const { tokenizeCommand, safeExec } = require("./safe-exec");
const { resolveCommand } = require("./command-allowlist");
const { webSearchMcp } = require("./web-search-client");
const { workspaceWrite, workspaceRead, workspaceList, getWorkspaceRoot } = require("./user-workspace");
const { createDocument, listTemplates } = require("./doc-generator");

const REPO = path.resolve(__dirname, "..", "..", "..");
const MAX_OUT = 4000;
const SKIP_DIR = /(^|[\\/])(\.git|node_modules|\.venv|\.venv-train|hf-cache)([\\/]|$)/;
const FETCH_TIMEOUT_MS = 10000;
const FETCH_MAX_BYTES = 512 * 1024; // 512 KB raw HTML cap

// Allowed URL schemes for web_fetch — no file://, no internal network ranges.
const _SAFE_URL = /^https?:\/\/(?!(?:127\.|10\.|192\.168\.|172\.(?:1[6-9]|2\d|3[01])\.|\[::1\]))/i;

function _fetchUrl(rawUrl) {
  return new Promise((resolve, reject) => {
    let url;
    try { url = new URL(rawUrl); } catch { return reject(new Error(`invalid URL: ${rawUrl}`)); }
    if (!_SAFE_URL.test(rawUrl)) return reject(new Error("URL not allowed (must be public http/https)"));
    const mod = url.protocol === "https:" ? https : http;
    const req = mod.get({ hostname: url.hostname, port: url.port || undefined, path: url.pathname + url.search, headers: { "User-Agent": "LanternOS/1.0 (+fetch)" } }, (res) => {
      if (res.statusCode >= 300 && res.statusCode < 400 && res.headers.location) {
        return resolve(_fetchUrl(res.headers.location)); // follow one redirect
      }
      let buf = "";
      res.on("data", (chunk) => { if (buf.length < FETCH_MAX_BYTES) buf += chunk; });
      res.on("end", () => resolve({ status: res.statusCode, body: buf }));
    });
    req.setTimeout(FETCH_TIMEOUT_MS, () => { req.destroy(); reject(new Error("timeout")); });
    req.on("error", reject);
  });
}

// Strip HTML tags + collapse whitespace → readable plain text.
function _htmlToText(html) {
  return html
    .replace(/<script[\s\S]*?<\/script>/gi, "")
    .replace(/<style[\s\S]*?<\/style>/gi, "")
    .replace(/<[^>]+>/g, " ")
    .replace(/&nbsp;/gi, " ").replace(/&amp;/gi, "&").replace(/&lt;/gi, "<").replace(/&gt;/gi, ">").replace(/&quot;/gi, '"')
    .replace(/\s{2,}/g, " ")
    .trim();
}

function _safe(p) {
  const abs = path.resolve(REPO, String(p == null ? "." : p));
  if (abs !== REPO && !abs.startsWith(REPO + path.sep)) throw new Error("path escapes repo");
  return abs;
}

function _globToRe(glob) {
  let re = String(glob || "*").replace(/[.+^${}()|[\]\\]/g, "\\$&");
  re = re.replace(/\*\*/g, "\u0000").replace(/\*/g, "[^/]*").replace(/\u0000/g, ".*").replace(/\?/g, ".");
  return new RegExp("^" + re + "$", "i");
}

function _runShell(command) {
  const cmd = String(command || "").trim();
  const resolved = resolveCommand(cmd);
  if (!resolved) { const e = new Error(`command not allowlisted: ${cmd}`); e.reason = "unsafe"; throw e; }
  return safeExec(tokenizeCommand(resolved), {
    cwd: REPO, encoding: "utf-8", timeout: 30000, maxBuffer: 1024 * 1024,
    env: { ...process.env, GIT_TERMINAL_PROMPT: "0" },
  });
}

// ── canonical registry (names/schemas == training == Claude Code) ───────────────
const REGISTRY = {
  Read: {
    policy: "read", desc: "Read a file from the filesystem (repo-relative).",
    schema: { type: "object", properties: { file_path: { type: "string" }, limit: { type: "integer" } }, required: ["file_path"] },
    run(i) {
      const p = _safe(i.file_path);
      if (!fs.statSync(p).isFile()) return `[not a file: ${i.file_path}]`;
      const n = Math.max(1, Math.min(400, parseInt(i.limit, 10) || 80));
      return fs.readFileSync(p, "utf8").split("\n").slice(0, n).join("\n");
    },
  },
  LS: {
    policy: "read", desc: "List the entries of a directory (repo-relative).",
    schema: { type: "object", properties: { path: { type: "string" } }, required: ["path"] },
    run(i) {
      const p = _safe(i.path || ".");
      if (!fs.statSync(p).isDirectory()) return `[not a directory: ${i.path}]`;
      const e = fs.readdirSync(p).sort();
      return `${e.length} entries:\n` + e.slice(0, 100).join("\n");
    },
  },
  Glob: {
    policy: "read", desc: "Find files matching a glob pattern (e.g. **/*.js).",
    schema: { type: "object", properties: { pattern: { type: "string" }, path: { type: "string" } }, required: ["pattern"] },
    run(i) {
      const re = _globToRe(i.pattern || "*");
      const hits = [];
      (function walk(d) {
        if (hits.length > 500 || SKIP_DIR.test(d)) return;
        let items; try { items = fs.readdirSync(d, { withFileTypes: true }); } catch { return; }
        for (const it of items) {
          const full = path.join(d, it.name);
          if (it.isDirectory()) walk(full);
          else { const rel = path.relative(REPO, full).replace(/\\/g, "/"); if (re.test(rel) || re.test(it.name)) hits.push(rel); }
        }
      })(_safe(i.path || "."));
      return `${hits.length} match(es) for ${i.pattern}:\n` + hits.slice(0, 100).join("\n");
    },
  },
  Grep: {
    policy: "read", desc: "Search file contents for a regular expression.",
    schema: { type: "object", properties: { pattern: { type: "string" }, path: { type: "string" } }, required: ["pattern"] },
    run(i) {
      const re = new RegExp(String(i.pattern || ""), "i");
      const out = [];
      const scan = (f) => { try { fs.readFileSync(f, "utf8").split("\n").forEach((ln, n) => { if (out.length < 80 && re.test(ln)) out.push(`${path.relative(REPO, f).replace(/\\/g, "/")}:${n + 1}: ${ln.trim().slice(0, 160)}`); }); } catch {} };
      const p = _safe(i.path || ".");
      if (fs.statSync(p).isFile()) scan(p);
      else for (const it of fs.readdirSync(p, { withFileTypes: true })) { if (it.isFile() && out.length < 80) scan(path.join(p, it.name)); }
      return out.length ? out.join("\n") : "[no matches]";
    },
  },
  Bash: {
    policy: "shell", desc: "Run an allowlisted shell command (git/tests/file-reads). Operator only.",
    schema: { type: "object", properties: { command: { type: "string" } }, required: ["command"] },
    run(i) { return _runShell(i.command); },
  },
  PowerShell: {
    policy: "shell", desc: "Run an allowlisted command (same allowlist as Bash). Operator only.",
    schema: { type: "object", properties: { command: { type: "string" } }, required: ["command"] },
    run(i) { return _runShell(i.command); },
  },
  Write: {
    policy: "mutating", desc: "Write a file (repo-relative), overwriting it. Operator only.",
    schema: { type: "object", properties: { file_path: { type: "string" }, content: { type: "string" } }, required: ["file_path", "content"] },
    run(i) { const p = _safe(i.file_path); fs.writeFileSync(p, String(i.content == null ? "" : i.content), "utf8"); return `wrote ${i.file_path} (${String(i.content || "").length} bytes)`; },
  },
  Edit: {
    policy: "mutating", desc: "Replace an exact unique string in a file (repo-relative). Operator only.",
    schema: { type: "object", properties: { file_path: { type: "string" }, old_string: { type: "string" }, new_string: { type: "string" } }, required: ["file_path", "old_string", "new_string"] },
    run(i) {
      const p = _safe(i.file_path);
      const src = fs.readFileSync(p, "utf8");
      const parts = src.split(String(i.old_string));
      if (parts.length === 1) return `[old_string not found in ${i.file_path}]`;
      if (parts.length > 2) return `[old_string is not unique in ${i.file_path} (${parts.length - 1} matches)]`;
      fs.writeFileSync(p, parts.join(String(i.new_string == null ? "" : i.new_string)), "utf8");
      return `edited ${i.file_path}`;
    },
  },

  // ── ADR-0008 capability tools ───────────────────────────────────────────────
  web_search: {
    policy: "read",
    desc: "Search the web for real-time information. Returns top results with title, URL, and snippet. Each result is cited per the Σ₀ External Reality Rule.",
    schema: {
      type: "object",
      properties: {
        query: { type: "string", description: "The search query" },
        max_results: { type: "integer", description: "Max results to return (1–10, default 5)" },
      },
      required: ["query"],
    },
    async run(i) {
      const query = String(i.query || "").trim();
      if (!query) return "[error: query is required]";
      const maxResults = Math.max(1, Math.min(10, parseInt(i.max_results, 10) || 5));
      const res = await webSearchMcp(query, maxResults);
      if (!res || !res.success) return `[web_search failed: ${res && res.error ? res.error : "MCP unavailable"}]`;
      const results = (res.results || []).slice(0, maxResults);
      if (!results.length) return `[no results for: ${query}]`;
      const lines = [`web_search("${query}") — ${results.length} result(s):\n`];
      results.forEach((r, idx) => {
        lines.push(`[${idx + 1}] ${r.title}`);
        lines.push(`    url: ${r.url}`);
        if (r.snippet) lines.push(`    snippet: ${r.snippet}`);
      });
      return lines.join("\n");
    },
  },

  web_fetch: {
    policy: "read",
    desc: "Fetch the text content of a public URL. HTML is stripped to readable plain text. Use for reading web pages, documentation, or articles. No internal/private IPs allowed.",
    schema: {
      type: "object",
      properties: {
        url: { type: "string", description: "The public https:// or http:// URL to fetch" },
        max_chars: { type: "integer", description: "Max characters of content to return (default 3000)" },
      },
      required: ["url"],
    },
    async run(i) {
      const url = String(i.url || "").trim();
      if (!url) return "[error: url is required]";
      const maxChars = Math.max(200, Math.min(MAX_OUT, parseInt(i.max_chars, 10) || 3000));
      let fetched;
      try { fetched = await _fetchUrl(url); }
      catch (e) { return `[web_fetch error: ${e.message}]`; }
      if (fetched && fetched.then) fetched = await fetched;
      const text = _htmlToText(fetched.body || "");
      const excerpt = text.length > maxChars ? text.slice(0, maxChars) + "\n…[truncated]" : text;
      return `web_fetch(${url}) — HTTP ${fetched.status}\n\n${excerpt}`;
    },
  },

  // ── ADR-0008 user workspace tools ──────────────────────────────────────────
  workspace_write: {
    policy: "mutating",
    desc: "Write a file to the user workspace (~/.keystone/workspace/). Use for saving user artifacts: resumes, cover letters, documents. Path must be relative, no .. escapes. Operator only.",
    schema: {
      type: "object",
      properties: {
        path: { type: "string", description: "Workspace-relative path, e.g. 'resumes/my-resume.md'" },
        content: { type: "string", description: "File content to write" },
      },
      required: ["path", "content"],
    },
    run(i) {
      const abs = workspaceWrite(String(i.path || ""), String(i.content || ""));
      return `wrote workspace:${i.path} (${String(i.content || "").length} bytes)\nfull path: ${abs}`;
    },
  },

  workspace_read: {
    policy: "read",
    desc: "Read a file from the user workspace (~/.keystone/workspace/). Path must be relative.",
    schema: {
      type: "object",
      properties: {
        path: { type: "string", description: "Workspace-relative path to read" },
      },
      required: ["path"],
    },
    run(i) {
      const content = workspaceRead(String(i.path || ""));
      return content.length > MAX_OUT ? content.slice(0, MAX_OUT) + "\n…[truncated]" : content;
    },
  },

  workspace_list: {
    policy: "read",
    desc: "List files and directories in the user workspace (~/.keystone/workspace/) or a subdirectory.",
    schema: {
      type: "object",
      properties: {
        path: { type: "string", description: "Workspace-relative directory to list (default: root)" },
      },
      required: [],
    },
    run(i) {
      const entries = workspaceList(String(i.path || ""));
      const root = getWorkspaceRoot();
      if (!entries.length) return `workspace:${i.path || "/"} is empty\nroot: ${root}`;
      const lines = [`workspace:${i.path || "/"} — ${entries.length} entries (root: ${root})`];
      entries.forEach((e) => lines.push(`  ${e.type === "dir" ? "[dir]" : "[file]"} ${e.name}${e.type === "file" ? ` (${e.size}B)` : ""}`));
      return lines.join("\n");
    },
  },

  // ── ADR-0008 document generation (#1097) ────────────────────────────────────
  create_document: {
    policy: "mutating",
    desc: 'Generate a document from a template and save it to the user workspace. Templates: "resume", "cover_letter". Pass structured fields matching the template. Returns the workspace path of the created file. Operator only.',
    schema: {
      type: "object",
      properties: {
        template: { type: "string", description: '"resume" or "cover_letter"' },
        fields: { type: "object", description: "Template-specific fields (name, email, experience, etc.)" },
        output_path: { type: "string", description: "Optional workspace-relative output path (auto-generated if omitted)" },
      },
      required: ["template", "fields"],
    },
    run(i) {
      if (!i.template) return "[error: template is required]";
      if (!i.fields || typeof i.fields !== "object") return "[error: fields must be an object]";
      try {
        const result = createDocument(String(i.template), i.fields, i.output_path || null);
        return [
          `created ${result.template}: workspace:${result.path}`,
          `full path: ${result.fullPath}`,
          `size: ${result.byteLength} bytes`,
          "",
          "--- preview (first 500 chars) ---",
          result.content.slice(0, 500) + (result.content.length > 500 ? "\n…" : ""),
        ].join("\n");
      } catch (e) {
        const tmplList = listTemplates().map((t) => `  ${t.name}: ${t.description}`).join("\n");
        return `[create_document error: ${e.message}]\n\nAvailable templates:\n${tmplList}`;
      }
    },
  },
};

const TOOL_NAMES = Object.keys(REGISTRY);

// Match Python json.dumps() default separators (", " / ": ") so this preamble is
// BYTE-identical to the bridge's _render_tools (scripts/ouro_anthropic_bridge.py), which
// the FC training corpus is generated through. Train/serve parity is the #1 FC rule —
// a model trained on the bridge format must see the bridge format here too.
function _pyJson(o) {
  if (Array.isArray(o)) return "[" + o.map(_pyJson).join(", ") + "]";
  if (o && typeof o === "object") return "{" + Object.keys(o).map((k) => JSON.stringify(k) + ": " + _pyJson(o[k])).join(", ") + "}";
  return JSON.stringify(o);
}

function renderToolPreamble() {
  const lines = [
    "You can use tools. To answer the user directly, reply in plain text.",
    "When you need a tool, respond with EXACTLY ONE tool call on a SINGLE LINE, nothing else, in this exact format (no code fences, no blank lines):",
    '<tool_call>{"name": "TOOL_NAME", "input": {"ARG": "VALUE"}}</tool_call>',
    'Rules: "name" must be one of the tools below, spelled exactly. "input" is a JSON object of arguments (use {} if none). Double quotes only, no trailing commas. Emit the call and STOP; do not explain it. Only call a tool if needed.',
    "",
    "Available tools:",
  ];
  for (const name of TOOL_NAMES) {
    const t = REGISTRY[name];
    const ex = {}; (t.schema.required || []).slice(0, 2).forEach((k) => { ex[k] = "..."; });
    lines.push(`Tool: ${name}`);
    lines.push(`Description: ${t.desc}`);
    lines.push(`Input (JSON schema): ${JSON.stringify(t.schema)}`);
    lines.push(`Example: <tool_call>${_pyJson({ name, input: ex })}</tool_call>`);
  }
  lines.push("");
  lines.push("Remember: plain text OR exactly one single-line <tool_call>...</tool_call>. Never both.");
  return lines.join("\n");
}

/**
 * Execute a parsed tool call under the policy.
 * @param {string} name  canonical tool name the model emitted
 * @param {object} input arguments
 * @param {{operator?:boolean}} ctx
 * @returns {{ok:boolean, result?:string, reason?:string, error?:string, policy?:string}}
 */
async function runTool(name, input, ctx = {}) {
  const entry = REGISTRY[name];
  if (!entry) return { ok: false, reason: "unknown", error: `unknown tool '${name}' (available: ${TOOL_NAMES.join(", ")})` };
  if (entry.policy !== "read" && !ctx.operator) {
    return { ok: false, reason: "auth", policy: entry.policy, error: `'${name}' (${entry.policy}) requires operator access` };
  }
  try {
    let out = String((await entry.run(input || {})) || "");
    if (out.length > MAX_OUT) out = out.slice(0, MAX_OUT) + "\n…[truncated]";
    return { ok: true, result: out, policy: entry.policy };
  } catch (e) {
    return { ok: false, reason: e.reason || "error", policy: entry.policy, error: String(e.stderr || e.message || e).slice(0, MAX_OUT) };
  }
}

// ── native Anthropic tool schemas (same single source of truth as the preamble) ──
// Renders the registry as `tools` for the Messages API. Cloud models (Haiku/Sonnet)
// emit native `tool_use` blocks, so they don't need the free-text preamble — they get
// the exact same name + input_schema. When !operator, advertise ONLY read-policy tools
// so the model never emits a shell/mutating call the policy would reject (runTool still
// enforces the policy regardless — this just keeps the advertised surface honest).
function anthropicTools({ operator = false } = {}) {
  return TOOL_NAMES
    .filter((name) => operator || REGISTRY[name].policy === "read")
    .map((name) => ({
      name,
      description: REGISTRY[name].desc,
      input_schema: REGISTRY[name].schema,
    }));
}

// ── parse the model's free-text <tool_call> (light JSON repair; not a vocab hack) ──
function parseToolCall(text) {
  if (!text || typeof text !== "string") return null;
  let inner = null;
  const m = text.match(/<\s*tool_call\s*>/i);
  if (m) {
    let rest = text.slice(m.index + m[0].length);
    const close = rest.search(/<\s*\/\s*tool_call\s*>/i);
    if (close !== -1) rest = rest.slice(0, close);
    inner = _firstJsonObject(rest);
  }
  if (inner === null) { const b = text.match(/\{[\s\S]*?"name"[\s\S]*?\}/); if (b) inner = _firstJsonObject(b[0]); }
  if (inner === null) return null;
  const obj = _loadsLenient(inner);
  if (!obj || typeof obj !== "object") return null;
  const name = typeof obj.name === "string" ? obj.name.trim() : "";
  if (!name) return null;
  const input = (obj.input && typeof obj.input === "object") ? obj.input : {};
  return { name, input };
}

function _firstJsonObject(s) {
  const start = s.indexOf("{");
  if (start === -1) return null;
  let depth = 0, inStr = false, esc = false, q = "";
  for (let i = start; i < s.length; i++) {
    const c = s[i];
    if (inStr) { if (esc) esc = false; else if (c === "\\") esc = true; else if (c === q) inStr = false; continue; }
    if (c === '"' || c === "'") { inStr = true; q = c; }
    else if (c === "{") depth++;
    else if (c === "}") { depth--; if (depth === 0) return s.slice(start, i + 1); }
  }
  return s.slice(start);
}

function _loadsLenient(raw) {
  if (raw == null) return null;
  raw = String(raw).trim();
  try { return JSON.parse(raw); } catch {}
  let r = raw.replace(/,\s*([}\]])/g, "$1");           // trailing commas
  try { return JSON.parse(r); } catch {}
  r = r.replace(/\\(?!["\\/bfnrtu])/g, "\\\\");         // invalid escapes -> literal backslash
  try { return JSON.parse(r); } catch {}
  return null;
}

module.exports = { parseToolCall, runTool, renderToolPreamble, anthropicTools, REGISTRY, TOOL_NAMES };
