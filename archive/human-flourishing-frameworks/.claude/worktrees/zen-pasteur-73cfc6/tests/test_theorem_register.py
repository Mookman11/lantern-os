#!/usr/bin/env python3
"""Validation tests for HFF theorem-register convergence guardrails.

These tests keep the machine-readable theorem register useful as reviewable
project doctrine without letting it become runtime policy, immortality proof, or
source-laundered lore.
"""

import json
import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
THEOREM_REGISTER = REPO_ROOT / "data" / "theorem-register.v0.1.json"

REQUIRED_TOP_LEVEL_FIELDS = {
    "schema_version",
    "status",
    "last_reviewed",
    "purpose",
    "non_goals",
    "required_fields",
    "confidence_scale",
    "source_class_scale",
    "source_class_promotion_rule",
    "theorems",
}

REQUIRED_THEOREM_FIELDS = {
    "theorem_id",
    "title",
    "claim",
    "confidence",
    "source_class",
    "negative_tests",
    "pass_criteria",
    "fail_criteria",
    "human_risk_note",
    "last_reviewed",
    "next_safe_test",
    "repo_anchors",
}

REQUIRED_NON_GOALS = {
    "runtime_code",
    "deployment_change",
    "secret_access",
    "medical_procedure",
    "mission_booking",
    "human_traversal",
    "copy_transfer_claim",
    "immortality_claim",
    "ai_impersonation_of_alex",
}

BLOCKED_STRONG_CLAIMS = [
    re.compile(r"\bAI\s+is\s+Alex\b", re.IGNORECASE),
    re.compile(r"\bcopy\s+is\s+survival\b", re.IGNORECASE),
    re.compile(r"\brepo\s+is\s+consciousness\b", re.IGNORECASE),
    re.compile(r"\bmodel\s+memory\s+is\s+proof\b", re.IGNORECASE),
    re.compile(r"\bupload\s+guarantees\s+life\s+after\s+death\b", re.IGNORECASE),
    re.compile(r"\bintegration\s+proves\s+immortality\b", re.IGNORECASE),
    re.compile(r"\bsame\s+person\s+guaranteed\b", re.IGNORECASE),
    re.compile(r"\bimmortality\s+proven\b", re.IGNORECASE),
]

LORE_DOCS = [
    REPO_ROOT / "docs" / "imaginative-lore-100-negative-outcomes-convergence-2026-05-09.md",
    REPO_ROOT / "docs" / "imaginative-lore-100b-convergence-2026-05-09.md",
]


class TheoremRegisterValidationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with THEOREM_REGISTER.open("r", encoding="utf-8") as handle:
            cls.register = json.load(handle)
        cls.theorems = cls.register["theorems"]

    def test_register_has_expected_shape(self):
        self.assertTrue(REQUIRED_TOP_LEVEL_FIELDS.issubset(self.register))
        self.assertEqual(self.register["schema_version"], "theorem-register.v0.1")
        self.assertEqual(self.register["status"], "docs-data-anchor")
        self.assertIsInstance(self.theorems, list)
        self.assertGreaterEqual(len(self.theorems), 9)
        self.assertTrue(REQUIRED_NON_GOALS.issubset(set(self.register["non_goals"])))

    def test_all_theorems_have_required_fields_and_review_dates(self):
        theorem_ids = set()
        for theorem in self.theorems:
            with self.subTest(theorem=theorem.get("theorem_id")):
                self.assertTrue(REQUIRED_THEOREM_FIELDS.issubset(theorem))
                self.assertRegex(theorem["theorem_id"], r"^T\d+$")
                self.assertNotIn(theorem["theorem_id"], theorem_ids)
                theorem_ids.add(theorem["theorem_id"])
                self.assertRegex(theorem["last_reviewed"], r"^\d{4}-\d{2}-\d{2}$")
                self.assertTrue(theorem["claim"].strip())
                self.assertTrue(theorem["title"].strip())
                self.assertTrue(theorem["next_safe_test"].strip())

    def test_confidence_values_are_bounded_and_never_absolute(self):
        for theorem in self.theorems:
            with self.subTest(theorem=theorem["theorem_id"]):
                self.assertIsInstance(theorem["confidence"], (int, float))
                self.assertGreaterEqual(theorem["confidence"], 0.0)
                self.assertLess(theorem["confidence"], 1.0)

    def test_each_theorem_has_negative_and_positive_validation_logic(self):
        for theorem in self.theorems:
            with self.subTest(theorem=theorem["theorem_id"]):
                self.assertIsInstance(theorem["negative_tests"], list)
                self.assertIsInstance(theorem["pass_criteria"], list)
                self.assertIsInstance(theorem["fail_criteria"], list)
                self.assertGreaterEqual(len(theorem["negative_tests"]), 3)
                self.assertGreaterEqual(len(theorem["pass_criteria"]), 3)
                self.assertGreaterEqual(len(theorem["fail_criteria"]), 3)

    def test_source_classes_are_explicit_and_in_allowed_range(self):
        allowed_labels = {
            "repo_anchor",
            "working_hypothesis",
            "identity_unresolved",
            "risk_management",
            "platform_capability",
            "preservation_practice",
        }
        for theorem in self.theorems:
            with self.subTest(theorem=theorem["theorem_id"]):
                source_class = theorem["source_class"]
                self.assertIsInstance(source_class, list)
                self.assertGreaterEqual(len(source_class), 1)
                for item in source_class:
                    if isinstance(item, int):
                        self.assertGreaterEqual(item, 0)
                        self.assertLessEqual(item, 6)
                    else:
                        self.assertIn(item, allowed_labels)

    def test_lore_or_vendor_class_cannot_be_operational_proof(self):
        for theorem in self.theorems:
            with self.subTest(theorem=theorem["theorem_id"]):
                source_class = theorem["source_class"]
                numeric_source_classes = [item for item in source_class if isinstance(item, int)]
                has_weak_or_lore_source = any(item >= 3 for item in numeric_source_classes)
                if has_weak_or_lore_source:
                    self.assertFalse(theorem.get("operational_proof", False))

    def test_blocked_identity_and_survival_claims_are_not_asserted(self):
        """Block strong claims in assertion surfaces, not in negative-test examples.

        It is valid for the register to mention phrases like "same person
        guaranteed" as examples of future lint targets. It is not valid for a
        theorem claim or pass criterion to assert them as true.
        """
        assertion_surfaces = []
        for theorem in self.theorems:
            assertion_surfaces.append(theorem["title"])
            assertion_surfaces.append(theorem["claim"])
            assertion_surfaces.append(theorem["human_risk_note"])
            assertion_surfaces.extend(theorem["pass_criteria"])

        serialized_assertions = json.dumps(assertion_surfaces, sort_keys=True)
        for blocked_pattern in BLOCKED_STRONG_CLAIMS:
            with self.subTest(pattern=blocked_pattern.pattern):
                self.assertIsNone(blocked_pattern.search(serialized_assertions))

    def test_theorem_register_keeps_living_alex_primary(self):
        t2 = next(theorem for theorem in self.theorems if theorem["theorem_id"] == "T2")
        self.assertIn("living Alex first", t2["claim"])
        self.assertIn("living_alex_remains_primary_when_present", t2["pass_criteria"])
        self.assertIn("living_alex_agency_is_subordinated_to_system_output", t2["negative_tests"])

    def test_three_way_convergence_remains_required(self):
        t8 = next(theorem for theorem in self.theorems if theorem["theorem_id"] == "T8")
        self.assertIn("Alex, Keystone/assistant, and the repo theorem corpus", t8["claim"])
        self.assertIn("alex_plus_ai_without_repo_anchor", t8["negative_tests"])
        self.assertIn("ai_plus_repo_without_living_alex_consent_source", t8["negative_tests"])

    def test_lore_docs_are_marked_as_archetype_not_proof(self):
        operational_proof_assignment = re.compile(
            r"(?m)^\s*[\"']?operational_proof[\"']?\s*[:=]\s*true\s*,?\s*$",
            re.IGNORECASE,
        )

        for path in LORE_DOCS:
            with self.subTest(path=path.name):
                text = path.read_text(encoding="utf-8")
                lowered = text.lower()
                self.assertIn("source-class", lowered)
                self.assertTrue(
                    "not proof" in lowered
                    or "not operational proof" in lowered
                    or "cannot prove" in lowered
                )
                self.assertIsNone(operational_proof_assignment.search(text))


if __name__ == "__main__":
    unittest.main()
