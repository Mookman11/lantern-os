// #1433 — second brain: TF search ranking, related, and contradiction surfacing. Pure.
//
// Run: node apps/lantern-garage/test/second-brain.test.js
const assert = require("assert");
const sb = require("../lib/second-brain");

let failures = 0;
function check(name, fn) {
  try { fn(); process.stdout.write(`  ok  - ${name}\n`); }
  catch (e) { failures++; process.stderr.write(`  FAIL- ${name}\n       ${e.message}\n`); }
}

const NOW = Date.parse("2026-06-30T00:00:00.000Z");
const day = (n) => new Date(NOW - n * 86400000).toISOString();
const items = [
  { id: "a", title: "Coffee improves focus", content: "Caffeine boosts alertness and productivity.", tags: ["coffee", "health"], capturedAt: day(2) },
  { id: "b", title: "The myth of multitasking", content: "Multitasking does not work; it actually hurts focus.", tags: ["productivity"], capturedAt: day(20) },
  { id: "c", title: "Sleep and memory", content: "Deep sleep consolidates memory.", tags: ["sleep"], capturedAt: day(1) },
  { id: "d", title: "Coffee is bad late", content: "Caffeine late in the day is not good for sleep — it wrecks it.", tags: ["coffee", "sleep"], capturedAt: day(40) },
];

check("tokenize drops stopwords + short words", () =>
  assert.deepStrictEqual(sb.tokenize("The big cat is on a mat"), ["big", "cat", "mat"]));

check("search ranks title/tag hits above content-only", () => {
  const r = sb.search(items, "coffee");
  assert.strictEqual(r[0].item.id, "a");        // "coffee" in title + tag + content
  assert.ok(r.some((x) => x.item.id === "d"));
  assert.ok(!r.some((x) => x.item.id === "c")); // no coffee in sleep/memory note
});

check("search coverage prioritizes items hitting more query terms", () => {
  const r = sb.search(items, "coffee sleep");
  assert.strictEqual(r[0].item.id, "d");        // hits BOTH coffee and sleep
});

check("empty query → recency-ordered list", () => {
  const r = sb.search(items, "");
  assert.strictEqual(r[0].item.id, "c");        // most recent (1 day)
});

check("search returns a snippet around the hit", () => {
  const r = sb.search(items, "alertness");
  assert.ok(/alertness/i.test(r[0].snippet));
});

check("findRelated excludes the source item", () => {
  const r = sb.findRelated(items, "caffeine and sleep", { excludeId: "d" });
  assert.ok(!r.some((x) => x.item.id === "d"));
  assert.ok(r.some((x) => x.item.id === "c" || x.item.id === "a"));
});

check("findContradictions surfaces a negation-bearing item on the topic, with age", () => {
  const cs = sb.findContradictions(items, "drinking coffee improves sleep", NOW);
  // item d shares coffee + sleep terms AND has negation ("not good", "wrecks")
  assert.ok(cs.some((c) => c.id === "d"));
  const d = cs.find((c) => c.id === "d");
  assert.strictEqual(d.ageDays, 40);
  assert.ok(d.sharedTerms >= 2);
});

check("findContradictions stays quiet when nothing both matches topic and negates", () => {
  const cs = sb.findContradictions(items, "memory consolidation", NOW);
  // "Sleep and memory" matches topic but has NO negation cue → not flagged
  assert.ok(!cs.some((c) => c.id === "c"));
});

check("findContradictions empty for an empty claim", () =>
  assert.deepStrictEqual(sb.findContradictions(items, "", NOW), []));

if (failures) { process.stderr.write(`\n${failures} FAILED\n`); process.exit(1); }
process.stdout.write("\nall second-brain checks passed\n");
