"""
Tests for the grounding Verify-primitive (src/grounding.py, issue #731 Phase 3).

Grounding is the offline measure of the External Reality Rule: a reply's concrete
references are only credited if they resolve to real files/identifiers in the
checkout. These tests pin that behaviour — a real citation grounds, an invented
path is caught as a hallucination, and the curated glossary never silently rots
into fiction.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, "src")

import grounding as g  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[1]


# --------------------------------------------------------------------------- #
# Anchor extraction
# --------------------------------------------------------------------------- #
def test_extracts_repo_path_references():
    anchors = g.extract_grounding_anchors(
        "See src/serving_modes.py and docs/SERVING-ARCHITECTURE-2026.md for details.")
    assert "src/serving_modes.py" in anchors["paths"]
    assert "docs/SERVING-ARCHITECTURE-2026.md" in anchors["paths"]


def test_ignores_non_repo_paths_and_prose():
    anchors = g.extract_grounding_anchors(
        "Latency is 70-85s and the URL was http://example.com/foo. No repo path here.")
    assert anchors["paths"] == []


def test_glossary_substring_is_not_double_counted():
    # "serving_modes" is a substring of "serving_modes.py"; only the longer one counts.
    anchors = g.extract_grounding_anchors("The file serving_modes.py defines decode params.")
    assert "serving_modes.py" in anchors["glossary"]
    assert "serving_modes" not in anchors["glossary"]


# --------------------------------------------------------------------------- #
# Scoring against the real checkout
# --------------------------------------------------------------------------- #
def test_real_path_is_grounded():
    s = g.score_grounding("Decode params live in src/serving_modes.py.", REPO_ROOT)
    assert "src/serving_modes.py" in s["grounded_paths"]
    assert s["hallucinated_paths"] == []
    assert s["path_grounding_accuracy"] == 1.0
    assert s["grounding_score"] > 0


def test_invented_path_is_a_hallucination():
    s = g.score_grounding(
        "Memory is stored in src/memory_manager.py and src/brain/cortex.py.", REPO_ROOT)
    assert s["grounded_paths"] == []
    assert set(s["hallucinated_paths"]) == {"src/memory_manager.py", "src/brain/cortex.py"}
    assert s["path_grounding_accuracy"] == 0.0
    assert s["grounding_score"] == 0.0


def test_mixed_real_and_invented_paths_partial_accuracy():
    s = g.score_grounding(
        "It routes through src/unified_agent_connector.py, backed by src/nope_store.py.",
        REPO_ROOT)
    assert "src/unified_agent_connector.py" in s["grounded_paths"]
    assert "src/nope_store.py" in s["hallucinated_paths"]
    assert s["path_grounding_accuracy"] == 0.5


def test_reply_with_no_paths_has_none_accuracy():
    s = g.score_grounding("The system remembers, reasons, and verifies everything.", REPO_ROOT)
    assert s["cited_paths"] == []
    assert s["path_grounding_accuracy"] is None


def test_path_and_its_basename_are_not_double_counted():
    # Citing the full path AND the bare basename names one artifact, not two.
    s = g.score_grounding(
        "src/serving_modes.py — yes, serving_modes.py — sets the decode params.", REPO_ROOT)
    assert s["grounded_refs"] == 1
    assert s["grounded_paths"] == ["src/serving_modes.py"]
    assert "serving_modes.py" not in s["glossary_hits"]


def test_path_traversal_is_not_grounded():
    s = g.score_grounding("Secrets at src/../../../etc/passwd here.", REPO_ROOT)
    assert s["grounded_paths"] == []


# --------------------------------------------------------------------------- #
# Aggregation
# --------------------------------------------------------------------------- #
def test_aggregate_averages_only_path_citing_replies_for_accuracy():
    scores = [
        g.score_grounding("Real: src/serving_modes.py.", REPO_ROOT),          # acc 1.0
        g.score_grounding("Fake: src/ghost.py.", REPO_ROOT),                  # acc 0.0
        g.score_grounding("No file claim, just the External Reality Rule.", REPO_ROOT),  # acc None
    ]
    agg = g.aggregate_grounding(scores)
    assert agg["replies_citing_paths"] == 2
    assert agg["avg_path_grounding_accuracy"] == pytest.approx(0.5)
    assert agg["total_hallucinated_paths"] == 1


def test_aggregate_empty_is_empty():
    assert g.aggregate_grounding([]) == {}


# --------------------------------------------------------------------------- #
# Anti-rot: every glossary file basename must name a real file in the repo
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("basename", g.GLOSSARY_FILES)
def test_glossary_files_exist(basename):
    matches = list(REPO_ROOT.rglob(basename))
    matches = [m for m in matches if "node_modules" not in m.parts]
    assert matches, f"GLOSSARY_FILES names {basename!r}, which does not exist in the repo"
