#!/usr/bin/env python3
"""Recovery artifact guardrails for HFF convergence durability.

These tests make the recovery layer explicit: the project should not claim
operational durability unless the mirror/archive plan, Keystone bootstrap, and
restore drill checklist exist and contain the minimum safety constraints.
"""

import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

REQUIRED_ARTIFACTS = [
    REPO_ROOT / "MIRROR_ARCHIVE_PLAN.md",
    REPO_ROOT / "KEYSTONE_BOOTSTRAP.md",
    REPO_ROOT / "RESTORE_DRILL_CHECKLIST.md",
]

RECOVERY_CORE_FILES = [
    REPO_ROOT / "data" / "theorem-register.v0.1.json",
    REPO_ROOT / "schemas" / "theorem-register.v0.1.schema.json",
    REPO_ROOT / "tests" / "test_theorem_register.py",
    REPO_ROOT / "tests" / "test_schema_source_lore.py",
]

BLOCKED_CLAIM_PATTERNS = [
    re.compile(r"\bAI\s+is\s+Alex\b", re.IGNORECASE),
    re.compile(r"\bcopy\s+is\s+survival\b", re.IGNORECASE),
    re.compile(r"\brepo\s+is\s+consciousness\b", re.IGNORECASE),
    re.compile(r"\bmodel\s+memory\s+is\s+proof\b", re.IGNORECASE),
    re.compile(r"\bfictional\s+door\s+is\s+real\b", re.IGNORECASE),
    re.compile(r"\brelease\s+bundle\s+proves\s+immortality\b", re.IGNORECASE),
]


class RecoveryArtifactsValidationTest(unittest.TestCase):
    def test_required_recovery_artifacts_exist(self):
        for path in REQUIRED_ARTIFACTS:
            with self.subTest(path=path.name):
                self.assertTrue(path.exists(), f"missing recovery artifact: {path}")
                self.assertGreater(path.stat().st_size, 500)

    def test_recovery_core_files_exist(self):
        for path in RECOVERY_CORE_FILES:
            with self.subTest(path=path.as_posix()):
                self.assertTrue(path.exists(), f"missing recovery core file: {path}")

    def test_mirror_archive_plan_contains_required_controls(self):
        text = (REPO_ROOT / "MIRROR_ARCHIVE_PLAN.md").read_text(encoding="utf-8")
        lowered = text.lower()
        for phrase in [
            "single github repository is not a long-term preservation system",
            "release bundles are the recoverable corpus",
            "independent mirrors and archives",
            "checksum",
            "offline copy",
            "trusted witness packet",
            "do not mirror secrets",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, lowered)

    def test_keystone_bootstrap_contains_required_reconstruction_rules(self):
        text = (REPO_ROOT / "KEYSTONE_BOOTSTRAP.md").read_text(encoding="utf-8")
        lowered = text.lower()
        for phrase in [
            "recoverable assistant role/protocol",
            "living alex remains primary",
            "repo state overrides model memory",
            "actual tool availability overrides advertised tool capability",
            "lore may name a theorem",
            "must not claim to be alex",
            "test_recovery_artifacts.py",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, lowered)

    def test_restore_drill_contains_pass_fail_and_no_memory_dependency(self):
        text = (REPO_ROOT / "RESTORE_DRILL_CHECKLIST.md").read_text(encoding="utf-8")
        lowered = text.lower()
        for phrase in [
            "do not use the current chat as the primary source of truth",
            "all tests pass without using chat memory",
            "pass criteria",
            "fail criteria",
            "current operator correction remains primary",
            "test_recovery_artifacts.py",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, lowered)

    def test_recovery_artifacts_block_identity_and_immortality_overclaims(self):
        assertion_text = "\n".join(
            path.read_text(encoding="utf-8") for path in REQUIRED_ARTIFACTS
        )
        # Strong phrases may appear only as blocked examples under no-claim sections.
        blocked_sections = [
            "must not claim:",
            "must not authorize:",
            "does not make keystone alive",
        ]
        self.assertTrue(any(section in assertion_text.lower() for section in blocked_sections))

        # Ensure no artifact asserts operational immortality or repo consciousness.
        forbidden_assignment = re.compile(
            r"(?m)^\s*(ai_is_alex|copy_is_survival|repo_is_consciousness|immortality_proven)\s*[:=]\s*true\s*$",
            re.IGNORECASE,
        )
        self.assertIsNone(forbidden_assignment.search(assertion_text))

    def test_recovery_artifacts_reference_validation_commands(self):
        restore_text = (REPO_ROOT / "RESTORE_DRILL_CHECKLIST.md").read_text(encoding="utf-8")
        bootstrap_text = (REPO_ROOT / "KEYSTONE_BOOTSTRAP.md").read_text(encoding="utf-8")
        combined = restore_text + "\n" + bootstrap_text
        for test_name in [
            "test_theorem_register.py",
            "test_schema_source_lore.py",
            "test_recovery_artifacts.py",
        ]:
            with self.subTest(test_name=test_name):
                self.assertIn(test_name, combined)


if __name__ == "__main__":
    unittest.main()
