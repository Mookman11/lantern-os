"""Tests for safe opt-in background mode."""

import os
import unittest
from unittest.mock import patch

from background_mode import (
    BackgroundModeController,
    MAX_BACKGROUND_WINDOW_HOURS,
    bounded_window_hours,
    create_background_controller_from_env,
)
import safe_app


class BackgroundModeControllerTests(unittest.TestCase):
    def test_disabled_by_default_from_env(self):
        with patch.dict(os.environ, {}, clear=True):
            controller = create_background_controller_from_env()
        self.assertFalse(controller.enabled)
        self.assertFalse(controller.start())
        snapshot = controller.snapshot()
        self.assertFalse(snapshot["enabled"])
        self.assertFalse(snapshot["running"])
        self.assertEqual(snapshot["mode"], "disabled")
        self.assertEqual(snapshot["window"]["target_hours"], 8.0)
        self.assertEqual(snapshot["window"]["goal"], "8_hour_background_window")

    def test_window_hours_default_to_eight_and_clamp_to_safe_bound(self):
        self.assertEqual(bounded_window_hours(None), 8.0)
        self.assertEqual(bounded_window_hours(""), 8.0)
        self.assertEqual(bounded_window_hours("0"), 8.0)
        self.assertEqual(bounded_window_hours("-1"), 8.0)
        self.assertEqual(bounded_window_hours("2"), 2.0)
        self.assertEqual(bounded_window_hours("12"), MAX_BACKGROUND_WINDOW_HOURS)

    def test_controller_from_env_uses_window_hours_without_exceeding_eight(self):
        with patch.dict(
            os.environ,
            {
                "HFF_BACKGROUND_MODE": "true",
                "HFF_BACKGROUND_INTERVAL_SECONDS": "2",
                "HFF_BACKGROUND_WINDOW_HOURS": "12",
            },
            clear=True,
        ):
            controller = create_background_controller_from_env()
        self.assertTrue(controller.enabled)
        self.assertEqual(controller.interval_seconds, 2.0)
        self.assertEqual(controller.window_hours, 8.0)

    def test_heartbeat_only_mode_has_no_side_effects(self):
        controller = BackgroundModeController(enabled=True, interval_seconds=1.0)
        self.assertTrue(controller.start())
        controller.tick()
        snapshot = controller.snapshot()
        controller.stop()

        self.assertTrue(snapshot["enabled"])
        self.assertTrue(snapshot["running"])
        self.assertEqual(snapshot["mode"], "heartbeat_only")
        self.assertGreaterEqual(snapshot["tick_count"], 1)
        self.assertEqual(snapshot["window"]["target_hours"], 8.0)
        self.assertEqual(snapshot["window"]["max_hours"], 8.0)
        self.assertEqual(snapshot["window"]["goal"], "8_hour_background_window")
        self.assertLessEqual(
            snapshot["window"]["remaining_seconds"],
            snapshot["window"]["target_seconds"],
        )
        self.assertEqual(
            snapshot["side_effects"],
            {
                "network": False,
                "live_sensors": False,
                "mesh_sync": False,
                "public_writes": False,
                "personal_data": False,
                "device_or_actuator_control": False,
            },
        )

    def test_background_window_completes_without_side_effects(self):
        controller = BackgroundModeController(
            enabled=True,
            interval_seconds=1.0,
            window_hours=0.000001,
        )
        self.assertTrue(controller.start())
        controller._started_monotonic -= 1.0
        controller.tick()
        snapshot = controller.snapshot()
        controller.stop()

        self.assertEqual(snapshot["mode"], "completed")
        self.assertEqual(snapshot["window"]["state"], "completed")
        self.assertEqual(snapshot["window"]["remaining_seconds"], 0.0)
        self.assertFalse(snapshot["side_effects"]["network"])
        self.assertFalse(snapshot["side_effects"]["public_writes"])

    def test_background_status_route_visible_and_default_safe(self):
        client = safe_app.app.test_client()
        response = client.get("/background/status")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("background_mode", data)
        mode = data["background_mode"]
        self.assertFalse(mode["enabled"])
        self.assertFalse(mode["running"])
        self.assertEqual(mode["mode"], "disabled")
        self.assertEqual(mode["window"]["goal"], "8_hour_background_window")
        self.assertEqual(mode["window"]["max_hours"], 8.0)
        self.assertFalse(mode["side_effects"]["network"])
        self.assertFalse(mode["side_effects"]["live_sensors"])
        self.assertFalse(mode["side_effects"]["mesh_sync"])
        self.assertFalse(mode["side_effects"]["public_writes"])
        self.assertFalse(mode["side_effects"]["personal_data"])
        self.assertFalse(mode["side_effects"]["device_or_actuator_control"])


if __name__ == "__main__":
    unittest.main()
