#!/usr/bin/env python3
"""Contract test for the operator-facing live polling readiness checklist."""

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = ROOT / "docs" / "live-polling-readiness.md"


class LivePollingReadinessDocTest(unittest.TestCase):
    def test_readiness_doc_exists_and_names_runtime_checks(self):
        self.assertTrue(DOC_PATH.exists(), "docs/live-polling-readiness.md is required")

        text = DOC_PATH.read_text(encoding="utf-8")
        required_fragments = [
            "ENABLE_LIVE_SENSORS=true",
            "/api/world/status",
            "live_observation_status",
            "status_reason",
            "last_error_count",
            "ran_with_updates",
            "failed",
            "PBFT consensus is not required for live polling to start",
            "teaching/research-grade",
        ]

        for fragment in required_fragments:
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, text)

    def test_readiness_doc_preserves_operator_status_reason_table(self):
        text = DOC_PATH.read_text(encoding="utf-8")
        statuses = [
            "not_enabled",
            "registered_not_run",
            "running",
            "ran_no_measurements",
            "ran_with_measurements_no_updates",
            "ran_with_updates",
            "failed",
        ]

        for status in statuses:
            with self.subTest(status=status):
                self.assertIn(status, text)


if __name__ == "__main__":
    unittest.main()
