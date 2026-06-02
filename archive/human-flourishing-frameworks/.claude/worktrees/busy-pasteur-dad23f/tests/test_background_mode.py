"""Tests for safe opt-in background mode."""

import os
import time
import unittest
from unittest.mock import patch

from background_mode import BackgroundModeController, create_background_controller_from_env
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
        self.assertFalse(mode["side_effects"]["network"])
        self.assertFalse(mode["side_effects"]["live_sensors"])
        self.assertFalse(mode["side_effects"]["mesh_sync"])
        self.assertFalse(mode["side_effects"]["public_writes"])
        self.assertFalse(mode["side_effects"]["personal_data"])
        self.assertFalse(mode["side_effects"]["device_or_actuator_control"])


if __name__ == "__main__":
    unittest.main()
