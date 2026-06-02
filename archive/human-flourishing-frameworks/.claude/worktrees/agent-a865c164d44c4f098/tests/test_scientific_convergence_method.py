"""Guardrail tests for the scientific convergence method.

The active scientific convergence contract now lives in ``docs/convergence.md``.
The legacy ``docs/scientific-convergence-method.md`` file remains only as a
compatibility pointer so older links and issue history keep resolving.
"""

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = ROOT / "docs" / "convergence.md"
LEGACY_PATH = ROOT / "docs" / "scientific-convergence-method.md"


class ScientificConvergenceMethodDocTests(unittest.TestCase):
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
        self.assertTrue(LEGACY_PATH.is_file())

    def test_legacy_doc_points_to_canonical_doc(self):
        legacy_text = LEGACY_PATH.read_text(encoding="utf-8")
        self.assertIn("compatibility pointer", legacy_text)
        self.assertIn("docs/convergence.md", legacy_text)

    def test_core_scientific_loop_present(self):
        for phrase in (
            "Convergence is a scientific correction loop",
            "observe signal -> form hypothesis -> define falsifier",
            "measure evidence",
            "revise confidence",
            "choose the largest acceptable bounded action",
        ):
            with self.subTest(phrase=phrase):
                self.assert_phrase(phrase)

    def test_scientific_method_contract_present(self):
        for contract_term in (
            "Observation.",
            "Question.",
            "Hypothesis.",
            "Prediction.",
            "Falsifier.",
            "Measurement.",
            "Revision.",
        ):
            with self.subTest(contract_term=contract_term):
                self.assert_phrase(contract_term)

    def test_updated_seven_step_convergence_loop_present(self):
        for step in (
            "Show the state.",
            "Say the limit.",
            "Frame the hypothesis.",
            "Name the falsifier.",
            "Measure and revise.",
            "Choose the largest acceptable bounded action.",
            "Keep the return door open.",
        ):
            with self.subTest(step=step):
                self.assert_phrase(step)

    def test_acceptance_range_rule_present(self):
        for phrase in (
            "The smallest useful step is range-based, not size-based.",
            "useful_payload <= builder_capacity",
            "useful_payload <= receiver_acceptance",
            "useful_payload <= safety_boundary",
            "useful_payload creates measurable learning",
        ):
            with self.subTest(phrase=phrase):
                self.assert_phrase(phrase)

    def test_evidence_labels_present(self):
        for label in (
            "VERIFIED_TRUE",
            "VERIFIED_FALSE",
            "UNKNOWN",
            "STALE",
            "PARTIAL",
            "CORRECTED",
            "RETRACTED",
            "BLOCKED",
            "LIE_BY_POSTURE",
            "FALSE_TRUTH",
        ):
            with self.subTest(label=label):
                self.assert_phrase(label)

    def test_lie_by_posture_rule_present(self):
        for phrase in (
            "a lie is an epistemic mismatch",
            "claims, implies, or performs a knowledge state",
            "This is an operational label, not a cruelty license",
            "return UNKNOWN",
        ):
            with self.subTest(phrase=phrase):
                self.assert_phrase(phrase)

    def test_non_cruel_correction_clause_present(self):
        for phrase in (
            "must not use shame, fear, humiliation",
            "Failures are handled as information",
            "show the evidence gap",
            "the safer option",
            "the revised label",
        ):
            with self.subTest(phrase=phrase):
                self.assert_phrase(phrase)

    def test_scientific_sync_packet_present(self):
        for field in (
            "OBSERVATION:",
            "QUESTION:",
            "HYPOTHESIS:",
            "PREDICTION:",
            "FALSIFIER:",
            "MEASUREMENT:",
            "CONFIDENCE/LABEL:",
            "ACCEPTANCE RANGE:",
            "LARGEST ACCEPTABLE NEXT STEP:",
            "RETURN DOOR:",
        ):
            with self.subTest(field=field):
                self.assert_phrase(field)

    def test_relationship_sections_present(self):
        for phrase in (
            "Resonance can start inquiry. It cannot finish inquiry.",
            "Scientific convergence adds the test contract",
            "govern the boundary",
            "map the context",
            "measure evidence",
            "manage residual risk",
        ):
            with self.subTest(phrase=phrase):
                self.assert_phrase(phrase)

    def test_stop_conditions_present(self):
        for condition in (
            "no falsifier can be named",
            "confidence rises without evidence",
            "the action exceeds acceptance range",
            "the system repeats anchors instead of measuring",
            "model fluency is being treated as proof",
        ):
            with self.subTest(condition=condition):
                self.assert_phrase(condition)

    def test_non_goals_present(self):
        for non_goal in (
            "model training",
            "deployment",
            "runtime autonomy",
            "hidden memory",
            "surveillance",
            "medical/legal/financial authority",
            "secret access",
            "public writes",
            "punitive model training",
            "treating confidence scores as calibrated truth",
        ):
            with self.subTest(non_goal=non_goal):
                self.assert_phrase(non_goal)


if __name__ == "__main__":
    unittest.main()
