#!/usr/bin/env python3
"""Tests for the default-closed operator device telemetry API."""

import unittest

import werkzeug
from flask import Flask

if not hasattr(werkzeug, "__version__"):
    werkzeug.__version__ = "test"

from operator_device_api import (  # noqa: E402
    DEVICE_TOKEN_HEADER,
    LatestDeviceTelemetryStore,
    create_device_telemetry_blueprint,
)


class OperatorDeviceApiTest(unittest.TestCase):
    def _client(self, tokens=None, store=None):
        tokens = tokens or {"device": "device-secret", "write": "write-secret"}
        store = store or LatestDeviceTelemetryStore()
        app = Flask(__name__)
        app.register_blueprint(
            create_device_telemetry_blueprint(
                store=store,
                token_provider=lambda: tokens,
            )
        )
        return app.test_client(), store

    def _valid_payload(self, **overrides):
        payload = {
            "device_id": "alex-iphone-001",
            "device_kind": "phone",
            "device_label": "Alex iPhone",
            "battery_level": 77,
            "battery_state": "charging",
            "power_state": "charging",
            "network_state": "wifi",
            "manual_mode": "working",
            "client_version": "device-heartbeat-v1",
            "operator_note": "manual check-in",
        }
        payload.update(overrides)
        return payload

    def test_heartbeat_is_closed_without_token(self):
        client, store = self._client()

        response = client.post(
            "/api/operator/device/heartbeat",
            json=self._valid_payload(),
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.get_json()["error"], "device_telemetry_grant_required")
        self.assertIsNone(store.get_latest())

    def test_heartbeat_accepts_device_bearer_token(self):
        client, store = self._client()

        response = client.post(
            "/api/operator/device/heartbeat",
            json=self._valid_payload(),
            headers={"Authorization": "Bearer device-secret"},
        )

        self.assertEqual(response.status_code, 200)
        body = response.get_json()
        self.assertEqual(body["status"], "accepted")
        self.assertEqual(body["telemetry"]["device_id"], "alex-iphone-001")
        self.assertEqual(body["telemetry"]["device_kind"], "phone")
        self.assertEqual(body["telemetry"]["battery_level"], 77)
        self.assertEqual(store.get_latest()["telemetry"]["client_version"], "device-heartbeat-v1")

    def test_heartbeat_accepts_device_header_token(self):
        client, _store = self._client()

        response = client.post(
            "/api/operator/device/heartbeat",
            json=self._valid_payload(device_kind="laptop", device_label="Alex Laptop"),
            headers={DEVICE_TOKEN_HEADER: "device-secret"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["telemetry"]["device_kind"], "laptop")

    def test_heartbeat_accepts_write_token_fallback(self):
        client, _store = self._client()

        response = client.post(
            "/api/operator/device/heartbeat",
            json=self._valid_payload(device_kind="raspberry_pi", device_label="Desk Pi"),
            headers={"X-HFF-Write-Token": "write-secret"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["telemetry"]["device_kind"], "raspberry_pi")

    def test_heartbeat_rejects_private_location_and_health_fields(self):
        client, store = self._client()

        response = client.post(
            "/api/operator/device/heartbeat",
            json=self._valid_payload(latitude=40.0, health_steps=1000),
            headers={"Authorization": "Bearer device-secret"},
        )

        self.assertEqual(response.status_code, 400)
        body = response.get_json()
        self.assertEqual(body["error"], "invalid_device_telemetry")
        self.assertIn("latitude", body["message"])
        self.assertIn("health_steps", body["message"])
        self.assertIsNone(store.get_latest())

    def test_heartbeat_rejects_non_object_json(self):
        client, store = self._client()

        response = client.post(
            "/api/operator/device/heartbeat",
            json=["not", "an", "object"],
            headers={"Authorization": "Bearer device-secret"},
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["error"], "json_object_required")
        self.assertIsNone(store.get_latest())

    def test_latest_returns_empty_until_heartbeat(self):
        client, _store = self._client()

        response = client.get("/api/operator/device/latest")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"status": "empty", "telemetry": None})

    def test_latest_returns_only_sanitized_latest_heartbeat(self):
        client, _store = self._client()
        client.post(
            "/api/operator/device/heartbeat",
            json=self._valid_payload(device_id="first", battery_level=10),
            headers={"Authorization": "Bearer device-secret"},
        )
        client.post(
            "/api/operator/device/heartbeat",
            json=self._valid_payload(device_id="second", battery_level=90),
            headers={"Authorization": "Bearer device-secret"},
        )

        response = client.get("/api/operator/device/latest")

        self.assertEqual(response.status_code, 200)
        body = response.get_json()
        self.assertEqual(body["status"], "ok")
        self.assertEqual(body["telemetry"]["device_id"], "second")
        self.assertEqual(body["telemetry"]["battery_level"], 90)
        self.assertNotIn("token", body["telemetry"])
        self.assertNotIn("latitude", body["telemetry"])
        self.assertNotIn("health_steps", body["telemetry"])


if __name__ == "__main__":
    unittest.main()
