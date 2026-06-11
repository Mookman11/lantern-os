/**
 * Dream Chat API Routes
 * Conversation management, file upload, message history
 */

const fs = require("fs");
const path = require("path");

const DATA_DIR = path.join(__dirname, "..", "..", "data", "conversations");

// Ensure data directory exists
if (!fs.existsSync(DATA_DIR)) {
  fs.mkdirSync(DATA_DIR, { recursive: true });
}

module.exports = async function dreamsRoutes(req, res, url, deps) {
  const { sendJson, collectRequestBody } = deps;

  // GET /api/dreams/conversations — list all conversations
  if (url.pathname === "/api/dreams/conversations" && req.method === "GET") {
    try {
      const files = fs.readdirSync(DATA_DIR).filter(f => f.endsWith(".jsonl"));
      const convos = files.map(f => {
        const data = fs.readFileSync(path.join(DATA_DIR, f), "utf8");
        const lines = data.trim().split("\n");
        const first = lines[0] ? JSON.parse(lines[0]) : {};
        const last = lines[lines.length - 1] ? JSON.parse(lines[lines.length - 1]) : {};
        return {
          id: f.replace(".jsonl", ""),
          name: first.text?.slice(0, 50) || "Untitled",
          messageCount: lines.length,
          created: first.timestamp || 0,
          updated: last.timestamp || 0,
        };
      });
      sendJson(res, { conversations: convos.sort((a, b) => b.updated - a.updated) }, 200);
    } catch (err) {
      sendJson(res, { error: err.message }, 500);
    }
    return true;
  }

  // GET /api/dreams/conversations/:id — get one conversation with messages
  if (url.pathname.startsWith("/api/dreams/conversations/") && req.method === "GET") {
    try {
      const id = url.pathname.split("/").pop();
      const filePath = path.join(DATA_DIR, `${id}.jsonl`);
      if (!fs.existsSync(filePath)) {
        sendJson(res, { error: "Conversation not found" }, 404);
        return true;
      }
      const data = fs.readFileSync(filePath, "utf8");
      const messages = data.trim().split("\n").map(line => line ? JSON.parse(line) : null).filter(Boolean);
      sendJson(res, { id, messages }, 200);
    } catch (err) {
      sendJson(res, { error: err.message }, 500);
    }
    return true;
  }

  // POST /api/dreams/conversations — create new conversation (returns new ID)
  if (url.pathname === "/api/dreams/conversations" && req.method === "POST") {
    try {
      const id = `convo-${Date.now()}`;
      const filePath = path.join(DATA_DIR, `${id}.jsonl`);
      fs.writeFileSync(filePath, "");
      sendJson(res, { id, created: true }, 201);
    } catch (err) {
      sendJson(res, { error: err.message }, 500);
    }
    return true;
  }

  // POST /api/dreams/conversations/:id/messages — add message to conversation
  if (url.pathname.match(/^\/api\/dreams\/conversations\/[^/]+\/messages$/) && req.method === "POST") {
    try {
      const id = url.pathname.split("/")[4];
      const body = await collectRequestBody(req);
      const payload = body ? JSON.parse(body) : {};

      const filePath = path.join(DATA_DIR, `${id}.jsonl`);
      const msg = {
        ...payload,
        timestamp: Date.now(),
      };
      fs.appendFileSync(filePath, JSON.stringify(msg) + "\n");
      sendJson(res, { ok: true, messageId: msg.timestamp }, 200);
    } catch (err) {
      sendJson(res, { error: err.message }, 500);
    }
    return true;
  }

  // DELETE /api/dreams/conversations/:id — delete a conversation
  if (url.pathname.match(/^\/api\/dreams\/conversations\/[^/]+$/) && req.method === "DELETE") {
    try {
      const id = url.pathname.split("/").pop();
      const filePath = path.join(DATA_DIR, `${id}.jsonl`);
      if (fs.existsSync(filePath)) {
        fs.unlinkSync(filePath);
      }
      sendJson(res, { ok: true }, 200);
    } catch (err) {
      sendJson(res, { error: err.message }, 500);
    }
    return true;
  }

  // POST /api/dreams/files — upload and process file
  if (url.pathname === "/api/dreams/files" && req.method === "POST") {
    try {
      // Parse multipart form data (simplified)
      const body = await collectRequestBody(req);
      const boundary = req.headers["content-type"]?.split("boundary=")[1];

      if (!boundary || !body) {
        sendJson(res, { error: "Invalid file upload" }, 400);
        return true;
      }

      // Extract file content from multipart
      const parts = body.split(`--${boundary}`);
      const filePart = parts.find(p => p.includes('filename='));

      if (!filePart) {
        sendJson(res, { error: "No file in request" }, 400);
        return true;
      }

      // Extract filename and content
      const filenameMatch = filePart.match(/filename="([^"]+)"/);
      const filename = filenameMatch ? filenameMatch[1] : "upload";
      const contentStart = filePart.indexOf("\r\n\r\n") + 4;
      const contentEnd = filePart.lastIndexOf("\r\n");
      const fileContent = filePart.slice(contentStart, contentEnd);

      // Store file temporarily
      const uploadDir = path.join(DATA_DIR, "uploads");
      if (!fs.existsSync(uploadDir)) {
        fs.mkdirSync(uploadDir, { recursive: true });
      }
      const fileId = `file-${Date.now()}`;
      const filePath = path.join(uploadDir, `${fileId}-${filename}`);
      fs.writeFileSync(filePath, fileContent);

      sendJson(res, {
        ok: true,
        fileId,
        filename,
        size: fileContent.length,
        path: `uploads/${fileId}-${filename}`,
      }, 200);
    } catch (err) {
      sendJson(res, { error: err.message }, 500);
    }
    return true;
  }

  return false;
};
