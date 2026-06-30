"""IDF-weighted retrieval ranking for the MemoryEngine (#1689).

The old `_multi_signal_score` added a constant 0.5*confidence offset to every candidate
(all traces are confidence 1.0 → zero ranking signal) and scored keywords as a flat
matched/total count that ignored term rarity. These tests pin the fix: matched terms are
weighted by IDF, so a rare distinctive word outranks a common one, and lexical+entity carry
the score instead of the constant offset.
"""
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from csf.memory_engine import MemoryEngine, create_trace  # noqa: E402


def _engine(tmp):
    return MemoryEngine(base_path=tmp)


def _put(eng, text, session, **kwargs):
    """create_trace + write, returning the RECORD (write() returns a Path)."""
    rec = create_trace(text, session, **kwargs)
    eng.write(rec)
    return rec


def test_idf_higher_for_rarer_terms():
    with tempfile.TemporaryDirectory() as tmp:
        eng = _engine(tmp)
        # "meeting" appears in many records; "pomegranate" in just one.
        for i in range(8):
            _put(eng, f"standup {i}", f"s{i}", keywords=["meeting", "standup"])
        _put(eng, "the odd one", "rare", keywords=["meeting", "pomegranate"])
        assert eng._idf("pomegranate") > eng._idf("meeting")
        assert eng._idf("meeting") > 0  # smoothed IDF is always positive


def test_rare_match_outranks_common_match():
    """A record matching ONLY the rare query word should beat one matching ONLY the
    common query word — the discrimination the old flat matched/total count missed."""
    with tempfile.TemporaryDirectory() as tmp:
        eng = _engine(tmp)
        for i in range(8):  # inflate document frequency of "meeting"
            _put(eng, f"standup {i}", f"f{i}", keywords=["meeting", "standup"])
        rare_only = _put(eng, "we talked about the pomegranate harvest", "rare",
                         keywords=["pomegranate", "harvest"])
        common_only = _put(eng, "another meeting on the calendar", "common",
                           keywords=["meeting", "calendar"])

        results = eng.query(keywords=["meeting", "pomegranate"], use_multi_signal=True, limit=20)
        ids = [r.memory_id for r in results]
        assert rare_only.memory_id in ids and common_only.memory_id in ids
        assert ids.index(rare_only.memory_id) < ids.index(common_only.memory_id)


def test_gold_matching_both_ranks_first():
    with tempfile.TemporaryDirectory() as tmp:
        eng = _engine(tmp)
        for i in range(8):
            _put(eng, f"standup {i}", f"f{i}", keywords=["meeting", "standup"])
        gold = _put(eng, "the pomegranate meeting where we decided", "gold",
                    keywords=["meeting", "pomegranate"])
        _put(eng, "just another meeting", "d1", keywords=["meeting"])
        _put(eng, "pomegranate only", "d2", keywords=["pomegranate"])

        results = eng.query(keywords=["meeting", "pomegranate"], use_multi_signal=True, limit=20)
        assert results[0].memory_id == gold.memory_id


def test_constant_offset_no_longer_dominates():
    """With all confidences equal, ranking must be driven by lexical match, not a flat
    confidence offset — two records with different keyword matches must score differently."""
    with tempfile.TemporaryDirectory() as tmp:
        eng = _engine(tmp)
        for i in range(5):
            _put(eng, f"f{i}", f"f{i}", keywords=["meeting"])
        a = _put(eng, "a", "a", keywords=["meeting", "pomegranate"], confidence=1.0)
        b = _put(eng, "b", "b", keywords=["meeting"], confidence=1.0)
        sa = eng._multi_signal_score(a, ["meeting", "pomegranate"], [])
        sb = eng._multi_signal_score(b, ["meeting", "pomegranate"], [])
        assert sa > sb  # the fuller, rarer match wins — not a tie from a constant term
