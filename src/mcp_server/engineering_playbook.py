"""
Engineering Playbook — the LEARN + SELF-IMPROVEMENT stages of the work loop.

The convergence work tools (github_work_issue / github_fix_failed_checks) already
write durable *receipts* to data/convergence/{issue,pr}-work-records.jsonl — but
nothing ever read them back, so the worker kept re-solving the same class of
problem. This module closes that loop:

  LEARN            distill each real fix (patch / PR) into a reusable pattern and
                   append it to data/convergence/engineering-playbook.jsonl.
  READ-BACK        at investigate (UNDERSTAND) time, retrieve the most similar
                   prior patterns so the agent reasons from past solutions.
  SELF-IMPROVEMENT cluster the playbook by signature to surface recurring
                   failures / weak modules and propose maintenance issues.

This is *persistent learning, not weight modification* (per CLAUDE.md): the loop
improves by retrieval over an append-only log, never by retraining.

Pure library — stdlib only, no network, no import of convergence_tools (the
workflow layer imports THIS). IO is injected (`append_jsonl`, `repo_root`) the
same way the convergence tools receive their context, so every function here is
unit-testable offline.

Confidence tiers mirror the Keystone thresholds in CLAUDE.md:
  >= 0.8 file/act · 0.5–0.79 needs-review · 0.2–0.49 log · < 0.2 trivial
"""

import re
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

# ── Confidence tiers (Keystone charter, CLAUDE.md) ────────────────────────────
FILE_THRESHOLD = 0.8     # >= this → high confidence, safe to act/file automatically
REVIEW_THRESHOLD = 0.5   # >= this (but < FILE) → needs human review
TRIVIAL_THRESHOLD = 0.2  # < this → trivial, discard

PLAYBOOK_FILE = "engineering-playbook.jsonl"
_REAL_OUTCOMES = ("pr_opened", "patched")  # outcomes that represent an actual fix

_STOPWORDS = frozenset({
    "the", "and", "for", "with", "from", "this", "that", "into", "onto", "only",
    "not", "are", "was", "were", "has", "have", "had", "via", "per", "out", "off",
    "issue", "pull", "request", "automated", "patch", "plan", "repo", "branch",
})
_TOKEN_RE = re.compile(r"[a-z][a-z0-9]{2,}")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ── Tokenisation + signature (clustering / lookup key) ────────────────────────
def _tokens(text: str) -> List[str]:
    """Lowercase word tokens (len >= 3, alpha-initial), stopwords removed."""
    return [t for t in _TOKEN_RE.findall((text or "").lower()) if t not in _STOPWORDS]


def signature(parts: Iterable[Any]) -> str:
    """Deterministic clustering key: unique, sorted, stopword-free tokens of the
    joined parts. Two problems with the same signature are 'the same kind'."""
    joined = " ".join(str(p) for p in parts if p)
    return " ".join(sorted(set(_tokens(joined))))


# ── Entry construction (no IO) ────────────────────────────────────────────────
def build_entry(
    *,
    surface: str,
    problem: str,
    root_cause: str = "",
    solution: str = "",
    files: Optional[Iterable[str]] = None,
    outcome: str = "",
    pattern: str = "",
    issue: Any = None,
    pr: Any = None,
    branch: Any = None,
    confidence: float = 0.3,
    verified: bool = False,
    tests_added: Any = None,
    signature_parts: Optional[Iterable[Any]] = None,
    timestamp: Optional[str] = None,
) -> Dict[str, Any]:
    """Build one normalized playbook entry. Pure — callers do the IO via record()."""
    files = list(files or [])
    sig_parts = list(signature_parts) if signature_parts is not None else [problem, root_cause, *files]
    return {
        "timestamp": timestamp or _now(),
        "surface": surface,
        "problem": (problem or "").strip()[:240],
        "signature": signature(sig_parts),
        "root_cause": (root_cause or "").strip()[:400],
        "solution": (solution or "").strip()[:400],
        "files": files,
        "tests_added": tests_added if tests_added is not None else [],
        "pattern": (pattern or _derive_pattern(outcome, problem)).strip()[:200],
        "outcome": outcome or "investigated",
        "issue": issue,
        "pr": pr,
        "branch": branch,
        "confidence": float(confidence),
        "verified": bool(verified),
    }


def _derive_pattern(outcome: str, problem: str) -> str:
    return f"[{outcome or 'investigated'}] {(problem or '').strip()}"[:200]


# ── Distill a thin work-receipt into a playbook entry ─────────────────────────
def _files_from_actions(actions: Iterable[str]) -> List[str]:
    seen: List[str] = []
    for a in actions or []:
        if isinstance(a, str) and a.startswith("push_files:"):
            for f in a.split(":", 1)[1].split(","):
                f = f.strip()
                if f and f not in seen:
                    seen.append(f)
    return seen


