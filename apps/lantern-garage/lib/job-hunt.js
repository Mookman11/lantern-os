"use strict";
/**
 * Job hunt that runs itself (#1431).
 *
 * Tracks every application and turns the pile into a recruiting FUNNEL: how many made it
 * applied → screen → interview → offer, the conversion rate at each step, response/ghost
 * rates, and the weekly application pace vs a target. Plus per-application next-actions
 * (follow up after silence, log what a rejection taught you) so the hunt keeps moving.
 *
 * The funnel math + next-action cadence are pure/deterministic; persistence is thin JSONL.
 */
const fs = require("fs");
const path = require("path");
const crypto = require("crypto");

const DEFAULT_REPO_ROOT = path.resolve(__dirname, "../../..");
const DAY_MS = 86_400_000;
const STAGES = ["applied", "screen", "interview", "offer"];   // ordered funnel
const OUTCOMES = ["pending", "rejected", "ghosted", "accepted"];
const stageRank = (s) => Math.max(0, STAGES.indexOf(s));

// Did an application reach AT LEAST `stage` (by its furthest stage, even if later rejected)?
function reached(app, stage) {
  if (app.outcome === "accepted" && stage === "offer") return true;
  return stageRank(app.stage) >= stageRank(stage);
}

function rate(n, d) { return d > 0 ? Math.round((n / d) * 1000) / 1000 : null; }

// The funnel + conversion rates + response/ghost/offer rates + weekly pace.
function funnelStats(apps, opts = {}) {
  const list = (apps || []).filter((a) => a && typeof a === "object");
  const now = opts.nowMs != null ? opts.nowMs : Date.now();
  const total = list.length;
  if (!total) return { total: 0, status: "insufficient_data", funnel: [], target: opts.weeklyTarget || 5, appliedThisWeek: 0 };

  const reachedScreen = list.filter((a) => reached(a, "screen")).length;
  const reachedInterview = list.filter((a) => reached(a, "interview")).length;
  const reachedOffer = list.filter((a) => reached(a, "offer")).length;
  const ghosted = list.filter((a) => a.outcome === "ghosted").length;
  const rejected = list.filter((a) => a.outcome === "rejected").length;
  const accepted = list.filter((a) => a.outcome === "accepted").length;
  const appliedThisWeek = list.filter((a) => (Date.parse(a.appliedAt) || 0) >= now - 7 * DAY_MS).length;

  return {
    total, status: "ok",
    funnel: [
      { stage: "applied", count: total, conversionFromPrev: null },
      { stage: "screen", count: reachedScreen, conversionFromPrev: rate(reachedScreen, total) },
      { stage: "interview", count: reachedInterview, conversionFromPrev: rate(reachedInterview, reachedScreen) },
      { stage: "offer", count: reachedOffer, conversionFromPrev: rate(reachedOffer, reachedInterview) },
    ],
    responseRate: rate(reachedScreen, total),       // got past the initial screen
    ghostRate: rate(ghosted, total),
    offerRate: rate(reachedOffer, total),
    accepted, rejected, ghosted,
    appliedThisWeek, weeklyTarget: opts.weeklyTarget || 5,
  };
}

// What to do next with a single application, given its stage / outcome / age.
function nextAction(app, nowMs) {
  const now = nowMs != null ? nowMs : Date.now();
  const days = Math.max(0, Math.round((now - (Date.parse(app.lastUpdate || app.appliedAt) || now)) / DAY_MS));
  if (app.outcome === "accepted") return { action: "celebrate", text: "Offer accepted — close out the other applications." };
  if (app.outcome === "rejected") return { action: "learn", text: "Rejected — jot down what you'd change next time (the hunt learns from rejections)." };
  if (app.outcome === "ghosted") return { action: "move-on", text: "No reply for a while — mark it ghosted and focus your energy elsewhere." };
  // pending
  if (app.stage === "applied") {
    return days >= 10
      ? { action: "follow-up", text: `Applied ${days} days ago with no response — send one polite follow-up, then move on.` }
      : { action: "wait", text: `Applied ${days} day(s) ago — give it ~10 days before nudging.` };
  }
  if (app.stage === "screen" || app.stage === "interview") {
    return days >= 7
      ? { action: "follow-up", text: `${days} days since the last ${app.stage} contact — follow up to keep momentum.` }
      : { action: "wait", text: `In ${app.stage} (${days}d ago) — prep and wait for their next step.` };
  }
  if (app.stage === "offer") return { action: "decide", text: "You have an offer — evaluate it (try the Decision Journal) and respond." };
  return { action: "review", text: "Review this application." };
}

// ── thin JSONL persistence (local-only) ─────────────────────────────────────────
function _file(root) { return path.join(root || DEFAULT_REPO_ROOT, "data", "job-hunt", "applications.jsonl"); }
function readApps(root) {
  try {
    return fs.readFileSync(_file(root), "utf8").split("\n").filter((l) => l.trim())
      .map((l) => { try { return JSON.parse(l); } catch { return null; } }).filter(Boolean);
  } catch { return []; }
}
function _writeAll(root, apps) {
  const f = _file(root); fs.mkdirSync(path.dirname(f), { recursive: true });
  fs.writeFileSync(f, apps.map((a) => JSON.stringify(a)).join("\n") + (apps.length ? "\n" : ""));
}
function addApp(root, input, nowIso) {
  const company = String(input.company || "").trim();
  const role = String(input.role || "").trim();
  if (!company || !role) throw new Error("company and role are required");
  const app = {
    id: `job:${crypto.randomUUID()}`,
    company: company.slice(0, 160), role: role.slice(0, 160),
    source: String(input.source || "").slice(0, 120), notes: String(input.notes || "").slice(0, 1000),
    stage: STAGES.includes(input.stage) ? input.stage : "applied",
    outcome: OUTCOMES.includes(input.outcome) ? input.outcome : "pending",
    appliedAt: nowIso, lastUpdate: nowIso,
  };
  const all = readApps(root); all.push(app); _writeAll(root, all);
  return app;
}
function updateApp(root, id, fields, nowIso) {
  const all = readApps(root); const a = all.find((x) => x.id === id);
  if (!a) return null;
  if (STAGES.includes(fields.stage)) a.stage = fields.stage;
  if (OUTCOMES.includes(fields.outcome)) a.outcome = fields.outcome;
  a.lastUpdate = nowIso;
  _writeAll(root, all);
  return a;
}

module.exports = { STAGES, OUTCOMES, reached, funnelStats, nextAction, readApps, addApp, updateApp };
