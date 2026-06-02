"""Regression tests for public dashboard authority claims.

The live Docker entrypoint currently uses safe_app:app. These tests ensure the
entrypoint sanitizes the known false-authority dashboard copy before serving the
public template.
"""

import unittest

import safe_app


class SafePublicCopyTest(unittest.TestCase):
    def test_safe_entrypoint_removes_false_governance_claims(self):
        template = safe_app._app_module.HTML_TEMPLATE

        forbidden = [
            "ALGORITHMIC GOVERNANCE",
            "No human board",
            "irreversible after a 24-hour lock",
        ]

        for phrase in forbidden:
            with self.subTest(phrase=phrase):
                self.assertNotIn(phrase, template)

    def test_safe_entrypoint_keeps_advisory_operator_review_language(self):
        template = safe_app._app_module.HTML_TEMPLATE

        required = [
            "EXPERIMENTAL ADVISORY AGENTS",
            "not a human board, regulator, court, enforcement system, or autonomous authority",
            "Escalations are review records only unless explicitly authorized by an operator",
        ]

        for phrase in required:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, template)

    def test_safe_entrypoint_omits_synthetic_violations_demo(self):
        template = safe_app._app_module.HTML_TEMPLATE

        forbidden = [
            "DEMO DATA",
            "Synthetic Violations",
            "violations-section",
            "violations-list",
            "violation-count",
            "Demo System Alpha",
            "Test Healthcare AI",
            "Example Hiring Screener",
            "Demo Recidivism Scorer",
            "Affected (simulated)",
        ]

        for phrase in forbidden:
            with self.subTest(phrase=phrase):
                self.assertNotIn(phrase, template)


if __name__ == "__main__":
    unittest.main()
