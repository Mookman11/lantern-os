// Tests for the A2→mergeDetections wiring: a window that statistically stands
// out earns an additive `novel` tag; the integration is fully guarded so it
// never fires (and never regresses) when novelty can't be computed.
// Standalone: `node tests/test_merge_novel.js`.

"use strict";

const assert = require("assert");
const { mergeDetections } = require("../apps/lantern-garage/lib/highlight-engine");

let passed = 0;
function test(name, fn) {
  try { fn(); passed++; console.log(`  ok  - ${name}`); }
  catch (err) { console.error(`  FAIL - ${name}\n        ${err.message}`); process.exitCode = 1; }
}

// Build a motion frame series from per-window constant values (windowSec*fps frames each).
function buildMotion(windowVals, windowSec = 2, fps = 5) {
  const frames = [];
  const perWin = windowSec * fps;
  windowVals.forEach((v, wi) => {
    for (let k = 0; k < perWin; k++) {
      frames.push({ timestamp: Number(((wi * perWin + k) / fps).toFixed(2)), motion: v });
    }
  });
  return frames;
}

test("a standout window earns an additive `novel` tag on its highlight", () => {
  // 6 windows; window 3 (t≈6–8s) is a clear motion outlier vs the rest.
  const motion = buildMotion([4, 6, 5, 38, 6, 4]);
  const highlights = mergeDetections(motion, [], [], 5, 2, 60);
  assert.ok(highlights.length > 0, "the burst forms a highlight");
  const burst = highlights.find((h) => h.start >= 6 && h.start < 8);
  assert.ok(burst, "highlight lands in the burst window");
  assert.ok(burst.tags.includes("novel"), "burst highlight is tagged novel");
  assert.ok(/novel/.test(burst.reason));
});

test("guard: too few windows → no novelty computed → no `novel` tag (no regression)", () => {
  // 3 windows (6s) < MIN_WINDOWS(4): noveltyScores returns [] so nothing is tagged.
  const motion = buildMotion([5, 5, 40]);
  const highlights = mergeDetections(motion, [], [], 5, 2, 60);
  assert.ok(highlights.length > 0, "the burst still forms a highlight");
  assert.ok(highlights.every((h) => !h.tags.includes("novel")), "no novel tag without enough windows");
});

test("empty motion input still returns [] (unchanged contract)", () => {
  assert.deepStrictEqual(mergeDetections([], [], [], 5, 2, 60), []);
});

console.log(`\n${passed} checks passed.`);
