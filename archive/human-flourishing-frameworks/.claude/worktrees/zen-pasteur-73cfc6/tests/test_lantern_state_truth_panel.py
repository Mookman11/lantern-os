"""Read-only truth panel tests for Lantern state slice."""

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class LanternStateTruthPanelTests(unittest.TestCase):
    def setUp(self):
        from lantern import server as lantern_server
        lantern_server.app.config["TESTING"] = True
        self.client = lantern_server.app.test_client()

    def test_health_reports_state_endpoint_wired_but_substrate_unwired(self):
        response = self.client.get("/api/lantern/health")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data.get("state_endpoint_wired"))
        self.assertFalse(data.get("substrate_wired"))

    def test_state_endpoint_reports_read_only_repo_truth(self):
        response = self.client.get("/api/lantern/state")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()

        self.assertEqual(data.get("status"), "ok")
        self.assertEqual(data.get("state_status"), "ok")
        self.assertTrue(data.get("truth_panel_wired"))

        repo = data.get("repo") or {}
        for key in (
            "status",
            "path",
            "branch",
            "commit",
            "commit_short",
            "dirty",
            "dirty_status",
            "status_short",
            "errors",
        ):
            with self.subTest(key=key):
                self.assertIn(key, repo)

        self.assertIsInstance(repo.get("status_short"), list)
        self.assertIsInstance(repo.get("errors"), list)

    def test_state_endpoint_names_evidence_and_limits(self):
        response = self.client.get("/api/lantern/state")
        data = response.get_json()

        self.assertIn("timestamp_utc", data)
        self.assertIn("loaded_doctrine", data)
        self.assertIn("last_test", data)
        self.assertIn("local_llm_context", data)
        self.assertIn("limits", data)

        self.assertIn("docs/lantern-chat-design.md", data.get("loaded_doctrine") or [])
        self.assertIsInstance(data.get("last_test"), dict)
        self.assertIsInstance(data.get("local_llm_context"), dict)
        self.assertTrue(any(
            "read-only" in limit
            for limit in (data.get("limits") or [])
        ))

    def test_state_slice_does_not_shell_out_or_write_repo(self):
        source = (ROOT / "lantern" / "server.py").read_text(encoding="utf-8")
        self.assertNotIn("subprocess", source)
        self.assertNotIn("shell=True", source)
        self.assertNotIn("git status", source)
        self.assertNotIn("git pull", source)
        self.assertNotIn("git reset", source)
        self.assertNotIn("git clean", source)


if __name__ == "__main__":
    unittest.main()
