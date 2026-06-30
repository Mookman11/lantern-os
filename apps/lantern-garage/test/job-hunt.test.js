// #1431 — job-hunt funnel conversion math + next-action cadence. Pure, deterministic.
//
// Run: node apps/lantern-garage/test/job-hunt.test.js
const assert = require("assert");
const jh = require("../lib/job-hunt");

let failures = 0;
function check(name, fn) {
  try { fn(); process.stdout.write(`  ok  - ${name}\n`); }
  catch (e) { failures++; process.stderr.write(`  FAIL- ${name}\n       ${e.message}\n`); }
}

const NOW = Date.parse("2026-06-30T00:00:00.000Z");
const DAY = 86400000;
const app = (stage, outcome, appliedDaysAgo) => ({
  stage, outcome: outcome || "pending",
  appliedAt: new Date(NOW - (appliedDaysAgo || 0) * DAY).toISOString(),
  lastUpdate: new Date(NOW - (appliedDaysAgo || 0) * DAY).toISOString(),
});

// reached
check("reached counts furthest stage, even if later rejected", () => {
  assert.strictEqual(jh.reached(app("interview", "rejected"), "screen"), true);
  assert.strictEqual(jh.reached(app("applied"), "screen"), false);
  assert.strictEqual(jh.reached({ stage: "applied", outcome: "accepted" }, "offer"), true);   // accepted ⇒ reached offer
});

// funnel + conversions
check("funnel counts + step conversions", () => {
  const apps = [
    app("applied"), app("applied"), app("applied", "ghosted"), app("applied", "rejected"),  // 4 applied, 0 past
    app("screen"), app("screen", "rejected"),                                                 // 2 reached screen
    app("interview"),                                                                          // 1 reached interview
    app("offer", "accepted"),                                                                  // 1 reached offer
  ];
  const f = jh.funnelStats(apps, { nowMs: NOW });
  assert.strictEqual(f.total, 8);
  const byStage = Object.fromEntries(f.funnel.map((s) => [s.stage, s.count]));
  assert.strictEqual(byStage.applied, 8);
  assert.strictEqual(byStage.screen, 4);       // screen+interview+offer reached screen
  assert.strictEqual(byStage.interview, 2);    // interview + offer
  assert.strictEqual(byStage.offer, 1);
  // conversion screen-from-applied = 4/8 = 0.5
  assert.strictEqual(f.funnel.find((s) => s.stage === "screen").conversionFromPrev, 0.5);
  // interview-from-screen = 2/4 = 0.5
  assert.strictEqual(f.funnel.find((s) => s.stage === "interview").conversionFromPrev, 0.5);
});

check("response / ghost / offer rates", () => {
  const apps = [app("applied"), app("applied", "ghosted"), app("screen"), app("offer", "accepted")];
  const f = jh.funnelStats(apps, { nowMs: NOW });
  assert.strictEqual(f.responseRate, jh.funnelStats(apps, { nowMs: NOW }).funnel[1].count / 4);  // reachedScreen/total
  assert.strictEqual(f.ghostRate, 0.25);
  assert.strictEqual(f.offerRate, 0.25);
});

check("appliedThisWeek counts last 7 days; weekly target default", () => {
  const apps = [app("applied", null, 1), app("applied", null, 3), app("applied", null, 20)];
  const f = jh.funnelStats(apps, { nowMs: NOW });
  assert.strictEqual(f.appliedThisWeek, 2);
  assert.strictEqual(f.weeklyTarget, 5);
});

check("empty → insufficient_data", () =>
  assert.strictEqual(jh.funnelStats([], { nowMs: NOW }).status, "insufficient_data"));

// nextAction cadence
check("applied <10d → wait; ≥10d → follow-up", () => {
  assert.strictEqual(jh.nextAction(app("applied", null, 3), NOW).action, "wait");
  assert.strictEqual(jh.nextAction(app("applied", null, 12), NOW).action, "follow-up");
});
check("screen/interview ≥7d → follow-up", () =>
  assert.strictEqual(jh.nextAction(app("interview", null, 9), NOW).action, "follow-up"));
check("outcomes drive their own action", () => {
  assert.strictEqual(jh.nextAction({ stage: "screen", outcome: "rejected" }, NOW).action, "learn");
  assert.strictEqual(jh.nextAction({ stage: "applied", outcome: "ghosted" }, NOW).action, "move-on");
  assert.strictEqual(jh.nextAction({ stage: "offer", outcome: "accepted" }, NOW).action, "celebrate");
  assert.strictEqual(jh.nextAction({ stage: "offer", outcome: "pending" }, NOW).action, "decide");
});

if (failures) { process.stderr.write(`\n${failures} FAILED\n`); process.exit(1); }
process.stdout.write("\nall job-hunt checks passed\n");
