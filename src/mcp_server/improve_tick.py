"""
improve_tick — ONE bounded pass of the autonomous improvement loop.

This is the honest form of the design's "REPEAT FOREVER". A tick does a single
pass — observe → verify prior work → converge the current lane → (act) → learn —
and then EXITS. "Forever" is an external scheduler (Windows Task Scheduler / cron)
invoking this on an interval, never an in-process while(True). All state lives in
the queue + append-only JSONL, so a tick is crash-safe and resumable.

Safety posture (read-mostly, gated):
- The tick NEVER opens PRs or merges. It investigates (read-only), verifies, and
  recommends. Actual code-writing stays with the worker behind the existing write
  gates; the tick only *pulls* the worker when LANTERN_TICK_AUTONOMOUS=1.
- Monoworkstream-aware: if a bot PR lane is already open and not green, the tick
  says "converge that lane" instead of starting new work (one PR per lane).
- Verification only ever *upgrades* the playbook (append-only); analyze() dedups
  so a verified entry supersedes the initial low-confidence one.

Registered as the MCP tool `improve_tick`; also runnable as a CLI for the
scheduler: `python src/mcp_server/improve_tick.py`.
"""
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

import engineering_playbook as ep
import confidence as cf

_CTX: Dict[str, Any] = {}
_MAX_VERIFY = 5                       # cap gh calls per tick when verifying prior PRs
TICK_FILE = "improve-tick-records.jsonl"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _repo_root() -> Any:
    return _CTX.get("repo_root", ".")


def _append():
    return _CTX.get("append_jsonl", lambda *a, **k: None)


def _tick_count() -> int:
    return len(ep._read_jsonl(Path(_repo_root()) / "data" / "convergence" / TICK_FILE))


def _record_tick(receipt: Dict[str, Any]) -> None:
    try:
        _append()(Path(_repo_root()) / "data" / "convergence" / TICK_FILE, receipt)
    except Exception:
        pass


def _verify_prior(ct, owner: str, repo: str) -> List[Dict[str, Any]]:
    """Re-check bot PRs we opened: if their checks are green, append a verified,
    high-confidence playbook entry — the fix is proven. Append-only; analyze()
    dedups so this supersedes the original low-confidence record."""
    root = _repo_root()
    entries = ep.read_entries(root)
    already = {(e.get("issue"), e.get("pr")) for e in entries if e.get("verified")}
    seen, candidates = set(), []
    for e in entries:
        pr = e.get("pr")
        if e.get("outcome") != "pr_opened" or not pr:
            continue
        key = (e.get("issue"), pr)
        if key in already or key in seen:
            continue
        seen.add(key)
        candidates.append(e)

    upgraded: List[Dict[str, Any]] = []
    for e in candidates[:_MAX_VERIFY]:
        try:
            st = ct.github_pr_status(owner, repo, int(e["pr"]))
        except Exception:
            continue
        if not st.get("ok") or st.get("status") != "ready":
            continue
        conf = cf.compute({"checks_green": True, "has_changes": True,
                           "prior_pattern": True, "issue_specified": True})
        entry = ep.build_entry(
            surface=e.get("surface", "improve_tick"), problem=e.get("problem", ""),
            root_cause=e.get("root_cause", ""), solution=e.get("solution", ""),
            files=e.get("files", []), outcome="verified", issue=e.get("issue"),
            pr=e["pr"], branch=e.get("branch"), confidence=conf["confidence"], verified=True)
        entry["signature"] = e.get("signature", entry["signature"])  # cluster with the original
        ep.record(root, _append(), entry)
        upgraded.append({"pr": e["pr"], "confidence": conf["confidence"]})
    return upgraded


