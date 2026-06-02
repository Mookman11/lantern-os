#!/usr/bin/env python3
"""Validation tests for the HFF convergence restore drill runner."""

import tempfile
import unittest
import zipfile
from pathlib import Path

from tools.run_restore_drill import (
    REQUIRED_RESTORE_FILES,
    RESTORE_TEST_PATTERNS,
    run_restore_drill,
    verify_checksum_file,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


class RestoreDrillRunnerValidationTest(unittest.TestCase):
    def test_restore_drill_required_files_exist_in_repo(self):
        for relative in REQUIRED_RESTORE_FILES:
            with self.subTest(relative=relative):
                self.assertTrue((REPO_ROOT / relative).is_file(), f"missing {relative}")

    def test_restore_drill_patterns_include_all_guardrail_suites(self):
        for pattern in [
            "test_theorem_register.py",
            "test_schema_source_lore.py",
            "test_recovery_artifacts.py",
            "test_ci_workflow.py",
            "test_release_bundle.py",
            "test_restore_drill.py",
        ]:
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, RESTORE_TEST_PATTERNS)

    def test_restore_drill_builds_extracts_and_verifies_bundle_without_recursive_tests(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            result = run_restore_drill(REPO_ROOT, output_dir, run_tests=False)

            self.assertTrue(result.release_zip.is_file())
            self.assertTrue(result.checksum_file.is_file())
            self.assertTrue(result.extract_dir.is_dir())
            self.assertTrue(result.report_file.is_file())
            self.assertEqual(result.tests_run, ())

            with zipfile.ZipFile(result.release_zip, "r") as archive:
                names = set(archive.namelist())
            self.assertIn("RESTORE_DRILL_CHECKLIST.md", names)
            self.assertIn("tools/run_restore_drill.py", names)
            self.assertIn("tests/test_restore_drill.py", names)
            self.assertNotIn(".git/config", names)

            for relative in REQUIRED_RESTORE_FILES:
                with self.subTest(relative=relative):
                    self.assertTrue((result.extract_dir / relative).is_file())

            verified = verify_checksum_file(result.extract_dir, result.extract_dir / "CHECKSUMS.sha256")
            self.assertIn("tools/run_restore_drill.py", verified)
            self.assertIn("tests/test_restore_drill.py", verified)

            report_text = result.report_file.read_text(encoding="utf-8")
            self.assertIn("result: PASS", report_text)
            self.assertIn("verified_checksum_files:", report_text)


if __name__ == "__main__":
    unittest.main()
