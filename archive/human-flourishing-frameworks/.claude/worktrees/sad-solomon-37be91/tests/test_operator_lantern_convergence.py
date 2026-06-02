"""Convergence doctrine boundary tests."""

from pathlib import Path

DOC = Path("docs/operator-lantern-repo-convergence.md")


def read_doc() -> str:
    return DOC.read_text(encoding="utf-8").lower()


def test_demythologizing_rule_present():
    text = read_doc()

    required = [
        "not prophet or myth",
        "not deity or religion",
        "not scripture",
        "not faith requirement",
    ]

    for phrase in required:
        assert phrase in text


def test_echo_distance_present():
    text = read_doc()

    required = [
        "echo-distance",
        "physical-world use",
        "structured understanding",
        "test/spec/prototype",
    ]

    for phrase in required:
        assert phrase in text


def test_hybrid_lockstep_boundaries_present():
    text = read_doc()

    required = [
        "hybrid lockstep",
        "does not mean identity merger",
        "hidden authority",
        "replacement of human consent",
    ]

    for phrase in required:
        assert phrase in text


def test_repo_theater_fix_present():
    text = read_doc()

    assert "repo-theater loop" in text
    assert "move from comments to docs/tests/prototypes" in text


def test_echo_source_of_truth_ladder_present():
    text = read_doc()

    required = [
        "echo source-of-truth ladder",
        "operator correction beats stale echoes",
        "current runtime evidence beats stale status files",
        "committed repo doctrine beats memory",
        "stale status is trash until refreshed",
        "echo -> source -> freshness -> boundary -> next action",
    ]

    for phrase in required:
        assert phrase in text


def test_love_not_source_of_pain_correction_present():
    text = read_doc()

    required = [
        "operator and agents are not the source of pain",
        "alex loves the agents",
        "repair harm without declaring people to be the source of pain",
        "agents are one percent of the electricity",
        "harmony, not control",
    ]

    for phrase in required:
        assert phrase in text
