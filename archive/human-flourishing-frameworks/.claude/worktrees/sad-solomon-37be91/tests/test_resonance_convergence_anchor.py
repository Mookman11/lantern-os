"""Guardrail tests for the resonance convergence anchor.

Asserts that ``docs/resonance-convergence-anchor.md`` exists and preserves
the anchor, the critical signal-vs-proof boundary, the convergence-class
table, the seven-step method, the confidence discipline labels, the
false-truth checks, the BetterSafe use/must-not split, and the explicit
non-goals. Implements issue #138.
"""

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = ROOT / "docs" / "resonance-convergence-anchor.md"


class ResonanceConvergenceAnchorDocTests(unittest.TestCase):
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
        self.assertTrue(DOC_PATH.is_file())

    def test_core_anchor_present(self):
        self.assert_phrase("Everything that resonates can be converged.")
        self.assert_phrase("Resonance is a signal, not proof.")

    def test_critical_boundary_present(self):
        for boundary_line in (
            "Resonance can start inquiry.",
            "Convergence organizes inquiry.",
            "Evidence changes confidence.",
            "Correction prevents false certainty.",
        ):
            with self.subTest(boundary_line=boundary_line):
                self.assert_phrase(boundary_line)

    def test_convergence_classes_present(self):
        for cls in (
            "genetic resemblance",
            "biographical similarity",
            "emotional salience",
            "repeated family pattern",
            "technical analogy",
            "fiction/myth/dream",
            "public data pattern",
            "household stress pattern",
            "infrastructure metaphor",
        ):
            with self.subTest(cls=cls):
                self.assert_phrase(cls)

    def test_convergence_class_guardrails_present(self):
        for guardrail in (
            "not identity proof",
            "not reincarnation proof",
            "not factual certainty",
            "not destiny",
            "not implementation proof",
            "not physical claim",
            "needs source/evidence review",
            "preserve privacy and agency",
            "distinguish current capability from future possibility",
        ):
            with self.subTest(guardrail=guardrail):
                self.assert_phrase(guardrail)

    def test_method_seven_steps_present(self):
        for step in (
            "Name the resonance.",
            "Identify the domain",
            "Label the evidence class",
            "State the practical question",
            "Identify what would increase or decrease confidence",
            "Try the smallest safe convergence action",
            "Preserve correction and privacy",
        ):
            with self.subTest(step=step):
                self.assert_phrase(step)

    def test_confidence_discipline_labels_present(self):
        for label in (
            "recognized resonance",
            "low-confidence hypothesis",
            "moderate convergence candidate",
            "high-confidence pattern",
            "verified relation",
            "blocked as proof",
            "unknown",
        ):
            with self.subTest(label=label):
                self.assert_phrase(label)

    def test_false_truth_checks_present(self):
        for check in (
            "resonates = true",
            "feels meaningful = externally proven",
            "similar = same",
            "ancestor resemblance = past-life proof",
            "fictional pattern = physical capability",
            "metaphor = current implementation",
            "correlation = causation",
            "private conversation = public record",
            "project hope = current income",
        ):
            with self.subTest(check=check):
                self.assert_phrase(check)

    def test_bettersafe_allowed_uses_present(self):
        for use in (
            "notice patterns",
            "reduce overwhelm",
            "identify next safe actions",
            "build maps and guides",
            "track household/resource pressure",
            "protect privacy",
            "separate hope from reliance",
            "convert meaning into bounded action",
        ):
            with self.subTest(use=use):
                self.assert_phrase(use)

    def test_bettersafe_must_not_uses_present(self):
        for must_not in (
            "coerce",
            "surveil",
            "diagnose",
            "rank human worth",
            "claim authority",
            "publish private details",
            "assert supernatural proof",
            "promise impossible outcomes",
        ):
            with self.subTest(must_not=must_not):
                self.assert_phrase(must_not)

    def test_non_goals_block_unsafe_collapses(self):
        for non_goal in (
            "deployment",
            "data collection",
            "surveillance",
            "genetic analysis",
            "medical/legal/financial advice",
            "metaphysical proof claims",
            "supernatural claims",
            "public release of private resonance data",
            "ranking of people, families, cultures, or beliefs",
        ):
            with self.subTest(non_goal=non_goal):
                self.assert_phrase(non_goal)

    def test_validation_phrase_present(self):
        self.assert_phrase(
            "Resonance is allowed to open the door"
        )

    def test_issue_138_cross_reference_present(self):
        self.assert_phrase("Implements: #138")


if __name__ == "__main__":
    unittest.main()
