// #1425 — adversarial verify: refute lenses, vote tally, verdicts. Pure, deterministic.
//
// Run: node apps/lantern-garage/test/verify-service.test.js
const assert = require("assert");
const vs = require("../lib/verify-service");

let failures = 0;
function check(name, fn) {
  try { fn(); process.stdout.write(`  ok  - ${name}\n`); }
  catch (e) { failures++; process.stderr.write(`  FAIL- ${name}\n       ${e.message}\n`); }
}

check("empty claim → insufficient_data", () =>
  assert.strictEqual(vs.verifyClaim("").status, "insufficient_data"));

check("empirical claim with NO evidence is NOT confirmed (External Reality Rule)", () => {
  const r = vs.verifyClaim("The new model increases accuracy by 30%.");
  assert.notStrictEqual(r.verdict, "confirmed");                 // never auto-confirm
  assert.ok(["uncertain", "refuted"].includes(r.verdict), r.verdict);
  // the evidence lens should have voted to refute (cite-or-abstain)
  assert.ok(r.votes.some((v) => v.lens === "evidence" && v.refuted));
});

check("absolute claim with no evidence → refutable (counterexample lens fires)", () => {
  const r = vs.verifyClaim("Every user always prefers dark mode.");
  assert.ok(r.votes.some((v) => v.lens === "counterexample" && v.refuted));
  assert.notStrictEqual(r.verdict, "confirmed");
});

check("claim backed by supporting evidence → confirmed", () => {
  const r = vs.verifyClaim("Caching reduced latency in the benchmark.",
    ["The benchmark showed caching reduced latency by 40%.", "Latency dropped after enabling the cache."]);
  assert.strictEqual(r.verdict, "confirmed");
  assert.ok(r.confidence >= 0.5);
  assert.ok(r.votes.find((v) => v.lens === "support" && !v.refuted));
});

check("claim contradicted by evidence → refuted", () => {
  const r = vs.verifyClaim("The cache improved latency.",
    ["The cache did not improve latency; it made it worse.", "Latency was not reduced by caching."]);
  assert.strictEqual(r.verdict, "refuted");
  assert.ok(r.votes.find((v) => v.lens === "contradiction" && v.refuted));
});

check("hedged statement → uncertain, no firm verdict", () => {
  const r = vs.verifyClaim("This change might possibly help performance.");
  assert.strictEqual(r.verdict, "uncertain");
  assert.ok(/Hedged/i.test(r.note || ""));
});

check("tallyVotes: majority refute (weighted) → refuted", () => {
  const t = vs.tallyVotes([
    { lens: "a", refuted: true, confidence: 0.8 },
    { lens: "b", refuted: true, confidence: 0.6 },
    { lens: "support", refuted: false, confidence: 0.1 },
  ]);
  assert.strictEqual(t.verdict, "refuted");
});

check("tallyVotes: zero refute + real support → confirmed; split → uncertain", () => {
  assert.strictEqual(vs.tallyVotes([{ lens: "support", refuted: false, confidence: 0.7 }]).verdict, "confirmed");
  assert.strictEqual(vs.tallyVotes([
    { lens: "support", refuted: false, confidence: 0.3 },
    { lens: "evidence", refuted: true, confidence: 0.5 },
  ]).verdict, "uncertain");
});

check("response always carries [claim, verdict, confidence, sources]", () => {
  const r = vs.verifyClaim("Tests pass.", ["All tests pass in CI."]);
  for (const k of ["claim", "verdict", "confidence", "sources", "votes"]) assert.ok(k in r, `missing ${k}`);
});

if (failures) { process.stderr.write(`\n${failures} FAILED\n`); process.exit(1); }
process.stdout.write("\nall verify-service checks passed\n");
