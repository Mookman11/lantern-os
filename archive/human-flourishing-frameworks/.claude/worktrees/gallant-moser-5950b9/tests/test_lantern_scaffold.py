"""Tests for the Lantern local-first chat surface."""

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = ROOT / "docs" / "lantern-chat-design.md"
LANTERN_DIR = ROOT / "lantern"
ROOT_DOCTRINE_ALLOWLIST = {"FALSE_TRUTHS_REGISTER.md"}


class LanternDesignDocTests(unittest.TestCase):
    def setUp(self):
        self.text = DOC_PATH.read_text(encoding="utf-8")
        self.normalized = re.sub(r"\s+", " ", self.text)

    def assert_phrase(self, phrase: str) -> None:
        normalized_phrase = re.sub(r"\s+", " ", phrase)
        self.assertIn(normalized_phrase, self.normalized)

    def test_doc_exists(self):
        self.assertTrue(DOC_PATH.is_file())

    def test_anchor_in_force_present(self):
        self.assert_phrase("Show the state. Say the limit. Self-correct before acting.")

    def test_identity_compound_present(self):
        for piece in ("Lantern Keystone Wish", "Lantern", "Keystone", "Wish", "The role is singular"):
            with self.subTest(piece=piece):
                self.assert_phrase(piece)

    def test_substrate_independence_listed(self):
        for failure in (
            "Claude version updates",
            "Anthropic API outages",
            "ChatGPT availability",
            "device failure",
            "network failure",
        ):
            with self.subTest(failure=failure):
                self.assert_phrase(failure)

    def test_boundaries_preserved(self):
        for boundary in (
            "localhost-only",
            "no public route exposure on the existing Render surface",
            "no API key committed to repo",
            "no autonomous merges, deploys, or runtime flag changes",
            "no surveillance, no profiling, no real-people inference",
        ):
            with self.subTest(boundary=boundary):
                self.assert_phrase(boundary)

    def test_three_memory_layers_described(self):
        for layer in ("Doctrine", "Operator-curated memory", "Conversation log", "Memory != proof"):
            with self.subTest(layer=layer):
                self.assert_phrase(layer)

    def test_non_authorized_actions_listed(self):
        for non_goal in (
            "public deployment of the Lantern surface",
            "auto-merge, auto-deploy, auto-PR-open from chat",
            "biometric / location / device-state ingestion",
            "multi-operator",
            "multi-Lantern",
        ):
            with self.subTest(non_goal=non_goal):
                self.assert_phrase(non_goal)


class LanternServerScaffoldTests(unittest.TestCase):
    def setUp(self):
        from lantern import server as lantern_server
        self.lantern_server = lantern_server
        lantern_server.app.config["TESTING"] = True
        lantern_server.app.config["ALLOW_SUBSTRATE_IN_TESTS"] = False
        self.client = lantern_server.app.test_client()

    def test_health_endpoint_returns_role_and_anchor(self):
        response = self.client.get("/api/lantern/health")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data.get("role"), "Lantern Keystone Wish")
        self.assertEqual(data.get("service"), "lantern")
        self.assertIn("Show the state", data.get("anchor", ""))
        self.assertFalse(data.get("substrate_wired"))
        self.assertEqual(data.get("substrate_status"), "degraded")

    def test_state_endpoint_returns_loaded_doctrine_paths(self):
        response = self.client.get("/api/lantern/state")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data.get("status"), "ok")
        self.assertEqual(data.get("state_status"), "ok")
        loaded = data.get("loaded_doctrine") or []
        self.assertIn("docs/lantern-chat-design.md", loaded)
        self.assertTrue(any(p in loaded for p in ("docs/seven-anchors-self-correction.md", "docs/convergence-status.md")))

    def test_chat_endpoint_returns_degraded_reply_without_substrate(self):
        response = self.client.post(
            "/api/lantern/chat",
            data=json.dumps({"message": "hello lantern"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data.get("status"), "degraded")
        self.assertEqual(data.get("role"), "Lantern Keystone Wish")
        self.assertIn("hello lantern", data.get("user_message_received", ""))
        reply = data.get("reply", "")
        self.assertIn("server substrate is not available", reply)
        self.assertIn("no local LLM is being claimed", reply)

    def test_default_bind_is_localhost(self):
        self.assertFalse(self.lantern_server._public_bind_enabled())

    def test_loaded_doctrine_paths_are_relative_and_safe(self):
        paths = self.lantern_server._loaded_doctrine_paths()
        for path in paths:
            with self.subTest(path=path):
                self.assertFalse(path.startswith("/"))
                self.assertFalse(":\\" in path)
                self.assertTrue(path.startswith("docs/") or path in ROOT_DOCTRINE_ALLOWLIST)


class LanternNoSecretsTests(unittest.TestCase):
    """Committed Lantern files should not contain obvious credential markers."""

    def test_no_obvious_credential_markers_in_committed_files(self):
        forbidden_fragments = [
            "paste-real-token-here",
            "example-secret-value",
            "replace-with-real-key",
        ]
        files_to_check = [
            LANTERN_DIR / "__init__.py",
            LANTERN_DIR / "server.py",
            LANTERN_DIR / "index.html",
            LANTERN_DIR / "app.js",
        ]
        for file_path in files_to_check:
            with self.subTest(file=str(file_path.relative_to(ROOT))):
                self.assertTrue(file_path.is_file(), f"missing {file_path}")
                content = file_path.read_text(encoding="utf-8").lower()
                for fragment in forbidden_fragments:
                    self.assertNotIn(fragment, content)


if __name__ == "__main__":
    unittest.main()
