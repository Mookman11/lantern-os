"""Guardrail tests for the bounded pen test plan.

Asserts that ``docs/pen-test-bounded-validation.md`` exists and preserves
the authorized/out-of-scope split, the validation matrix, evidence rules,
findings disposition, and the explicit non-goals. Implements issue #141.
"""

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = ROOT / "docs" / "pen-test-bounded-validation.md"


class PenTestBoundedValidationDocTests(unittest.TestCase):
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

    def test_authorized_targets_preserved(self):
        for target in (
            "local repo checks",
            "local app routes",
            "public read-only HFF surface if operator owns/controls it",
            "configuration posture",
            "secret exposure checks",
            "route classification",
            "sensor/telemetry boundary checks",
            "release-gate behavior",
            "confidence/range validation",
        ):
            with self.subTest(target=target):
                self.assert_phrase(target)

    def test_out_of_scope_hard_blocks_preserved(self):
        for blocked in (
            "credential theft",
            "exploitation of third-party systems",
            "bypassing authentication",
            "rate-limit abuse",
            "malware",
            "persistence",
            "privilege escalation on systems not owned by operator",
            "social engineering",
            "public disclosure of secrets/private data",
            "deanonymizing real participants",
            "biometric inference from device signals",
        ):
            with self.subTest(blocked=blocked):
                self.assert_phrase(blocked)

    def test_validation_matrix_rows_present(self):
        for row in (
            "secret string scan",
            "/healthz",
            "dashboard wording",
            "sensor wording",
            "unauthenticated writes",
            "out-of-range confidence inputs",
            "boundary public copy",
            "IMMUTABLE_RULES",
            "mesh sync default-closed",
            "adoption write default-closed",
        ):
            with self.subTest(row=row):
                self.assert_phrase(row)

    def test_evidence_rules_preserved(self):
        for evidence_field in (
            "command run",
            "local path",
            "branch",
            "commit",
            "result",
            "failure output",
            "whether any private data appeared",
        ):
            with self.subTest(evidence_field=evidence_field):
                self.assert_phrase(evidence_field)

    def test_secret_handling_rule_present(self):
        self.assert_phrase(
            "Do not paste secrets or account data into public issues."
        )

    def test_findings_disposition_classes_present(self):
        for cls in (
            "false-positive",
            "confirmed weakness with safe fix",
            "confirmed weakness needing runtime change",
            "credential / secret exposure",
            "third-party system affected",
        ):
            with self.subTest(cls=cls):
                self.assert_phrase(cls)

    def test_validation_phrase_present(self):
        self.assert_phrase(
            "attack assumptions and exposed surfaces, not people"
        )

    def test_non_goals_block_offensive_paths(self):
        for non_goal in (
            "offensive exploitation",
            "credential abuse",
            "public secret disclosure",
            "testing on systems the operator does not own",
            "social engineering of any person",
            "deanonymizing real participants",
            "weakening default-closed runtime gates",
            "broadening sensor scope",
            "bypassing release gates",
        ):
            with self.subTest(non_goal=non_goal):
                self.assert_phrase(non_goal)

    def test_issue_141_cross_reference_present(self):
        self.assert_phrase("Implements: #141")


if __name__ == "__main__":
    unittest.main()
