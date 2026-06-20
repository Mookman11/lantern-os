"""Unit/wiring tests for the bounded autonomous improve_tick (offline)."""
import sys
import json
from pathlib import Path

import pytest

_MCP = Path(__file__).resolve().parents[1] / "src" / "mcp_server"
sys.path.insert(0, str(_MCP))

import improve_tick as it  # noqa: E402
import convergence_tools as ct  # noqa: E402
import engineering_playbook as ep  # noqa: E402


def _appender():
    def _a(path, obj):
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "a", encoding="utf-8") as f:
            f.write(json.dumps(obj) + "\n")
        return True
    return _a


def _wire(repo_root):
    it.register({}, {"repo_root": Path(repo_root), "append_jsonl": _appender(),
                     "task_queue": [], "run_task": None})


def _stub_ct(monkeypatch, prs=None, top_issues=None, pr_status=None):
    monkeypatch.setattr(ct, "convergence_run", lambda **k: {
        "summary": "s", "recommended": "do x", "top_issues": top_issues or []})
    monkeypatch.setattr(ct, "github_triage_prs", lambda *a, **k: {"ok": True, "prs": prs or []})
    monkeypatch.setattr(ct, "github_work_issue",
                        lambda *a, **k: {"confidence": 0.4, "prior_patterns": []})
    monkeypatch.setattr(ct, "github_pr_status",
                        lambda o, r, n: pr_status or {"ok": True, "status": "ready"})


def test_tick_investigates_top_issue_when_lane_free(tmp_path, monkeypatch):
    _wire(tmp_path)
    _stub_ct(monkeypatch, prs=[], top_issues=[{"number": 42, "title": "t"}])
    r = it.improve_tick()
    assert r["ok"] and r["tick"] == 1 and r["lane_busy"] is False
    act = [s for s in r["steps"] if s["stage"] == "act"][0]
    assert act["decision"] == "investigated_top_issue" and act["issue"] == 42
    # tick receipt persisted
    recs = ep._read_jsonl(tmp_path / "data" / "convergence" / it.TICK_FILE)
    assert len(recs) == 1 and recs[0]["decision"] == "investigated_top_issue"


def test_tick_converges_busy_bot_lane(tmp_path, monkeypatch):
    _wire(tmp_path)
    _stub_ct(monkeypatch, prs=[{"number": 7, "branch": "mcp/issue-7",
                                "status": "blocked", "next_action": "fix checks"}])
    r = it.improve_tick()
    assert r["lane_busy"] is True
    act = [s for s in r["steps"] if s["stage"] == "act"][0]
    assert act["decision"] == "converge_current_lane" and act["pr"] == 7


def test_tick_verifies_prior_pr_and_upgrades_playbook(tmp_path, monkeypatch):
    _wire(tmp_path)
    ep.record(tmp_path, _appender(), ep.build_entry(
        surface="github_work_issue", problem="null guard parser", files=["p.py"],
        outcome="pr_opened", issue=5, pr=10, confidence=0.5, verified=False))
    _stub_ct(monkeypatch, prs=[], top_issues=[],
             pr_status={"ok": True, "status": "ready"})
    r = it.improve_tick()
    verify = [s for s in r["steps"] if s["stage"] == "verify"][0]
    assert len(verify["upgraded"]) == 1 and verify["upgraded"][0]["pr"] == 10
    entries = ep.read_entries(tmp_path)
    verified = [e for e in entries if e.get("verified")]
    assert len(verified) == 1 and verified[0]["confidence"] >= 0.8
    assert verified[0]["signature"] == entries[0]["signature"]   # clusters with original


def test_tick_does_not_upgrade_when_pr_not_green(tmp_path, monkeypatch):
    _wire(tmp_path)
    ep.record(tmp_path, _appender(), ep.build_entry(
        surface="github_work_issue", problem="x", outcome="pr_opened", pr=11,
        confidence=0.5))
    _stub_ct(monkeypatch, pr_status={"ok": True, "status": "blocked"})
    r = it.improve_tick()
    assert [s for s in r["steps"] if s["stage"] == "verify"][0]["upgraded"] == []
    assert [e for e in ep.read_entries(tmp_path) if e.get("verified")] == []


def test_tick_runs_self_improve_on_schedule(tmp_path, monkeypatch):
    _wire(tmp_path)
    _stub_ct(monkeypatch, top_issues=[])
    called = {}

    def fake_analyze(**k):
        called["hit"] = True
        return {"recurring": 2}

    monkeypatch.setattr(ct, "playbook_analyze", fake_analyze)
    r = it.improve_tick(self_improve_every=1)          # tick 1 % 1 == 0 → fires
    assert called.get("hit") is True
    assert any(s["stage"] == "self_improve" for s in r["steps"])


def test_lantern_command_routes_improve(tmp_path, monkeypatch):
    _wire(tmp_path)
    _stub_ct(monkeypatch, top_issues=[])
    # convergence_tools owns lantern_command; it lazily imports improve_tick.
    ct.register({}, {"task_queue": [], "run_task": lambda t: {},
                     "append_jsonl": _appender(), "repo_root": Path(tmp_path)})
    r = ct.lantern_command("!improve")
    assert r["ok"] and r["routed_to"] == "improve_tick"
