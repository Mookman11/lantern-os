"use strict";
/**
 * Verification-as-a-service (#1425, Verify stage).
 *
 * The adversarial-verify harness as one primitive: POST a claim (+ optional evidence) and
 * get back independent refute-ATTEMPTS, their votes, a verdict, a confidence, and the
 * sources. Each refuter is a distinct lens that TRIES to knock the claim down; the verdict
 * is the tally. Enforces the External Reality Rule — a bare empirical claim with no
 * evidence does NOT get "confirmed"; absent support, it stays `uncertain` (cite-or-abstain).
 *
 * Offline + deterministic by design (no model required), so it always runs and is fully
 * testable. A model-backed refuter can be layered on top later without changing the tally.
 */

const STOP = new Set("the a an of to in is are was were be been and or for on at by with as it this that these those from".split(" "));
const ABSOLUTES = /\b(all|every|always|never|none|no one|nobody|everyone|everything|guaranteed|impossible|certainly|definitely|100%|zero|cannot ever)\b/i;
const HEDGES = /\b(might|maybe|possibly|perhaps|could|seems|appears|likely|probably|some|often|sometimes|generally)\b/i;
const EMPIRICAL = /\b(is|are|was|were|will|causes?|increases?|decreases?|reduces?|improves?|kills?|cures?|prevents?|proves?|shows?|means|equals?|\d)\b/i;
const NEGATORS = /\b(not|no|never|cannot|can't|won't|isn't|aren't|wasn't|false|incorrect|wrong|fails?|without|lacks?)\b/i;

function terms(s) {
  return new Set(String(s || "").toLowerCase().replace(/[^a-z0-9% ]+/g, " ").split(/\s+/).filter((w) => w.length > 2 && !STOP.has(w)));
}
function overlap(a, b) {
  const A = terms(a), B = terms(b);
  if (!A.size || !B.size) return 0;
  let n = 0; for (const w of A) if (B.has(w)) n++;
  return Math.round((n / A.size) * 1000) / 1000;
}
function isNeg(s) { return NEGATORS.test(String(s || "")); }

// Each refuter returns a vote: { lens, refuted, confidence, reason }. refuted=true means
// "this lens found grounds to reject the claim (as confirmed-true)".
const REFUTERS = {
  // An absolute claim ("always/never/all") is trivially refuted by a single counterexample,
  // so it carries the burden of proof — without supporting evidence, treat as refutable.
  counterexample(claim, evidence) {
    const abs = ABSOLUTES.test(claim);
    const supported = evidence.some((e) => overlap(claim, e) >= 0.4 && isNeg(claim) === isNeg(e));
    if (abs && !supported) return { lens: "counterexample", refuted: true, confidence: 0.6, reason: "Absolute claim with no supporting evidence — one counterexample refutes it." };
    return { lens: "counterexample", refuted: false, confidence: abs ? 0.3 : 0.2, reason: abs ? "Absolute, but evidence backs it." : "Not an absolute claim." };
  },
  // External Reality Rule: an empirical claim with NO evidence can't be confirmed.
  evidence(claim, evidence) {
    const empirical = EMPIRICAL.test(claim);
    if (empirical && evidence.length === 0) return { lens: "evidence", refuted: true, confidence: 0.5, reason: "Empirical claim with zero cited evidence — cannot be accepted (cite-or-abstain)." };
    return { lens: "evidence", refuted: false, confidence: evidence.length ? 0.4 : 0.2, reason: evidence.length ? `${evidence.length} evidence item(s) provided.` : "Non-empirical or self-evident." };
  },
  // Does any evidence directly CONTRADICT the claim (shared subject, opposite polarity)?
  contradiction(claim, evidence) {
    for (const e of evidence) {
      if (overlap(claim, e) >= 0.4 && isNeg(claim) !== isNeg(e)) {
        return { lens: "contradiction", refuted: true, confidence: 0.8, reason: `Evidence contradicts the claim: "${String(e).slice(0, 80)}"` };
      }
    }
    return { lens: "contradiction", refuted: false, confidence: 0.3, reason: "No evidence directly contradicts the claim." };
  },
  // Does evidence SUPPORT it (shared subject, same polarity)? A supporting refuter votes
  // NOT-refuted with real confidence — this is what lets a well-cited claim get confirmed.
  support(claim, evidence) {
    let best = 0, src = null;
    for (const e of evidence) {
      if (isNeg(claim) === isNeg(e)) { const o = overlap(claim, e); if (o > best) { best = o; src = e; } }
    }
    if (best >= 0.4) return { lens: "support", refuted: false, confidence: Math.min(0.9, 0.4 + best / 2), reason: `Evidence supports the claim: "${String(src).slice(0, 80)}"` };
    return { lens: "support", refuted: false, confidence: 0.1, reason: "No evidence strongly supports the claim." };
  },
};

// Tally the refuter votes into a verdict. Σ₀: default to `uncertain` unless the signal is
// clear. `confirmed` requires real support and a minority of refuters; `refuted` requires a
// majority (weighted) to refute.
function tallyVotes(votes) {
  const n = votes.length || 1;
  const refuters = votes.filter((v) => v.refuted);
  const refuteWeight = refuters.reduce((a, v) => a + v.confidence, 0);
  const supportWeight = votes.filter((v) => v.lens === "support" || v.lens === "contradiction" && !v.refuted)
    .reduce((a, v) => a + (v.refuted ? 0 : v.confidence), 0);
  const supportLens = votes.find((v) => v.lens === "support");
  const hasSupport = supportLens && supportLens.confidence >= 0.5;

  // A single high-confidence refutation (e.g. evidence directly contradicts the claim) is
  // decisive; otherwise require a weighted majority of refuters.
  const strongRefute = refuters.some((v) => v.confidence >= 0.75);

  let verdict, confidence;
  if (strongRefute || (refuters.length >= Math.ceil(n / 2) && refuteWeight >= 1.0)) {
    verdict = "refuted";
    confidence = Math.min(0.95, Math.round((refuteWeight / (refuteWeight + supportWeight + 0.01)) * 100) / 100);
  } else if (hasSupport && refuters.length === 0) {
    verdict = "confirmed";
    confidence = Math.min(0.9, supportLens.confidence);
  } else {
    verdict = "uncertain";
    confidence = Math.round((1 - Math.abs(refuteWeight - supportWeight) / (refuteWeight + supportWeight + 1)) * 100) / 100;
  }
  return { verdict, confidence, refuteCount: refuters.length, totalRefuters: n };
}

// Run the full adversarial verify on a claim (+ optional evidence list of strings).
function verifyClaim(claim, evidence = [], opts = {}) {
  const c = String(claim || "").trim();
  if (!c) return { status: "insufficient_data", error: "empty claim" };
  const ev = (Array.isArray(evidence) ? evidence : []).map((e) => String(e || "").trim()).filter(Boolean);
  if (HEDGES.test(c) && !ABSOLUTES.test(c) && ev.length === 0) {
    // A hedged statement ("X might help") isn't a firm claim — nothing to confirm/refute.
    return { status: "ok", claim: c, verdict: "uncertain", confidence: 0.2, votes: [], sources: ev,
      note: "Hedged statement — not a firm claim to verify." };
  }
  const votes = Object.values(REFUTERS).map((fn) => fn(c, ev));
  const tally = tallyVotes(votes);
  return {
    status: "ok", claim: c,
    verdict: tally.verdict, confidence: tally.confidence,
    refuteCount: tally.refuteCount, totalRefuters: tally.totalRefuters,
    votes, sources: ev,
  };
}

module.exports = { terms, overlap, tallyVotes, verifyClaim, REFUTERS };
