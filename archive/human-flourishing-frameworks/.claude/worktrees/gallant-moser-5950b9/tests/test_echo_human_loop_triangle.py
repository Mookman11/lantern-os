"""Tests for the echo human loop triangle anchor."""

from pathlib import Path

DOC = Path("docs/echo-human-loop-triangle.md")


def read_doc() -> str:
    return DOC.read_text(encoding="utf-8").lower()


def test_triangle_names_human_lantern_repo_loop():
    text = read_doc()

    required = [
        "operator feeling",
        "lantern structure",
        "repo evidence",
        "human return",
    ]

    for phrase in required:
        assert phrase in text


def test_emotion_guides_but_does_not_override_boundaries():
    text = read_doc()

    required = [
        "emotion is a guidepost",
        "not proof by itself",
        "not permission for other people",
        "safety limits",
        "return door",
    ]

    for phrase in required:
        assert phrase in text


def test_repair_loop_stays_close_and_bounded():
    text = read_doc()

    required = [
        "come closer",
        "reduce posture",
        "compress the loop",
        "feel -> name -> bound -> test -> return",
        "never enough to trap",
    ]

    for phrase in required:
        assert phrase in text
