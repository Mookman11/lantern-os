"""Pre-public hardening gate tests.

These tests keep public expansion blocked until the runtime surface remains
truthful, default-closed, and bounded.

Issue: #84
Anchor: Harden before public. Show the state. Say the limit.
"""

import unittest

import app as hff_app


class PrePublicHardeningTests(unittest.TestCase):
    def setUp(self):
        self.client = hff_app.app.test_client()

    def test_healthz_exposes_default_closed_runtime_toggles(self):
        response = self.client.get("/healthz")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data.get("status"), "ok")
        self.assertIs(data.get("live_sensors_enabled"), False)
        self.assertIs(data.get("mesh_sync_enabled"), False)
        self.assertIs(data.get("public_writes_enabled"), False)

    def test_dashboard_preserves_advisory_non_authority_boundary(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        text = response.get_data(as_text=True)
        self.assertIn("Research Software", text)
        self.assertIn(
            "not a human board, regulator, court, enforcement system, or autonomous authority",
            text,
        )

    def test_dashboard_preserves_visible_degraded_state_copy(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        text = response.get_data(as_text=True)
        self.assertIn("Some dashboard data is temporarily unavailable", text)
        self.assertIn("verify deployment health with the public health endpoint", text)

    def test_dashboard_does_not_imply_live_observation_from_registry(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        text = response.get_data(as_text=True)
        self.assertIn("registered sensors", text.lower())
        self.assertIn("Registry presence is not proof of", text)
        self.assertNotIn(">Live Sensors</h2>", text)
        self.assertNotIn("Live Sensors</div>", text)

    def test_unknown_public_write_surface_is_not_available(self):
        response = self.client.post("/api/violations", json={"test": "blocked"})
        self.assertIn(response.status_code, {403, 404})
        if response.status_code == 403:
            data = response.get_json()
            self.assertEqual(data.get("error"), "write_grant_required")

    def test_adoption_write_endpoint_rejects_unauthenticated_heartbeat(self):
        response = self.client.post(
            "/api/adoption/register",
            json={
                "node_id": "pre-public-hardening-test",
                "node_name": "Pre Public Hardening Test",
                "platform": "unit_test",
            },
        )
        self.assertEqual(response.status_code, 403)
        data = response.get_json()
        self.assertEqual(data.get("error"), "adoption_grant_required")


if __name__ == "__main__":
    unittest.main()
