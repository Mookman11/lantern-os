"""Unit + wiring tests for the engineering playbook (LEARN + self-improvement).

Offline: gh is stubbed, IO goes to a tmp repo_root. Mirrors the path setup in
test_mcp_convergence_tools.py so the flat `import engineering_playbook` resolves.
"""
import sys
import json
from pathlib import Path

import pytest

_MCP = Path(__file__).resolve().parents[1] / "src" / "mcp_server"
sys.path.insert(0, str(_MCP))

import engineering_playbook as ep  # noqa: E402
import convergence_tools as ct  # noqa: E402
import github_tools as gt  # noqa: E402


# ── helpers ───────────────────────────────────────────────────────────────────
def _appender():
    """A real append_jsonl(path, obj) that writes to disk (tests need true IO)."""
    def _append(path, obj):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(obj) + "\n")
        return True
    return _append


def _wire(repo_root, append=None):
    ct.register({}, {
        "task_queue": [],
        "run_task": lambda tid: {"ok": True, "status": "done", "confidence": 0.3},
        "append_jsonl": append or _appender(),
        "repo_root": Path(repo_root),
    })


def _issue_receipt(**kw):
    base = {"timestamp": "t", "surface": "github_work_issue", "issue": None, "pr": None,
            "branch": None, "actions_taken": [], "fix_plan": "", "evidence": [],
            "confidence": 0.3, "verified": False, "result": ""}
    base.update(kw)
    return base


# ── pure: tokenisation + signature ────────────────────────────────────────────
def test_signature_is_deterministic_and_stopword_free():
    s1 = ep.signature(["Async race condition in the queue worker"])
    s2 = ep.signature(["worker queue condition race async"])  # reordered
    assert s1 == s2                       # order-independent
    assert "the" not in s1.split()        # stopword removed
    assert "in" not in s1.split()         # short token removed
    assert "async" in s1.split() and "worker" in s1.split()


def test_confidence_tiers_match_keystone():
    assert ep.confidence_tier(0.85) == "high"
    assert ep.confidence_tier(0.5) == "medium"
    assert ep.confidence_tier(0.3) == "low"
    assert ep.confidence_tier(0.1) == "trivial"


# ── pure: build_entry + distill ───────────────────────────────────────────────
def test_build_entry_shape():
    e = ep.build_entry(surface="x", problem="State leak in store", files=["lib/store.js"],
                       outcome="patched", confidence=0.4)
    assert e["signature"] and isinstance(e["confidence"], float)
    assert e["files"] == ["lib/store.js"] and e["outcome"] == "patched"
    assert e["pattern"].startswith("[patched]")


def test_distill_pr_opened_from_issue_receipt():
    rec = _issue_receipt(issue=5, pr=10, branch="mcp/issue-5",
                         actions_taken=["investigate", "create_branch:mcp/issue-5",
                                        "push_files:a.py,b.py", "create_pull_request:#10"],
                         fix_plan="Null guard the parser. It crashed on empty input.",
                         result="PR #10 opened (not merged)")
    e = ep.distill(rec)
    assert e["outcome"] == "pr_opened"
    assert e["files"] == ["a.py", "b.py"] and e["issue"] == 5 and e["pr"] == 10
    assert e["problem"].startswith("Null guard the parser")
    assert e["timestamp"] == "t"               # receipt timestamp preserved


def test_distill_patched_and_refused():
    patched = ep.distill(_issue_receipt(surface="github_fix_failed_checks", pr=7,
                                        actions_taken=["inspect_checks", "push_files:c.py"],
                                        result="pushed to bot-owned branch"))
    assert patched["outcome"] == "patched"
    refused = ep.distill(_issue_receipt(actions_taken=["investigate"],
                                        result="refused: repo not allow-listed"))
    assert refused["outcome"] == "refused"


# ── read-back: lookup ranking ─────────────────────────────────────────────────
def test_lookup_ranks_by_signature_overlap(tmp_path):
    append = _appender()
    ep.record(tmp_path, append, ep.build_entry(
        surface="x", problem="async race condition in queue worker",
        files=["lib/queue.js"], outcome="patched"))
    ep.record(tmp_path, append, ep.build_entry(
        surface="x", problem="state leak in dream store immutable copy",
        files=["lib/store.js"], outcome="patched"))

    matches = ep.lookup(tmp_path, ["async race in the worker queue"], k=3)
    assert len(matches) == 1                        # the unrelated entry scores 0
    assert matches[0]["problem"].startswith("async race")
    assert matches[0]["match_score"] > 0

    assert ep.lookup(tmp_path, [""]) == []          # empty query → no matches


# ── self-improvement: analyze ─────────────────────────────────────────────────
def test_analyze_flags_recurring_and_needs_review(tmp_path):
    append = _appender()
    for _ in range(2):                               # same signature twice → recurring
        ep.record(tmp_path, append, ep.build_entry(
            surface="github_fix_failed_checks", problem="slop check failing on pull request",
            files=["scripts/slop.js"], outcome="patched", confidence=0.3))
    ep.record(tmp_path, append, ep.build_entry(      # singleton → not recurring
        surface="x", problem="unique one-off thing", outcome="patched"))

    report = ep.analyze(tmp_path, min_occurrences=2)
    assert report["recurring"] == 1
    p = report["proposals"][0]
    assert p["occurrences"] == 2
    assert p["needs_human_review"] is True           # conf 0.3 < 0.8 → never auto-file
    assert p["confidence_tier"] == "low"
    assert p["suggested_issue"]["title"].startswith("Recurring:")


