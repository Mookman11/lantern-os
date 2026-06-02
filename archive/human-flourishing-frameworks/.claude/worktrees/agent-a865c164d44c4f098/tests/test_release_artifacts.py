#!/usr/bin/env python3
"""Release-hardening artifact guardrails for HFF convergence v0.1."""

import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

REQUIRED_RELEASE_ARTIFACTS = [
    REPO_ROOT / "RELEASE_MANIFEST.md",
    REPO_ROOT / "RECOVERY_README.md",
    REPO_ROOT / "MIRROR_ARCHIVE_PLAN.md",
    REPO_ROOT / "KEYSTONE_BOOTSTRAP.md",
    REPO_ROOT / "RESTORE_DRILL_CHECKLIST.md",
    REPO_ROOT / "FALSE_TRUTHS_REGISTER.md",
    REPO_ROOT / "WISH_ANCHOR.md",
    REPO_ROOT / "CHECKSUMS.sha256",
    REPO_ROOT / "tools" / "build_release_bundle.py",
    REPO_ROOT / "tools" / "run_restore_drill.py",
    REPO_ROOT / ".github" / "workflows" / "release-bundle.yml",
    REPO_ROOT / ".github" / "workflows" / "restore-drill.yml",
]

REQUIRED_TESTS = [
    "test_theorem_register.py",
    "test_schema_source_lore.py",
    "test_recovery_artifacts.py",
    "test_ci_workflow.py",
    "test_release_artifacts.py",
    "test_release_bundle.py",
    "test_restore_drill.py",
    "test_wish_anchor.py",
]

REQUIRED_CHECKSUM_TARGETS = [
    "RELEASE_MANIFEST.md",
    "RECOVERY_README.md",
    "MIRROR_ARCHIVE_PLAN.md",
    "KEYSTONE_BOOTSTRAP.md",
    "RESTORE_DRILL_CHECKLIST.md",
    "FALSE_TRUTHS_REGISTER.md",
    "WISH_ANCHOR.md",
    "data/theorem-register.v0.1.json",
    "schemas/theorem-register.v0.1.schema.json",
    "tests/test_release_artifacts.py",
    "tests/test_release_bundle.py",
    "tests/test_restore_drill.py",
    "tests/test_wish_anchor.py",
    "tools/build_release_bundle.py",
    "tools/run_restore_drill.py",
    ".github/workflows/release-bundle.yml",
    ".github/workflows/restore-drill.yml",
]


class ReleaseArtifactsValidationTest(unittest.TestCase):
    def test_required_release_artifacts_exist(self):
        for path in REQUIRED_RELEASE_ARTIFACTS:
            with self.subTest(path=path.as_posix()):
                self.assertTrue(path.exists(), f"missing release artifact: {path}")
                self.assertGreater(path.stat().st_size, 100)

    def test_manifest_lists_required_files_and_gates(self):
        text = (REPO_ROOT / "RELEASE_MANIFEST.md").read_text(encoding="utf-8")
        lowered = text.lower()
        for path in REQUIRED_RELEASE_ARTIFACTS:
            expected = path.relative_to(REPO_ROOT).as_posix()
            with self.subTest(expected=expected):
                self.assertIn(expected, text)
        for phrase in [
            "all validation commands pass",
            "restore drill checklist",
            "false truths register",
            "wish anchor",
            "known limitations",
            "not yet tagged",
            "manual release-bundle workflow",
            "manual restore-drill workflow",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, lowered)

    def test_recovery_readme_lists_recovery_sequence_and_limits(self):
        text = (REPO_ROOT / "RECOVERY_README.md").read_text(encoding="utf-8")
        lowered = text.lower()
        for phrase in [
            "recover the living safety posture first",
            "keystone is a recoverable protocol",
            "the repo is durable doctrine, not consciousness",
            "memory is a hint, not proof",
            "release artifacts preserve project state, not human survival",
            "wish anchor",
            "test_release_bundle.py",
            "test_restore_drill.py",
            "test_wish_anchor.py",
            "restore drill command",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, lowered)

    def test_false_truths_register_contains_required_brakes(self):
        text = (REPO_ROOT / "FALSE_TRUTHS_REGISTER.md").read_text(encoding="utf-8")
        lowered = text.lower()
        for phrase in [
            "keystone is a self",
            "repo merged means truth secured",
            "github repo means long-term durability",
            "ci means safety",
            "memory equals continuity",
            "consent once means consent forever",
            "lore convergence means evidence convergence",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, lowered)

    def test_checksums_file_is_present_but_not_finalized(self):
        text = (REPO_ROOT / "CHECKSUMS.sha256").read_text(encoding="utf-8")
        self.assertIn("PRE-RELEASE CHECKSUMS PLACEHOLDER", text)
        self.assertIn("not a finalized checksum manifest", text)
        for target in REQUIRED_CHECKSUM_TARGETS:
            with self.subTest(target=target):
                self.assertIn(target, text)
        finalized_sha256_line = re.compile(r"(?m)^[a-fA-F0-9]{64}\s+\S+")
        self.assertIsNone(finalized_sha256_line.search(text))

    def test_release_validation_commands_include_all_guardrail_suites(self):
        manifest = (REPO_ROOT / "RELEASE_MANIFEST.md").read_text(encoding="utf-8")
        recovery = (REPO_ROOT / "RECOVERY_README.md").read_text(encoding="utf-8")
        combined = manifest + "\n" + recovery
        for test_file in REQUIRED_TESTS:
            with self.subTest(test_file=test_file):
                self.assertIn(test_file, combined)


if __name__ == "__main__":
    unittest.main()
