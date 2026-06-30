"use strict";
/**
 * Adaptive-compute coder with a visible thinking budget (#1423, Reason stage).
 *
 * Productizes the idea behind Ouro's trained Q-exit gate: spend more recurrent depth on
 * HARD lines and early-exit on boilerplate, then show a compute-spent-vs-confidence meter
 * and the resulting compute saved.
 *
 * HONESTY (Σ₀): this is a deterministic *estimator/visualizer*, not the trained gate. It
 * scores each line's difficulty from surface features, allocates a recurrent-depth budget,
 * models where a confidence-threshold Q-exit would fire, and reports the MEASURED savings
 * for the given input — it does not run an Ouro model or claim a fixed headline number.
 */

const MAX_DEPTH = 8;             // recurrent steps available per line (Ouro-style)
const EXIT_CONFIDENCE = 0.95;    // Q-exit fires once estimated confidence crosses this

// Boilerplate / trivial lines need ~no recurrent depth.
const BOILERPLATE = /^\s*(import |export |from |#|\/\/|\/\*|\*|}|\)|\];?|{|return;|break;|continue;|pass|else\s*{?|use strict)/;
const CONTROL = /\b(if|for|while|switch|case|catch|try|finally|await|yield|reduce|recurs|=>)\b/g;
const OPS = /[+\-*/%<>=!&|^?]+/g;

// Difficulty in [0,1] from surface features: control-flow density, operator density,
// nesting (leading indent), and length. Boilerplate short-circuits to ~0.
function lineDifficulty(line) {
  const raw = String(line || "");
  const trimmed = raw.trim();
  if (!trimmed) return 0;
  if (BOILERPLATE.test(raw) && trimmed.length < 40) return 0.05;
  const indent = (raw.match(/^\s*/)[0] || "").replace(/\t/g, "  ").length;
  const control = (trimmed.match(CONTROL) || []).length;
  const ops = (trimmed.match(OPS) || []).length;
  const len = trimmed.length;
  // weighted, then squashed to [0,1]
  const score = control * 0.22 + ops * 0.05 + Math.min(indent / 4, 3) * 0.06 + Math.min(len / 80, 1) * 0.25;
  return Math.max(0, Math.min(1, Math.round(score * 1000) / 1000));
}

// Recurrent depth budgeted for a difficulty: at least 1, scaling to MAX_DEPTH.
function depthFor(difficulty, maxDepth = MAX_DEPTH) {
  return Math.max(1, Math.min(maxDepth, Math.ceil(difficulty * maxDepth)));
}

// Estimated confidence after `depth` recurrent steps on a line of `difficulty`.
// Easy lines saturate fast; hard lines need more depth. Monotonic non-decreasing in depth.
function confidenceAtDepth(difficulty, depth, maxDepth = MAX_DEPTH) {
  const need = depthFor(difficulty, maxDepth);
  const c = depth >= need ? 1 - 0.04 * (difficulty) : depth / need * (1 - 0.04 * difficulty);
  return Math.max(0, Math.min(1, Math.round(c * 1000) / 1000));
}

// Where would the Q-exit fire for this line? Returns the exit depth (≤ budget) and the
// confidence there. The gate stops as soon as confidence crosses EXIT_CONFIDENCE, else
// runs the full budget.
function qExit(difficulty, opts = {}) {
  const maxDepth = opts.maxDepth || MAX_DEPTH;
  const threshold = opts.exitConfidence || EXIT_CONFIDENCE;
  const budget = depthFor(difficulty, maxDepth);
  for (let d = 1; d <= budget; d++) {
    if (confidenceAtDepth(difficulty, d, maxDepth) >= threshold) {
      return { exitDepth: d, confidence: confidenceAtDepth(difficulty, d, maxDepth), budget };
    }
  }
  return { exitDepth: budget, confidence: confidenceAtDepth(difficulty, budget, maxDepth), budget };
}

// Analyze a code blob: per-line depth/confidence + the aggregate compute-saved meter.
function analyzeCode(code, opts = {}) {
  const maxDepth = opts.maxDepth || MAX_DEPTH;
  const lines = String(code || "").split("\n");
  const rows = lines.map((text, i) => {
    const difficulty = lineDifficulty(text);
    const ex = qExit(difficulty, { maxDepth, exitConfidence: opts.exitConfidence });
    return { n: i + 1, text, difficulty, depth: ex.exitDepth, confidence: ex.confidence };
  });
  const counted = rows.filter((r) => r.text.trim().length > 0);
  const spent = counted.reduce((a, r) => a + r.depth, 0);
  const baseline = counted.length * maxDepth;       // fixed-depth (run every line to MAX_DEPTH)
  const computeSaved = baseline > 0 ? Math.round((1 - spent / baseline) * 1000) / 1000 : null;
  const avgConfidence = counted.length ? Math.round((counted.reduce((a, r) => a + r.confidence, 0) / counted.length) * 1000) / 1000 : null;
  return {
    status: counted.length ? "ok" : "insufficient_data",
    maxDepth, lines: rows.length, codeLines: counted.length,
    computeSpent: spent, computeBaseline: baseline,
    computeSaved,                                    // fraction of recurrent steps avoided
    fidelity: avgConfidence,                         // mean estimated confidence (fidelity proxy)
    rows,
  };
}

module.exports = { MAX_DEPTH, EXIT_CONFIDENCE, lineDifficulty, depthFor, confidenceAtDepth, qExit, analyzeCode };