def improve_tick(max_actions: int = 1, self_improve_every: int = 5) -> Dict[str, Any]:
    """Run one observe → verify → converge → (act) → learn pass, then return.
    Read-mostly and safe to schedule. Autonomous worker pickup is opt-in via
    LANTERN_TICK_AUTONOMOUS=1 (and still gated by the existing write gates)."""
    import convergence_tools as ct  # loaded by the server before us → no import cycle
    owner, repo = ct._default_repo()
    tick_no = _tick_count() + 1
    steps: List[Dict[str, Any]] = []

    # 1) OBSERVE
    obs = ct.convergence_run(mode="triage")
    tri = ct.github_triage_prs(owner, repo)
    steps.append({"stage": "observe", "summary": obs.get("summary"),
                  "recommended": obs.get("recommended_next_action")})

    # 2) VERIFY prior work → upgrade the playbook when our PRs went green
    upgraded = _verify_prior(ct, owner, repo)
    steps.append({"stage": "verify", "upgraded": upgraded})

    # 3) CONVERGE LANE (monoworkstream): is a bot PR already open and not green?
    bot_open = [p for p in (tri.get("prs") or [])
                if str(p.get("branch", "")).startswith(ct.BOT_PREFIX) and p.get("status") != "ready"]
    lane_busy = bool(bot_open)

    # 4) ACT — never opens PRs here. Investigate the top issue (read-only) when the
    #    lane is free; pull the worker only when autonomous mode is enabled.
    autonomous = os.getenv("LANTERN_TICK_AUTONOMOUS", "0") in ("1", "true", "True")
    if lane_busy:
        act = {"stage": "act", "decision": "converge_current_lane",
               "pr": bot_open[0].get("number"), "next": bot_open[0].get("next_action")}
    else:
        top = obs.get("top_issues") or []
        num = top[0].get("number") if top else None
        if num is not None:
            inv = ct.github_work_issue(owner, repo, int(num), mode="investigate")
            act = {"stage": "act", "decision": "investigated_top_issue", "issue": num,
                   "confidence": inv.get("confidence"),
                   "prior_patterns": len(inv.get("prior_patterns") or [])}
            if autonomous:
                act["worker"] = ct.worker_tick(max_actions)
        else:
            act = {"stage": "act", "decision": "idle",
                   "recommended": obs.get("recommended_next_action")}
    steps.append(act)

    # 5) SELF-IMPROVE (periodic)
    improve = None
    if self_improve_every and tick_no % int(self_improve_every) == 0:
        improve = ct.playbook_analyze(min_occurrences=2)
        steps.append({"stage": "self_improve", "recurring": improve.get("recurring")})

    # 6) RECORD (append-only tick receipt)
    receipt = {"timestamp": _now(), "surface": "improve_tick", "tick": tick_no,
               "lane_busy": lane_busy, "verified_upgrades": len(upgraded),
               "decision": act.get("decision"), "autonomous": autonomous,
               "recommended": obs.get("recommended_next_action"),
               "self_improve_recurring": (improve.get("recurring") if improve else None)}
    _record_tick(receipt)
    return {"ok": True, "tick": tick_no, "lane_busy": lane_busy, "autonomous": autonomous,
            "steps": steps, "receipt": receipt}


# ── Registration ──────────────────────────────────────────────────────────────
def register(registry: Dict[str, Any], ctx: Dict[str, Any]) -> List[str]:
    """Wire context (repo_root, append_jsonl, …) and expose the improve_tick tool."""
    _CTX.update(ctx)
    registry["improve_tick"] = improve_tick
    return ["improve_tick"]


# ── CLI entrypoint (what the external scheduler invokes) ──────────────────────
def run_cli(argv: List[str] = None) -> Dict[str, Any]:
    """Run exactly one tick, print JSON, and return. 'Forever' is the schedule
    that calls this — there is deliberately no loop here."""
    import json as _json
    import sys
    here = Path(__file__).resolve()
    sys.path.insert(0, str(here.parent))          # flat imports (convergence_tools, github_tools)
    repo_root = here.parents[2]                     # src/mcp_server/improve_tick.py → repo root

    def _append(path, obj):
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "a", encoding="utf-8") as fh:
            fh.write(_json.dumps(obj) + "\n")
        return True

    import convergence_tools as ct
    ctx = {"repo_root": repo_root, "append_jsonl": _append, "task_queue": [], "run_task": None}
    ct.register({}, ctx)        # wire the convergence tools' context
    register({}, ctx)           # wire ours
    out = improve_tick()
    print(_json.dumps(out, indent=2, default=str))
    return out


if __name__ == "__main__":
    run_cli()