# ── backfill: idempotent import of existing receipts ──────────────────────────
def test_backfill_imports_real_fixes_idempotently(tmp_path):
    conv = tmp_path / "data" / "convergence"
    conv.mkdir(parents=True)
    (conv / "issue-work-records.jsonl").write_text(
        json.dumps(_issue_receipt(issue=5, pr=10, timestamp="t1",
                                  actions_taken=["create_branch:mcp/issue-5", "push_files:a.py",
                                                 "create_pull_request:#10"],
                                  result="PR #10 opened")) + "\n" +
        json.dumps(_issue_receipt(issue=6, timestamp="t3", actions_taken=["investigate"],
                                  result="refused: writes disabled")) + "\n",
        encoding="utf-8")
    (conv / "pr-work-records.jsonl").write_text(
        json.dumps(_issue_receipt(surface="github_fix_failed_checks", pr=7, timestamp="t2",
                                  actions_taken=["inspect_checks", "push_files:b.py"],
                                  result="pushed")) + "\n",
        encoding="utf-8")

    first = ep.backfill(tmp_path, _appender())
    assert first["added"] == 2                       # the refused one is skipped
    again = ep.backfill(tmp_path, _appender())
    assert again["added"] == 0                        # idempotent on (surface, issue, pr, ts)
    assert len(ep.read_entries(tmp_path)) == 2


# ── wiring: convergence_tools integration ─────────────────────────────────────
def test_new_tools_registered():
    reg = {}
    ct.register(reg, {"task_queue": [], "run_task": lambda x: {},
                      "append_jsonl": lambda *a: True, "repo_root": Path(".")})
    for name in ("playbook_lookup", "playbook_analyze", "playbook_backfill"):
        assert name in reg


def test_record_auto_distills_real_fix(tmp_path):
    _wire(tmp_path)
    ct._record("issue", _issue_receipt(issue=5, pr=10, branch="mcp/issue-5",
                                       actions_taken=["push_files:x.py", "create_pull_request:#10"],
                                       fix_plan="fix the thing", result="PR #10 opened"))
    entries = ep.read_entries(tmp_path)
    assert len(entries) == 1 and entries[0]["outcome"] == "pr_opened" and entries[0]["pr"] == 10


def test_record_skips_investigation_only(tmp_path):
    _wire(tmp_path)
    ct._record("issue", _issue_receipt(issue=5, actions_taken=["investigate"],
                                       result="investigation only (no writes)"))
    assert ep.read_entries(tmp_path) == []            # nothing to learn from a read-only pass


def test_investigate_attaches_prior_patterns(tmp_path, monkeypatch):
    _wire(tmp_path)
    ep.record(tmp_path, _appender(), ep.build_entry(
        surface="x", problem="XSS vulnerability in image gallery",
        files=["public/gallery.js"], outcome="pr_opened"))
    monkeypatch.setattr(gt, "github_get_issue", lambda o, r, n: {
        "title": "XSS in image gallery", "state": "OPEN", "labels": ["security"], "body": "user input"})

    r = ct.github_work_issue("alex-place", "lantern-os", issue_number=42, mode="investigate")
    assert r["ok"] and "prior_patterns" in r
    assert len(r["prior_patterns"]) == 1
    assert "gallery" in r["prior_patterns"][0]["signature"]


def test_lantern_command_routes_playbook(tmp_path):
    _wire(tmp_path)
    assert ct.lantern_command("!self-improve")["routed_to"] == "playbook_analyze"
    r = ct.lantern_command("!playbook async race worker")
    assert r["routed_to"] == "playbook_lookup" and "matches" in r["result"]


# ── dedup: verification upgrades supersede, don't double-count ─────────────────
def test_dedup_collapses_same_issue_pr_to_best():
    low = ep.build_entry(surface="github_work_issue", problem="x", outcome="pr_opened",
                         issue=5, pr=10, confidence=0.5, verified=False)
    high = ep.build_entry(surface="github_work_issue", problem="x", outcome="verified",
                          issue=5, pr=10, confidence=0.9, verified=True)
    out = ep._dedup([low, high])
    assert len(out) == 1 and out[0]["verified"] and out[0]["confidence"] == 0.9


def test_dedup_keeps_distinct_and_unkeyed_entries():
    a = ep.build_entry(surface="x", problem="p1", outcome="patched", issue=1, pr=2, confidence=0.3)
    b = ep.build_entry(surface="x", problem="p2", outcome="patched", issue=3, pr=4, confidence=0.3)
    n1 = ep.build_entry(surface="x", problem="no keys a", outcome="patched")  # issue/pr None
    n2 = ep.build_entry(surface="x", problem="no keys b", outcome="patched")
    out = ep._dedup([a, b, n1, n2])
    assert len(out) == 4   # distinct keys + unkeyed both pass through
