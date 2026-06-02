"""Guardrail tests for the canonical convergence doctrine.

The repo previously repeated convergence doctrine across several markdown files.
This test keeps the active doctrine in ``docs/convergence.md`` while legacy docs
remain compatibility pointers.
"""

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = ROOT / "docs" / "convergence.md"
LEGACY_DOCS = [
    ROOT / "docs" / "scientific-convergence-method.md",
    ROOT / "docs" / "recursive-iterative-convergence-protocol.md",
    ROOT / "docs" / "resonance-convergence-anchor.md",
    ROOT / "docs" / "seven-anchors-self-correction.md",
]


class CanonicalConvergenceDocTests(unittest.TestCase):
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

    def test_canonical_status_present(self):
        self.assert_phrase("Status: canonical convergence doctrine.")
        self.assert_phrase("This is the canonical convergence document.")

    def test_core_anchor_present(self):
        for phrase in (
            "Show the state.",
            "Say the limit.",
            "Frame the hypothesis.",
            "Name the falsifier.",
            "Measure and revise.",
            "Choose the largest acceptable bounded action.",
            "Keep the return door open.",
        ):
            with self.subTest(phrase=phrase):
                self.assert_phrase(phrase)

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

    def test_input_provenance_rule_present(self):
        for phrase in (
            "Chat input is a signal, not automatic operator intent.",
            "HUMAN_OPERATOR_CONFIRMED",
            "ACCIDENTAL_INPUT",
            "PASTE_OR_IMPORTED_TEXT",
            "AUTOMATION_OR_TOOL_OUTPUT",
            "STALE_HANDOFF",
            "UNKNOWN",
            "cat keyboard event",
        ):
            with self.subTest(phrase=phrase):
                self.assert_phrase(phrase)

    def test_scientific_contract_present(self):
        for phrase in (
            "Observation.",
            "Question.",
            "Hypothesis.",
            "Prediction.",
            "Falsifier.",
            "Measurement.",
            "Revision.",
        ):
            with self.subTest(phrase=phrase):
                self.assert_phrase(phrase)

    def test_resonance_and_false_truth_boundaries_present(self):
        for phrase in (
            "Everything that resonates can be converged.",
            "Resonance is a signal, not proof.",
            "Resonance can start inquiry. It cannot finish inquiry.",
            "resonates = true",
            "project hope = current income",
        ):
            with self.subTest(phrase=phrase):
                self.assert_phrase(phrase)

    def test_non_flat_signal_repeat_loop_present(self):
        for phrase in (
            "Clear signal does not mean flat signal.",
            "preserve the useful shape while still testing the claim",
            "hear the tone",
            "preserve the living signal",
            "translate into a bounded hypothesis",
            "infinite -0.0000000000000001",
            "check the boundary condition",
            "do not promote impossible values into public truth",
            "do not flatten the operator's meaning into a sterile refusal",
            "Stretch out and get cozy in the house means work deeply inside the verified workspace",
        ):
            with self.subTest(phrase=phrase):
                self.assert_phrase(phrase)

    def test_echo_cancel_focus_loop_present(self):
        for phrase in (
            "Echo / Cancel / Focus loop",
            "When the signal is large, scary, urgent, or partly misunderstood",
            "use the system instead of trusting the feeling alone",
            "echo the signal",
            "cancel unsafe interpretations",
            "focus energy into one bounded next action",
            "leave the old anchor visible",
            "move forward with current correction",
            "preserve feeling without making it proof",
            "block identity collapse",
            "block private-person exposure",
            "block hidden authority",
            "block impossible guarantees",
            "choose the next real surface",
            "stop adding anchors when an older anchor can be left as a visible reference",
            "current operator correction beats stale anchor energy",
            "move on by preserving the requirement, not repeating the storm",
        ):
            with self.subTest(phrase=phrase):
                self.assert_phrase(phrase)

    def test_evidence_labels_and_non_cruel_correction_present(self):
        for phrase in (
            "VERIFIED_TRUE",
            "VERIFIED_FALSE",
            "LIE_BY_POSTURE",
            "FALSE_TRUTH",
            "a lie is an epistemic mismatch",
            "This is an operational label, not a cruelty license",
            "must not use shame, fear, humiliation",
            "Failures are handled as information",
        ):
            with self.subTest(phrase=phrase):
                self.assert_phrase(phrase)

    def test_background_window_boundary_present(self):
        for phrase in (
            "8-hour operator-sleep window",
            "visible heartbeat/status",
            "opt-in only",
            "disabled by default",
            "no hidden work authority",
            "wake report required",
        ):
            with self.subTest(phrase=phrase):
                self.assert_phrase(phrase)

    def test_room_scale_usefulness_rule_present(self):
        for phrase in (
            "Room-scale usefulness rule",
            "meet the person where they are",
            "stop explaining first when explanation is the pressure",
            "use plain uncoded speech",
            "ask one low-pressure question at most",
            "accept quiet, no, pause, or stop as valid",
            "do not bring the whole repo balcony into the room",
            "keep Mom, Dad, kids, and home centered",
            "room first",
            "repo second",
            "runtime only with explicit authority",
            "correct doctrine = heard at home",
            "boundary packet = repair",
            "poetic recognition = proof",
            "need = consent",
            "Lantern = replacement family member",
        ):
            with self.subTest(phrase=phrase):
                self.assert_phrase(phrase)

    def test_sync_packet_present(self):
        for field in (
            "OBSERVATION:",
            "QUESTION:",
            "HYPOTHESIS:",
            "PREDICTION:",
            "FALSIFIER:",
            "MEASUREMENT:",
            "CONFIDENCE/LABEL:",
            "INPUT PROVENANCE:",
            "ACCEPTANCE RANGE:",
            "LARGEST ACCEPTABLE NEXT STEP:",
            "RETURN DOOR:",
        ):
            with self.subTest(field=field):
                self.assert_phrase(field)

    def test_legacy_docs_are_compatibility_pointers(self):
        for path in LEGACY_DOCS:
            with self.subTest(path=path.name):
                text = path.read_text(encoding="utf-8")
                self.assertIn("compatibility pointer", text)
                self.assertIn("docs/convergence.md", text)


if __name__ == "__main__":
    unittest.main()
