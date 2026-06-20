"""
Confidence scoring — evidence-based, not a hardcoded constant.

Replaces the flat 0.3 the convergence work tools used to emit. Every score is
built from *observable signals*, each recorded as a {factor, weight, present}
triple, so the result satisfies the CLAUDE.md External Reality Rule:
[claim, evidence, confidence, source]. The factor breakdown IS the source.

Tiers come from engineering_playbook (single source of truth — the Keystone
charter): >= 0.8 file/act · 0.5–0.79 needs-review · 0.2–0.49 log · < 0.2 trivial.

Design intent (honesty): an *unverified* change can never look done. The only
factor that pushes a score into the high (auto-file) band is real verification —
green CI checks (checks_green) or passing local tests (tests_passed). Opening a
PR is, by itself, medium confidence at best until something confirms it works.

Pure stdlib, offline-testable.
"""
from typing import Any, Dict, List

from engineering_playbook import confidence_tier, FILE_THRESHOLD, REVIEW_THRESHOLD

BASE = 0.1  # start skeptical — nothing is assumed without evidence

# factor → weight. Presence is read from the evidence dict (truthy = present).
# Only verification (checks_green / tests_passed) can lift a score into the
# high band; everything else tops out in needs-review without it.
WEIGHTS = {
    "checks_green":    0.50,  # CI confirmed the change — strongest signal
    "tests_passed":    0.35,  # local test suite passed
    "prior_pattern":   0.15,  # read-back found a similar past fix
    "issue_specified": 0.10,  # the problem has a real body / labels
    "has_changes":     0.10,  # actual file changes were produced
    "reproduction":    0.05,  # issue includes steps / error / logs
    "small_change":    0.05,  # <= 2 files touched (low blast radius)
}


def compute(evidence: Dict[str, Any]) -> Dict[str, Any]:
    """Score confidence in [0, 1] from an evidence dict. Returns the score, its
    tier, whether it needs human review, and the present factors (the source)."""
    ev = evidence or {}

    # Hard floor: a refusal or hard error is never confident.
    if ev.get("refused") or ev.get("error"):
        return _result(0.1, [{"name": "refused", "weight": 0.0, "present": True,
                              "detail": str(ev.get("error") or "refused")}], capped="refused")

    factors: List[Dict[str, Any]] = []
    score = BASE
    for name, weight in WEIGHTS.items():
        present = bool(ev.get(name))
        if present:
            score += weight
        factors.append({"name": name, "weight": weight, "present": present})

    # Hard cap: with no changes AND no external verification, nothing was proven
    # done — keep it below the needs-review boundary (log tier at most).
    capped = None
    if not ev.get("has_changes") and not ev.get("checks_green") and not ev.get("tests_passed"):
        score = min(score, REVIEW_THRESHOLD - 0.001)
        capped = "no_changes"

    score = max(0.0, min(1.0, round(score, 3)))
    return _result(score, factors, capped=capped)


def _result(score: float, factors: List[Dict[str, Any]], capped=None) -> Dict[str, Any]:
    present = [f for f in factors if f.get("present")]
    return {
        "confidence": score,
        "tier": confidence_tier(score),
        "needs_human_review": score < FILE_THRESHOLD,
        "factors": present or factors,
        "capped": capped,
        "thresholds": {"file": FILE_THRESHOLD, "review": REVIEW_THRESHOLD},
    }


# ── Evidence builders (keep signal extraction in one place, testable) ─────────
_REPRO_HINTS = ("repro", "steps to", "stack trace", "traceback", "error:", "exception", "logs", "stderr")


def from_issue(info: Dict[str, Any], prior_patterns: List[Dict[str, Any]] = None,
               files: List[str] = None, opened_pr: bool = False,
               checks_green: bool = False) -> Dict[str, Any]:
    """Build an evidence dict from an issue + what we did about it."""
    body = (info.get("body") or "")
    labels = info.get("labels") or []
    pp = prior_patterns or []
    files = files or []
    return {
        "checks_green": bool(checks_green),
        "prior_pattern": bool(pp) and float(pp[0].get("match_score", 0)) >= 0.3,
        "issue_specified": len(body) >= 80 or bool(labels),
        "reproduction": any(h in body.lower() for h in _REPRO_HINTS),
        "has_changes": bool(files),
        "small_change": 0 < len(files) <= 2,
    }


def from_checks(failing: List[str], logs_tail: str = "", files: List[str] = None,
                checks_green: bool = False) -> Dict[str, Any]:
    """Build an evidence dict for a failing-checks repair."""
    files = files or []
    return {
        "checks_green": bool(checks_green),
        "issue_specified": bool(failing),          # we know exactly what's red
        "reproduction": bool(logs_tail),           # logs are the reproduction
        "has_changes": bool(files),
        "small_change": 0 < len(files) <= 2,
    }
