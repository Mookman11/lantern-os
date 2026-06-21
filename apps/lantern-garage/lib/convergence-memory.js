"use strict";
// #848 — Memory write-back (Converge → Remember, live serving path).
//
// The live serving path already emits a ConvergenceRecord (convergence-records.js),
// but a served kernel continuation never folded its converged result BACK into the
// append-only memory log — so the Remember stage couldn't retrieve what the loop just
// learned. This closes that wire in the live request path (not the offline batch).
//
// The emitted row mirrors src/convergence/objects.py::Memory.to_jsonl() EXACTLY so the
// Python Convergence Core (Kernel._load_memory_from_disk) can load it. The cross-language
// schema is locked by tests/test_convergence_memory_writeback.py. Write-back is
// best-effort and never throws — a failed memory write must never break a chat reply.

const path = require("path");
const { appendJsonlQueued } = require("./file-queue");

// Kernel default (kernel.py: memory_path="data/memory.jsonl"); __dirname is
// apps/lantern-garage/lib, so ../../.. is the repo root.
const MEMORY_REL = "data/memory.jsonl";
const MEMORY_PATH = path.resolve(__dirname, "..", "..", "..", MEMORY_REL);

function _id() {
  return `mem-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 8)}`;
}

/**
 * Append-only memory write-back. Returns the memory row, or null on failure.
 * @param {object} o
 * @param {string} o.source            which tool/agent/observation produced this
 * @param {object} o.content           the actual data (free-form object)
 * @param {number} [o.confidence]      0..1 (clamped)
 * @param {string[]} [o.evidence_ids]  supporting record/memory ids (e.g. the
 *        ConvergenceRecord this continuation emitted — grounds the write-back)
 */
async function writeMemory({
  source = "unknown",
  content = {},
  confidence = 0.5,
  evidence_ids = [],
} = {}) {
  try {
    const memory = {
      id: _id(),
      // Kernel._load_memory_from_disk parses with a RAW datetime.fromisoformat()
      // (no "Z" stripping, unlike the records loader). Emit an explicit-offset ISO
      // string so it loads on pre-3.11 Pythons too.
      timestamp: new Date().toISOString().replace("Z", "+00:00"),
      source: String(source || "unknown"),
      confidence: Math.max(0, Math.min(1, Number(confidence) || 0)),
      content: content && typeof content === "object" ? content : { value: content },
      evidence_ids: Array.isArray(evidence_ids) ? evidence_ids.map(String) : [],
    };
    await appendJsonlQueued(MEMORY_PATH, memory);
    return memory;
  } catch (err) {
    console.error("[convergence-memory] write-back failed (non-fatal):", err && err.message);
    return null;
  }
}

module.exports = { writeMemory, MEMORY_PATH, MEMORY_REL };
