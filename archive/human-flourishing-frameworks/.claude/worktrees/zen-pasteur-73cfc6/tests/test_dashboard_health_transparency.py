"""Regression tests for dashboard health and transparency posture.

These tests assert:
- core public routes (`/`, `/health`, `/healthz`, `/api/status`) respond;
- the `/healthz` payload exposes the public-write/sensor/mesh toggles so
  deployment platforms can see capability state without reading copy;
- the dashboard uses ``registered sensors`` language rather than the
  prior ``Live Sensors`` framing that implied always-on observation;
- the dashboard ships visible degraded-state copy so silent fetch
  failures cannot leave the page blank without explanation;
- the public dashboard preserves the advisory/research boundary.
"""

import unittest

import app as hff_app


class DashboardHealthTransparencyTests(unittest.TestCase):
    def setUp(self):
        self.client = hff_app.app.test_client()

    def test_dashboard_renders(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        text = response.get_data(as_text=True)
        self.assertIn("Human Flourishing Frameworks", text)
        self.assertIn("Research Software", text)
        self.assertIn(
            "not a human board, regulator, court, enforcement system, or autonomous authority",
            text,
        )

    def test_health_route_returns_json(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.get_json(), dict)

    def test_healthz_route_returns_json(self):
        response = self.client.get("/healthz")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data.get("status"), "ok")
        self.assertIn("live_sensors_enabled", data)
        self.assertIn("mesh_sync_enabled", data)
        self.assertIn("public_writes_enabled", data)

    def test_api_status_route_returns_json(self):
        response = self.client.get("/api/status")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.get_json(), dict)

    def test_dashboard_uses_registered_sensor_language(self):
        response = self.client.get("/")
        text = response.get_data(as_text=True)
        self.assertIn("registered sensors", text.lower())
        self.assertNotIn("Live Sensors</div>", text)
        self.assertNotIn(">Live Sensors</h2>", text)

    def test_dashboard_has_degraded_state_text(self):
        response = self.client.get("/")
        text = response.get_data(as_text=True)
        self.assertIn("Some dashboard data is temporarily unavailable", text)


if __name__ == "__main__":
    unittest.main()
