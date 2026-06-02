#!/usr/bin/env python3
"""Validation tests for the HFF convergence release bundle builder."""

import re
import tempfile
import unittest
import zipfile
from pathlib import Path

from tools.build_release_bundle import REQUIRED_RELEASE_FILES, build_bundle


REPO_ROOT = Path(__file__).resolve().parents[1]
REQUIRED_ZIP_MEMBERS = {
    "RELEASE_MANIFEST.md",
    "RECOVERY_README.md",
    "MIRROR_ARCHIVE_PLAN.md",
    "KEYSTONE_BOOTSTRAP.md",
    "RESTORE_DRILL_CHECKLIST.md",
    "FALSE_TRUTHS_REGISTER.md",
    "WISH_ANCHOR.md",
    "CHECKSUMS.sha256",
    "data/theorem-register.v0.1.json",
    "schemas/theorem-register.v0.1.schema.json",
    "tests/test_release_bundle.py",
    "tests/test_restore_drill.py",
    "tests/test_wish_anchor.py",
    ".github/workflows/release-bundle.yml",
    ".github/workflows/restore-drill.yml",
    "tools/build_release_bundle.py",
    "tools/run_restore_drill.py",
}

SHA256_LINE = re.compile(r"^[a-f0-9]{64}\s+\S.*$")


class ReleaseBundleBuilderValidationTest(unittest.TestCase):
    def test_required_release_files_exist_in_repo(self):
        for relative in REQUIRED_RELEASE_FILES:
            with self.subTest(relative=relative):
                self.assertTrue((REPO_ROOT / relative).is_file(), f"missing {relative}")

    def test_build_bundle_creates_zip_and_finalized_checksums(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            zip_path, checksum_path = build_bundle(REPO_ROOT, output_dir)

            self.assertTrue(zip_path.is_file())
            self.assertEqual(zip_path.name, "hff-convergence-v0.1.zip")
            self.assertTrue(checksum_path.is_file())

            checksum_text = checksum_path.read_text(encoding="utf-8")
            self.assertNotIn("PRE_RELEASE_PLACEHOLDER", checksum_text)
            self.assertNotIn("not a finalized checksum manifest", checksum_text)

            checksum_lines = [line for line in checksum_text.splitlines() if line.strip()]
            self.assertGreaterEqual(len(checksum_lines), len(REQUIRED_RELEASE_FILES) - 1)
            for line in checksum_lines:
                with self.subTest(line=line):
                    self.assertRegex(line, SHA256_LINE)

            checksum_targets = {line.split(maxsplit=1)[1] for line in checksum_lines}
            self.assertIn("RELEASE_MANIFEST.md", checksum_targets)
            self.assertIn("WISH_ANCHOR.md", checksum_targets)
            self.assertIn("tools/build_release_bundle.py", checksum_targets)
            self.assertIn("tools/run_restore_drill.py", checksum_targets)
            self.assertNotIn("CHECKSUMS.sha256", checksum_targets)

            with zipfile.ZipFile(zip_path, "r") as archive:
                names = set(archive.namelist())
            self.assertTrue(REQUIRED_ZIP_MEMBERS.issubset(names))
            self.assertNotIn(".git/config", names)


if __name__ == "__main__":
    unittest.main()