def _outcome_from(actions: Iterable[str], result: str) -> str:
    acts = [a for a in (actions or []) if isinstance(a, str)]
    res = (result or "").lower()
    if any(a.startswith("create_pull_request") for a in acts):
        return "pr_opened"
    if any(a.startswith("push_files") for a in acts):
        return "patched"
    if "refus" in res:
        return "refused"
    if "fail" in res:
        return "failed"
    return "investigated"


def _solution_from_actions(actions: Iterable[str]) -> str:
    keep = {"create_branch", "push_files", "create_pull_request"}
    meaningful = [a for a in (actions or []) if isinstance(a, str) and a.split(":", 1)[0] in keep]
    return "; ".join(meaningful)


def distill(receipt: Dict[str, Any]) -> Dict[str, Any]:
    """Transform a github_work_issue / github_fix_failed_checks receipt into a
    playbook entry. Preserves the receipt timestamp so backfill is idempotent."""
    actions = receipt.get("actions_taken") or []
    result = receipt.get("result", "") or ""
    plan = receipt.get("fix_plan", "") or ""
    issue = receipt.get("issue")
    pr = receipt.get("pr")
    outcome = _outcome_from(actions, result)
    problem = (plan.split(".")[0].strip() if plan else "") or (
        f"issue #{issue}" if issue else (f"PR #{pr}" if pr else "unknown"))
    return build_entry(
        surface=receipt.get("surface", "unknown"),
        problem=problem,
        root_cause=plan,
        solution=_solution_from_actions(actions) or result,
        files=_files_from_actions(actions),
        outcome=outcome,
        issue=issue,
        pr=pr,
        branch=receipt.get("branch"),
        confidence=float(receipt.get("confidence", 0.3) or 0.3),
        verified=bool(receipt.get("verified", False)),
        timestamp=receipt.get("timestamp"),
    )


# ── Store IO ──────────────────────────────────────────────────────────────────
def _playbook_path(repo_root: Any) -> Path:
    return Path(repo_root) / "data" / "convergence" / PLAYBOOK_FILE


