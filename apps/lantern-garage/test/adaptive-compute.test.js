// #1423 — adaptive-compute depth budget + Q-exit savings. Pure, deterministic.
//
// Run: node apps/lantern-garage/test/adaptive-compute.test.js
const assert = require("assert");
const ac = require("../lib/adaptive-compute");

let failures = 0;
function check(name, fn) {
  try { fn(); process.stdout.write(`  ok  - ${name}\n`); }
  catch (e) { failures++; process.stderr.write(`  FAIL- ${name}\n       ${e.message}\n`); }
}

check("boilerplate scores far below complex lines", () => {
  const easy = ac.lineDifficulty("import { x } from 'y';");
  const brace = ac.lineDifficulty("}");
  const hard = ac.lineDifficulty("      if (x > 0 && x % 2 === 0) { out.push(Math.sqrt(x) * w(x, b)); }");
  assert.ok(easy < 0.2 && brace < 0.2, `easy=${easy} brace=${brace}`);
  assert.ok(hard > easy + 0.3, `hard=${hard} should exceed easy=${easy}`);
  assert.strictEqual(ac.lineDifficulty(""), 0);   // blank
});

check("depthFor is >=1, <=maxDepth, monotonic in difficulty", () => {
  assert.strictEqual(ac.depthFor(0), 1);
  assert.strictEqual(ac.depthFor(1), ac.MAX_DEPTH);
  assert.ok(ac.depthFor(0.3) <= ac.depthFor(0.7));
});

check("confidenceAtDepth is non-decreasing in depth and reaches ~1 at budget", () => {
  const d = 0.6;
  let prev = -1;
  for (let step = 1; step <= ac.MAX_DEPTH; step++) {
    const c = ac.confidenceAtDepth(d, step);
    assert.ok(c >= prev, `confidence dropped at depth ${step}`);
    prev = c;
  }
  const budget = ac.depthFor(d);
  assert.ok(ac.confidenceAtDepth(d, budget) >= 0.9);
});

check("Q-exit fires earlier (or equal) for easy lines than hard lines", () => {
  const easy = ac.qExit(0.05);
  const hard = ac.qExit(0.9);
  assert.ok(easy.exitDepth <= hard.exitDepth, `easy ${easy.exitDepth} > hard ${hard.exitDepth}`);
  assert.ok(easy.confidence >= ac.EXIT_CONFIDENCE - 1e-9);
});

check("analyzeCode: boilerplate-heavy code saves a lot of recurrent compute", () => {
  const code = [
    "import x from 'y';", "export const a = 1;", "const b = 2;", "}", "return a;",
    "      if (cond && other) { do(thing); }",   // one hard line
  ].join("\n");
  const a = ac.analyzeCode(code);
  assert.strictEqual(a.status, "ok");
  assert.strictEqual(a.codeLines, 6);
  assert.strictEqual(a.computeBaseline, 6 * ac.MAX_DEPTH);
  assert.ok(a.computeSpent < a.computeBaseline, "should spend less than baseline");
  assert.ok(a.computeSaved > 0.4, `expected big savings on boilerplate, got ${a.computeSaved}`);
  assert.ok(a.fidelity > 0.9, `fidelity ${a.fidelity}`);
});

check("harder code saves less than boilerplate", () => {
  const boiler = ac.analyzeCode(["import a;", "const b=1;", "}", "return b;"].join("\n"));
  const hard = ac.analyzeCode(["if (a && b || c) { for (const x of xs) { y += f(x) * g(x, z); } }"].join("\n"));
  assert.ok(hard.computeSaved < boiler.computeSaved, `hard ${hard.computeSaved} should be < boiler ${boiler.computeSaved}`);
});

check("empty → insufficient_data", () =>
  assert.strictEqual(ac.analyzeCode("   \n  \n").status, "insufficient_data"));

if (failures) { process.stderr.write(`\n${failures} FAILED\n`); process.exit(1); }
process.stdout.write("\nall adaptive-compute checks passed\n");
