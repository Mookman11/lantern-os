"use strict";
/**
 * Negotiation & life-admin co-pilot (#1432).
 *
 * For the "I hate phone calls / paperwork" market: bills, insurance claims, refund
 * disputes, landlord emails. Tracks each case and its outcome, drafts a firm, structured
 * email (with the policy-citation slot and a real deadline + escalation path), and tells
 * you the next action. The draft scaffold + next-action + stats are pure/deterministic;
 * an LLM (local Ollama) can polish the wording on top, degrading to the scaffold if absent.
 */
const fs = require("fs");
const path = require("path");
const crypto = require("crypto");

const DEFAULT_REPO_ROOT = path.resolve(__dirname, "../../..");
const DAY_MS = 86_400_000;
const TYPES = ["refund", "insurance", "landlord", "bill", "subscription", "other"];

const ASSERTION = {
  refund: "Under consumer-protection rules and your own returns policy, I am entitled to a refund for this purchase.",
  insurance: "This loss is covered under the terms of my policy, and I am entitled to have the claim assessed and paid promptly.",
  landlord: "Under the tenancy agreement and local housing law, this is your responsibility to address.",
  bill: "This charge is incorrect, and under fair-billing rules I am entitled to have it corrected and any error refunded.",
  subscription: "I have cancelled / did not authorise this, and under the cancellation terms I am entitled to stop the charges and be refunded.",
  other: "I am writing to formally raise this issue and request that it be resolved.",
};
const ESCALATION = {
  refund: "my card issuer for a chargeback and the relevant consumer authority",
  insurance: "the insurance ombudsman / state insurance commissioner",
  landlord: "the local housing authority / tenancy tribunal",
  bill: "the billing regulator and a formal complaint",
  subscription: "my card issuer to block the payments and the consumer authority",
  other: "the appropriate ombudsman or regulator",
};

function _type(t) { return TYPES.includes(t) ? t : "other"; }
function _fmtDate(ms) { return new Date(ms).toISOString().slice(0, 10); }

// Build the firm, structured email scaffold for a case. Pure → testable.
function draftEmail(c = {}, nowMs) {
  const now = nowMs != null ? nowMs : Date.now();
  const type = _type(c.type);
  const counterparty = String(c.counterparty || "Sir or Madam").trim();
  const account = String(c.account || "").trim();
  const summary = String(c.summary || "the matter described above").trim();
  const desiredOutcome = String(c.desiredOutcome || "this issue resolved").trim();
  const clause = String(c.policyClause || "").trim();
  const name = String(c.name || "").trim() || "[your name]";
  const deadlineMs = now + 14 * DAY_MS;

  const subjectKind = { refund: "Refund request", insurance: "Insurance claim", landlord: "Repair / tenancy issue", bill: "Billing dispute", subscription: "Cancellation & refund", other: "Formal request" }[type];
  const subject = `${subjectKind}${account ? ` — account ${account}` : ""} — response required by ${_fmtDate(deadlineMs)}`;

  const lines = [
    `Dear ${counterparty},`,
    "",
    `I am writing about the following matter${account ? ` (account ${account})` : ""}: ${summary}`,
    "",
    ASSERTION[type],
    clause ? `Specifically, I refer you to ${clause}.` : `[If you have a specific policy clause or contract term, cite it here.]`,
    "",
    `I am requesting that you ${desiredOutcome}.`,
    "",
    `Please confirm in writing how you will resolve this by ${_fmtDate(deadlineMs)}. If I do not receive a satisfactory response by then, I will escalate this to ${ESCALATION[type]}.`,
    "",
    "I would prefer to resolve this directly and quickly. Thank you for your prompt attention.",
    "",
    "Regards,",
    name,
  ];
  return { subject, body: lines.join("\n"), deadline: _fmtDate(deadlineMs), escalationTarget: ESCALATION[type] };
}

// What to do next, given the case's status and age.
function nextAction(c = {}, nowMs) {
  const now = nowMs != null ? nowMs : Date.now();
  const status = c.status || "open";
  const sinceMs = Date.parse(c.lastActionAt || c.createdAt || "") || now;
  const days = Math.max(0, Math.round((now - sinceMs) / DAY_MS));
  if (status === "resolved") return { action: "closed", text: "Resolved — nothing more to do." };
  if (status === "open") return { action: "send", text: "Send the drafted email to start the clock." };
  if (status === "sent") {
    return days >= 14
      ? { action: "escalate", text: `No response in ${days} days — escalate now to ${ESCALATION[_type(c.type)]}.` }
      : { action: "wait", text: `Sent ${days} day(s) ago — give them until the 14-day deadline, then escalate.` };
  }
  if (status === "escalated") return { action: "follow-up", text: `Escalated ${days} day(s) ago — follow up with the escalation contact if still unresolved.` };
  return { action: "review", text: "Review the case." };
}

function caseStats(cases) {
  const cs = cases || [];
  const by = (s) => cs.filter((c) => (c.status || "open") === s).length;
  const resolved = cs.filter((c) => c.status === "resolved");
  const won = resolved.filter((c) => c.outcome === "won" || c.outcome === "partial").length;
  return {
    total: cs.length, open: by("open"), sent: by("sent"), escalated: by("escalated"), resolved: resolved.length,
    winRate: resolved.length ? Math.round(won / resolved.length * 100) / 100 : null,
    status: cs.length ? "ok" : "insufficient_data",
  };
}

// ── thin JSONL persistence (local-only) ─────────────────────────────────────────
function _file(root) { return path.join(root || DEFAULT_REPO_ROOT, "data", "admin-copilot", "cases.jsonl"); }
function readCases(root) {
  try {
    return fs.readFileSync(_file(root), "utf8").split("\n").filter((l) => l.trim())
      .map((l) => { try { return JSON.parse(l); } catch { return null; } }).filter(Boolean);
  } catch { return []; }
}
function _writeAll(root, cases) {
  const f = _file(root); fs.mkdirSync(path.dirname(f), { recursive: true });
  fs.writeFileSync(f, cases.map((c) => JSON.stringify(c)).join("\n") + (cases.length ? "\n" : ""));
}
function createCase(root, input, nowIso) {
  const c = {
    id: `case:${crypto.randomUUID()}`,
    type: _type(input.type), counterparty: String(input.counterparty || "").slice(0, 160),
    account: String(input.account || "").slice(0, 80), summary: String(input.summary || "").slice(0, 1000),
    desiredOutcome: String(input.desiredOutcome || "").slice(0, 500), policyClause: String(input.policyClause || "").slice(0, 300),
    name: String(input.name || "").slice(0, 120), status: "open", outcome: null,
    createdAt: nowIso, lastActionAt: nowIso,
  };
  const all = readCases(root); all.push(c); _writeAll(root, all);
  return c;
}
function updateStatus(root, id, status, outcome, nowIso) {
  const all = readCases(root); const c = all.find((x) => x.id === id);
  if (!c) return null;
  if (["open", "sent", "escalated", "resolved"].includes(status)) c.status = status;
  if (outcome !== undefined) c.outcome = outcome;
  c.lastActionAt = nowIso;
  _writeAll(root, all);
  return c;
}

module.exports = { TYPES, draftEmail, nextAction, caseStats, readCases, createCase, updateStatus };