def _read_jsonl(path: Path) -> List[Dict[str, Any]]:
    """Tolerant JSONL reader — missing file → [], bad lines skipped."""
    out: List[Dict[str, Any]] = []
    try:
        with open(path, "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except (ValueError, json.JSONDecodeError):
                    continue
                if isinstance(obj, dict):
                    out.append(obj)
    except FileNotFoundError:
        return []
    except OSError:
        return []
    return out


def read_entries(repo_root: Any) -> List[Dict[str, Any]]:
    """All playbook entries (append-only log)."""
    return _read_jsonl(_playbook_path(repo_root))


def record(repo_root: Any, append_jsonl, entry: Dict[str, Any]) -> Dict[str, Any]:
    """Append one entry to the playbook via the injected append_jsonl(path, obj)."""
    entry.setdefault("timestamp", _now())
    if not entry.get("signature"):
        entry["signature"] = signature([entry.get("problem", ""), *(entry.get("files") or [])])
    append_jsonl(_playbook_path(repo_root), entry)
    return entry


# ── READ-BACK: retrieve prior patterns for the UNDERSTAND stage ───────────────
def lookup(repo_root: Any, query_parts: Iterable[Any], k: int = 3,
           min_score: float = 0.0) -> List[Dict[str, Any]]:
    """Return up to k prior playbook entries most similar to the query, ranked by
    Jaccard overlap of signature tokens. Empty query or empty store → []."""
    q = set(_tokens(" ".join(str(p) for p in query_parts if p)))
    if not q:
        return []
    scored = []
    for idx, e in enumerate(read_entries(repo_root)):
        toks = set(_tokens(e.get("signature") or ""))
        inter = len(q & toks)
        if not inter:
            continue
        score = inter / len(q | toks)
        if score > min_score:
            scored.append((score, idx, e))
    scored.sort(key=lambda t: (-t[0], -t[1]))   # best score, then most recent
    return [{**e, "match_score": round(score, 3)} for score, _idx, e in scored[: max(1, int(k))]]


# ── SELF-IMPROVEMENT: cluster recurring patterns → maintenance proposals ──────
def confidence_tier(confidence: float) -> str:
    if confidence >= FILE_THRESHOLD:
        return "high"
    if confidence >= REVIEW_THRESHOLD:
        return "medium"
    if confidence >= TRIVIAL_THRESHOLD:
        return "low"
    return "trivial"


def _proposal_body(top_tokens: List[str], n: int, members: List[Dict[str, Any]],
                   files: List[str], issues: List[int], prs: List[int],
                   outcomes: Dict[str, int]) -> str:
    rep = next((m.get("root_cause") for m in members if m.get("root_cause")), "")
    lines = [
        f"**Recurring engineering pattern** — seen {n}× (signature: `{' '.join(top_tokens)}`).",
        "",
        f"- Outcomes: {', '.join(f'{k}×{v}' for k, v in outcomes.items())}",
    ]
    if issues:
        lines.append(f"- Related issues: {', '.join('#' + str(i) for i in issues)}")
    if prs:
        lines.append(f"- Related PRs: {', '.join('#' + str(p) for p in prs)}")
    if files:
        lines.append(f"- Files repeatedly touched: {', '.join('`' + f + '`' for f in files[:12])}")
    if rep:
        lines.append(f"- Representative root cause: {rep}")
    lines += [
        "",
        "**Suggested maintenance:** address the shared root cause once (refactor / "
        "guard / test) so this class of work stops recurring.",
        "",
        "_Filed by engineering_playbook self-improvement. Evidence-grounded; "
        "verify before acting._",
    ]
    return "\n".join(lines)


def analyze(repo_root: Any, min_occurrences: int = 2) -> Dict[str, Any]:
    """Cluster the playbook by signature and return recurring patterns as
    maintenance proposals. Read-only. Low-confidence / unverified clusters are
    flagged needs_human_review (never auto-filed) per the Keystone thresholds."""
    try:
        min_occurrences = max(2, int(min_occurrences))
    except (TypeError, ValueError):
        min_occurrences = 2
    entries = read_entries(repo_root)
    clusters: Dict[str, List[Dict[str, Any]]] = {}
    for e in entries:
        clusters.setdefault(e.get("signature", ""), []).append(e)

    proposals: List[Dict[str, Any]] = []
    for sig, members in clusters.items():
        if not sig or len(members) < min_occurrences:
            continue
        n = len(members)
        confs = [float(m.get("confidence", 0) or 0) for m in members]
        conf = round(sum(confs) / len(confs), 3) if confs else 0.0
        verified_all = all(m.get("verified") for m in members)
        files: List[str] = []
        for m in members:
            for f in (m.get("files") or []):
                if f not in files:
                    files.append(f)
        issues = sorted({m["issue"] for m in members if m.get("issue")})
        prs = sorted({m["pr"] for m in members if m.get("pr")})
        outcomes = dict(Counter(m.get("outcome", "investigated") for m in members))
        top_tokens = sig.split()[:4]
        needs_review = conf < FILE_THRESHOLD or not verified_all
        title = f"Recurring: {' '.join(top_tokens)} ({n}×)"
        proposals.append({
            "signature": sig,
            "occurrences": n,
            "confidence": conf,
            "confidence_tier": confidence_tier(conf),
            "needs_human_review": needs_review,
            "files": files,
            "issues": issues,
            "prs": prs,
            "outcomes": outcomes,
            "suggested_issue": {
                "title": title,
                "body": _proposal_body(top_tokens, n, members, files, issues, prs, outcomes),
                "labels": "maintenance,self-improvement,sigma0-grounded",
            },
        })
    proposals.sort(key=lambda p: (-p["occurrences"], -p["confidence"]))
    return {
        "ok": True,
        "clusters": len([s for s in clusters if s]),
        "recurring": len(proposals),
        "proposals": proposals,
        "min_occurrences": min_occurrences,
        "thresholds": {"file": FILE_THRESHOLD, "review": REVIEW_THRESHOLD},
    }


# ── Backfill: distill existing work-receipt logs into the playbook ────────────
def backfill(repo_root: Any, append_jsonl) -> Dict[str, Any]:
    """One-shot import of past github_work_issue / github_fix_failed_checks
    receipts into the playbook. Idempotent: dedupes on (surface, issue, pr,
    timestamp), and only real fixes (patched / pr_opened) are kept."""
    existing = read_entries(repo_root)
    seen = {(e.get("surface"), e.get("issue"), e.get("pr"), e.get("timestamp")) for e in existing}
    scanned = added = 0
    conv = Path(repo_root) / "data" / "convergence"
    for kind in ("issue", "pr"):
        for rec in _read_jsonl(conv / f"{kind}-work-records.jsonl"):
            scanned += 1
            entry = distill(rec)
            if entry.get("outcome") not in _REAL_OUTCOMES:
                continue
            key = (entry.get("surface"), entry.get("issue"), entry.get("pr"), entry.get("timestamp"))
            if key in seen:
                continue
            record(repo_root, append_jsonl, entry)
            seen.add(key)
            added += 1
    return {"ok": True, "scanned": scanned, "added": added, "total": len(existing) + added}
