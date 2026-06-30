// #1429 — life-memory: fact extraction, categorize, recall across time. Pure/deterministic.
//
// Run: node apps/lantern-garage/test/life-memory.test.js
const assert = require("assert");
const lm = require("../lib/life-memory");

let failures = 0;
function check(name, fn) {
  try { fn(); process.stdout.write(`  ok  - ${name}\n`); }
  catch (e) { failures++; process.stderr.write(`  FAIL- ${name}\n       ${e.message}\n`); }
}

check("extractFact parses possessive 'X's Y is Z'", () => {
  const f = lm.extractFact("my kid's shoe size is 7");
  assert.strictEqual(f.subject, "my kid");
  assert.strictEqual(f.attribute, "shoe size");
  assert.strictEqual(f.value, "7");
});

check("extractFact parses 'X is Y'", () => {
  const f = lm.extractFact("the landlord's name is Dana");
  assert.strictEqual(f.subject, "the landlord");
  assert.strictEqual(f.value, "Dana");
});

check("extractFact strips trailing period; bare text falls back to value", () => {
  assert.strictEqual(lm.extractFact("Mom's birthday is March 3.").value, "March 3");
  const f = lm.extractFact("we adopted a dog named Rex");
  assert.ok(f.value.includes("Rex"));
});

check("categorize buckets by keyword", () => {
  assert.strictEqual(lm.categorize("the landlord's name is Dana"), "people");
  assert.strictEqual(lm.categorize("the project deadline is April 5"), "dates");
  assert.strictEqual(lm.categorize("my shoe size is 7"), "preferences");
  assert.strictEqual(lm.categorize("the gym address is 5th street"), "places");
});

const NOW = Date.parse("2026-06-30T00:00:00Z");
const fact = (subject, attribute, value, monthsBack) => ({
  subject, attribute, value,
  savedAt: new Date(NOW - (monthsBack || 0) * 30 * 86400000).toISOString(),
});

check("recall returns the right fact for a question + months-ago longevity", () => {
  const facts = [
    fact("my kid", "shoe size", "7", 4),
    fact("the landlord", "name", "Dana", 8),
    fact("favorite coffee", "order", "oat flat white", 1),
  ];
  const r = lm.recall(facts, "what is my kid's shoe size?", { nowMs: NOW });
  assert.strictEqual(r.status, "ok");
  assert.ok(r.answer.startsWith("7"), r.answer);
  assert.ok(/4 months ago/.test(r.answer), r.answer);
  assert.strictEqual(r.matches[0].value, "7");
});

check("recall ranks the landlord fact for a landlord question", () => {
  const facts = [fact("my kid", "shoe size", "7", 4), fact("the landlord", "name", "Dana", 8)];
  const r = lm.recall(facts, "what's the landlord's name again?", { nowMs: NOW });
  assert.strictEqual(r.matches[0].value, "Dana");
});

check("recall abstains when nothing matches (no fabrication)", () => {
  const r = lm.recall([fact("my kid", "shoe size", "7", 4)], "what is my car's license plate?", { nowMs: NOW });
  assert.strictEqual(r.status, "no_memory");
  assert.strictEqual(r.matches.length, 0);
});

check("recall on empty query → insufficient_data", () =>
  assert.strictEqual(lm.recall([], "   ").status, "insufficient_data"));

check("monthsAgo math", () => {
  assert.strictEqual(lm.monthsAgo(new Date(NOW - 3 * 30 * 86400000).toISOString(), NOW), 3);
  assert.strictEqual(lm.monthsAgo(new Date(NOW).toISOString(), NOW), 0);
});

if (failures) { process.stderr.write(`\n${failures} FAILED\n`); process.exit(1); }
process.stdout.write("\nall life-memory checks passed\n");
