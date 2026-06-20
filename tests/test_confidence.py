"""Unit tests for evidence-based confidence scoring (offline, pure)."""
import sys
from pathlib import Path

_MCP = Path(__file__).resolve().parents[1] / "src" / "mcp_server"
sys.path.insert(0, str(_MCP))

import confidence as cf  # noqa: E402


def test_no_evidence_is_capped_low():
    r = cf.compute({})
    assert r["capped"] == "no_changes"
    assert r["confidence"] < cf.REVIEW_THRESHOLD
    assert r["needs_human_review"] is True


def test_investigation_cannot_look_done():
    # Strong investigation signals but no changes/verification → still < needs-review.
    r = cf.compute({"prior_pattern": True, "issue_specified": True, "reproduction": True})
    assert r["confidence"] < cf.REVIEW_THRESHOLD
    assert r["capped"] == "no_changes"


def test_unverified_change_is_medium_not_high():
    r = cf.compute({"has_changes": True, "prior_pattern": True,
                    "issue_specified": True, "small_change": True})
    assert cf.REVIEW_THRESHOLD <= r["confidence"] < cf.FILE_THRESHOLD
    assert r["tier"] == "medium"
    assert r["needs_human_review"] is True          # opening a PR is never auto-file-worthy


def test_verification_reaches_high():
    r = cf.compute({"checks_green": True, "has_changes": True,
                    "prior_pattern": True, "issue_specified": True})
    assert r["confidence"] >= cf.FILE_THRESHOLD
    assert r["tier"] == "high"
    assert r["needs_human_review"] is False


def test_refused_floors_confidence():
    r = cf.compute({"refused": True, "error": "writes disabled"})
    assert r["confidence"] == 0.1
    assert r["capped"] == "refused"


def test_factors_are_present_evidence():
    r = cf.compute({"has_changes": True, "checks_green": True})
    names = {f["name"] for f in r["factors"]}
    assert {"has_changes", "checks_green"} <= names    # the source of the claim


def test_from_issue_extracts_signals():
    ev = cf.from_issue(
        {"body": "x" * 100, "labels": ["bug"]},
        prior_patterns=[{"match_score": 0.6}], files=["a.py"])
    assert ev["issue_specified"] and ev["prior_pattern"]
    assert ev["has_changes"] and ev["small_change"]
    assert ev["reproduction"] is False
    ev2 = cf.from_issue({"body": "Traceback (most recent call last): boom"})
    assert ev2["reproduction"] is True


def test_from_checks_extracts_signals():
    ev = cf.from_checks(["CI", "Slop"], logs_tail="error: boom", files=["a.py"])
    assert ev["issue_specified"] and ev["reproduction"]
    assert ev["has_changes"] and ev["small_change"]
    assert cf.from_checks([], "", [])["has_changes"] is False
