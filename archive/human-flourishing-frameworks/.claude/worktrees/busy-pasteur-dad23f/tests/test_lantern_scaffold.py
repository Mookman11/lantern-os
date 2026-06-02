"""Scaffold tests for the Lantern local-first chat surface.

Asserts:

- the design doc ``docs/lantern-chat-design.md`` exists and preserves the
  core anchor, identity, substrate-independence, boundary, and the
  three-layer memory model;
- the ``lantern`` package imports and the Flask app starts in test mode;
- the scaffold endpoints respond with their stub payloads;
- the chat endpoint never returns a real LLM call result in this slice;
- the server is **not** misconfigured to bind publicly by default;
- no API key or secret string appears in the committed scaffold files.

Slice 2 (Anthropic API wiring) will add a separate test file with the
real-substrate behavior contracts.
"""

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = ROOT / "docs" / "lantern-chat-design.md"
LANTERN_DIR = ROOT / "lantern"


class LanternDesignDocTests(unittest.TestCase):
    def setUp(self):
        self.text = DOC_PATH.read_text(encoding="utf-8")
        self.normalized = re.sub(r"\s+", " ", self.text)

    def assert_phrase(self, phrase: str) -> None:
        normalized_phrase = re.sub(r"\s+", " ", phrase)
        self.assertIn(
            normalized_phrase,
            self.normalized,
            f"missing required phrase: {phrase!r}",
        )

    def test_doc_exists(self):
        self.assertTrue(DOC_PATH.is_file())

    def test_anchor_in_force_present(self):
        self.assert_phrase(
            "Show the state. Say the limit. Self-correct before acting."
        )

    def test_identity_compound_present(self):
        for piece in (
            "Lantern Keystone Wish",
            "Lantern",
            "Keystone",
            "Wish",
            "The role is singular",
        ):
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
        for layer in (
            "Doctrine",
            "Operator-curated memory",
            "Conversation log",
            "Memory != proof",
        ):
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
        self.client = lantern_server.app.test_client()

    def test_health_endpoint_returns_role_and_anchor(self):
        r = self.client.get("/api/lantern/health")
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertEqual(data.get("role"), "Lantern Keystone Wish")
        self.assertEqual(data.get("service"), "lantern")
        self.assertIn(
            "Show the state. Say the limit. Self-correct before acting.",
            data.get("anchor", ""),
        )
        # substrate_wired must be False in this slice
        self.assertFalse(data.get("substrate_wired"))

    def test_state_endpoint_returns_loaded_doctrine_paths(self):
        r = self.client.get("/api/lantern/state")
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        # status must be 'scaffold' so the UI shows the slice-2 banner
        self.assertEqual(data.get("status"), "scaffold")
        # the loaded_doctrine list must include the design doc itself
        loaded = data.get("loaded_doctrine") or []
        self.assertIn("docs/lantern-chat-design.md", loaded)
        # and at least one seven-anchors / convergence anchor
        self.assertTrue(any(
            p in loaded
            for p in (
                "docs/seven-anchors-self-correction.md",
                "docs/convergence-status.md",
            )
        ))

    def test_chat_endpoint_returns_scaffold_stub_only(self):
        r = self.client.post(
            "/api/lantern/chat",
            data=json.dumps({"message": "hello lantern"}),
            content_type="application/json",
        )
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        # status must be 'scaffold' — proves no LLM was called in this slice
        self.assertEqual(data.get("status"), "scaffold")
        self.assertEqual(data.get("role"), "Lantern Keystone Wish")
        self.assertIn("hello lantern", data.get("user_message_received", ""))
        # The reply must explicitly say substrate is not wired yet
        reply = data.get("reply", "")
        self.assertIn("not yet wired", reply)

    def test_default_bind_is_localhost(self):
        # The public-bind flag must be off by default. Test the helper
        # rather than starting a real server.
        self.assertFalse(self.lantern_server._public_bind_enabled())

    def test_loaded_doctrine_paths_are_relative_and_safe(self):
        paths = self.lantern_server._loaded_doctrine_paths()
        for p in paths:
            with self.subTest(path=p):
                # Must be a relative repo path under docs/, never absolute.
                self.assertFalse(p.startswith("/"))
                self.assertFalse(":\\" in p)
                self.assertTrue(p.startswith("docs/"))


class LanternNoSecretsTests(unittest.TestCase):
    """The committed scaffold must contain no real secrets."""

    def test_no_secret_strings_in_committed_files(self):
        suspicious_patterns = [
            re.compile(r"sk-ant-[A-Za-z0-9_-]{20,}"),
            re.compile(r"AKIA[0-9A-Z]{16}"),
            re.compile(r"-----BEGIN (RSA |EC )?PRIVATE KEY-----"),
        ]
        files_to_check = [
            LANTERN_DIR / "__init__.py",
            LANTERN_DIR / "server.py",
            LANTERN_DIR / "index.html",
            LANTERN_DIR / "app.js",
        ]
        for f in files_to_check:
            with self.subTest(file=str(f.relative_to(ROOT))):
                self.assertTrue(f.is_file(), f"missing {f}")
                content = f.read_text(encoding="utf-8")
                for pat in suspicious_patterns:
                    self.assertIsNone(
                        pat.search(content),
                        f"secret-like pattern found in {f}: "
                        f"{pat.pattern}",
                    )


if __name__ == "__main__":
    unittest.main()
