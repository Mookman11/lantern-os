// #1432 — admin co-pilot: draft scaffolding, next-action, case stats. Pure, deterministic.
//
// Run: node apps/lantern-garage/test/admin-copilot.test.js
const assert = require("assert");
const ac = require("../lib/admin-copilot");

let failures = 0;
function check(name, fn) {
  try { fn(); process.stdout.write(`  ok  - ${name}\n`); }
  catch (e) { failures++; process.stderr.write(`  FAIL- ${name}\n       ${e.message}\n`); }
}

const NOW = Date.parse("2026-06-30T00:00:00.000Z");
const DAY = 86400000;

check("draftEmail builds a firm scaffold with deadline + escalation", () => {
  const d = ac.draftEmail({ type: "refund", counterparty: "Acme", account: "X1", summary: "a faulty blender",
    desiredOutcome: "refund the full $89", policyClause: "your 30-day returns policy", name: "Alex" }, NOW);
  assert.ok(/Refund request/.test(d.subject));
  assert.ok(/account X1/.test(d.subject));
  assert.strictEqual(d.deadline, "2026-07-14");           // +14 days
  assert.ok(/Dear Acme,/.test(d.body));
  assert.ok(/refund the full \$89/.test(d.body));
  assert.ok(/your 30-day returns policy/.test(d.body));
  assert.ok(/chargeback/.test(d.body));                    // refund escalation path
  assert.ok(/Alex/.test(d.body));
});

check("draftEmail inserts a citation prompt when no clause given", () => {
  const d = ac.draftEmail({ type: "bill", summary: "a wrong charge", desiredOutcome: "correct it" }, NOW);
  assert.ok(/cite it here/.test(d.body));
});

check("draftEmail escalation path varies by type", () => {
  assert.ok(/ombudsman|commissioner/.test(ac.draftEmail({ type: "insurance" }, NOW).body));
  assert.ok(/housing authority|tribunal/.test(ac.draftEmail({ type: "landlord" }, NOW).body));
});

check("unknown type degrades to 'other'", () => {
  const d = ac.draftEmail({ type: "bogus", summary: "x" }, NOW);
  assert.ok(/Formal request/.test(d.subject));
});

// nextAction
check("open case → send", () =>
  assert.strictEqual(ac.nextAction({ status: "open", createdAt: new Date(NOW).toISOString() }, NOW).action, "send"));
check("sent <14d → wait", () =>
  assert.strictEqual(ac.nextAction({ status: "sent", lastActionAt: new Date(NOW - 3 * DAY).toISOString(), type: "refund" }, NOW).action, "wait"));
check("sent ≥14d → escalate", () => {
  const na = ac.nextAction({ status: "sent", lastActionAt: new Date(NOW - 15 * DAY).toISOString(), type: "insurance" }, NOW);
  assert.strictEqual(na.action, "escalate");
  assert.ok(/ombudsman|commissioner/.test(na.text));
});
check("escalated → follow-up; resolved → closed", () => {
  assert.strictEqual(ac.nextAction({ status: "escalated", lastActionAt: new Date(NOW - 2 * DAY).toISOString() }, NOW).action, "follow-up");
  assert.strictEqual(ac.nextAction({ status: "resolved" }, NOW).action, "closed");
});

// caseStats
check("caseStats counts by status + win rate over resolved", () => {
  const s = ac.caseStats([
    { status: "open" }, { status: "sent" }, { status: "escalated" },
    { status: "resolved", outcome: "won" }, { status: "resolved", outcome: "partial" }, { status: "resolved", outcome: "lost" },
  ]);
  assert.strictEqual(s.total, 6);
  assert.strictEqual(s.open, 1); assert.strictEqual(s.resolved, 3);
  assert.strictEqual(s.winRate, 0.67);                     // won + partial / resolved, rounded 2dp
});
check("caseStats empty → insufficient_data, null win rate", () => {
  const s = ac.caseStats([]);
  assert.strictEqual(s.status, "insufficient_data");
  assert.strictEqual(s.winRate, null);
});

if (failures) { process.stderr.write(`\n${failures} FAILED\n`); process.exit(1); }
process.stdout.write("\nall admin-copilot checks passed\n");
