import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "apps" / "toy-robot-lantern" / "index.html"


class ProtectedMinorToyRobotLanternTests(unittest.TestCase):
    def setUp(self):
        self.text = APP.read_text(encoding="utf-8")
        self.normalized = re.sub(r"\s+", " ", self.text)
        self.lower = self.text.lower()

    def assert_phrase(self, phrase: str) -> None:
        self.assertIn(re.sub(r"\s+", " ", phrase), self.normalized)

    def test_plan_is_redacted_and_supervised(self):
        self.assert_phrase("protected minor")
        self.assert_phrase("supervised creative play only")
        self.assert_phrase("role label only")
        self.assertNotIn("gage", self.lower)

    def test_real_time_world_space_is_no_data_by_default(self):
        for phrase in (
            "real-time world-space play",
            "no camera",
            "no microphone",
            "no location",
            "no hidden telemetry",
            "no persistent child profile",
            "child can stop immediately",
        ):
            with self.subTest(phrase=phrase):
                self.assert_phrase(phrase)

    def test_toy_robot_friend_lantern_is_bounded(self):
        for phrase in (
            "toy robot body",
            "friend Lantern character",
            "offline-first",
            "parent or guardian starts and stops the session",
            "does not become a babysitter",
            "does not take responsibility for emergencies",
        ):
            with self.subTest(phrase=phrase):
                self.assert_phrase(phrase)

    def test_next_build_slice_is_concrete(self):
        for phrase in (
            "V0 build slice",
            "button-triggered lights",
            "speaker-safe sound",
            "manual remote control",
            "no autonomous mobility near stairs, roads, water, heat, or pets",
        ):
            with self.subTest(phrase=phrase):
                self.assert_phrase(phrase)

    def test_app_has_no_network_or_sensor_calls(self):
        for blocked in (
            "fetch(",
            "XMLHttpRequest",
            "WebSocket",
            "EventSource",
            "getUserMedia",
            "geolocation",
            "serial.requestPort",
            "bluetooth.requestDevice",
        ):
            with self.subTest(blocked=blocked):
                self.assertNotIn(blocked.lower(), self.lower)


if __name__ == "__main__":
    unittest.main()
