"use strict";
// Tests for the Ouro-style looped reasoner (Q-exit CDF + adaptive depth).
// Run: node tests/test_loop_reasoner.js
const assert = require("assert");
const { cdfExit, loopedReason, extractConfidence } = require("../apps/lantern-garage/lib/loop-reasoner");

let pass = 0;
function ok(name, cond) { assert.ok(cond, name); console.log("  ok -", name); pass++; }

(async () => {
  // cdfExit decision matrix
  ok("threshold_met at high confidence", cdfExit([0.9]).reason === "threshold_met");
  ok("converged on plateau", cdfExit([0.5, 0.52]).reason === "converged");
  ok("continuing while improving", cdfExit([0.4, 0.6]).reason === "continuing");
  ok("max_loops at budget", cdfExit([0.4, 0.5, 0.6, 0.7]).reason === "max_loops");
  ok("no_data on empty", cdfExit([]).reason === "no_data");

  // confidence extraction
  ok("parses percent", Math.abs(extractConfidence("Confidence: 80%") - 0.8) < 1e-9);
  ok("parses decimal", Math.abs(extractConfidence("Confidence: 0.7") - 0.7) < 1e-9);

  // looped reasoning exits early when confidence ramps past threshold
  let i = 0;
  const ramp = async () => ["Confidence: 50%", "Confidence: 70%", "Confidence: 90%", "Confidence: 95%"][i++];
  const r = await loopedReason({ prompt: "x", callLLM: ramp, maxLoops: 4 });
  ok("looped exits at threshold (loop 3)", r.loop_n === 3 && r.exit_reason === "threshold_met");
  ok("looped returns history", Array.isArray(r.history) && r.history.length === 3);

  // hits max_loops when confidence keeps improving but never crosses threshold
  let j = 0;
  const subThreshold = async () => ["Confidence: 30%", "Confidence: 50%", "Confidence: 70%"][j++];
  const r2 = await loopedReason({ prompt: "x", callLLM: subThreshold, maxLoops: 3 });
  ok("looped honors maxLoops", r2.loop_n === 3 && r2.exit_reason === "max_loops");

  // flat confidence converges (plateau) before maxLoops
  const flat = async () => "plain text, no confidence field";
  const r3 = await loopedReason({ prompt: "x", callLLM: flat, maxLoops: 4 });
  ok("flat confidence converges early", r3.exit_reason === "converged" && r3.loop_n === 2);

  console.log(`\n${pass} passed`);
})().catch((e) => { console.error("FAIL:", e.message); process.exit(1); });
