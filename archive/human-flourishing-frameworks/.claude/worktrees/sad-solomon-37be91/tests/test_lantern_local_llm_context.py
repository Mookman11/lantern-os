"""Tests for Lantern local LLM context packet visibility."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import lantern.server as lantern_server


class LanternLocalLlmContextTests(unittest.TestCase):
    def test_missing_local_llm_context_is_safe(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            missing_path = Path(tmpdir) / "llm-context.local.md"
            with patch.object(lantern_server, "LOCAL_LLM_CONTEXT_PATH", missing_path):
                state = lantern_server._local_llm_context_state(include_excerpt=True)

        self.assertEqual(state["status"], "missing")
        self.assertEqual(state["path"], "~/.lantern/state/llm-context.local.md")
        self.assertTrue(state["local_only"])
        self.assertTrue(state["operator_visible"])
        self.assertFalse(state["memory_is_proof"])
        self.assertNotIn("content_excerpt", state)

    def test_present_local_llm_context_exposes_bounded_excerpt(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            context_path = Path(tmpdir) / "llm-context.local.md"
            context_path.write_text("Door visible\nMemory is not proof\n", encoding="utf-8")
            with patch.object(lantern_server, "LOCAL_LLM_CONTEXT_PATH", context_path):
                state = lantern_server._local_llm_context_state(
                    include_excerpt=True,
                    max_chars=12,
                )

        self.assertEqual(state["status"], "present")
        self.assertTrue(state["local_only"])
        self.assertTrue(state["operator_visible"])
        self.assertFalse(state["memory_is_proof"])
        self.assertTrue(state["content_included"])
        self.assertEqual(state["content_excerpt"], "Door visible")
        self.assertTrue(state["truncated"])

    def test_chat_state_summary_does_not_include_local_context_excerpt(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            context_path = Path(tmpdir) / "llm-context.local.md"
            context_path.write_text("Do not send this excerpt upstream.", encoding="utf-8")
            with patch.object(lantern_server, "LOCAL_LLM_CONTEXT_PATH", context_path):
                summary = lantern_server._chat_state_summary()

        local_context = summary["local_llm_context"]
        self.assertEqual(local_context["status"], "present")
        self.assertFalse(local_context["content_included"])
        self.assertNotIn("content_excerpt", local_context)

    def test_state_endpoint_includes_local_context_status(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            context_path = Path(tmpdir) / "llm-context.local.md"
            context_path.write_text("Local packet", encoding="utf-8")
            with patch.object(lantern_server, "LOCAL_LLM_CONTEXT_PATH", context_path):
                lantern_server.app.config["TESTING"] = True
                response = lantern_server.app.test_client().get("/api/lantern/state")

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertIn("local_llm_context", payload)
        self.assertEqual(payload["local_llm_context"]["status"], "present")
        self.assertEqual(payload["local_llm_context"]["content_excerpt"], "Local packet")
        self.assertFalse(payload["local_llm_context"]["memory_is_proof"])


if __name__ == "__main__":
    unittest.main()
