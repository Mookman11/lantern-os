"use strict";
/**
 * Self-distillation flywheel as an observable product (#1421).
 *
 * The flywheel: every local→cloud escalation is a gap the local model couldn't close —
 * mine those as a training corpus, retrain, and the local model closes more of the gap
 * over time. This makes that loop OBSERVABLE: the local model's capability trajectory
 * (pass@1 over time), how much of the gap-to-target it has closed, the corpus mined from
 * escalations, and whether escalations are trending down (the flywheel turning).
 *
 * Pure aggregation (no I/O), deterministic, testable. Reads the eval leaderboard +
 * router-gate decisions the system already appends.
 */
const fs = require("fs");
const path = require("path");

const DEFAULT_REPO_ROOT = path.resolve(__dirname, "../../..");
const WEEK_MS = 7 * 86_400_000;
const LOCAL_RE = /ouro|ollama|qwen|keystone|lantern|local|sigma0|cached|harvest/i;

// Leaderboard `ts` is sometimes a unix-seconds string, sometimes ISO. Normalize to ms.
function _ms(ts) {
  if (ts == null) return 0;
  const s = String(ts);
  if (/^\d{9,11}$/.test(s)) return parseInt(s, 10) * 1000;   // unix seconds
  return Date.parse(s) || 0;
}
const round = (x, p = 3) => Math.round(x * Math.pow(10, p)) / Math.pow(10, p);

function localSeries(leaderboard) {
  return (leaderboard || [])
    .filter((r) => r && LOCAL_RE.test(String(r.engine || r.base_model || "")) && typeof r["pass@1"] === "number")
    .map((r) => ({ ms: _ms(r.ts), pass1: r["pass@1"], n: r.n || 0, engine: r.engine, benchmark: r.benchmark }))
    .filter((r) => r.ms > 0)
    .sort((a, b) => a.ms - b.ms);
}

function trend(recent, prior) {
  if (prior === 0) return recent > 0 ? "rising" : "flat";
  const r = recent / prior;
  return r >= 1.2 ? "rising" : (r <= 0.8 ? "falling" : "stable");
}

/**
 * @param {Array} leaderboard  eval rows ({ ts, engine, "pass@1", n, ... })
 * @param {Array} decisions    router-gate decisions ({ timestamp, escalate, ... })
 * @param {object} opts        { nowMs, windowMs=7d, target=0.7 }
 */
function flywheelStats(leaderboard, decisions, opts = {}) {
  const nowMs = opts.nowMs != null ? opts.nowMs : Date.now();
  const windowMs = opts.windowMs || WEEK_MS;
  const target = opts.target != null ? opts.target : 0.7;     // the capability the gap is measured against

  const series = localSeries(leaderboard);
  const localStart = series.length ? series[0].pass1 : null;
  const localNow = series.length ? series[series.length - 1].pass1 : null;
  const bestEver = series.length ? Math.max(...series.map((s) => s.pass1)) : null;
  const improvement = (localStart != null && localNow != null) ? round(localNow - localStart) : null;
  // How much of the start→target gap the local model has closed.
  const gapClosedPct = (localStart != null && localNow != null && target > localStart)
    ? round(Math.max(0, Math.min(1, (localNow - localStart) / (target - localStart))), 3) : null;
  const remainingGap = localNow != null ? round(Math.max(0, target - localNow)) : null;

  // Corpus: each escalation is a distillation candidate (a gap the local model couldn't close).
  const esc = (decisions || []).filter((d) => d && d.escalate === true);
  const escMs = (d) => _ms(d.timestamp || d.ts);
  const recentEsc = esc.filter((d) => escMs(d) >= nowMs - windowMs);
  const priorEsc = esc.filter((d) => escMs(d) >= nowMs - 2 * windowMs && escMs(d) < nowMs - windowMs);
  const escTrend = trend(recentEsc.length, priorEsc.length);

  const verdict = series.length < 2
    ? "Not enough eval history yet to chart the flywheel — keep logging eval runs."
    : improvement > 0.01
    ? `Flywheel is turning: local pass@1 rose ${Math.round(improvement * 100)} pts (${gapClosedPct != null ? Math.round(gapClosedPct * 100) + "% of the gap to target closed" : "trending up"}).`
    : improvement < -0.01
    ? `Local capability slipped ${Math.round(Math.abs(improvement) * 100)} pts since the first eval — retraining/regression to investigate.`
    : "Local capability is flat — the corpus may need fresh escalation data or a retrain.";

  return {
    target,
    localStart, localNow, bestEver, improvement, gapClosedPct, remainingGap,
    corpusSize: esc.length, corpusThisWeek: recentEsc.length,
    escalationTrend: escTrend,
    evalRuns: series.length,
    series: series.map((s) => ({ ms: s.ms, pass1: s.pass1 })),
    verdict,
    status: series.length ? "ok" : "insufficient_data",
  };
}

function readLeaderboard(root) { return _readJsonl(path.join(root || DEFAULT_REPO_ROOT, "data", "eval", "leaderboard.jsonl")); }
function readDecisions(root) { return _readJsonl(path.join(root || DEFAULT_REPO_ROOT, "data", "router-gate-decisions.jsonl")); }
function _readJsonl(f) {
  try {
    return fs.readFileSync(f, "utf8").split("\n").filter((l) => l.trim())
      .map((l) => { try { return JSON.parse(l); } catch { return null; } }).filter(Boolean);
  } catch { return []; }
}

module.exports = { localSeries, trend, flywheelStats, readLeaderboard, readDecisions };
