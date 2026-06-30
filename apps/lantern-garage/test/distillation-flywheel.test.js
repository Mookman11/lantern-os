// #1421 — distillation flywheel observability aggregation. Pure, deterministic.
//
// Run: node apps/lantern-garage/test/distillation-flywheel.test.js
const assert = require("assert");
const fw = require("../lib/distillation-flywheel");

let failures = 0;
function check(name, fn) {
  try { fn(); process.stdout.write(`  ok  - ${name}\n`); }
  catch (e) { failures++; process.stderr.write(`  FAIL- ${name}\n       ${e.message}\n`); }
}

const NOW = Date.parse("2026-06-30T00:00:00.000Z");
const sec = (msIso) => String(Math.floor(Date.parse(msIso) / 1000));      // unix-seconds string like the real log
const lb = [
  { ts: sec("2026-06-01T00:00:00Z"), engine: "ouro-fast-cached", "pass@1": 0.20, n: 164 },
  { ts: sec("2026-06-15T00:00:00Z"), engine: "ouro-fast-cached", "pass@1": 0.32, n: 164 },
  { ts: sec("2026-06-28T00:00:00Z"), engine: "ouro-fast-cached", "pass@1": 0.40, n: 164 },
  { ts: sec("2026-06-20T00:00:00Z"), engine: "gpt-cloud", "pass@1": 0.9, n: 164 },   // cloud, not local
];
const decisions = [];
const dayAgo = (n) => String(Math.floor((NOW - n * 86400000) / 1000));
for (let i = 0; i < 5; i++) decisions.push({ timestamp: dayAgo(2 + i), escalate: true });   // this week
for (let i = 0; i < 2; i++) decisions.push({ timestamp: dayAgo(10 + i), escalate: true });   // prior week
decisions.push({ timestamp: dayAgo(1), escalate: false });                                   // not an escalation

check("localSeries selects local engines with pass@1, sorted by time", () => {
  const s = fw.localSeries(lb);
  assert.strictEqual(s.length, 3);                 // cloud row excluded
  assert.deepStrictEqual(s.map((x) => x.pass1), [0.20, 0.32, 0.40]);
});

check("capability now/start/improvement computed", () => {
  const f = fw.flywheelStats(lb, decisions, { nowMs: NOW, target: 0.7 });
  assert.strictEqual(f.localStart, 0.20);
  assert.strictEqual(f.localNow, 0.40);
  assert.ok(Math.abs(f.improvement - 0.2) < 1e-9);
});

check("gapClosedPct = (now-start)/(target-start)", () => {
  const f = fw.flywheelStats(lb, decisions, { nowMs: NOW, target: 0.7 });
  // (0.40-0.20)/(0.70-0.20) = 0.4
  assert.ok(Math.abs(f.gapClosedPct - 0.4) < 1e-9);
  assert.ok(Math.abs(f.remainingGap - 0.3) < 1e-9);
});

check("corpus = escalations; this-week window respected", () => {
  const f = fw.flywheelStats(lb, decisions, { nowMs: NOW, windowMs: 7 * 86400000 });
  assert.strictEqual(f.corpusSize, 7);             // 5 + 2 escalations (the non-escalation excluded)
  assert.strictEqual(f.corpusThisWeek, 5);
});

check("rising capability → flywheel-turning verdict", () => {
  const f = fw.flywheelStats(lb, decisions, { nowMs: NOW, target: 0.7 });
  assert.ok(/Flywheel is turning/.test(f.verdict));
  assert.strictEqual(f.status, "ok");
});

check("regression in capability is flagged", () => {
  const down = [
    { ts: sec("2026-06-01T00:00:00Z"), engine: "ouro", "pass@1": 0.40 },
    { ts: sec("2026-06-28T00:00:00Z"), engine: "ouro", "pass@1": 0.25 },
  ];
  const f = fw.flywheelStats(down, [], { nowMs: NOW });
  assert.ok(f.improvement < 0);
  assert.ok(/slipped|regression/i.test(f.verdict));
});

check("no eval history → insufficient_data, null capability", () => {
  const f = fw.flywheelStats([], [], { nowMs: NOW });
  assert.strictEqual(f.status, "insufficient_data");
  assert.strictEqual(f.localNow, null);
});

check("unix-seconds and ISO timestamps both parse", () => {
  const mixed = [
    { ts: "1748736000", engine: "ouro", "pass@1": 0.1 },                 // unix seconds
    { ts: "2026-06-28T00:00:00Z", engine: "ouro", "pass@1": 0.3 },        // ISO
  ];
  const s = fw.localSeries(mixed);
  assert.strictEqual(s.length, 2);
  assert.ok(s[0].ms < s[1].ms);
});

if (failures) { process.stderr.write(`\n${failures} FAILED\n`); process.exit(1); }
process.stdout.write("\nall distillation-flywheel checks passed\n");
