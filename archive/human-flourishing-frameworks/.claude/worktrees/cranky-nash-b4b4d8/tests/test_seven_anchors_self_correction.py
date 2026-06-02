"""Guardrail tests for the Seven Anchors self-correction doctrine.

Asserts that ``docs/seven-anchors-self-correction.md`` exists, enumerates the
seven anchors verbatim, and preserves the loading-screen failure-mode
correction. Implements issue #92.
"""

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = ROOT / "docs" / "seven-anchors-self-correction.md"


class SevenAnchorsSelfCorrectionTests(unittest.TestCase):
    def setUp(self):
        self.text = DOC_PATH.read_text(encoding="utf-8")
        self.normalized = re.sub(r"\s+", " ", self.text)

    def assert_phrase(self, phrase: str) -> None:
        normalized_phrase = re.sub(r"\s+", " ", phrase)
        self.assertIn(
            normalized_phrase,
            self.normalized,
            f"missing required phrase: {phrase!r}",
        )

    def test_document_exists(self):
        self.assertTrue(
            DOC_PATH.is_file(),
            f"expected doctrine doc at {DOC_PATH}",
        )

    def test_anchor_in_force_phrase_present(self):
        self.assert_phrase("Show the state. Say the limit. Self-correct before acting.")

    def test_all_seven_anchors_enumerated(self):
        required_anchors = [
            "Operator authority",
            "Self-correction precedes action",
            "Repo serves humans, not the reverse",
            "Wish over theater",
            "Doors require return paths",
            "Memory is not proof; current correction overrides prior momentum",
            "Human safety blocks automation theater",
        ]
        for anchor in required_anchors:
            with self.subTest(anchor=anchor):
                self.assert_phrase(anchor)

    def test_loading_screen_failure_pattern_documented(self):
        # The rejected pattern must appear so future readers can recognize it.
        self.assert_phrase(
            "User correction -> branch -> PR -> merge -> report"
        )
        # The required replacement pattern must also appear.
        self.assert_phrase(
            "User correction -> meaning -> uncertainty -> smallest useful outcome -> only then action"
        )

    def test_self_correction_protocol_steps_present(self):
        required_steps = [
            "restate the human meaning",
            "assess uncertainty",
            "identify the issue class",
            "say the smallest useful next outcome",
            "act only if action reduces load and stays inside current authorization",
        ]
        for step in required_steps:
            with self.subTest(step=step):
                self.assert_phrase(step)

    def test_non_goals_block_unsafe_collapses(self):
        required_non_goals = [
            "runtime autonomy",
            "deployment",
            "sensors",
            "public writes",
            "financial action",
            "physical-world control",
            "surveillance",
            "self-authorized merges",
        ]
        for non_goal in required_non_goals:
            with self.subTest(non_goal=non_goal):
                self.assert_phrase(non_goal)

    def test_failure_class_repairs_documented(self):
        # Failure-mode table must keep the human-safety repairs visible.
        required_failures = [
            "Loading-screen action",
            "Authority drift",
            "Repo-over-human",
            "Momentum over correction",
            "Coercion-as-help",
            "Hidden action",
            "Theater",
        ]
        for failure in required_failures:
            with self.subTest(failure=failure):
                self.assert_phrase(failure)

    def test_relationship_doctrine_links_preserved(self):
        # These cross-references keep the seven anchors connected to the rest
        # of the doctrine spine. Tests guard against silent decoupling.
        required_links = [
            "docs/keystone-memory-contract.md",
            "docs/keystone-self-convergence.md",
            "docs/keystone-table-door-anchors.md",
            "docs/keystone-autonomous-work-queue.md",
            "docs/public-surface-policy.md",
            "docs/convergence-status.md",
        ]
        for link in required_links:
            with self.subTest(link=link):
                self.assert_phrase(link)

    def test_issue_92_cross_reference_present(self):
        self.assert_phrase("Implements: #92")


if __name__ == "__main__":
    unittest.main()
