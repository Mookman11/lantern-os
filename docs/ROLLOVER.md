# Keystone Rollover — Staged Plan & Exit Criteria

**Issue:** [#892](https://github.com/alex-place/lantern-os/issues/892)  
**Status:** Stage 0 — Shadow (active)  
**Principle:** *No stage advances without a `leaderboard.jsonl` row showing the gate passed.*

---

## Overview

This document defines the evidence-gated plan for rolling over the primary coding
agent from Claude (Anthropic) to Keystone chat — the in-house
GROUND→PLAN→PATCH→VERIFY kernel (`keystoneRun` in
`apps/lantern-garage/lib/keystone-runtime.js`) running the Keystone/Ouro model,
with Claude demoted to an explicit, recorded fallback.

The rollover is **not a hard cutover**. Keystone earns each stage by passing
measurable gates on `data/eval/leaderboard.jsonl`. A gate that fails resets to the
previous stage; the leaderboard row is the only admissible evidence.

---

## Current state (grounding)

| Component | Status |
|---|---|
| `keystoneRun()` kernel | [built] — model-agnostic, GROUND→PLAN→PATCH→VERIFY |
| Ouro-1.4B local model | [built] — served via Ollama (`ouro:latest`) |
| `eval_keystone.py` golden set | [built] — 65 prompts, 34% cold baseline (Stage 0 bar) |
| `provider-router.js` fallback chain | [built] — `coding` chain: ollama → mistral → anthropic |
| Stage-tagged leaderboard rows | [built] — `--stage` flag in `eval_keystone.py` |
| Autowork gating bugs (#870, #871) | open — must close before Stage 1 |
| Rollover dashboard (#898) | not started |

---

## Rollover stages

### Stage 0 — Shadow (current)

Keystone runs the loop on issues and proposes changes. Claude lands all PRs.
Win/loss + cost are captured per run so Stage 1's gate can be set from evidence.

**Exit criteria (all must be met to advance to Stage 1):**

| Gate | Metric | Bar |
|---|---|---|
| S0-A | `eval_keystone.py --stage 0` accuracy | ≥ 40% (beats 34% cold baseline) |
| S0-B | Win/loss cost ratio logged | ≥ 10 shadow runs in `data/rollover/shadow-runs.jsonl` |
| S0-C | No false-positive verifications | autowork gating bugs #870/#871 closed |

**How to run the Stage 0 gate:**
```bash
python scripts/eval_keystone.py --label keystone-shadow --stage 0 --gate-bar 0.40
```
A `gate_passed: true` row in `data/eval/leaderboard.jsonl` is required before
Stage 1 begins.

---

### Stage 1 — Assist

Keystone lands low-risk issues (`cleanup`/`p2` labels) autonomously. Claude is the
fallback on red (failed verification). Each Claude fallback is recorded as a
convergence event (see `convergence-records.js`).

**Exit criteria:**

| Gate | Metric | Bar |
|---|---|---|
| S1-A | `eval_keystone.py --stage 1` accuracy | ≥ 50% |
| S1-B | Keystone autonomous landings | ≥ 5 merged PRs with `[keystone-autonomous]` label |
| S1-C | Claude fallback rate | < 40% of attempted issues |
| S1-D | No uncaught verification failures | all `auto/` PRs have a `leaderboard.jsonl` gate row |

**How to run the Stage 1 gate:**
```bash
python scripts/eval_keystone.py --label keystone-assist --stage 1 --gate-bar 0.50
```

---

### Stage 2 — Default

Keystone is the default coding provider. Claude is fallback only, invoked when
Keystone returns a failed verification or when the issue is explicitly tagged
`escalate-to-claude`.

**Exit criteria:**

| Gate | Metric | Bar |
|---|---|---|
| S2-A | `eval_keystone.py --stage 2` accuracy | ≥ 60% |
| S2-B | Keystone share of closed issues | ≥ 60% of last 30 closed (last 30 days) |
| S2-C | Zero regressions on golden set | no prompt that was `ok=True` flips to `ok=False` |
| S2-D | Rollover dashboard live | `#898` closed |

**How to run the Stage 2 gate:**
```bash
python scripts/eval_keystone.py --label keystone-default --stage 2 --gate-bar 0.60
```

---

### Stage 3 — Independent

The `ANTHROPIC_API_KEY` default requirement is dropped. Keystone runs fully
local-first; cloud providers (Anthropic, OpenAI) are opt-in fallbacks configured
explicitly in `.env`.

**Exit criteria:**

| Gate | Metric | Bar |
|---|---|---|
| S3-A | `eval_keystone.py --stage 3` accuracy | ≥ 65% |
| S3-B | Server starts cleanly without `ANTHROPIC_API_KEY` | CI green |
| S3-C | Keystone share of closed issues | ≥ 80% of last 30 closed |
| S3-D | `ROLLOVER.md` updated to reflect completion | this file updated |

**How to run the Stage 3 gate:**
```bash
python scripts/eval_keystone.py --label keystone-independent --stage 3 --gate-bar 0.65
```

---

## Leaderboard row format

`data/eval/leaderboard.jsonl` — one JSON object per line:

```json
{
  "benchmark": "keystone",
  "ts": "1750000000",
  "label": "keystone-shadow",
  "model": "ouro:latest",
  "stage": 0,
  "gate_bar": 0.40,
  "gate_passed": true,
  "n": 65,
  "accuracy": 0.42,
  "pass@1": 0.42,
  "avg_latency_s": 12.4,
  "tok_per_s": 3.1
}
```

Fields `stage`, `gate_bar`, and `gate_passed` are set by `--stage` / `--gate-bar`
flags. Rows without a `stage` field are pre-rollover benchmark runs.

---

## Shadow run log format

`data/rollover/shadow-runs.jsonl` — one JSON object per completed shadow issue:

```json
{
  "ts": "2026-06-21T00:00:00Z",
  "issue_number": 901,
  "keystone_proposed": true,
  "claude_landed": true,
  "keystone_patch_correct": null,
  "cost_keystone_usd": 0.00,
  "cost_claude_usd": 0.04,
  "notes": "Keystone proposed correct diff; Claude applied it"
}
```

`keystone_patch_correct` is `null` until manually graded (or graded by the eval
harness). Once 10 rows exist and S0-A passes, Stage 1 can open.

---

## Fallback / escalation recording

All Claude fallback invocations MUST be recorded as convergence events. See
`apps/lantern-garage/lib/convergence-records.js` — emit a record with:

```json
{
  "type": "claude_fallback",
  "trigger": "verification_failed | explicit_escalate | stage_gate_failed",
  "issue_number": 901,
  "keystone_stage": 1,
  "evidence": "...error from verification...",
  "confidence": 1.0
}
```

This implements #897 and feeds the rollover dashboard (#898).

---

## Related

- [SIGMA0-K1-KERNEL-SPEC.md](SIGMA0-K1-KERNEL-SPEC.md) — kernel spec, gates A–F
- [CONVERGANCE-SIGMA0-BRIEFING.md](CONVERGANCE-SIGMA0-BRIEFING.md) — North Star
- [autowork-worktree.js](../apps/lantern-garage/lib/autowork-worktree.js) — issue isolation
- [keystone-runtime.js](../apps/lantern-garage/lib/keystone-runtime.js) — GROUND→PLAN→PATCH→VERIFY loop
- [provider-router.js](../apps/lantern-garage/lib/provider-router.js) — provider fallback chain
- Sub-issues: #894 #895 #896 #897 #898 #899
