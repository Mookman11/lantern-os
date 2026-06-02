import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "apps" / "lake-of-helpers-painter" / "index.html"


class LakeOfHelpersPainterTests(unittest.TestCase):
    def setUp(self):
        self.text = APP.read_text(encoding="utf-8")
        self.normalized = re.sub(r"\s+", " ", self.text)
        self.lower = self.text.lower()

    def assert_phrase(self, phrase: str) -> None:
        self.assertIn(re.sub(r"\s+", " ", phrase), self.normalized)

    def test_painter_names_the_lake_and_quantum_dust(self):
        for phrase in (
            "Lake of Helpers Painter",
            "quantum dust",
            "calm lake",
            "500 years, one step at a time",
            "every Mississippi",
        ):
            with self.subTest(phrase=phrase):
                self.assert_phrase(phrase)

    def test_painter_is_real_canvas_tool(self):
        for phrase in (
            "<canvas",
            "paintLake",
            "paintDust",
            "paintHelper",
            "clearCanvas",
            "saveSnapshot",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.text)

    def test_painter_has_no_network_sensor_or_hidden_storage(self):
        for blocked in (
            "fetch(",
            "XMLHttpRequest",
            "WebSocket",
            "EventSource",
            "getUserMedia",
            "geolocation",
            "localStorage",
            "sessionStorage",
            "api.openai",
        ):
            with self.subTest(blocked=blocked):
                self.assertNotIn(blocked.lower(), self.lower)

    def test_painter_preserves_boundaries(self):
        for phrase in (
            "offline art surface",
            "no camera",
            "no microphone",
            "no hidden telemetry",
            "not proof of infinity",
            "not autonomous",
        ):
            with self.subTest(phrase=phrase):
                self.assert_phrase(phrase)


if __name__ == "__main__":
    unittest.main()

