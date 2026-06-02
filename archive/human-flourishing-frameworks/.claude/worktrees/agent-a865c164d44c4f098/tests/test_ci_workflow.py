#!/usr/bin/env python3
"""Guardrails for the convergence-validation GitHub Actions workflow."""

import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "convergence-validation.yml"
RESTORE_WORKFLOW = REPO_ROOT / ".github" / "workflows" / "restore-drill.yml"

REQUIRED_TEST_COMMANDS = [
    'python -m unittest discover -s tests -p "test_theorem_register.py" -t .',
    'python -m unittest discover -s tests -p "test_schema_source_lore.py" -t .',
    'python -m unittest discover -s tests -p "test_recovery_artifacts.py" -t .',
    'python -m unittest discover -s tests -p "test_ci_workflow.py" -t .',
    'python -m unittest discover -s tests -p "test_release_artifacts.py" -t .',
    'python -m unittest discover -s tests -p "test_release_bundle.py" -t .',
    'python -m unittest discover -s tests -p "test_restore_drill.py" -t .',
    'python -m unittest discover -s tests -p "test_wish_anchor.py" -t .',
]


class CIWorkflowValidationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = WORKFLOW.read_text(encoding="utf-8")
        cls.lowered = cls.text.lower()
        cls.restore_text = RESTORE_WORKFLOW.read_text(encoding="utf-8")

    def test_workflow_file_exists(self):
        self.assertTrue(WORKFLOW.exists())
        self.assertGreater(WORKFLOW.stat().st_size, 500)

    def test_workflow_runs_on_pr_push_and_manual_dispatch(self):
        self.assertIn("pull_request:", self.text)
        self.assertIn("push:", self.text)
        self.assertIn("workflow_dispatch:", self.text)
        self.assertIn("- master", self.text)

    def test_workflow_has_read_only_contents_permission(self):
        self.assertIn("permissions:", self.text)
        self.assertIn("contents: read", self.text)

    def test_workflow_uses_python_and_checkout_actions(self):
        self.assertIn("uses: actions/checkout@v4", self.text)
        self.assertIn("uses: actions/setup-python@v6", self.text)
        self.assertIn("python-version: '3.12'", self.text)

    def test_workflow_runs_all_guardrail_suites(self):
        for command in REQUIRED_TEST_COMMANDS:
            with self.subTest(command=command):
                self.assertIn(command, self.text)

    def test_workflow_has_timeout(self):
        self.assertIn("timeout-minutes: 15", self.text)

    def test_restore_drill_workflow_exists_and_uploads_report(self):
        self.assertTrue(RESTORE_WORKFLOW.exists())
        self.assertIn("workflow_dispatch:", self.restore_text)
        self.assertIn("python tools/run_restore_drill.py --output-dir dist", self.restore_text)
        self.assertIn("dist/RESTORE_DRILL_REPORT.md", self.restore_text)
        self.assertIn("actions/upload-artifact@v4", self.restore_text)


if __name__ == "__main__":
    unittest.main()
