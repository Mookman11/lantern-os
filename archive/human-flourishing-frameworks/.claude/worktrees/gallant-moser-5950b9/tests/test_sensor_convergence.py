"""Regression tests for HFF sensor convergence boundaries.

These tests keep sensor terminology aligned with the public-surface policy:
sensor definitions are not live observation, and live observation is not personal
monitoring or device enrollment.
"""

from pathlib import Path
import unittest

import app as hff_app
import live_sensors


ROOT = Path(__file__).resolve().parents[1]


class SensorConvergenceTests(unittest.TestCase):
    def test_live_sensors_default_disabled(self):
        self.assertFalse(hff_app.ENABLE_LIVE_SENSORS)
        self.assertFalse(hff_app.ENABLE_MESH_SYNC)
        self.assertFalse(hff_app.ALLOW_PUBLIC_WRITES)

    def test_current_sensor_definitions_are_public_aggregate_only(self):
        sensors = live_sensors.create_live_sensors()
        sensor_ids = {sensor.sensor_id for sensor in sensors}
        self.assertEqual(
            sensor_ids,
            {
                "wb-life-expectancy",
                "wb-infant-mortality",
                "wb-maternal-mortality",
                "wb-gdp-per-capita",
                "wb-gini-index",
                "wb-adult-literacy",
                "wb-co2-per-capita",
                "wb-forest-area",
                "wb-protected-areas",
            },
        )
        self.assertTrue(all(sensor.sensor_id.startswith("wb-") for sensor in sensors))

    def test_sensor_convergence_doc_defines_boundaries(self):
        text = (ROOT / "docs" / "sensor-convergence.md").read_text(encoding="utf-8")
        required = [
            "sensor definition != live observation",
            "live observation != personal monitoring",
            "aggregate public-data polling != device enrollment",
            "signal != person",
            "signal != proof of inner state",
            "ENABLE_LIVE_SENSORS=false",
            "ENABLE_MESH_SYNC=false",
            "HFF_ALLOW_PUBLIC_WRITES=false",
            "live sensors: disabled",
            "9 sensor definitions available",
        ]
        for phrase in required:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_operator_webcam_p0_is_visible_bounded_and_not_background_capture(self):
        text = (ROOT / "docs" / "sensor-convergence.md").read_text(encoding="utf-8")
        required = [
            "Operator webcam session | P0 operator-owned readiness",
            "visible preview",
            "hard off switch",
            "fresh consent each session",
            "no hidden monitoring",
            "no background capture",
            "stale status is not live camera truth",
        ]
        for phrase in required:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_public_surface_policy_still_blocks_sensitive_sensor_paths(self):
        text = (ROOT / "docs" / "public-surface-policy.md").read_text(encoding="utf-8")
        required = [
            "Live sensors | Disabled by default",
            "People do not \"have sensors\" as objects attached to them.",
            "Protected minor device/sensor pilot",
            "No hidden telemetry",
            "sensor = person",
            "signal = proof",
        ]
        for phrase in required:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
