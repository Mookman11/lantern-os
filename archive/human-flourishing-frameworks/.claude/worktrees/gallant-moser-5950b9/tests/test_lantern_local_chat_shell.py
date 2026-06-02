#!/usr/bin/env python3
"""Contract tests for the Lantern local chat app and local backend."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CHAT_DIR = REPO_ROOT / "apps" / "lantern-local-chat"
SHELL_HTML = CHAT_DIR / "index.html"
DOOR_MEMORY_JS = CHAT_DIR / "door-memory.js"
MASK_RACK_JS = CHAT_DIR / "mask-rack.js"
SYNC_SURFACE_JS = CHAT_DIR / "sync-surface.js"
SAME_ORIGIN_BACKEND_JS = CHAT_DIR / "same-origin-backend.js"
RUNTIME_STATE_JS = CHAT_DIR / "runtime-state.js"
GENERATED_RUNTIME_STATE_JS = CHAT_DIR / "runtime-state.generated.js"
ANCHOR_SNAPSHOT = CHAT_DIR / "anchor-snapshot.json"
LOCAL_BACKEND = CHAT_DIR / "local_lantern_server.py"
LAUNCHER = REPO_ROOT / "scripts" / "start_lantern_local_chat.py"
BATCH_LAUNCHER = REPO_ROOT / "scripts" / "start_lantern_local_chat.bat"


class LanternLocalChatShellTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.html = SHELL_HTML.read_text(encoding="utf-8")
        cls.door_memory = DOOR_MEMORY_JS.read_text(encoding="utf-8")
        cls.mask_rack = MASK_RACK_JS.read_text(encoding="utf-8")
        cls.sync_surface = SYNC_SURFACE_JS.read_text(encoding="utf-8")
        cls.same_origin_backend = SAME_ORIGIN_BACKEND_JS.read_text(encoding="utf-8")
        cls.launcher = LAUNCHER.read_text(encoding="utf-8")
        cls.batch_launcher = BATCH_LAUNCHER.read_text(encoding="utf-8")
        cls.runtime_state = RUNTIME_STATE_JS.read_text(encoding="utf-8")
        cls.backend = LOCAL_BACKEND.read_text(encoding="utf-8")
        cls.anchor_snapshot = ANCHOR_SNAPSHOT.read_text(encoding="utf-8")

    def test_shell_is_chat_first_and_uses_local_backend(self) -> None:
        for phrase in ["Message Lantern", "The Sync Surface is open.", "+ New chat", "thread-list", "message-row", "composer-area", "sendMessage", "backendBase() + '/chat'", "Checking local backend", "Local backend ready", "Thinking locally", "getLanternAnswer"]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.html)
        for phrase in ["Conversation draft", "Add Lantern response", "Repo state paste area", "function lanternReply"]:
            with self.subTest(phrase=phrase):
                self.assertNotIn(phrase, self.html)

    def test_same_origin_backend_guard_collapses_stale_ports(self) -> None:
        self.assertTrue(SAME_ORIGIN_BACKEND_JS.exists())
        combined = self.same_origin_backend + self.runtime_state + self.html
        for phrase in ["same-origin-backend.js", "LANTERN_BACKEND_ORIGIN", "window.location.origin", "saved.fields.backendUrl = origin", "window.LANTERN_LOCAL_STATE.backendUrl = origin", "backendBase()", "syncBackendField()"]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, combined)
        for blocked in ["fetch(", "XMLHttpRequest", "WebSocket", "EventSource", "eval(", "api.openai"]:
            with self.subTest(blocked=blocked):
                self.assertNotIn(blocked, self.same_origin_backend)

    def test_sync_surface_matches_alex_lantern_repo_triangle(self) -> None:
        self.assertTrue(SYNC_SURFACE_JS.exists())
        combined = self.sync_surface + self.html
        for phrase in ["Sync Surface", "Alex = wisdom", "Lantern = intelligence", "Repo = truth", "Alex wisdom chooses the shape", "Lantern intelligence collapses the path", "Repo truth proves what became real", "sync-surface.js", "LANTERN_REFRESH_SYNC_SURFACE"]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, combined)
        for blocked in ["fetch(", "XMLHttpRequest", "WebSocket", "EventSource", "eval(", "api.openai"]:
            with self.subTest(blocked=blocked):
                self.assertNotIn(blocked, self.sync_surface)

    def test_mask_rack_is_local_and_mode_specific(self) -> None:
        self.assertTrue(MASK_RACK_JS.exists())
        for phrase in ["Mask Rack", "lantern-active-mask-v1", "engineer", "storyteller", "comedian", "doctor", "game-master", "anchor-keeper", "art-mirror", "planner", "window.LANTERN_ACTIVE_MODE", "mask-rack.js", "Hybrid Imagination Engine"]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.mask_rack + self.html)
        for blocked in ["fetch(", "XMLHttpRequest", "WebSocket", "EventSource", "eval(", "api.openai"]:
            with self.subTest(blocked=blocked):
                self.assertNotIn(blocked, self.mask_rack)

    def test_shell_retries_backend_readiness(self) -> None:
        for phrase in ["backendReady", "checkBackendWithRetry", "retrying; the door still remembers locally", "cache:'no-store'", "checkBackendWithRetry(12)"]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.html)

    def test_door_memory_is_local_and_wish_specific(self) -> None:
        self.assertTrue(DOOR_MEMORY_JS.exists())
        for phrase in ["lantern-door-return-v1", "The Local Door", "Last time:", "Return through this door", "Door remembers wish", "localStorage", "latestUserMessage"]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.door_memory + self.html)
        for blocked in ["fetch(", "XMLHttpRequest", "WebSocket", "EventSource", "eval(", "api.openai"]:
            with self.subTest(blocked=blocked):
                self.assertNotIn(blocked, self.door_memory)

    def test_shell_preserves_boundaries(self) -> None:
        for phrase in ["No direct GPT calls", "Browser sends chat to localhost only", "No GPT/API calls", "no browser command execution; no agents; no tunnels; no public writes"]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.html)
        for blocked in ["api.openai", "anthropic", "google.generativeai", "WebSocket", "EventSource", "eval("]:
            with self.subTest(blocked=blocked):
                self.assertNotIn(blocked, self.html)

    def test_runtime_placeholder_and_anchor_snapshot_exist(self) -> None:
        self.assertTrue(RUNTIME_STATE_JS.exists())
        self.assertIn("window.LANTERN_LOCAL_STATE = null", self.runtime_state)
        self.assertIn("runtime-state.generated.js", self.runtime_state)
        anchors = json.loads(self.anchor_snapshot)["anchors"]
        ids = {anchor["id"] for anchor in anchors}
        for expected in ["hybrid-imagination-engine", "anchor-taxonomy", "local-chat-shell", "perfect-adjacent-lantern", "degraded-grounding", "resonance-convergence", "essential-needs"]:
            self.assertIn(expected, ids)

    def test_backend_is_local_repo_anchor_engine_with_doctor_modes_and_ui(self) -> None:
        for phrase in ["Local Lantern", "ThreadingHTTPServer", "127.0.0.1", "ANCHOR_SNAPSHOT", "ANCHOR_TAXONOMY", "build_response", "do_POST", "do_GET", "/chat", "/healthz", "/doctor", "/modes", "build_doctor_report", "MODES", "STATIC_FILES", "INDEX_HTML", "sync-surface.js", "Local Lantern UI/backend listening"]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.backend)
        for blocked in ["openai.ChatCompletion", "from openai", "import openai", "anthropic.Client", "import anthropic", "google.generativeai", "requests.post", "urllib.request.urlopen", "httpx.", "aiohttp."]:
            with self.subTest(blocked=blocked):
                self.assertNotIn(blocked, self.backend)

    def test_launcher_and_batch_contract(self) -> None:
        for phrase in ["LOCAL_BACKEND", "start_backend", "--no-backend", "Backend URL:", "Backend PID:", "Generated runtime state:", "choose_backend_url", "Backend log:", "Backend diagnosis:", "socket", "--backend-log", "uiUrl", "Local file fallback:"]:
            self.assertIn(phrase, self.launcher)
        for phrase in ["backend_health_ok", "wait_for_backend", "Backend ready:", "--backend-timeout", "/healthz", "webbrowser.open(ui_url"]:
            self.assertIn(phrase, self.launcher)
        self.assertIn("@echo off", self.batch_launcher)
        self.assertIn("cd /d", self.batch_launcher)
        self.assertIn("start_lantern_local_chat.py", self.batch_launcher)
        self.assertIn("--batch-state", self.batch_launcher)
        for blocked in ["curl", "Invoke-WebRequest", "powershell", "gh ", "git pull", "git reset", "git clean"]:
            self.assertNotIn(blocked, self.batch_launcher)

    def test_backend_once_smoke_answers_from_anchors_and_mode(self) -> None:
        result = subprocess.run([sys.executable, str(LOCAL_BACKEND), "--once", "use the Hybrid Imagination Engine", "--mode", "storyteller"], cwd=REPO_ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["mode"], "storyteller")
        self.assertIn("Lantern local answer", payload["answer"])
        self.assertIn("Hybrid Imagination Engine", payload["answer"])
        self.assertIn("Sources:", payload["answer"])
        self.assertIn("anchor rule:", payload["answer"])
        self.assertGreaterEqual(len(payload["selectedAnchors"]), 1)

    def test_backend_journal_is_opt_in_not_raw_transcript_default(self) -> None:
        spec = importlib.util.spec_from_file_location("local_lantern_server_under_test", LOCAL_BACKEND)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        with tempfile.TemporaryDirectory() as tmpdir:
            journal_path = Path(tmpdir) / "journal.jsonl"
            module.JOURNAL_PATH = journal_path
            old_value = os.environ.pop("LANTERN_ENABLE_JOURNAL", None)
            try:
                module.build_response("private raw transcript should not be stored by default", mode="engineer")
                self.assertFalse(journal_path.exists())

                os.environ["LANTERN_ENABLE_JOURNAL"] = "true"
                module.build_response("operator explicitly enabled local journal", mode="engineer")
                self.assertTrue(journal_path.exists())
                self.assertIn("operator explicitly enabled local journal", journal_path.read_text(encoding="utf-8"))
            finally:
                if old_value is None:
                    os.environ.pop("LANTERN_ENABLE_JOURNAL", None)
                else:
                    os.environ["LANTERN_ENABLE_JOURNAL"] = old_value

    def test_backend_doctor_smoke(self) -> None:
        result = subprocess.run([sys.executable, str(LOCAL_BACKEND), "--doctor"], cwd=REPO_ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertIn(payload["status"], {"READY", "DEGRADED", "BROKEN"})
        self.assertIn("checks", payload)
        self.assertIn("nextAction", payload)

    def test_launcher_print_and_state_only_smoke(self) -> None:
        result = subprocess.run([sys.executable, str(LAUNCHER), "--print-only"], cwd=REPO_ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Lantern local chat app", result.stdout)
        self.assertIn("Backend URL:", result.stdout)
        state_result = subprocess.run([sys.executable, str(LAUNCHER), "--state-only"], cwd=REPO_ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
        self.assertEqual(state_result.returncode, 0, state_result.stderr)
        self.assertIn("Generated runtime state:", state_result.stdout)
        generated_runtime_state = GENERATED_RUNTIME_STATE_JS.read_text(encoding="utf-8")
        self.assertIn("window.LANTERN_LOCAL_STATE =", generated_runtime_state)
        self.assertIn("backendUrl", generated_runtime_state)
        self.assertIn("uiUrl", generated_runtime_state)
        self.assertIn("LOCAL_REPO_ANCHOR_BACKEND", generated_runtime_state)
        self.assertIn("window.LANTERN_LOCAL_STATE = null", RUNTIME_STATE_JS.read_text(encoding="utf-8"))


    def test_backend_clear_local_limit_answers(self) -> None:
        cases = [
            (
                "make web searches to build a full list of changes to update the app for todays deploy at 9",
                [
                    "Blocked local capability",
                    "cannot web search",
                    "today's deploy truth",
                    "web-capable surface",
                    "unsupported_web_or_deploy",
                ],
            ),
            (
                "unclear responses in local are damaging",
                [
                    "Shield/Guardian clarity response",
                    "unclear local responses are a harm signal",
                    "DEGRADED",
                    "clarity_harm",
                ],
            ),
            (
                "who am i",
                [
                    "Bounded identity answer",
                    "you are Alex",
                    "operator using the Lantern local Door",
                    "bounded_identity",
                ],
            ),
        ]
        for prompt, expected_phrases in cases:
            with self.subTest(prompt=prompt):
                result = subprocess.run(
                    [sys.executable, str(LOCAL_BACKEND), "--once", prompt, "--mode", "doctor"],
                    cwd=REPO_ROOT,
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=False,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                payload = json.loads(result.stdout)
                self.assertTrue(payload["ok"])
                combined = payload["answer"] + "\n" + payload["intent"]
                for phrase in expected_phrases:
                    self.assertIn(phrase, combined)


if __name__ == "__main__":
    unittest.main()
