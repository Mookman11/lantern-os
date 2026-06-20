"""
Grounding measurement (Verify-stage primitive) — issue #731 Phase 3.

The Convergence Core's External Reality Rule says *nothing is accepted without
evidence*. This module turns that rule into a measurable signal: given a model
reply, how many of its concrete references actually resolve to real artifacts in
the repository, and how many are invented?

It is deliberately objective and offline — no LLM judge, no network. A reference
is "grounded" only if it can be verified against the checkout:

  - **Path references** (e.g. ``src/serving_modes.py``) are grounded iff the file
    exists on disk under ``repo_root``. A path that does not exist is recorded as
    a *hallucinated* reference — the model claimed a file that is not there.
  - **Glossary references** are distinctive, real Lantern OS identifiers
    (component names, module basenames, core concepts). They cannot be
    hallucinated by construction, so they measure *coverage* of real concepts,
    not accuracy.

Headline metrics (see :func:`score_grounding`):
  - ``path_grounding_accuracy`` — of the file paths the reply cited, the fraction
    that are real. ``None`` when the reply cited no paths (it made no checkable
    file claim). This is the "grounding accuracy" the issue asks for.
  - ``grounding_score`` — a single comparable 0..1 number,
    ``grounded / (grounded + hallucinated + 1)``: rewards verifiable references,
    penalizes invented ones, and keeps a reply that cites nothing near 0.

This is a serving-quality measure, not a Convergence Record. It strengthens the
Verify stage; it does not add a parallel memory system.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List, Optional

# Top-level directories a real repo path can start with. Anchoring on these keeps
# the path regex from matching version strings ("70-85s"), URLs, or prose.
_REPO_DIRS = (
    "src", "apps", "docs", "tests", "scripts", "data", "lib", "services",
    "config", "csf", "caad", "skills", "experiments", "routes",
)

# A path reference: a known top-level dir, one or more segments, ending in a
# file with an extension. Forward slashes only (pathlib resolves them on Windows).
_PATH_RE = re.compile(
    r"\b(?:" + "|".join(_REPO_DIRS) + r")/[\w./-]*\w+\.\w{1,6}\b"
)

# Distinctive, real Lantern OS identifiers. Referencing one is evidence the reply
# is talking about *this* system, not a generic one. Kept specific on purpose —
# bare words like "memory" or "reason" would over-credit. Matched case-insensitively
# as whole tokens/phrases. These are curated facts about the repo, verified by the
# accompanying tests (test_grounding.py asserts the module basenames exist).
GLOSSARY: tuple[str, ...] = (
    # Core architecture
    "convergence core", "convergence record", "external reality rule",
    "observe → converge", "observe->converge", "observe→converge",
    # Serving subsystem (Phase 1-3)
    "serving_modes.py", "serving_benchmark.py", "serving_modes", "serving_benchmark",
    "unified_agent_connector.py", "unified_agent_connector", "unifiedagentconnector",
    "ouro_native", "fast mode", "deep mode", "q-exit", "leaderboard.jsonl",
    # Garage / product modules
    "lantern-garage", "dream-chat.js", "dreamer-store.js", "conversation-store.js",
    "rag-house.js", "stream-chat.js", "file-queue.js", "dream-chat",
    # Memory / archive
    "csf archive", "csf", "mcp server", "agent-profiles.json",
)

# Glossary entries that are module basenames; the test suite verifies each names a
# file that really exists, so the glossary never silently rots into fiction.
GLOSSARY_FILES: tuple[str, ...] = (
    "serving_modes.py", "serving_benchmark.py", "unified_agent_connector.py",
    "dream-chat.js", "dreamer-store.js", "conversation-store.js",
    "rag-house.js", "stream-chat.js", "file-queue.js",
)


def extract_grounding_anchors(text: str) -> Dict[str, List[str]]:
    """Pull candidate references out of a reply.

    Returns ``{"paths": [...], "glossary": [...]}`` — ``paths`` are raw path-like
    tokens (not yet checked for existence); ``glossary`` is the distinct real
    identifiers mentioned. Both are de-duplicated, order-stable.
    """
    lower = text.lower()

    paths: List[str] = []
    for m in _PATH_RE.finditer(text):
        p = m.group(0)
        if p not in paths:
            paths.append(p)

    matched = [term for term in GLOSSARY if term in lower]
    # Drop a term that is a substring of another matched term ("serving_modes" when
    # "serving_modes.py" also matched) so one concept is not counted twice.
    glossary: List[str] = []
    for term in matched:
        if any(term != other and term in other for other in matched):
            continue
        if term not in glossary:
            glossary.append(term)

    return {"paths": paths, "glossary": glossary}


def _path_exists(repo_root: Path, rel: str) -> bool:
    """True if ``rel`` (a forward-slash repo path) resolves to a real file.

    Guards against ``..`` escapes so a reply can never probe outside the checkout.
    """
    candidate = (repo_root / rel).resolve()
    try:
        candidate.relative_to(repo_root.resolve())
    except ValueError:
        return False
    return candidate.is_file()


def score_grounding(text: str, repo_root: Path | str) -> Dict[str, Any]:
    """Measure how grounded a reply is against the repository at ``repo_root``.

    Every concrete file path is checked for existence; invented paths count
    against the reply. Glossary references add verifiable coverage. See module
    docstring for metric definitions.
    """
    repo_root = Path(repo_root)
    anchors = extract_grounding_anchors(text)

    grounded_paths: List[str] = []
    hallucinated_paths: List[str] = []
    for p in anchors["paths"]:
        (grounded_paths if _path_exists(repo_root, p) else hallucinated_paths).append(p)

    # A glossary basename that names the same file as a grounded path is the same
    # reference — don't count it twice (e.g. cited "src/serving_modes.py" AND
    # "serving_modes.py" in prose).
    grounded_basenames = {Path(p).name.lower() for p in grounded_paths}
    glossary_hits = [g for g in anchors["glossary"] if g.lower() not in grounded_basenames]
    grounded = len(grounded_paths) + len(glossary_hits)
    hallucinated = len(hallucinated_paths)

    cited_paths = len(anchors["paths"])
    path_grounding_accuracy: Optional[float] = (
        round(len(grounded_paths) / cited_paths, 3) if cited_paths else None
    )

    word_count = max(len(text.split()), 1)
    grounding_density = round(grounded / (word_count / 100.0), 3)
    grounding_score = round(grounded / (grounded + hallucinated + 1), 3)

    return {
        "grounding_score": grounding_score,
        "path_grounding_accuracy": path_grounding_accuracy,
        "grounding_density_per_100w": grounding_density,
        "grounded_refs": grounded,
        "hallucinated_paths_count": hallucinated,
        "cited_paths": anchors["paths"],
        "grounded_paths": grounded_paths,
        "hallucinated_paths": hallucinated_paths,
        "glossary_hits": glossary_hits,
        "word_count": word_count,
    }


def aggregate_grounding(scores: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Aggregate per-reply grounding scores into run-level means.

    ``avg_path_grounding_accuracy`` averages only over replies that cited at least
    one path (a reply that names no file has no accuracy to average).
    """
    if not scores:
        return {}
    accuracies = [s["path_grounding_accuracy"] for s in scores
                  if s.get("path_grounding_accuracy") is not None]
    n = len(scores)
    return {
        "avg_grounding_score": round(sum(s["grounding_score"] for s in scores) / n, 3),
        "avg_grounding_density_per_100w": round(
            sum(s["grounding_density_per_100w"] for s in scores) / n, 3),
        "avg_path_grounding_accuracy": (
            round(sum(accuracies) / len(accuracies), 3) if accuracies else None),
        "replies_citing_paths": len(accuracies),
        "total_grounded_refs": sum(s["grounded_refs"] for s in scores),
        "total_hallucinated_paths": sum(s["hallucinated_paths_count"] for s in scores),
    }
